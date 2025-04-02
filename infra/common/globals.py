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

from enum import Enum
from typing import Literal

import datarobot as dr
from pydantic import BaseModel


class RuntimeEnvironment(BaseModel):
    name: str

    @property
    def id(self) -> str:
        client = dr.client.get_client()
        try:
            environments = client.get(
                "executionEnvironments/", params={"searchFor": self.name}
            ).json()
            env_id: str = next(
                environment["id"]
                for environment in environments["data"]
                if environment["name"] == self.name
            )
            return env_id
        except Exception as e:
            raise ValueError(
                f"Could not find the Execution Environment ID for {self.name}"
            ) from e


class ResourceBundle(BaseModel):
    name: str
    description: str
    id: str


class GlobalCustomApplicationResourceBundles(Enum):
    CPU_XXS = ResourceBundle(name="XXS", description="1 CPU | 128MB RAM", id="cpu.nano")
    CPU_XS = ResourceBundle(name="XS", description="1 CPU | 256MB RAM", id="cpu.micro")
    CPU_S = ResourceBundle(name="S", description="1 CPU | 512MB RAM", id="cpu.small")
    CPU_M = ResourceBundle(name="M", description="1 CPU | 1GB RAM", id="cpu.medium")
    CPU_L = ResourceBundle(name="L", description="2 CPU | 1.5GB RAM", id="cpu.large")
    CPU_XL = ResourceBundle(name="XL", description="2 CPU | 2GB RAM", id="cpu.xlarge")
    CPU_XXL = ResourceBundle(
        name="2XL", description="2 CPU | 3GB RAM", id="cpu.2xlarge"
    )
    CPU_3XL = ResourceBundle(
        name="3XL", description="2 CPU | 4GB RAM", id="cpu.3xlarge"
    )
    CPU_4XL = ResourceBundle(
        name="4XL", description="2 CPU | 6GB RAM", id="cpu.4xlarge"
    )
    CPU_5XL = ResourceBundle(
        name="5XL", description="2 CPU | 8GB RAM", id="cpu.5xlarge"
    )
    CPU_6XL = ResourceBundle(
        name="6XL", description="2 CPU | 10GB RAM", id="cpu.6xlarge"
    )
    CPU_7XL = ResourceBundle(
        name="7XL", description="2 CPU | 12GB RAM", id="cpu.7xlarge"
    )
    CPU_8XL = ResourceBundle(
        name="8XL", description="2 CPU | 14GB RAM", id="cpu.8xlarge"
    )


