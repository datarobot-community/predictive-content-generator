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

from pydantic import BaseModel


class RuntimeEnvironment(BaseModel):
    name: str
    id: str


class GlobalRuntimeEnvironment(Enum):
    PYTHON_312_APPLICATION_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.12",
        id="66d07fae0513a1edf18595bb",
    )
    PYTHON_311_NOTEBOOK_BASE = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Base Image",
        id="664388ff6d426582042bb3e4",
    )
    PYTHON_311_MODERATIONS = RuntimeEnvironment(
        name="[GenAI] Python 3.11 with Moderations", id="65f9b27eab986d30d4c64268"
    )
    PYTHON_39_CUSTOM_METRICS = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Custom Metrics Templates Drop-In",
        id="659bf1626529ceb502d12ae2",
    )
    PYTHON_311_NOTEBOOK_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 Notebook Drop-In", id="6583d56f5627082b3cff990e"
    )
    PYTHON_39_STREAMLIT = RuntimeEnvironment(
        name="[Experimental] Python 3.9 Streamlit", id="6542cd582a9d3d51bf4ac71e"
    )
    PYTHON_311_GENAI = RuntimeEnvironment(
        name="[DataRobot] Python 3.11 GenAI", id="64d2ba178dd3f0b1fa2162f0"
    )
    PYTHON_39_GENAI = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 GenAI", id="64c964448dd3f0c07f47d040"
    )
    # TODO: add once this support applications
    # PYTHON_312_STREAMLIT = RuntimeEnvironment(
    #     name="[DataRobot] Python 3.12 Streamlit", id="66fd777f534b15baa0a1e88e"
    # )
    PYTHON_39_ONNX = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 ONNX Drop-In", id="62059a573f7d5f5cebabcba5"
    )
    JULIA_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Julia Drop-In", id="606234e1879feab31ec1abdd"
    )
    PYTHON_39_PMML = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 PMML Drop-In", id="5ee7dfc6433a8423386102ce"
    )
    R_421_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] R 4.2.1 Drop-In", id="5ea850ca1d41c8173c2feef6"
    )
    PYTHON_39_PYTORCH = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 PyTorch Drop-In", id="5e8c888007389fe0f466c72b"
    )
    JAVA_11_DROP_IN = RuntimeEnvironment(
        name="[DataRobot] Java 11 Drop-In (DR Codegen, H2O)",
        id="5e3028d9c38741266ef86452",
    )
    PYTHON_39_SCIKIT_LEARN = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Scikit-Learn Drop-In",
        id="5e8c889607389fe0f466c72d",
    )
    PYTHON_39_XGBOOST = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 XGBoost Drop-In", id="5e8c88a407389fe0f466c72f"
    )
    PYTHON_39_KERAS = RuntimeEnvironment(
        name="[DataRobot] Python 3.9 Keras Drop-In", id="5e8c886607389fe0f466c729"
    )


class GlobalLLM(str, Enum):
    AZURE_OPENAI_GPT_3_5_TURBO = "azure-openai-gpt-3.5-turbo"
    AZURE_OPENAI_GPT_3_5_TURBO_16K = "azure-openai-gpt-3.5-turbo-16k"
    AZURE_OPENAI_GPT_4 = "azure-openai-gpt-4"
    AZURE_OPENAI_GPT_4_32K = "azure-openai-gpt-4-32k"
    AZURE_OPENAI_GPT_4_TURBO = "azure-openai-gpt-4-turbo"
    AMAZON_TITAN = "amazon-titan"
    ANTHROPIC_CLAUDE_2_1 = "anthropic-claude-2"
    ANTROPIC_CLAUDE_3_HAIKU = "anthropic-claude-3-haiku"
    ANTROPIC_CLAUDE_3_SONNET = "anthropic-claude-3-sonnet"
    GOOGLE_BISON = "google-bison"
    GOOGLE_GEMINI_1_5_FLASH = "google-gemini-1.5-flash"
    GOOGLE_1_5_PRO = "google-gemini-1.5-pro"
    DEPLOYED_LLM = "custom-model"


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
    TOKEN_COUNT = "Token Count"
    TOXICITY = "Toxicity"


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
