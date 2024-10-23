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

# disable mypy:
# type: ignore

import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import pulumi_datarobot as datarobot
import pytest
from datarobot_drum.drum.drum import CMRunner
from datarobot_drum.drum.runtime import DrumRuntime

sys.path.append("../")
from infra.components.dr_credential import DRCredential
from nbo.schema import LLMRequest


class ExtendedDRCredential(DRCredential):
    def __init__(self, *args, **kwargs):
        # Store all arguments for later inspection
        self._init_kwargs = kwargs

        # Call the original __init__ method
        super().__init__(*args, **kwargs)

    def get_init_kwargs(self) -> Dict[str, Any]:
        """Return the arguments passed to __init__"""
        return self._init_kwargs


class ExtendedCustomModel(datarobot.CustomModel):
    def __init__(self, *args, **kwargs):
        # Store all arguments for later inspection
        self._init_kwargs = kwargs

        # Call the original __init__ method
        super().__init__(*args, **kwargs)

    def get_init_kwargs(self) -> Dict[str, Any]:
        """Return the arguments passed to __init__"""
        return self._init_kwargs


@pytest.fixture
def output_dir() -> Path:
    path = Path("tests/output")
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def test_input(output_dir: Path) -> Path:
    from nbo.credentials import AzureOpenAICredentials

    credentials = AzureOpenAICredentials()

    rag_input = LLMRequest(
        prompt="Tell me about DataRobot",
        association_id="id42",
        model=credentials.azure_deployment,
        number_of_explanations=1,
        system_prompt="You are a helpful Assistant",
        temperature=0.0,
        tone="Friendly",
        verbosity="brief",
    )
    data = rag_input.model_dump(mode="json", by_alias=True)
    pd.DataFrame.from_records([data]).to_csv(
        output_dir / "test_input.csv",
    )
    return str(output_dir / "test_input.csv")


@pytest.fixture
def generative_custom_model(code_dir) -> ExtendedCustomModel:
    from infra.settings_generative import (
        custom_model_args,
        get_files,
    )
    from infra.settings_llm_credential import credential, credential_args

    llm_credential = ExtendedDRCredential(
        resource_name="llm-credential",
        credential=credential,
        credential_args=credential_args,
    )
    diy_rag_files = get_files(
        runtime_parameter_values=llm_credential.runtime_parameter_values,
    )

    generative_custom_model = ExtendedCustomModel(
        files=diy_rag_files,
        runtime_parameter_values=llm_credential.runtime_parameter_values,
        **custom_model_args.model_dump(mode="json", exclude_none=True),
    )
    return generative_custom_model


def run_drum(
    code_dir: str,
    input: str,
    output: str,
    #  runtime_params_file: str
):
    with DrumRuntime() as runtime:
        options = Namespace(
            subparser_name="score",
            code_dir=code_dir,
            verbose=False,
            input=input,
            logging_level="info",
            docker=None,
            skip_deps_install=False,
            memory=None,
            output=output,
            show_perf=False,
            sparse_column_file=None,
            language=None,
            show_stacktrace=False,
            monitor=False,
            monitor_embedded=False,
            deployment_id=None,
            model_id=None,
            monitor_settings=None,
            allow_dr_api_access=False,
            webserver=None,
            api_token=None,
            gpu_predictor=None,
            triton_host="http://localhost",
            triton_http_port="8000",
            triton_grpc_port="8001",
            target_type=None,
            query=None,
            content_type=None,
            user_secrets_mount_path=None,
            user_secrets_prefix=None,
        )

        runtime.options = options
        # if "runtime_params_file" in options and options.runtime_params_file:
        #     loader = RuntimeParametersLoader(
        #         options.runtime_params_file, options.code_dir
        #     )
        #     loader._yaml_content["OPENAI_API_KEY"]["apiToken"] = credential.api_key
        #     loader.setup_environment_variables()
        # runtime.options = options
        runner = CMRunner(runtime)
        runner.run()


@pytest.fixture
def code_dir() -> str:
    from infra.settings_generative import (
        generative_deployment_path,
    )

    code_dir = generative_deployment_path
    code_dir.mkdir(exist_ok=True, parents=True)
    return code_dir


def test_diy_rag_custom_model(
    code_dir: str, test_input: Path, output_dir: Path, pulumi_up
) -> None:
    from infra.settings_generative import (
        custom_model_args,
    )

    os.environ["TARGET_NAME"] = str(custom_model_args.target_name)
    output = str(output_dir / "out.csv")
    run_drum(
        code_dir=code_dir,
        input=test_input,
        output=output,
    )
    with open(output) as f:
        content = f.read()

    assert "DataRobot" in content
