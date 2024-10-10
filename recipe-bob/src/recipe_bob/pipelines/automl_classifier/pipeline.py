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

import datarobot as dr
from datarobotx.idp.autopilot import get_or_create_autopilot_run
from datarobotx.idp.datasets import get_or_create_dataset_from_df
from datarobotx.idp.deployments import (
    get_replace_or_create_deployment_from_registered_model,
)

from datarobotx.idp.use_cases import get_or_create_use_case

from .nodes import (
    ensure_deployment_settings,
    get_or_create_registered_model_with_threshold,
)


def create_pipeline(**kwargs) -> Pipeline:
    nodes = [
        node(
            name="make_datarobot_usecase",
            func=get_or_create_use_case,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:use_case.name",
                "description": "params:use_case.description",
            },
            outputs="use_case_id",
        ),
        node(
            name="make_dataset",
            func=get_or_create_dataset_from_df,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:dataset.name",
                "data_frame": "raw_data",
                "use_cases": "use_case_id",
            },
            outputs="dataset_id",
        ),
        node(
            name="make_autopilot_run",
            func=get_or_create_autopilot_run,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "name": "params:project.name",
                "dataset_id": "dataset_id",
                "analyze_and_model_config": "params:project.analyze_and_model_config",
                "advanced_options_config": "params:project.advanced_options_config",
                "use_case": "use_case_id",
            },
            outputs="project_id",
        ),
        node(
            name="get_recommended_model",
            func=lambda project_id: dr.ModelRecommendation.get(project_id).model_id,
            inputs="project_id",
            outputs="recommended_model_id",
        ),
        node(
            name="make_registered_model",
            func=get_or_create_registered_model_with_threshold,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "project_id": "project_id",
                "model_id": "recommended_model_id",
                "registered_model_name": "params:registered_model.name",
            },
            outputs="registered_model_version_id",
        ),
        node(
            name="make_deployment",
            func=get_replace_or_create_deployment_from_registered_model,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "registered_model_version_id": "registered_model_version_id",
                "registered_model_name": "params:registered_model.name",
                "label": "params:deployment.label",
                "description": "params:deployment.description",
                "prediction_environment_id": "params:credentials.datarobot.prediction_environment_id",
            },
            outputs="deployment_id",
        ),
        node(
            name="ensure_deployment_settings",
            func=ensure_deployment_settings,
            inputs={
                "endpoint": "params:credentials.datarobot.endpoint",
                "token": "params:credentials.datarobot.api_token",
                "deployment_id": "deployment_id",
            },
            outputs=None,
        ),
    ]
    pipeline_inst = pipeline(nodes)
    return pipeline(
        pipeline_inst,
        namespace="automl_classifier",
        parameters={
            "params:credentials.datarobot.endpoint",
            "params:credentials.datarobot.api_token",
            "params:credentials.datarobot.prediction_environment_id",
        },
        outputs={
            "dataset_id",
            "project_id",
            "recommended_model_id",
            "deployment_id",
            "use_case_id",
        },
    )
