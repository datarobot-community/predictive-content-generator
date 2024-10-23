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

from __future__ import annotations

from typing import Any, Dict, Optional, Union

from pydantic import AliasChoices, AliasPath, Field
from pydantic_settings import (
    BaseSettings,
)


class AzureOpenAICredentials(BaseSettings):
    """LLM credentials auto-constructed using environment variables."""

    api_version: str = Field(
        validation_alias=AliasChoices(
            AliasPath("MLOPS_RUNTIME_PARAM_OPENAI_API_VERSION", "payload"),
            "OPENAI_API_VERSION",
        ),
    )
    azure_endpoint: str = Field(
        validation_alias=AliasChoices(
            AliasPath("MLOPS_RUNTIME_PARAM_OPENAI_API_BASE", "payload"),
            "OPENAI_API_BASE",
        )
    )
    api_key: str = Field(
        validation_alias=AliasChoices(
            AliasPath("MLOPS_RUNTIME_PARAM_OPENAI_API_KEY", "payload", "apiToken"),
            "OPENAI_API_KEY",
        ),
    )
    azure_deployment: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            AliasPath("MLOPS_RUNTIME_PARAM_OPENAI_API_DEPLOYMENT_ID", "payload"),
            "OPENAI_API_DEPLOYMENT_ID",
        ),
    )

    def test(self, model: str | None = None) -> None:
        import openai

        try:
            client = openai.AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version,
            )
            client.chat.completions.create(
                messages=[{"role": "user", "content": "hello"}],
                model=model or self.azure_deployment,  # type: ignore[arg-type]
            )
        except Exception as e:
            raise ValueError(
                f"Unable to run a successful test completion against model '{model}' "
                "with provided Azure OpenAI credentials. Please validate your credentials."
            ) from e


class GoogleLLMCredentials(BaseSettings):
    service_account_key: Dict[str, Any] = Field(
        validation_alias=AliasChoices(
            AliasPath(
                "MLOPS_RUNTIME_PARAM_GOOGLE_SERVICE_ACCOUNT", "payload", "gcpKey"
            ),
            "GOOGLE_SERVICE_ACCOUNT",
        )
    )
    region: Optional[str] = Field(
        validation_alias=AliasChoices(
            AliasPath("MLOPS_RUNTIME_PARAM_GOOGLE_REGION", "payload"),
            "GOOGLE_REGION",
        ),
        default="us-west1",
    )

    def test(self, model: str) -> None:
        try:
            import requests
            from google.auth.transport.requests import (  # type: ignore[import-untyped]
                Request,
            )
            from google.oauth2 import service_account  # type: ignore[import-untyped]

            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_key,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            credentials.refresh(Request())

            messages = [{"role": "user", "parts": [{"text": "Hello"}]}]
            resp = requests.post(
                f"https://{self.region}-aiplatform.googleapis.com/v1/projects/"
                f"{credentials.project_id}/locations/{self.region}/publishers/"
                f"google/models/{model}:generateContent",
                headers={"Authorization": f"Bearer {credentials.token}"},
                json={"contents": messages},
            )
            resp.raise_for_status()
        except Exception as e:
            raise ValueError(
                f"Unable to run a successful test completion against model '{model}' "
                "with provided Azure OpenAI credentials. Please validate your credentials."
            ) from e


LLMCredentials = Union[AzureOpenAICredentials, GoogleLLMCredentials]
