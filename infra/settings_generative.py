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
import pathlib
import textwrap

import datarobot as dr
import pulumi_datarobot as datarobot
from datarobotx.idp.custom_metrics import get_update_or_create_custom_metric
from jinja2 import BaseLoader, Environment

from infra.common.globals import GlobalRuntimeEnvironment
from infra.common.schema import (
    BaselineValues,
    CustomMetricArgs,
    CustomModelArgs,
    DeploymentArgs,
    RegisteredModelArgs,
)
from nbo.schema import GenerativeDeploymentSettings, association_id

from .settings_main import (
    default_prediction_server_id,
    project_name,
)

generative_deployment_path = pathlib.Path("deployment_generative/")

custom_model_args = CustomModelArgs(
    resource_name=f"Generative Custom Model [{project_name}]",
    name=f"Generative Custom Model [{project_name}]",
    base_environment_id=GlobalRuntimeEnvironment.PYTHON_311_GENAI.value.id,
    target_name=GenerativeDeploymentSettings().target_feature_name,
    target_type=dr.enums.TARGET_TYPE.TEXT_GENERATION,
)


registered_model_args = RegisteredModelArgs(
    resource_name=f"Generative Registered Model [{project_name}]",
)

deployment_args = DeploymentArgs(
    resource_name=f"Generative Deployment [{project_name}]",
    label=f"Generative Deployment [{project_name}]",
    association_id_settings=datarobot.DeploymentAssociationIdSettingsArgs(
        column_names=[association_id],
        auto_generate_id=False,
        required_in_prediction_requests=True,
    ),
    predictions_settings=(
        None
        if default_prediction_server_id
        else datarobot.DeploymentPredictionsSettingsArgs(
            min_computes=0, max_computes=1, real_time=True
        )
    ),
    predictions_data_collection_settings=datarobot.DeploymentPredictionsDataCollectionSettingsArgs(
        enabled=True,
    ),
)


def get_files(
    runtime_parameter_values: list[datarobot.CustomModelRuntimeParameterValueArgs],
) -> list[tuple[str, str]]:
    llm_runtime_parameter_specs = "\n".join(
        [
            textwrap.dedent(
                f"""\
            - fieldName: {param.key}
              type: {param.type}"""
            )
            for param in runtime_parameter_values
        ]
    )

    with open(generative_deployment_path / "model-metadata.yaml.jinja") as f:
        template = Environment(loader=BaseLoader()).from_string(f.read())
    with open(generative_deployment_path / "model-metadata.yaml", "w") as f:
        runtime_parameters = template.render(
            custom_model_name=custom_model_args.name,
            target_type=custom_model_args.target_type,
            runtime_parameters=llm_runtime_parameter_specs,
        )
        f.write(runtime_parameters)

    files = [
        (str(f), str(f.relative_to(generative_deployment_path)))
        for f in generative_deployment_path.glob("**/*")
        if f.is_file() and f.name not in ("README.md", "model-metadata.yaml.jinja")
    ] + [
        (
            "nbo/__init__.py",
            "nbo/__init__.py",
        ),
        ("nbo/schema.py", "nbo/schema.py"),
        ("nbo/credentials.py", "nbo/credentials.py"),
    ]
    return files


custom_metrics = {
    "confidence": CustomMetricArgs(
        name="Confidence",
        description="Confidence Score",
        baseline_values=[BaselineValues(value=0.65)],
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Score",
    ),
    "llm_cost": CustomMetricArgs(
        name="LLM Cost",
        description="Tracks the total cost of the LLM. For this deployment, cost is reported directly from OpenAI",
        baseline_values=[BaselineValues(value=0.025)],
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Dollars",
    ),
    "sentiment": CustomMetricArgs(
        name="Sentiment",
        description="Sentiment Score",
        baseline_values=[BaselineValues(value=0.3)],
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Score",
    ),
    "reading_time": CustomMetricArgs(
        name="Reading Time",
        description="Estimated Reading Time",
        baseline_values=[BaselineValues(value=75)],
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Seconds",
    ),
    "readability_level": CustomMetricArgs(
        name="Readability",
        description="Readability Level",
        baseline_values=[BaselineValues(value=50)],
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Score",
    ),
    "response_token_count": CustomMetricArgs(
        name="Response Token Count",
        description="Number of LLM app response tokens",
        baseline_values=[BaselineValues(value=225)],
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Count",
    ),
    "prompt_token_count": CustomMetricArgs(
        name="Prompt Token Count",
        description="Number of LLM app prompt tokens",
        baseline_values=[BaselineValues(value=225)],
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Count",
    ),
    "user_feedback": CustomMetricArgs(
        name="User Feedback",
        description="User provided rating of the generated email",
        baseline_values=[BaselineValues(value=0.75)],
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        is_model_specific=False,
        type=dr.enums.CustomMetricAggregationType.AVERAGE,
        units="Upvotes",
    ),
}

custom_metric_baselines = {
    metric_name: cm.baseline_values[0]["value"]
    for metric_name, cm in custom_metrics.items()
    if cm.baseline_values
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
