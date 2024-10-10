# Copyright 2024 DataRobot, Inc. and its affiliates.
# All rights reserved.
# DataRobot, Inc.
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
# Released under the terms of DataRobot Tool and Utility Agreement.

import json
from typing import Any, Dict

import requests
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog


class ExtraCredentialsHooks:
    """Include credentials in the catalog so they can be used by nodes."""

    @hook_impl
    def after_catalog_created(
        self,
        catalog: DataCatalog,
        conf_catalog: Dict[str, Any],
        conf_creds: Dict[str, Any],
        save_version: str,
        load_versions: Dict[str, str],
    ) -> None:
        import datarobot as dr

        dr_creds = conf_creds["datarobot"]
        azure_creds = conf_creds["azure_openai_llm_credentials"]

        prediction_server_id = dr_creds["prediction_environment_id"]
        if not any(
            [prediction_server_id == server.id for server in dr.PredictionServer.list()]
        ):
            msg = (
                "The value for `prediction_environment_id` specified in credentials.yml: "
                f"'{prediction_server_id}' does not correspond to an available prediction server."
            )
            raise ValueError(msg)

        url = f"{azure_creds['azure_endpoint']}/openai/deployments/gpt-35-turbo/chat/completions?api-version={azure_creds['api_version']}"

        # Headers including the Content-Type and api-key
        headers = {
            "Content-Type": "application/json",
            "api-key": azure_creds["api_key"],
        }

        # Data payload as a dictionary converted to a JSON string
        data = json.dumps(
            {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": "What is the capital of Germany. One word answer.",
                    },
                ]
            }
        )

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        assert (
            "Berlin" in response.json()["choices"][0]["message"]["content"]
        ), "Azure OpenAI credentials are invalid"
