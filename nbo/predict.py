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
from dataclasses import dataclass
from typing import Any, Dict, Optional

import datarobot as dr
import pandas as pd
from datarobot.models.deployment.deployment import Deployment
from datarobot_predict.deployment import (  # type: ignore[import-untyped]
    PredictionResult,
    predict,
)
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
    deployment = dr.Deployment.get(deployment_id)  # type: ignore[attr-defined]
    target_name = deployment.model["target_name"]  # type: ignore[index]
    return DeploymentInfo(deployment, str(target_name))


def make_pred_ai_deployment_predictions(
    df: pd.DataFrame, max_explanations: Optional[int] = None
) -> list[Prediction]:
    deployment_info = _get_deployment_info(pred_ai_deployment_id)
    deployment = deployment_info.deployment
    target_name = deployment_info.target_name

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


def make_generative_deployment_predictions(
    requests: list[LLMRequest],
) -> list[Generation]:
    deployment_info = _get_deployment_info(generative_deployment_id)
    deployment = deployment_info.deployment
    target_name = deployment_info.target_name
    df = pd.DataFrame(
        [request.model_dump(mode="json", by_alias=True) for request in requests]
    )

    predictions = predict(deployment, data_frame=df).dataframe

    predictions = predictions.rename(
        columns={f"{target_name}_PREDICTION": "prediction"}
    )
    predictions.columns = predictions.columns.str.replace(
        "_(PREDICTION|OUTPUT)$", "", regex=True
    )

    return [
        Generation(
            content=prediction["prediction"],
            prompt_used=request.prompt,
            association_id=request.association_id,
        )
        for prediction, request in zip(predictions.to_dict(orient="records"), requests)
    ]