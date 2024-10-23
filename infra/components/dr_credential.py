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
from typing import List, Optional, Union

import pulumi
import pulumi_datarobot as datarobot

from nbo.credentials import (
    AzureOpenAICredentials,
    GoogleLLMCredentials,
    LLMCredentials,
)

from ..common.schema import (
    CredentialArgs,
)


class DRCredential(pulumi.ComponentResource):
    """DR Credential for use with a custom deployment or app.

    Abstracts creation of the appropriate credential type, structuring runtime parameters.
    """

    def __init__(
        self,
        resource_name: str,
        credential: LLMCredentials,
        credential_args: CredentialArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("custom:datarobot:DRCredential", resource_name, None, opts)

        self.credential_raw = credential
        self.credential: Union[
            datarobot.ApiTokenCredential, datarobot.GoogleCloudCredential
        ]
        if isinstance(self.credential_raw, AzureOpenAICredentials):
            self.credential = datarobot.ApiTokenCredential(
                **credential_args.model_dump(),
                api_token=credential.api_key,  # type: ignore[union-attr]
                opts=pulumi.ResourceOptions(parent=self),
            )
        elif isinstance(self.credential_raw, GoogleLLMCredentials):
            self.credential = datarobot.GoogleCloudCredential(
                **credential_args.model_dump(),
                gcp_key=json.dumps(credential.service_account_key),  # type: ignore[union-attr]
                opts=pulumi.ResourceOptions(parent=self),
            )
        else:
            raise ValueError("Unsupported credential type")

        self.register_outputs(
            {
                "id": self.credential.id,
            }
        )

    @property
    def runtime_parameter_values(
        self,
    ) -> List[datarobot.CustomModelRuntimeParameterValueArgs]:
        if isinstance(self.credential_raw, AzureOpenAICredentials):
            runtime_parameter_values = [
                datarobot.CustomModelRuntimeParameterValueArgs(
                    key=key,
                    type=type_,
                    value=value,  # type: ignore[arg-type]
                )
                for key, type_, value in [
                    ("OPENAI_API_KEY", "credential", self.credential.id),
                    (
                        "OPENAI_API_BASE",
                        "string",
                        self.credential_raw.azure_endpoint,
                    ),
                    (
                        "OPENAI_API_DEPLOYMENT_ID",
                        "string",
                        self.credential_raw.azure_deployment,
                    ),
                    ("OPENAI_API_VERSION", "string", self.credential_raw.api_version),
                ]
            ]
        elif isinstance(self.credential_raw, GoogleLLMCredentials):
            runtime_parameter_values = [
                datarobot.CustomModelRuntimeParameterValueArgs(
                    key="GOOGLE_SERVICE_ACCOUNT",
                    type="credential",
                    value=self.credential.id,
                ),
            ]
            if self.credential_raw.region is not None:
                runtime_parameter_values.append(
                    datarobot.CustomModelRuntimeParameterValueArgs(
                        key="GOOGLE_REGION",
                        type="string",
                        value=self.credential_raw.region,
                    )
                )
        else:
            raise NotImplementedError("Unsupported credential type")
        return runtime_parameter_values

    @property
    def app_runtime_parameter_values(
        self,
    ) -> List[datarobot.ApplicationSourceRuntimeParameterValueArgs]:
        if isinstance(self.credential_raw, AzureOpenAICredentials):
            runtime_parameter_values = [
                datarobot.ApplicationSourceRuntimeParameterValueArgs(
                    key=key,
                    type=type_,
                    value=value,  # type: ignore[arg-type]
                )
                for key, type_, value in [
                    ("OPENAI_API_KEY", "credential", self.credential.id),
                    (
                        "OPENAI_API_BASE",
                        "string",
                        json.dumps({"payload": self.credential_raw.azure_endpoint}),
                    ),
                    (
                        "OPENAI_API_DEPLOYMENT_ID",
                        "string",
                        json.dumps({"payload": self.credential_raw.azure_deployment}),
                    ),
                    (
                        "OPENAI_API_VERSION",
                        "string",
                        json.dumps({"payload": self.credential_raw.api_version}),
                    ),
                ]
            ]
        elif isinstance(self.credential_raw, GoogleLLMCredentials):
            runtime_parameter_values = [
                datarobot.ApplicationSourceRuntimeParameterValueArgs(
                    key="GOOGLE_SERVICE_ACCOUNT",
                    type="credential",
                    value=self.credential.id,
                ),
            ]
            if self.credential_raw.region is not None:
                runtime_parameter_values.append(
                    datarobot.ApplicationSourceRuntimeParameterValueArgs(
                        key="GOOGLE_REGION",
                        type="string",
                        value=json.dumps({"payload": self.credential_raw.region}),
                    )
                )
        else:
            raise NotImplementedError("Unsupported credential type")
        return runtime_parameter_values