class GlobalCustomModelResourceBundles(Enum):
    CPU_XXS = ResourceBundle(name="XXS", description="1 CPU | 128MB RAM", id="cpu.nano")
    CPU_XS = ResourceBundle(name="XS", description="1 CPU | 256MB RAM", id="cpu.micro")
    CPU_S = ResourceBundle(name="S", description="1 CPU | 512MB RAM", id="cpu.small")
    CPU_M = ResourceBundle(name="M", description="1 CPU | 1GB RAM", id="cpu.medium")
    CPU_L = ResourceBundle(name="L", description="2 CPU | 1.5GB RAM", id="cpu.large")
    CPU_XL = ResourceBundle(name="XL", description="2 CPU | 2GB RAM", id="cpu.xlarge")
    CPU_XXL = ResourceBundle(
        name="XXL", description="2 CPU | 3GB RAM", id="cpu.2xlarge"
    )
    CPU_3XL = ResourceBundle(
        name="3XL", description="2 CPU | 4GB RAM", id="cpu.3xlarge"
    )
    CPU_4XL = ResourceBundle(
        name="4XL", description="2 CPU | 6GB RAM", id="cpu.4xlarge"
    )
    CPU_5XL = ResourceBundle(
        name="5XL", description="2 CPU | 8GB RAM", id="cpu.5xlarge"
    )
    CPU_6XL = ResourceBundle(
        name="6XL", description="2 CPU | 10GB RAM", id="cpu.6xlarge"
    )
    CPU_7XL = ResourceBundle(
        name="7XL", description="2 CPU | 12GB RAM", id="cpu.7xlarge"
    )
    CPU_8XL = ResourceBundle(
        name="8XL", description="2 CPU | 14GB RAM", id="cpu.8xlarge"
    )
    CPU_16XL = ResourceBundle(
        name="16XL", description="4 CPU | 28GB RAM", id="cpu.16xlarge"
    )
    GPU_S = ResourceBundle(
        name="GPU - S",
        description="1 x NVIDIA T4 | 16GB VRAM | 4 CPU | 16GB RAM",
        id="DRAWS_g4dn.xlarge_frac1_regular",
    )
    GPU_M = ResourceBundle(
        name="GPU - M",
        description="1 x NVIDIA T4 | 16GB VRAM | 8 CPU | 32GB RAM",
        id="DRAWS_g4dn.2xlarge_frac1_regular",
    )
    GPU_L = ResourceBundle(
        name="GPU - L",
        description="1 x NVIDIA A10G | 24GB VRAM | 8 CPU | 32GB RAM",
        id="DRAWS_g5.2xlarge_frac1_regular",
    )
    GPU_XL = ResourceBundle(
        name="GPU - XL",
        description="1 x NVIDIA L40S | 48GB VRAM | 4 CPU | 32GB RAM",
        id="DRAWS_g6e.xlarge_frac1_regular",
    )
    GPU_XXL = ResourceBundle(
        name="GPU - XXL",
        description="4 x NVIDIA A10G | 96GB VRAM | 48 CPU | 192GB RAM",
        id="DRAWS_g5.12xlarge_frac1_regular",
    )
    GPU_3XL = ResourceBundle(
        name="GPU - 3XL",
        description="4 x NVIDIA L40S | 192GB VRAM | 48 CPU | 384GB RAM",
        id="DRAWS_g6e.12xlarge_frac1_regular",
    )
    GPU_4XL = ResourceBundle(
        name="GPU - 4XL",
        description="8 x NVIDIA A10G | 192GB VRAM | 192 CPU | 768GB RAM",
        id="DRAWS_g5.48xlarge_frac1_regular",
    )
    GPU_5XL = ResourceBundle(
        name="GPU - 5XL",
        description="8 x NVIDIA L40S | 384GB VRAM | 192 CPU | 1.5TB RAM",
        id="DRAWS_g6e.48xlarge_frac1_regular",
    )


class GlobalRuntimeEnvironment(Enum):
    PYTHON_312_APPLICATION_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.12 Applications Base"
    )
    PYTHON_311_NOTEBOOK_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Base Image"
    )
    PYTHON_311_MODERATIONS = RuntimeEnvironment(
        name="[GenAI] Python 3.11 with Moderations"
    )
    PYTHON_312_MODERATIONS = RuntimeEnvironment(
        name="[GenAI] Python 3.12 with Moderations"
    )
    PYTHON_39_CUSTOM_METRICS = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Custom Metrics Templates Drop-In",
    )
    PYTHON_311_NOTEBOOK_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Drop-In"
    )
    PYTHON_39_STREAMLIT = RuntimeEnvironment(name="[Experimental] Python 3.9 Streamlit")
    PYTHON_311_GENAI = RuntimeEnvironment(name="[DataRobot] Python 3.11 GenAI")
    PYTHON_39_GENAI = RuntimeEnvironment(name="[DataRobot] Python 3.9 GenAI")
    PYTHON_39_ONNX = RuntimeEnvironment(name="[DataRobot] Python 3.9 ONNX Drop-In")
    JULIA_DROP_IN = RuntimeEnvironment(name="[DataRobot] Julia Drop-In")
    PYTHON_39_PMML = RuntimeEnvironment(name="[DataRobot] Python 3.9 PMML Drop-In")
    R_421_DROP_IN = RuntimeEnvironment(name="[DataRobot] R 4.2.1 Drop-In")
    PYTHON_39_PYTORCH = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 PyTorch Drop-In"
    )
    JAVA_11_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Java 11 Drop-In (DR Codegen, H2O)"
    )
    PYTHON_39_SCIKIT_LEARN = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Scikit-Learn Drop-In"
    )
    PYTHON_39_XGBOOST = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 XGBoost Drop-In"
    )
    PYTHON_39_KERAS = RuntimeEnvironment(name="[DataRobot] Python 3.9 Keras Drop-In")


class GlobalRegisteredModelName(str, Enum):
    TOXICITY = "[Hugging Face] Toxicity Classifier"
    SENTIMENT = "[Hugging Face] Sentiment Classifier"
    REFUSAL = "[DataRobot] LLM Refusal Score"
    PROMPT_INJECTION = "[Hugging Face] Prompt Injection Classifier"


