# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

import datetime as dt
import json
import uuid


def test_llm_deployment_prediction(project_context, make_prediction):
    deployment_id = project_context.catalog.load("llm_deployment_id")
    prompt_feature_name = project_context.params["deploy_llm"]["custom_model"][
        "prompt_feature_name"
    ]
    association_id = f"{uuid.uuid4().hex}_{dt.datetime.now()}"

    input = json.dumps(
        [
            {
                prompt_feature_name: "What is the capital of France?",
                "association_id": association_id,
            }
        ]
    )
    output = make_prediction(input, deployment_id)["data"]
    assert len(output) == 1
