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

import datetime as dt
import logging
from typing import Any, Callable, Dict, Mapping, Optional, Tuple

import datarobot as dr
import pandas as pd
import tiktoken
from datarobot.models.deployment.custom_metrics import CustomMetric as DrCustomMetric
from pydantic import BaseModel, ConfigDict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit.elements.metric import DeltaColor
from textblob import TextBlob

from nbo.resources import CustomMetricIds, GenerativeDeployment

logger = logging.getLogger(__name__)


class MetricInput(BaseModel):
    """Represents the input requirements for a metric calculation"""

    name: str
    type: str
    description: str = ""
    required: bool = True


class CustomMetric(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Basic metadata
    id: str
    name: str
    description: str
    units: str

    # Display configuration
    show_in_app: bool = True
    display_icon: str
    display_format: str = "{value}"
    display_column_width: int = 3
    delta_color: DeltaColor = "normal"

    # Metric behavior
    baseline_value: float
    directionality: str
    is_model_specific: bool = False
    aggregation_type: dr.enums.CustomMetricAggregationType = (
        dr.enums.CustomMetricAggregationType.AVERAGE  # type: ignore[assignment]
    )

    # Calculation function
    required_inputs: list[MetricInput]
    calculate_fn: Callable[..., Tuple[float, Any]]

    def calculate(self, *args: Any, **kwargs: Any) -> Tuple[float, Any]:
        """Calculate the metric value and display value"""
        return self.calculate_fn(*args, **kwargs)

    def get_delta(self, value: float) -> float:
        """Calculate the delta from baseline"""
        if self.directionality == dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER:
            return value - self.baseline_value
        return self.baseline_value - value

    def format_delta(self, delta: float) -> str:
        """Format the delta value for display"""
        if self.units == "Score":
            return f"{delta:.2f}"
        elif self.units == "Percent":
            return f"{delta:.1%}"
        elif self.units == "Seconds":
            return f"{int(delta)} seconds"
        return f"{delta}"


# Metric calculation functions
def count_syllables(word: str) -> int:
    vowels = "aeiouy"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count


def calculate_readability(generated_email: str) -> Tuple[float, str]:
    """Calculate Flesch reading ease score and readability level"""
    sentences = (
        generated_email.count(".")
        + generated_email.count("!")
        + generated_email.count("?")
    )
    words = len(generated_email.split())
    syllables = sum(count_syllables(word) for word in generated_email.split())

    try:
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
    except ZeroDivisionError:
        return 0.0, "Error"

    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)

    if score >= 50:
        readability = "High"
    elif score >= 30:
        readability = "Medium"
    else:
        readability = "Low"

    return score, readability


def calculate_reading_time(generated_email: str) -> Tuple[int, int]:
    """Calculate estimated reading time in seconds"""
    words = len(generated_email.split())
    seconds = int(words / (225 / 60))
    return seconds, seconds


def calculate_sentiment(generated_email: str) -> Tuple[float, str]:
    """Calculate sentiment score and reaction emoji"""
    blob = TextBlob(generated_email)
    polarity = blob.sentiment.polarity

    reactions = ["😠", "🙁", "😐", "🙂", "😃"]
    if polarity >= 0.33:
        reaction = reactions[4]
    elif polarity >= 0.2:
        reaction = reactions[3]
    elif polarity >= -0.1:
        reaction = reactions[2]
    elif polarity >= -0.33:
        reaction = reactions[1]
    else:
        reaction = reactions[0]

    return polarity, reaction


def calculate_confidence(prompt_used: str, generated_email: str) -> Tuple[float, float]:
    """Calculate confidence score using cosine similarity"""
    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform([prompt_used, generated_email])
    similarity = float(cosine_similarity(count_matrix[0:1], count_matrix[1:2])[0][0])
    return similarity, similarity


def get_num_tokens_from_string(
    text: str, encoding_name: str = "cl100k_base"
) -> Tuple[int, int]:
    """Calculate number of tokens"""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens, num_tokens


def calculate_input_tokens(
    prompt_used: str, encoding_name: str = "cl100k_base"
) -> Tuple[int, int]:
    return get_num_tokens_from_string(prompt_used, encoding_name)


def calculate_output_tokens(
    generated_email: str, encoding_name: str = "cl100k_base"
) -> Tuple[int, int]:
    return get_num_tokens_from_string(generated_email, encoding_name)


def calculate_cost(
    prompt_used: str, generated_email: str, input_cost: float, output_cost: float
) -> Tuple[float, float]:
    """Calculate total cost"""
    input_tokens, _ = calculate_input_tokens(prompt_used, encoding_name="cl100k_base")
    output_tokens, _ = calculate_output_tokens(
        generated_email, encoding_name="cl100k_base"
    )
    total_cost = (input_tokens / 1000 * input_cost) + (
        output_tokens / 1000 * output_cost
    )
    return total_cost, total_cost