class GlobalGuardrailTemplateName(str, Enum):
    CUSTOM_DEPLOYMENT = "Custom Deployment"
    FAITHFULNESS = "Faithfulness"
    PII_DETECTION = "PII Detection"
    PROMPT_INJECTION = "Prompt Injection"
    ROUGE_1 = "Rouge 1"
    SENTIMENT_CLASSIFIER = "Sentiment Classifier"
    STAY_ON_TOPIC_FOR_INPUTS = "Stay on topic for inputs"
    STAY_ON_TOPIC_FOR_OUTPUTS = "Stay on topic for output"
    TOXICITY = "Toxicity"
    RESPONSE_TOKENS = "Response Tokens"
    PROMPT_TOKENS = "Prompt Tokens"


# ('aws', 'gcp', 'azure', 'onPremise', 'datarobot', 'datarobotServerless', 'openShift', 'other', 'snowflake', 'sapAiCore')
class GlobalPredictionEnvironmentPlatforms(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "onPremise"
    DATAROBOT = "datarobot"
    DATAROBOT_SERVERLESS = "datarobotServerless"
    OPEN_SHIFT = "openShift"
    OTHER = "other"
    SNOWFLAKE = "snowflake"
    SAP_AI_CORE = "sapAiCore"


CredentialType = Literal["azure", "aws", "google", "api"]


class LLMConfig(BaseModel):
    name: str
    credential_type: CredentialType


class GlobalLLM:
    """Available LLM configurations"""

    # Azure Models
    AZURE_OPENAI_GPT_3_5_TURBO = LLMConfig(
        name="azure-openai-gpt-3.5-turbo",
        credential_type="azure",
    )
    AZURE_OPENAI_GPT_3_5_TURBO_16K = LLMConfig(
        name="azure-openai-gpt-3.5-turbo-16k", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4 = LLMConfig(name="azure-openai-gpt-4", credential_type="azure")
    AZURE_OPENAI_GPT_4_32K = LLMConfig(
        name="azure-openai-gpt-4-32k", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_TURBO = LLMConfig(
        name="azure-openai-gpt-4-turbo", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_O = LLMConfig(
        name="azure-openai-gpt-4-o", credential_type="azure"
    )
    AZURE_OPENAI_GPT_4_O_MINI = LLMConfig(
        name="azure-openai-gpt-4-o-mini", credential_type="azure"
    )
    # AWS Models
    AMAZON_TITAN = LLMConfig(name="amazon-titan", credential_type="aws")
    ANTHROPIC_CLAUDE_2 = LLMConfig(name="anthropic-claude-2", credential_type="aws")
    ANTHROPIC_CLAUDE_3_HAIKU = LLMConfig(
        name="anthropic-claude-3-haiku", credential_type="aws"
    )
    ANTHROPIC_CLAUDE_3_SONNET = LLMConfig(
        name="anthropic-claude-3-sonnet", credential_type="aws"
    )
    ANTHROPIC_CLAUDE_3_OPUS = LLMConfig(
        name="anthropic-claude-3-opus", credential_type="aws"
    )
    # Google Models
    GOOGLE_BISON = LLMConfig(name="google-bison", credential_type="google")
    GOOGLE_GEMINI_1_5_FLASH = LLMConfig(
        name="google-gemini-1.5-flash", credential_type="google"
    )
    GOOGLE_1_5_PRO = LLMConfig(name="google-gemini-1.5-pro", credential_type="google")

    # API Models
    DEPLOYED_LLM = LLMConfig(name="custom-model", credential_type="api")


class ApplicationTemplate(BaseModel):
    name: str

    @property
    def id(self) -> str:
        client = dr.client.get_client()
        try:
            templates = client.get(
                "customTemplates/", params={"templateType": "customApplicationTemplate"}
            ).json()
            template_id: str = next(
                template["id"]
                for template in templates["data"]
                if template["name"] == self.name
            )
            return template_id
        except Exception as e:
            raise ValueError(
                f"Could not find the Application Template ID for {self.name}"
            ) from e


class GlobalApplicationTemplates(Enum):
    FLASK_APP_BASE = ApplicationTemplate(name="Flask App Base")
    Q_AND_A_CHAT_GENERATION_APP = ApplicationTemplate(name="Q&A Chat Generation App")
    SLACK_BOT_APP = ApplicationTemplate(name="Slack Bot App")
    STREAMLIT_APP_BASE = ApplicationTemplate(name="Streamlit App Base")
    NODE_JS_AND_REACT_APP = ApplicationTemplate(name="Node.js & React Base App")
