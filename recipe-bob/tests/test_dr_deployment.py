# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.


import pandas as pd


def test_automl_deployment_prediction(project_context, make_prediction):
    data = project_context.catalog.load("automl_classifier.raw_data")
    deployment_id = project_context.catalog.load("deployment_id")

    model_input = data.head(10).to_json(orient="records")
    output = pd.DataFrame(make_prediction(model_input, deployment_id)["data"])

    assert isinstance(output, pd.DataFrame)
    assert not output.empty
