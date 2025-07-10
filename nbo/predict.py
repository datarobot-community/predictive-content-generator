# Copyright 2024 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

import datarobot as dr
import pandas as pd
from datarobot.models.deployment.deployment import Deployment
from datarobot_predict.deployment import (
    PredictionResult,
)
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import ValidationError

from nbo.resources import GenerativeDeployment, PredAIDeployment
from nbo.schema import Generation, LLMRequest, Prediction  # noqa: E402

logger = logging.getLogger(__name__)

try:
    pred_ai_deployment_id = PredAIDeployment().id
    generative_deployment_id = GenerativeDeployment().id
    logger.info(f"Pred AI deployment: {pred_ai_deployment_id}")
    logger.info(f"Email LLM deployment: {generative_deployment_id}")
except ValidationError as e:
    raise ValueError(
        (
            "Unable to load DataRobot deployment ids. If running locally, verify you have selected "
            "the correct stack and that it is active using `pulumi stack output`. "
            "If running in DataRobot, verify your runtime parameters have been set correctly."
        )
    ) from e


@dataclass
class DeploymentInfo:
    deployment: Deployment
    target_name: str


def _get_deployment_info(deployment_id: str) -> DeploymentInfo:
    deployment = dr.Deployment.get(deployment_id)
    target_name = deployment.model["target_name"]  # type: ignore[index]
    return DeploymentInfo(deployment, str(target_name))


def make_pred_ai_deployment_predictions(
    df: pd.DataFrame, max_explanations: Optional[int] = None
) -> list[Prediction]:
    deployment_info = _get_deployment_info(pred_ai_deployment_id)
    deployment = deployment_info.deployment
    target_name = deployment_info.target_name
    # TODO: remove once datarobot-predict supports maxNgramExplanations
    from datarobot_predict.deployment import _deployment_predict, _read_response_csv

    params: Dict[str, Any] = (
        {
            "maxExplanations": max_explanations,
            "maxNgramExplanations": "all",
        }
        if max_explanations
        else {}
    )

    headers: Dict[str, str] = {}

    response = _deployment_predict(
        deployment=deployment,
        endpoint="predictions",
        headers=headers,
        params=params,
        data=df,
        stream=False,
        timeout=600,
        prediction_endpoint=None,
    )
    prediction_result = PredictionResult(_read_response_csv(response), response.headers)
    prediction = prediction_result.dataframe
    prediction = prediction.rename(columns={f"{target_name}_PREDICTION": "prediction"})
    prediction.columns = prediction.columns.str.replace(
        "_(PREDICTION|OUTPUT)$", "", regex=True
    )
    return [
        Prediction.parse_dict(p, target_name)
        for p in prediction.to_dict(orient="records")
    ]


def extract_association_id_from_completion(response: ChatCompletion) -> str:
    """
    Extract the returned DataRobot association ID from the ChatCompletion response.
    If all attempts fail, generate a new association ID.
    """
    model_extra = response.model_extra
    if model_extra is None:
        model_extra = {}

    # Check for direct association ID first
    # If the generative deployment execution environment includes datarobot-drum>=1.16.16,
    # there should be a datarobot_association_id returned.
    returned_association_id = model_extra.get("datarobot_association_id")
    if returned_association_id is not None:
        return cast(str, returned_association_id)

    # Check moderations for association ID
    # If the generative deployment is running with datarobot-drum<1.16.16,
    # the association ID is only returned when moderations are enabled.
    datarobot_moderations = model_extra.get("datarobot_moderations", {})
    returned_association_id = datarobot_moderations.get("association_id")
    if returned_association_id is not None:
        return cast(str, returned_association_id)

    # Generate new association ID as fallback
    # In this case we have no choice but to generate a new association ID,
    # as we have exhausted our methods for extracting it from the output.
    return str(uuid.uuid4())


def make_generative_deployment_predictions(
    requests: list[LLMRequest],
) -> list[Generation]:
    deployment_info = _get_deployment_info(generative_deployment_id)
    deployment = deployment_info.deployment
    dr_client = dr.client.get_client()

    openai_client = OpenAI(
        base_url=f"{dr_client.endpoint.rstrip('/')}/deployments/{deployment.id}",
        api_key=dr_client.token,
    )
    result = []

    for llm_request in requests:
        response = openai_client.chat.completions.create(
            model="datarobot-deployed-llm",
            messages=[
                {"role": "system", "content": llm_request.system_prompt},
                {"role": "user", "content": llm_request.prompt},
            ],
        )
        association_id = extract_association_id_from_completion(response)
        generation = Generation(
            content=response.choices[0].message.content,
            prompt_used=llm_request.prompt,
            association_id=association_id,
        )

        result.append(generation)

    return result
