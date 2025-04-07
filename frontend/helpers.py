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

import itertools
import subprocess
import sys
import uuid
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import yaml
from pydantic import ValidationError

sys.path.append("..")  # Adds the parent directory to the system path
from nbo.custom_metrics import CUSTOM_METRICS, CustomMetric
from nbo.predict import make_generative_deployment_predictions
from nbo.resources import (
    CustomMetricIds,
    GenerativeDeployment,
    PredAIDeployment,
)
from nbo.schema import (
    QUALITATIVE_STRENGTHS,
    AppDataScienceSettings,
    Explanation,
    Generation,
    LLMRequest,
    OutcomeDetail,
    Prediction,
)


def get_stack_suffix() -> str:
    try:
        return (
            "."
            + subprocess.check_output(
                ["pulumi", "stack", "--show-name", "--non-interactive"],
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
        )
    except Exception:
        pass
    return ""


try:
    with open(f"app_settings{get_stack_suffix()}.yaml") as f:
        app_settings = AppDataScienceSettings(**yaml.safe_load(f))

    custom_metric_ids = CustomMetricIds().custom_metric_ids
    pred_ai_deployment_id = PredAIDeployment().id
    generative_deployment_id = GenerativeDeployment().id
except (FileNotFoundError, ValidationError) as e:
    raise ValueError(
        (
            "Unable to read App settings. If running locally, verify you have selected "
            "the correct stack and that it is active using `pulumi stack output`. "
            "If running in DataRobot, verify your runtime parameters have been set correctly."
        )
    ) from e


def set_outcome_details(
    outcome_detail_list: List[OutcomeDetail],
) -> Dict[str, OutcomeDetail]:
    """Convert outcome details into a dictionary"""

    return {
        outcome_detail.prediction: outcome_detail
        for outcome_detail in outcome_detail_list
    }


def get_important_text_features(
    text_explanations: List[Dict[str, Any]],
    text: str,
    # n_selected=10,
    # use_downward_drivers=False,
) -> dict[str, Any]:
    """
    Get the important text features from the text explanations.

    Parameters
    ----------
    text_explanations : List[Dict[str, Any]]
        The text explanations.
    text : str
        The text to extract the important features from.
    Returns
    -------
    List[str]
        The important text features.
    """
    ngram_texts = {}

    for word in text_explanations:
        ngram_index = word["ngrams"][0]
        start, end = ngram_index["starting_index"], ngram_index["ending_index"]
        text_word = text[start:end]
        if text_word not in ngram_texts:
            ngram_texts[text_word] = word["strength"]
    return ngram_texts


def color_texts(text: str, ngram_texts: Dict[str, float]) -> str:
    """
    Color the text based on the strength of the ngram.

    Parameters
    ----------
    text : str
        The text to color.
    ngram_texts : Dict[str, float]
        The ngram texts.

    Returns
    -------
    str
        The colored text.
    """
    all_words = []
    html_style = "<mark style='padding: 0 5px 0 5px; border-radius: 5px;background-color:{}'>{}</mark>"
    for word in text.replace(":", "").split(" "):
        if word in ngram_texts and ngram_texts[word] != 0:
            qual_strength = Explanation.create_qualitative_strength(ngram_texts[word])
            color = QUALITATIVE_STRENGTHS[qual_strength]["color"]
            word = html_style.format(color, word)
        all_words.append(word)
    text = " ".join(all_words)
    return text


def make_important_features_list(
    prediction_explanations: list[Explanation],
) -> tuple[str, dict[str, float]]:
    # Initialize an empty list to store response strings
    rsp = []

    # Loop through the filtered prediction explanations to build the response
    text_explanations = None
    for prediction_explanation in prediction_explanations:
        # Replace underscores in feature names with spaces
        feature = prediction_explanation.feature_name.replace("_", " ")

        # Round feature values if they are integers or floats
        featureValue = (
            round(prediction_explanation.feature_value, 0)
            if isinstance(prediction_explanation.feature_value, (int, float))
            else prediction_explanation.feature_value
        )
        if (
            prediction_explanation.per_n_gram_text_explanation
            and len(prediction_explanation.per_n_gram_text_explanation) > 0
            and prediction_explanation.feature_name
            == app_settings.text_explanation_feature
        ):
            text_explanations = get_important_text_features(
                prediction_explanation.per_n_gram_text_explanation,
                prediction_explanation.feature_value,
            )
            if prediction_explanation.qualitative_strength not in QUALITATIVE_STRENGTHS:
                prediction_explanation.qualitative_strength = (
                    Explanation.create_qualitative_strength(
                        prediction_explanation.strength
                    )
                )
            explanation = (
                f"-{feature} {QUALITATIVE_STRENGTHS[prediction_explanation.qualitative_strength]['label']} "
                + app_settings.target_probability_description
            )

        else:
            if (
                prediction_explanation.qualitative_strength is None
                or prediction_explanation.qualitative_strength
                != prediction_explanation.qualitative_strength
            ):
                prediction_explanation.qualitative_strength = (
                    Explanation.create_qualitative_strength(
                        prediction_explanation.strength
                    )
                )
            # Build explanation string
            explanation = (
                f"-{feature} of {featureValue} {QUALITATIVE_STRENGTHS[prediction_explanation.qualitative_strength]['label']} "
                + app_settings.target_probability_description
            )

            # Append the explanation to the response list
        rsp.append(explanation)

    return "\n\n".join(rsp), text_explanations  # type: ignore[return-value]


def create_prompt(
    prediction_data: Prediction,
    selected_record: str,
    number_of_explanations: int,
    tone: str,
    verbosity: str,
) -> str:
    email_prompt = app_settings.email_prompt
    target_description = app_settings.target_probability_description

    outcome_details = st.session_state.outcome_details

    predicted_label = prediction_data.predicted_label
    customer_predicted_label = outcome_details[predicted_label].label
    outcome_description = outcome_details[predicted_label].description
    prediction_explanations = prediction_data.explanations
    prediction_explanations = [
        pe for pe in prediction_explanations if abs(pe.strength) > 0
    ]
    rsp_list = []
    for pe in prediction_explanations[:number_of_explanations]:
        if pe.qualitative_strength not in QUALITATIVE_STRENGTHS:
            pe.qualitative_strength = Explanation.create_qualitative_strength(
                pe.strength
            )
        feature = pe.feature_name.replace("_", " ")
        featureValue = (
            float(pe.feature_value)
            if isinstance(pe.feature_value, (int, float))
            else pe.feature_value
        )
        explanation = f"-{feature} of {featureValue} {QUALITATIVE_STRENGTHS[pe.qualitative_strength]['label']} {target_description}"
        rsp_list.append(explanation)
    rsp = "\n\n".join(rsp_list)
    prompt = email_prompt.format(
        prediction_label=customer_predicted_label,
        selected_record=selected_record,
        outcome_description=outcome_description,
        tone=tone,
        verbosity=verbosity,
        rsp=rsp,
    )

    return prompt


def get_llm_response(
    prediction: Prediction,
    selected_record: str,
    number_of_explanations: int,
    tone: str,
    verbosity: str,
) -> Generation:
    # Create prompt for GPT
    prompt = create_prompt(
        prediction_data=prediction,
        selected_record=selected_record,
        number_of_explanations=number_of_explanations,
        tone=tone,
        verbosity=verbosity,
    )
    request_id = str(uuid.uuid4())

    # Get output
    request = LLMRequest(
        prompt=prompt,
        association_id=request_id,
        number_of_explanations=number_of_explanations,
        tone=tone,
        verbosity=verbosity,
        system_prompt=app_settings.system_prompt,
    )
    generations = make_generative_deployment_predictions(
        [request],
    )
    # output = response.to_dict(orient="records")[0]["prediction"]
    return generations[0]


def batch_email_responses(
    record_ids: List[str],
    predictions: List[Prediction],
    number_of_explanations: int,
    tone: str,
    verbosity: str,
) -> pd.DataFrame:
    prompts = []
    for selected_record, prediction in zip(record_ids, predictions):
        prompt = create_prompt(
            prediction_data=prediction,
            selected_record=selected_record,
            number_of_explanations=number_of_explanations,
            tone=tone,
            verbosity=verbosity,
        )
        prompts.append(prompt)
    request_ids = [str(uuid.uuid4()) for _ in range(len(record_ids))]
    llm_request_data = [
        LLMRequest(
            prompt=prompt,
            association_id=request_id,
            number_of_explanations=number_of_explanations,
            tone=tone,
            verbosity=verbosity,
            system_prompt=app_settings.system_prompt,
        )
        for prompt, request_id in zip(prompts, request_ids)
    ]
    generations = make_generative_deployment_predictions(
        llm_request_data,
    )
    emails = [generation.content for generation in generations]

    outcome_details = st.session_state.outcome_details
    predicted_labels = []
    for prediction in predictions:
        predicted_label = prediction.predicted_label
        customer_predicted_label = outcome_details[predicted_label].label
        predicted_labels.append(customer_predicted_label)

    return pd.DataFrame(
        {
            "record_id": record_ids,
            "label": predicted_labels,
            "email": emails,
        }
    )


@st.cache_data(show_spinner=False)
def format_metrics_for_datarobot(
    results: Dict[str, Dict[str, Any]],
) -> Dict[str, float]:
    """Format metrics results for DataRobot submission"""
    return {metric_id: result["value"] for metric_id, result in results.items()}


def display_custom_metric(
    metric: CustomMetric, value: float, display_value: Any
) -> None:
    """Display the metric in Streamlit"""
    delta = metric.get_delta(value)
    st.metric(
        label=f"{metric.display_icon} {metric.name}",
        value=metric.display_format.format(value=display_value),
        delta=metric.format_delta(delta),
        delta_color=metric.delta_color,
    )


def display_metrics(metrics_results: Dict[str, Dict[str, Any]]) -> None:
    """Display all metrics in Streamlit"""
    st.subheader("**Monitoring Metrics:**")
    st.markdown("---")

    metrics_results = {
        k: v for k, v in metrics_results.items() if CUSTOM_METRICS[k].show_in_app
    }
    metrics = {k: v for k, v in CUSTOM_METRICS.items() if v.show_in_app}
    # Create columns for metrics display
    cols = st.columns(
        list(
            itertools.chain(
                *zip(
                    [metric.display_column_width for metric in metrics.values()],
                    [1] * (len(metrics)),
                )
            )
        )
    )  # Add spacing columns - see https://www.geeksforgeeks.org/python-interleave-multiple-lists-of-same-length/

    # Display each metric
    for i, (metric_id, result) in enumerate(metrics_results.items()):
        with cols[i * 2]:  # Skip spacing columns
            display_custom_metric(
                metrics[metric_id],
                value=result["value"],
                display_value=result["display"],
            )

    st.markdown("---")
