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

import json

import datarobot as dr
import pulumi_datarobot as datarobot
from datarobotx.idp.custom_metrics import get_update_or_create_custom_metric

from infra.common.globals import GlobalLLM, GlobalRuntimeEnvironment
from infra.common.schema import (
    BaselineValues,
    CustomMetricArgs,
    CustomModelArgs,
    DeploymentArgs,
    LLMBlueprintArgs,
    PlaygroundArgs,
    RegisteredModelArgs,
)
from nbo.custom_metrics import CustomMetric, metrics_manager
from nbo.schema import GenerativeDeploymentSettings, association_id

from .settings_main import (
    default_prediction_server_id,
    project_name,
)

LLM = GlobalLLM.AZURE_OPENAI_GPT_4_O

playground_args = PlaygroundArgs(
    resource_name=f"Predictive Content Generator Playground [{project_name}]",
)


llm_blueprint_args = LLMBlueprintArgs(
    resource_name=f"Predictive Content Generator LLM Blueprint [{project_name}]",
    llm_id=LLM.name,
    llm_settings=datarobot.LlmBlueprintLlmSettingsArgs(
        max_completion_length=512,
        temperature=0.5,
    ),
)

custom_model_args = CustomModelArgs(
    resource_name=f"Predictive Content Generator Generative Model [{project_name}]",
    name=f"Predictive Content Generator Generative Model [{project_name}]",
    base_environment_id=GlobalRuntimeEnvironment.PYTHON_311_MODERATIONS.value.id,
    target_name=GenerativeDeploymentSettings().target_feature_name,
    target_type=dr.enums.TARGET_TYPE.TEXT_GENERATION,
)


registered_model_args = RegisteredModelArgs(
    resource_name=f"Predictive Content Generator Generative Model [{project_name}]",
)

deployment_args = DeploymentArgs(
    resource_name=f"Predictive Content Generator Generative Deployment [{project_name}]",
    label=f"Predictive Content Generator Generative Deployment [{project_name}]",
    association_id_settings=datarobot.DeploymentAssociationIdSettingsArgs(
        column_names=[association_id],
        auto_generate_id=False,
        required_in_prediction_requests=True,
    ),
    predictions_settings=(
        None
        if default_prediction_server_id
        else datarobot.DeploymentPredictionsSettingsArgs(min_computes=0, max_computes=1)
    ),
    predictions_data_collection_settings=datarobot.DeploymentPredictionsDataCollectionSettingsArgs(
        enabled=True,
    ),
)


def to_custom_metric_args(metric: CustomMetric) -> CustomMetricArgs:
    """Convert to DataRobot CustomMetricArgs format"""
    return CustomMetricArgs(
        name=metric.name,
        description=metric.description,
        baseline_values=[BaselineValues(value=metric.baseline_value)],
        directionality=metric.directionality,
        is_model_specific=metric.is_model_specific,
        type=metric.aggregation_type,
        units=metric.units,
    )


custom_metrics = {
    k: to_custom_metric_args(v) for k, v in metrics_manager.metrics.items()
}


def set_custom_metrics(deployment_id: str) -> str:
    client = dr.client.get_client()
    custom_metric_ids = {}
    for metric in custom_metrics:
        custom_metric_ids[metric] = get_update_or_create_custom_metric(
            endpoint=client.endpoint,
            token=client.token,
            deployment_id=deployment_id,
            **custom_metrics[metric].model_dump(mode="json", exclude_none=True),
        )
    return json.dumps(custom_metric_ids)
