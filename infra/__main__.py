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
import os
import pathlib
import sys
import textwrap

import datarobot as dr
import papermill as pm
import pulumi
import pulumi_datarobot as datarobot
import yaml
from datarobot_pulumi_utils.common import check_feature_flags
from datarobot_pulumi_utils.pulumi.custom_model_deployment import CustomModelDeployment
from datarobot_pulumi_utils.pulumi.proxy_llm_blueprint import ProxyLLMBlueprint
from datarobot_pulumi_utils.schema.llms import LLMs

sys.path.append("..")

from infra import (
    settings_app_infra,
    settings_generative,
    settings_main,
    settings_predictive,
)
from infra.settings_proxy_llm import CHAT_MODEL_NAME
from nbo.credentials import DRCredentials
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
from utils.credentials import (
    get_credential_runtime_parameter_values,
    get_credentials,
)

TEXTGEN_DEPLOYMENT_ID = os.environ.get("TEXTGEN_DEPLOYMENT_ID")
TEXTGEN_REGISTERED_MODEL_ID = os.environ.get("TEXTGEN_REGISTERED_MODEL_ID")

if settings_generative.LLM == LLMs.DEPLOYED_LLM:
    pulumi.info(f"{TEXTGEN_DEPLOYMENT_ID=}")
    pulumi.info(f"{TEXTGEN_REGISTERED_MODEL_ID=}")
    if (TEXTGEN_DEPLOYMENT_ID is None) == (TEXTGEN_REGISTERED_MODEL_ID is None):  # XOR
        raise ValueError(
            "Either TEXTGEN_DEPLOYMENT_ID or TEXTGEN_REGISTERED_MODEL_ID must be set when using a deployed LLM. Plese check your .env file"
        )

LocaleSettings().setup_locale()

check_feature_flags(pathlib.Path("feature_flag_requirements.yaml"))

if not (
    settings_main.model_training_output_infra_settings.exists()
    and settings_main.model_training_output_ds_settings.exists()
):
    pulumi.info(f"Executing model training notebook {settings_main.model_training_nb}")
    try:
        pm.execute_notebook(
            settings_main.model_training_nb,
            output_path=None,
            cwd=settings_main.model_training_nb.parent,
            log_output=False,
            progress_bar=False,
            stderr_file=sys.stderr,
            stdout_file=sys.stdout,
        )
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

credentials: DRCredentials | None

try:
    credentials = get_credentials(settings_generative.LLM)
except ValueError:
    raise
except TypeError:
    pulumi.warn(
        textwrap.dedent("""\
        Failed to find credentials for LLM. Continuing deployment without LLM support.

        If you intended to provide credentials, please consult the Readme and follow the instructions.
        """)
    )
    credentials = None

credentials_runtime_parameters_values = get_credential_runtime_parameter_values(
    credentials=credentials
)

playground = datarobot.Playground(
    use_case_id=use_case.id,
    **settings_generative.playground_args.model_dump(),
)

if settings_generative.LLM == LLMs.DEPLOYED_LLM:
    if TEXTGEN_REGISTERED_MODEL_ID is not None:
        proxy_llm_registered_model = datarobot.RegisteredModel.get(
            resource_name="Existing TextGen Registered Model",
            id=TEXTGEN_REGISTERED_MODEL_ID,
        )

        proxy_llm_deployment = datarobot.Deployment(
            resource_name=f"Predictive Content Generator LLM Deployment [{settings_main.project_name}]",
            registered_model_version_id=proxy_llm_registered_model.version_id,
            prediction_environment_id=prediction_environment.id,
            label=f"Predictive Content Generator LLM Deployment [{settings_main.project_name}]",
            use_case_ids=[use_case.id],
            opts=pulumi.ResourceOptions(
                replace_on_changes=["registered_model_version_id"]
            ),
        )
    elif TEXTGEN_DEPLOYMENT_ID is not None:
        proxy_llm_deployment = datarobot.Deployment.get(
            resource_name="Existing LLM Deployment", id=TEXTGEN_DEPLOYMENT_ID
        )
    else:
        raise ValueError(
            "Either TEXTGEN_REGISTERED_MODEL_ID or TEXTGEN_DEPLOYMENT_ID have to be set in `.env`"
        )

    llm_blueprint = ProxyLLMBlueprint(
        use_case_id=use_case.id,
        playground_id=playground.id,
        proxy_llm_deployment_id=proxy_llm_deployment.id,
        chat_model_name=CHAT_MODEL_NAME,
        **settings_generative.llm_blueprint_args.model_dump(mode="python"),
    )
elif settings_generative.LLM != LLMs.DEPLOYED_LLM:
    llm_blueprint = datarobot.LlmBlueprint(  # type: ignore[assignment]
        playground_id=playground.id,
        **settings_generative.llm_blueprint_args.model_dump(),
    )

generative_custom_model = datarobot.CustomModel(
    **settings_generative.custom_model_args.model_dump(exclude_none=True),
    use_case_ids=[use_case.id],
    source_llm_blueprint_id=llm_blueprint.id,
    runtime_parameter_values=[]
    if settings_generative.LLM.name == LLMs.DEPLOYED_LLM.name
    else credentials_runtime_parameters_values,
)

generative_deployment = CustomModelDeployment(
    resource_name=f"Predictive Content Generator LLM Deployment [{settings_main.project_name}]",
    custom_model_version_id=generative_custom_model.version_id,
    registered_model_args=settings_generative.registered_model_args,
    prediction_environment=prediction_environment,
    deployment_args=settings_generative.deployment_args,
    use_case_ids=[use_case.id],
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
