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

import json
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field

association_id = "association_id"


class GenerativeDeploymentSettings(BaseModel):
    target_feature_name: str = "completion"
    prompt_feature_name: str = "promptText"


class LLMModelSpec(BaseModel):
    name: str
    input_price_per_1k_tokens: float
    output_price_per_1k_tokens: float


class OutcomeDetail(BaseModel):
    prediction: Any
    label: str
    description: str


class AppDataScienceSettings(BaseModel):
    association_id_column_name: str
    page_title: str
    page_subtitle: str
    record_identifier: dict[str, str]
    custom_metric_baselines: dict[str, float]
    default_number_of_explanations: int
    text_explanation_feature: str
    no_text_gen_label: Optional[str]
    models: list[LLMModelSpec]
    default_temperature: float
    tones: list[str]
    verbosity: list[str]
    target_probability_description: str
    system_prompt: str
    email_prompt: str
    outcome_details: list[OutcomeDetail]


class AppInfraSettings(BaseModel):
    registered_model_name: str
    registered_model_version_id: str
    scoring_dataset_id: str
    use_case_id: str
    project_id: str


class LLMRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str = Field(
        serialization_alias=GenerativeDeploymentSettings().prompt_feature_name
    )
    association_id: str = Field(serialization_alias=association_id)
    number_of_explanations: int
    tone: str
    verbosity: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float | None = None


class Generation(BaseModel):
    content: str
    prompt_used: str
    association_id: str


class Explanation(BaseModel):
    feature_name: str
    strength: float
    qualitative_strength: str
    feature_value: Any
    per_n_gram_text_explanation: Optional[list[dict[str, Any]]] = Field(default=None)


class Prediction(BaseModel):
    predicted_label: Any
    class_probabilities: dict[str, float]
    explanations: list[Explanation]

    # Class variables
    _original_dict: ClassVar[dict[str, Any]] = {}
    _offers_prefix: ClassVar[str] = ""

    @classmethod
    def parse_dict(cls, data: dict[str, Any], offers_prefix: str) -> "Prediction":
        # Store the original dictionary and offers prefix
        cls._original_dict = data
        cls._offers_prefix = offers_prefix

        # Extract predicted label
        predicted_label = data["prediction"]

        # Extract class probabilities
        class_probabilities = {
            k.replace(f"{offers_prefix}_", ""): v
            for k, v in data.items()
            if k.startswith(f"{offers_prefix}_")
        }

        # Extract explanations
        explanations = []
        for i in range(1, 11):  # Assuming there are 10 explanations
            prefix = f"CLASS_1_EXPLANATION_{i}_"
            if f"{prefix}FEATURE_NAME" in data:
                explanation = Explanation(
                    feature_name=data[f"{prefix}FEATURE_NAME"],
                    strength=float(data[f"{prefix}STRENGTH"]),
                    qualitative_strength=data[f"{prefix}QUALITATIVE_STRENGTH"],
                    feature_value=data[f"{prefix}ACTUAL_VALUE"],
                    per_n_gram_text_explanation=(
                        json.loads(data[f"{prefix}TEXT_NGRAMS"])
                        if data[f"{prefix}TEXT_NGRAMS"] != "[]"
                        else None
                    ),
                )
                explanations.append(explanation)

        # Create and return the Prediction object
        return cls(
            predicted_label=predicted_label,
            class_probabilities=class_probabilities,
            explanations=explanations,
        )
