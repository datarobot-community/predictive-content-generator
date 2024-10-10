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

from datarobotx.idp.common.asset_resolver import prepare_yaml_content, merge_asset_paths

from datarobotx.idp.custom_application_source import (
    get_or_create_custom_application_source,
)
from datarobotx.idp.custom_application_source_version import (
    get_or_create_custom_application_source_version,
)
from datarobotx.idp.custom_applications import get_replace_or_create_custom_app


from .nodes import log_outputs, ensure_app_settings


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            name="map_custom_metric_baselines",
            func=lambda custom_metrics: {
                metric: custom_metrics[metric]["baseline_values"][0]["value"]
                for metric in custom_metrics.keys()
            },
            inputs={"custom_metrics": "params:llm_deployment.custom_metrics"},
            outputs="custom_metric_baselines",
        ),
        node(
            name="make_app_parameters",
            func=prepare_yaml_content,
            inputs={
                "prediction_server_id": "params:credentials.datarobot.prediction_environment_id",
                "dataset_id": "dataset_id",
                "deployment_id": "deployment_id",
                "llm_deployment_id": "llm_deployment_id",
                "association_id_column_name": "params:llm_deployment.association_id_column_name",
                "application_name": "params:custom_app_name",
                "page_title": "params:page_title",
                "page_subtitle": "params:page_subtitle",
                "record_identifier": "params:record_identifier",
                "custom_metric_ids": "custom_metric_ids",
                "custom_metric_baselines": "custom_metric_baselines",
                "default_number_of_explanations": "params:default_number_of_explanations",
                "text_explanation_feature": "params:text_explanation_feature",
                "no_text_gen_label": "params:no_text_gen_label",
                "prompt_feature_name": "params:custom_model.prompt_feature_name",
                "target_feature_name": "params:custom_model.target_feature_name",
                "models": "params:models",
                "default_temperature": "params:default_temperature",
                "tones": "params:tones",
                "verbosity": "params:verbosity",
                "target_probability_description": "params:target_probability_description",
                "system_prompt": "params:system_prompt",
                "email_prompt": "params:email_prompt",
                "outcome_details": "params:outcome_details",
            },
            outputs="app_parameters",
        ),
        node(
            name="make_app_assets",
            func=merge_asset_paths,
            inputs=["app_parameters", "app_assets"],
            outputs="deployment_assets",
        ),
        node(
            name="create_custom_application_source",
            func=get_or_create_custom_application_source,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:custom_app_name",
            },
            outputs="custom_application_source_id",
        ),
        node(
            name="make_application_source_version",
            func=get_or_create_custom_application_source_version,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "custom_application_source_id": "custom_application_source_id",
                "base_environment_id": "params:base_environment_id",
                "folder_path": "deployment_assets",
                "name": "params:custom_app_name",
            },
            outputs="custom_application_source_version_id",
        ),
        node(
            name="deploy_app",
            func=get_replace_or_create_custom_app,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "custom_application_source_version_id": "custom_application_source_version_id",
                "name": "params:custom_app_name",
            },
            outputs="application_id",
        ),
        node(
            name="ensure_app_settings",
            func=ensure_app_settings,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "app_id": "application_id",
                "allow_auto_stopping": "params:allow_auto_stopping",
            },
            outputs=None,
        ),
        node(
            name="log_outputs",
            func=log_outputs,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "project_id": "project_id",
                "model_id": "recommended_model_id",
                "deployment_id": "deployment_id",
                "application_id": "application_id",
                "project_name": "params:project.name",
                "deployment_name": "params:deployment.label",
                "app_name": "params:custom_app_name",
            },
            outputs=None,
        ),
    ]
    pipeline_inst = pipeline(nodes)
    return pipeline(
        pipeline_inst,
        namespace="deploy_streamlit_app",
        parameters={
            "params:credentials.datarobot.endpoint": "params:credentials.datarobot.endpoint",
            "params:credentials.datarobot.api_token": "params:credentials.datarobot.api_token",
            "params:credentials.datarobot.prediction_environment_id": "params:credentials.datarobot.prediction_environment_id",
            "params:project.name": "params:automl_classifier.project.name",
            "params:deployment.label": "params:automl_classifier.deployment.label",
            "params:custom_model.prompt_feature_name": "params:deploy_llm.custom_model.prompt_feature_name",
            "params:custom_model.target_feature_name": "params:deploy_llm.custom_model.target_feature_name",
            "params:llm_deployment.association_id_column_name": "params:deploy_llm.deployment.association_id_column_name",
            "params:llm_deployment.custom_metrics": "params:deploy_llm.custom_metrics",
        },
        inputs={
            "dataset_id",
            "project_id",
            "recommended_model_id",
            "deployment_id",
            "llm_deployment_id",
            "custom_metric_ids",
        },
        outputs={"application_id"},
    )
