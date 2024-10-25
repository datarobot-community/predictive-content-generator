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

# mypy: ignore-errors

from __future__ import annotations

import pandas as pd
from openai import AzureOpenAI

from nbo.credentials import AzureOpenAICredentials
from nbo.schema import GenerativeDeploymentSettings, LLMRequest


def load_model(input_dir: str) -> tuple[AzureOpenAI, str, str]:
    credentials = AzureOpenAICredentials()
    generative_settings = GenerativeDeploymentSettings()
    prompt_feature_name = generative_settings.prompt_feature_name
    target_feature_name = generative_settings.target_feature_name

    client = AzureOpenAI(
        azure_endpoint=credentials.azure_endpoint,
        api_key=credentials.api_key,
        api_version=credentials.api_version,
    )
    return client, prompt_feature_name, target_feature_name


def score(data: pd.DataFrame, model: tuple[AzureOpenAI, str, str], **kwargs):
    client, prompt_feature_name, target_feature_name = model
    data = data.rename(columns={prompt_feature_name: "prompt"})

    requests = [
        LLMRequest.model_validate(record) for record in data.to_dict(orient="records")
    ]
    result = []
    for request in requests:
        try:
            resp = client.chat.completions.create(
                model=request.model,
                messages=[
                    {
                        "role": "system",
                        "content": request.system_prompt or "You are an AI assistant.",
                    },
                    {"role": "user", "content": str(request.prompt)},
                ],
                temperature=request.temperature or 1.0,
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                timeout=30,
            )
            completion = resp.choices[0].message.content
        except Exception as e:
            completion = str(e)
        result.append(completion)
    return pd.DataFrame({target_feature_name: result})
