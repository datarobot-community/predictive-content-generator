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

import datetime as dt
from typing import Dict, Optional

from datarobot.rest import RESTClientObject
import streamlit as st
import tiktoken
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob


@st.cache_data(show_spinner=False)
def calculate_metrics(metric_ids: Dict[str, str], response: Dict) -> Dict[str, float]:
    """Do the actual metric calculations"""
    metrics = {}
    # Prompt Tokens
    for metric_name in response:
        metrics[metric_ids[metric_name]] = response[metric_name]

    return metrics


def submit_metrics(
    client: RESTClientObject,
    deployment_id: str,
    metric_scores: Dict[str, float],
    metric_ids: Dict[str, str],
    request_id: Optional[str] = None,
) -> None:
    """Submit custom metric data to DataRobot"""

    route = "deployments/{}/customMetrics/{}/fromJSON/"

    timestamp = dt.datetime.utcnow()
    rev_metrics = {value: key for key, value in metric_ids.items()}
    for id, metric in metric_scores.items():
        print(f"Sending {rev_metrics[id]}")

        rows = [
            {
                "timestamp": timestamp.isoformat(),
                "value": metric,
                "associationId": request_id,
            }
        ]
        response = client.post(
            url=route.format(deployment_id, id),
            json={
                "buckets": rows,
            },
        )
        response.raise_for_status()


# Define readability
@st.cache_data(show_spinner=False)
def count_syllables(word):
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
def flesch_reading_ease(text):
    sentences = text.count(".") + text.count("!") + text.count("?")
    words = len(text.split())
    syllables = sum(count_syllables(word) for word in text.split())

    try:
        avg_sentence_length = words / sentences
        avg_syllables_per_word = syllables / words
    except ZeroDivisionError:
        return 0.0

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
def estimated_reading_time(text, wps=225 / 60):
    words = len(text.split())
    seconds = words / wps
    return int(seconds)


@st.cache_data(show_spinner=False)
def get_sentiment(text):
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
def get_cosine_similarity(text1, text2):
    # Convert texts to vectors
    vectorizer = CountVectorizer()
    count_matrix = vectorizer.fit_transform([text1, text2])

    # Compute the cosine similarity
    cosine_sim = cosine_similarity(count_matrix[0:1], count_matrix[1:2])[0][0]
    return cosine_sim
