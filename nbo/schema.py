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
import sys
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

sys.path.append("..")
from nbo.i18n import gettext

association_id = "association_id"


class GenerativeDeploymentSettings(BaseModel):
    target_feature_name: str = "resultText"
    prompt_feature_name: str = "promptText"


class LLMModelSpec(BaseModel):
    input_price_per_1k_tokens: float
    output_price_per_1k_tokens: float


class OutcomeDetail(BaseModel):
    prediction: Any
    label: str
    description: str


class AppDataScienceSettings(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    association_id_column_name: str
    page_title: str
    page_subtitle: str
    record_identifier: dict[str, str]
    custom_metric_baselines: dict[str, float]
    default_number_of_explanations: int
    text_explanation_feature: str
    no_text_gen_label: Optional[str]
    tones: list[str]
    verbosity: list[str]
    target_probability_description: str
    email_prompt: str
    outcome_details: list[OutcomeDetail]
    system_prompt: str
    model_spec: LLMModelSpec


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
    system_prompt: str


class Generation(BaseModel):
    content: str
    prompt_used: str
    association_id: str


# Dictionary to map quantitative strength symbols to descriptive text
QUALITATIVE_STRENGTHS = {
    "+++": {"label": gettext("is significantly increasing"), "color": "#ff0000"},
    "++": {"label": gettext("is increasing"), "color": "#ff5252"},
    "+": {"label": gettext("is slightly increasing"), "color": "#ff7b7b"},
    "-": {"label": gettext("is slightly decreasing"), "color": "#c8deff"},
    "--": {"label": gettext("is decreasing"), "color": "#afcdfb"},
    "---": {"label": gettext("is significantly decreasing"), "color": "#91bafb"},
}


class Explanation(BaseModel):
    feature_name: str
    strength: float
    qualitative_strength: str
    feature_value: Any
    per_n_gram_text_explanation: Optional[list[dict[str, Any]]] = Field(default=None)

    @field_validator("qualitative_strength", mode="before")
    @classmethod
    def convert_qualitative_strength(
        cls, qualitative_strength: Any, info: ValidationInfo
    ) -> str:
        if (
            isinstance(qualitative_strength, str)
            and qualitative_strength in QUALITATIVE_STRENGTHS
        ):
            return qualitative_strength
        else:
            strength = info.data["strength"]
            return cls.create_qualitative_strength(strength)

    @staticmethod
    def create_qualitative_strength(strength: float) -> str:
        if strength > 0.5:
            return "+++"
        elif strength > 0.3:
            return "++"
        elif strength > 0:
            return "+"
        elif strength > -0.3:
            return "-"
        elif strength > -0.5:
            return "--"
        else:
            return "---"


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

        # multiclass case
        prefix = "CLASS_1_EXPLANATION_{}_"

        # binary case
        if prefix.format(1) + "FEATURE_NAME" not in data:
            prefix = prefix.replace("CLASS_1_", "")

        for i in range(1, 11):  # Assuming there are 10 explanations
            i_prefix = prefix.format(i)

            if f"{i_prefix}FEATURE_NAME" in data:
                explanation = Explanation(
                    feature_name=data[f"{i_prefix}FEATURE_NAME"],
                    strength=float(data[f"{i_prefix}STRENGTH"]),
                    qualitative_strength=data[f"{i_prefix}QUALITATIVE_STRENGTH"],
                    feature_value=data[f"{i_prefix}ACTUAL_VALUE"],
                    per_n_gram_text_explanation=(
                        json.loads(data[f"{i_prefix}TEXT_NGRAMS"])
                        if data[f"{i_prefix}TEXT_NGRAMS"] != "[]"
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
