# Copyright 2024 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.

from kedro.pipeline import node, Pipeline
from kedro.pipeline.modular_pipeline import pipeline

from datarobotx.idp.common.asset_resolver import (
    render_jinja_template,
    merge_asset_paths,
)
from datarobotx.idp.credentials import get_replace_or_create_credential
from datarobotx.idp.custom_models import get_or_create_custom_model
from datarobotx.idp.custom_model_versions import get_or_create_custom_model_version
from datarobotx.idp.deployments import (
    get_replace_or_create_deployment_from_registered_model,
)
from datarobotx.idp.registered_model_versions import (
    get_or_create_registered_custom_model_version,
)

from .nodes import (
    ensure_deployment_settings,
    get_update_or_create_custom_metrics,
)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            name="make_datarobot_llm_credential",
            func=get_replace_or_create_credential,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:dr_credential.name",
                "credential_type": "params:dr_credential.credential_type",
                "api_token": "params:credentials.azure_openai_llm_credentials.api_key",
            },
            outputs="dr_credential_id",
        ),
        node(
            name="make_llm_model_metadata",
            func=render_jinja_template,
            inputs={
                "template_file": "model_metadata_template",
                "custom_model_name": "params:custom_model.name",
                "credential_name": "params:dr_credential.name",
                "azure_endpoint": "params:credentials.azure_openai_llm_credentials.azure_endpoint",
                "openai_api_version": "params:credentials.azure_openai_llm_credentials.api_version",
                "prompt_feature_name": "params:custom_model.prompt_feature_name",
                "target_feature_name": "params:custom_model.target_feature_name",
            },
            outputs="model_metadata",
        ),
        node(
            name="make_llm_deployment_assets",
            func=merge_asset_paths,
            inputs=["custom_py", "model_metadata", "requirements"],
            outputs="llm_deployment_assets",
        ),
        node(
            name="make_llm_custom_model",
            func=get_or_create_custom_model,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:custom_model.name",
                "target_type": "params:custom_model.target_type",
                "target_name": "params:custom_model.target_feature_name",
            },
            outputs="custom_model_id",
        ),
        node(
            name="make_runtime_credential",
            func=lambda credential_name, credential_id: [
                {
                    "field_name": credential_name,
                    "type": "credential",
                    "value": credential_id,
                }
            ],
            inputs={
                "credential_name": "params:dr_credential.name",
                "credential_id": "dr_credential_id",
            },
            outputs="runtime_credential",
        ),
        node(
            name="make_llm_custom_model_version",
            func=get_or_create_custom_model_version,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "custom_model_id": "custom_model_id",
                "runtime_parameter_values": "runtime_credential",
                "base_environment_id": "params:custom_model.base_environment_id",
                "folder_path": "llm_deployment_assets",
            },
            outputs="custom_model_version_id",
        ),
        node(
            name="make_llm_registered_model",
            func=get_or_create_registered_custom_model_version,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "custom_model_version_id": "custom_model_version_id",
                "registered_model_name": "params:registered_model_name",
            },
            outputs="custom_model_registered_version_id",
        ),
        node(
            name="make_llm_deployment",
            func=get_replace_or_create_deployment_from_registered_model,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "registered_model_version_id": "custom_model_registered_version_id",
                "registered_model_name": "params:registered_model_name",
                "label": "params:deployment.name",
                "prediction_environment_id": "params:credentials.datarobot.prediction_environment_id",
            },
            outputs="llm_deployment_id",
        ),
        node(
            name="make_custom_metrics",
            func=get_update_or_create_custom_metrics,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "llm_deployment_id",
                "custom_metrics": "params:custom_metrics",
            },
            outputs="custom_metric_ids",
        ),
        node(
            name="ensure_deployment_settings",
            func=ensure_deployment_settings,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "llm_deployment_id",
                "association_id_column_name": "params:deployment.association_id_column_name",
            },
            outputs=None,
        ),
    ]
    pipeline_inst = pipeline(nodes)
    return pipeline(
        pipeline_inst,
        namespace="deploy_llm",
        parameters={
            "params:credentials.datarobot.endpoint": "params:credentials.datarobot.endpoint",
            "params:credentials.datarobot.api_token": "params:credentials.datarobot.api_token",
            "params:credentials.datarobot.prediction_environment_id": "params:credentials.datarobot.prediction_environment_id",
            "params:credentials.azure_openai_llm_credentials.api_key": "params:credentials.azure_openai_llm_credentials.api_key",
            "params:credentials.azure_openai_llm_credentials.azure_endpoint": "params:credentials.azure_openai_llm_credentials.azure_endpoint",
            "params:credentials.azure_openai_llm_credentials.api_version": "params:credentials.azure_openai_llm_credentials.api_version",
        },
        outputs={
            "llm_deployment_id",
            "custom_metric_ids",
        },
    )
