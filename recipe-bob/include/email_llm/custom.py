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

from datarobot_drum import RuntimeParameters
import pandas as pd
from openai import AzureOpenAI


def load_model(input_dir):
    try:
        azure_endpoint = RuntimeParameters.get("azure_endpoint")
        api_key = RuntimeParameters.get("openai_api_key")["apiToken"]
        api_version = RuntimeParameters.get("openai_api_version")

        prompt_feature_name = RuntimeParameters.get("prompt_feature_name")
        target_feature_name = RuntimeParameters.get("target_feature_name")

    except Exception:
        print(
            "Exception raised while loading runtime parameters. Attempting load from Kedro.."
        )

        from local_helpers import get_kedro_catalog

        project_root = "../../"
        catalog = get_kedro_catalog(project_root)
        llm_credentials = catalog.load(
            "params:credentials.azure_openai_llm_credentials"
        )
        prompt_feature_name = catalog.load(
            "params:deploy_llm.custom_model.prompt_feature_name"
        )
        target_feature_name = catalog.load(
            "params:deploy_llm.custom_model.prompt_feature_name"
        )
        azure_endpoint = llm_credentials["azure_endpoint"]
        api_key = llm_credentials["api_key"]
        api_version = llm_credentials["api_version"]

    client = AzureOpenAI(
        azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version
    )
    return client, prompt_feature_name, target_feature_name


def score(data, model, **kwargs):
    client, prompt_feature_name, target_feature_name = model
    df = data[prompt_feature_name].tolist()

    if "temperature" not in data.columns:
        data["temperature"] = 1.0
    if "model" not in data.columns:
        data["model"] = "gpt-35-turbo"
    if "system_prompt" not in data.columns:
        data["system_prompt"] = "You are an AI assistant."

    result = []
    for i, prompt in enumerate(df):
        try:
            resp = client.chat.completions.create(
                model=data["model"][i],
                messages=[
                    {"role": "system", "content": data["system_prompt"][i]},
                    {"role": "user", "content": str(prompt)},
                ],
                temperature=data["temperature"][i],
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


if __name__ == "__main__":
    client, prompt_feature_name, target_feature_name = load_model(".")
    data = pd.DataFrame(
        {
            prompt_feature_name: [
                "What is the capital of France?",
                "What is the capital of Germany?",
                "What is the capital of Italy?",
            ],
            "temperature": [0.5, 0.5, 0.5],
            "model": ["gpt-35-turbo", "gpt-35-turbo-16k", "gpt-4o"],
            "system_prompt": [
                "You are an AI assistant.",
                "You are an AI assistant.",
                "You are an AI assistant.",
            ],
        }
    )
    result = score(data, (client, prompt_feature_name, target_feature_name))
    print(result)