# Define all custom metrics
CUSTOM_METRICS = {
    "user_feedback": CustomMetric(
        id="user_feedback",
        name="User Feedback",
        description="User provided rating of the generated email",
        units="Upvotes",
        show_in_app=False,
        display_icon="🗳️",
        display_format="{value}",
        baseline_value=0.75,
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="feedback_value",
                type="float",
                description="Binary feedback value (1 for upvote, 0 for downvote)",
            )
        ],
        calculate_fn=lambda: None,
    ),
    "readability": CustomMetric(
        id="readability",
        name="Readability",
        description="Flesch reading ease score and readability level",
        units="Score",
        display_icon="📖",
        display_format="{value}",
        baseline_value=50,
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="generated_email", type="str", description="Text to analyze"
            )
        ],
        calculate_fn=calculate_readability,
    ),
    "reading_time": CustomMetric(
        id="reading_time",
        name="Reading Time",
        description="Estimated reading time",
        units="Seconds",
        display_icon="⏱️",
        display_format="{value} seconds",
        baseline_value=75,
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        delta_color="inverse",
        required_inputs=[
            MetricInput(
                name="generated_email", type="str", description="Text to analyze"
            )
        ],
        calculate_fn=calculate_reading_time,
    ),
    "sentiment": CustomMetric(
        id="sentiment",
        name="Sentiment",
        description="Text sentiment analysis",
        units="Score",
        display_icon="✍",
        display_format="{value}",
        baseline_value=0.3,
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="generated_email", type="str", description="Text to analyze"
            )
        ],
        calculate_fn=calculate_sentiment,
    ),
    "confidence": CustomMetric(
        id="confidence",
        name="Confidence",
        description="Confidence score based on prompt-response similarity",
        units="Percent",
        display_icon="✅",
        display_format="{value:.1%}",
        baseline_value=0.65,
        directionality=dr.enums.CustomMetricDirectionality.HIGHER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="prompt_used", type="str", description="First text for comparison"
            ),
            MetricInput(
                name="generated_email",
                type="str",
                description="Second text for comparison",
            ),
        ],
        calculate_fn=calculate_confidence,
    ),
    "prompt_tokens": CustomMetric(
        id="prompt_tokens",
        name="Prompt Tokens",
        description="Number of tokens in the prompt",
        units="Count",
        show_in_app=False,
        display_icon="🔤",
        display_format="{value:,}",
        baseline_value=225,
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="prompt_used", type="str", description="First text for comparison"
            ),
            MetricInput(
                name="encoding_name",
                type="str",
                description="Tokenizer encoding",
                required=False,
            ),
        ],
        calculate_fn=calculate_input_tokens,
    ),
    "response_tokens": CustomMetric(
        id="response_tokens",
        name="Response Tokens",
        description="Number of tokens in the response",
        units="Count",
        show_in_app=False,
        display_icon="🔤",
        display_format="{value:,}",
        baseline_value=225,
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="generated_email", type="str", description="Text to tokenize"
            ),
            MetricInput(
                name="encoding_name",
                type="str",
                description="Tokenizer encoding",
                required=False,
            ),
        ],
        calculate_fn=calculate_output_tokens,
    ),
    "llm_cost": CustomMetric(
        id="llm_cost",
        name="LLM Cost",
        description="Total cost of LLM API usage",
        units="Dollars",
        display_icon="💰",
        display_format="${value:.4f}",
        baseline_value=0.025,
        directionality=dr.enums.CustomMetricDirectionality.LOWER_IS_BETTER,
        required_inputs=[
            MetricInput(
                name="prompt_used", type="str", description="First text for comparison"
            ),
            MetricInput(
                name="generated_email", type="str", description="Text to tokenize"
            ),
            MetricInput(
                name="input_cost", type="float", description="Cost per 1K input tokens"
            ),
            MetricInput(
                name="output_cost",
                type="float",
                description="Cost per 1K output tokens",
            ),
        ],
        calculate_fn=calculate_cost,
    ),
}


class MetricsManager:
    def __init__(self, metrics: Dict[str, CustomMetric]):
        self.metrics = metrics

    def get_baseline_values(self) -> Dict[str, float]:
        """Get baseline values for all metrics"""
        return {metric.id: metric.baseline_value for metric in self.metrics.values()}

    def calculate_all_metrics(self, **inputs: Any) -> Dict[str, Dict[str, Any]]:
        """Calculate all metrics using provided inputs"""
        results: dict[str, Any] = {}
        missing_inputs: dict[str, set[str]] = {}

        # First pass: Calculate metrics that don't depend on other metrics
        for metric_id, metric in self.metrics.items():
            # Check if all required inputs are available
            required_inputs = {
                input.name for input in metric.required_inputs if input.required
            }

            # Filter inputs for this metric
            metric_inputs = {}
            missing_for_metric = set()

            for input_def in metric.required_inputs:
                if input_def.name in inputs:
                    metric_inputs[input_def.name] = inputs[input_def.name]
                elif input_def.name in results:
                    # Use result from previously calculated metric
                    metric_inputs[input_def.name] = results[input_def.name]["value"]
                elif input_def.required:
                    missing_for_metric.add(input_def.name)

            # Track missing inputs for this metric
            if missing_for_metric:
                missing_inputs[metric_id] = missing_for_metric

            # Calculate metric if all required inputs are available
            if all(req_input in metric_inputs for req_input in required_inputs):
                value, display = metric.calculate(**metric_inputs)
                results[metric_id] = {"value": value, "display": display}

        return results

    def submit_metrics(
        self,
        metric_scores: Mapping[str, Optional[float]],
        request_id: Optional[str] = None,
        timestamp: Optional[dt.datetime] = None,
    ) -> None:
        """Submit custom metric data to DataRobot"""
        if timestamp is None:
            timestamp = dt.datetime.now()

        # Get deployment
        deployment_id = GenerativeDeployment().id
        custom_metric_ids = CustomMetricIds().custom_metric_ids
        # Submit each metric
        for metric_id, value in metric_scores.items():
            if value is not None:  # Only submit if we have a value
                custom_metric = DrCustomMetric.get(
                    deployment_id=deployment_id,
                    custom_metric_id=custom_metric_ids[metric_id],
                )

                # Create DataFrame with metric data
                metric_data = pd.DataFrame.from_records(
                    [
                        {
                            "value": value,
                            "timestamp": timestamp,
                            "association_id": request_id,
                            "sample_size": 1,
                        }
                    ]
                )

                # Submit to DataRobot
                custom_metric.submit_values(data=metric_data)


metrics_manager = MetricsManager(CUSTOM_METRICS)
