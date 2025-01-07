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

import pathlib

import datarobot as dr
import pulumi
import pulumi_datarobot as datarobot
import yaml

from infra import (
    settings_app_infra,
    settings_generative,
    settings_main,
    settings_predictive,
)
from infra.common.feature_flags import check_feature_flags
from infra.common.papermill import run_notebook
from infra.components.custom_model_deployment import CustomModelDeployment
from infra.components.dr_llm_credential import (
    get_credential_runtime_parameter_values,
    get_credentials,
)
from infra.components.rag_custom_model import RAGCustomModel
from nbo.i18n import LocaleSettings
from nbo.resources import (
    app_env_name,
    custom_metric_id_env_name,
    dataset_id_env_name,
    generative_deployment_env_name,
    pred_ai_deployment_env_name,
)
from nbo.schema import AppInfraSettings
from nbo.urls import get_deployment_url

LocaleSettings().setup_locale()

check_feature_flags(pathlib.Path("infra/feature_flag_requirements.yaml"))

if not (
    settings_main.model_training_output_infra_settings.exists()
    and settings_main.model_training_output_ds_settings.exists()
):
    pulumi.info(f"Executing model training notebook {settings_main.model_training_nb}")
    try:
        run_notebook(settings_main.model_training_nb)
    except Exception as e:
        raise pulumi.RunError(
            f"Failed to execute notebook {settings_main.model_training_nb}: {e}"
        )
else:
    pulumi.info(
        f"Using existing model training outputs in '{settings_main.model_training_output_infra_settings}'"
    )
with open(settings_main.model_training_output_infra_settings) as f:
    model_training_output = AppInfraSettings(**yaml.safe_load(f))


use_case = datarobot.UseCase.get(
    id=model_training_output.use_case_id,
    resource_name="Predictive Content Generator Use Case",
)

if settings_main.default_prediction_server_id is not None:
    prediction_environment = datarobot.PredictionEnvironment.get(
        resource_name=settings_main.prediction_environment_resource_name,
        id=settings_main.default_prediction_server_id,
    )
else:
    prediction_environment = datarobot.PredictionEnvironment(
        resource_name=settings_main.prediction_environment_resource_name,
        platform=dr.enums.PredictionEnvironmentPlatform.DATAROBOT_SERVERLESS,
    )

pred_ai_deployment = datarobot.Deployment(
    registered_model_version_id=model_training_output.registered_model_version_id,
    prediction_environment_id=prediction_environment.id,
    use_case_ids=[use_case.id],
    **settings_predictive.deployment_args.model_dump(exclude_none=True),
)

credentials = get_credentials(settings_generative.LLM)

credential_runtime_parameter_values = get_credential_runtime_parameter_values(
    credentials=credentials
)


generative_custom_model = RAGCustomModel(
    resource_name=f"Predictive Content Generator Prep [{settings_main.project_name}]",
    custom_model_args=settings_generative.custom_model_args,
    llm_blueprint_args=settings_generative.llm_blueprint_args,
    playground_args=settings_generative.playground_args,
    use_case=use_case,
    runtime_parameter_values=credential_runtime_parameter_values,
)

generative_deployment = CustomModelDeployment(
    resource_name=f"Generative Custom Model Deployment [{settings_main.project_name}]",
    custom_model_version_id=generative_custom_model.version_id,
    registered_model_args=settings_generative.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_generative.deployment_args,
    use_case_ids=[model_training_output.use_case_id],
)


custom_metrics = generative_deployment.id.apply(settings_generative.set_custom_metrics)

app_runtime_parameters = [
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=generative_deployment_env_name,
        type="deployment",
        value=generative_deployment.id,
    ),
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=pred_ai_deployment_env_name,
        type="deployment",
        value=pred_ai_deployment.id,
    ),
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=custom_metric_id_env_name,
        type="string",
        value=custom_metrics,
    ),
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key=dataset_id_env_name,
        type="string",
        value=model_training_output.scoring_dataset_id,
    ),
    datarobot.ApplicationSourceRuntimeParameterValueArgs(
        key="APP_LOCALE", type="string", value=LocaleSettings().app_locale
    ),
]

app_source = datarobot.ApplicationSource(
    files=settings_app_infra.get_app_files(
        runtime_parameter_values=app_runtime_parameters
    ),
    runtime_parameter_values=app_runtime_parameters,
    **settings_app_infra.app_source_args,
)

app = datarobot.CustomApplication(
    resource_name=settings_app_infra.app_resource_name,
    source_version_id=app_source.version_id,
    use_case_ids=[model_training_output.use_case_id],
)

app.id.apply(settings_app_infra.ensure_app_settings)

pulumi.export(generative_deployment_env_name, generative_deployment.id)
pulumi.export(pred_ai_deployment_env_name, pred_ai_deployment.id)
pulumi.export(custom_metric_id_env_name, custom_metrics)
pulumi.export(dataset_id_env_name, model_training_output.scoring_dataset_id)
pulumi.export(app_env_name, app.id)

pulumi.export(
    settings_generative.deployment_args.resource_name,
    generative_deployment.id.apply(get_deployment_url),
)
pulumi.export(
    settings_predictive.deployment_args.resource_name,
    pred_ai_deployment.id.apply(get_deployment_url),
)
pulumi.export(
    settings_app_infra.app_resource_name,
    app.application_url,
)
