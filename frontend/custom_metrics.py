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

import datetime as dt
import sys
from typing import Any, Mapping, Optional

import datarobot as dr
import pandas as pd
import streamlit as st
import tiktoken
from datarobot.models.deployment import CustomMetric  # type: ignore[attr-defined]
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob

sys.path.append("..")
from nbo.resources import GenerativeDeployment


@st.cache_data(show_spinner=False)
def calculate_metrics(
    metric_ids: dict[str, str], response: dict[str, Any]
) -> dict[str, float]:
    """Do the actual metric calculations"""
    metrics = {}
    # Prompt Tokens
    for metric_name in response:
        metrics[metric_ids[metric_name]] = response[metric_name]

    return metrics


def submit_metrics(
    metric_scores: Mapping[str, Optional[float]],
    request_id: Optional[str] = None,
) -> None:
    """Submit custom metric data to DataRobot"""
    generative_deployment = GenerativeDeployment()
    deployment = dr.Deployment.get(generative_deployment.id)  # type: ignore[attr-defined]

    timestamp = dt.datetime.now()
    # rev_metrics = {value: key for key, value in metric_ids.items()}
    for id, metric in metric_scores.items():
        custom_metric = CustomMetric.get(
            deployment_id=deployment.id,
            custom_metric_id=id,
        )
        custom_metric.submit_values(
            data=pd.DataFrame.from_records(
                [
                    {
                        "value": metric,
                        "timestamp": timestamp,
                        "association_id": request_id,
                        "sample_size": 1,
                    }
                ]
            ),
        )


# Define readability
@st.cache_data(show_spinner=False)
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


def get_num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


@st.cache_data(show_spinner=False)
def flesch_reading_ease(text: str) -> tuple[float, str]:
    sentences = text.count(".") + text.count("!") + text.count("?")
    words = len(text.split())
    syllables = sum(count_syllables(word) for word in text.split())

    try:
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
    except ZeroDivisionError:
        return 0.0, "Error"

    # Formula for Flesch reading ease
    score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)

    if score >= 50:
        readability = "High"
    elif score >= 30:
        readability = "Medium"
    else:
        readability = "Low"

    return score, readability


# Define estimated reading time
@st.cache_data(show_spinner=False)
def estimated_reading_time(text: str, wps: float = 225 / 60) -> int:
    words = len(text.split())
    seconds = words / wps
    return int(seconds)


@st.cache_data(show_spinner=False)
def get_sentiment(text: str) -> tuple[float, str]:
    blob = TextBlob(text)

    # Polarity
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


@st.cache_data(show_spinner=False)
def get_cosine_similarity(text1: str, text2: str) -> float:
    # Convert texts to vectors
    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform([text1, text2])

    # Compute the cosine similarity
    cosine_sim = cosine_similarity(count_matrix[0:1], count_matrix[1:2])[0][0]
    return float(cosine_sim)
