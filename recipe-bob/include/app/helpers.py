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

from __future__ import annotations
from typing import Any, Dict, List, TYPE_CHECKING
from urllib.parse import urljoin
import uuid

import datarobot as dr
import pandas as pd
import requests
import streamlit as st

if TYPE_CHECKING:
    from kedro.io import DataCatalog

# Dictionary to map quantitative strength symbols to descriptive text
QUALITATIVE_STRENGTHS = {
    "+++": {"label": "is significantly increasing", "color": "#ff0000"},
    "++": {"label": "is increasing", "color": "#ff5252"},
    "+": {"label": "is slightly increasing", "color": "#ff7b7b"},
    "-": {"label": "is slightly decreasing", "color": "#c8deff"},
    "--": {"label": "is decreasing", "color": "#afcdfb"},
    "---": {"label": "is significantly decreasing", "color": "#91bafb"},
}


def get_kedro_catalog(kedro_project_root: str) -> DataCatalog:
    """Initialize a kedro data catalog (as a singleton)."""
    if "KEDRO_CATALOG" not in st.session_state:
        try:
            import pathlib
            from kedro.framework.startup import bootstrap_project
            from kedro.framework.session import KedroSession
        except ImportError as e:
            raise ImportError(
                "Please ensure you've installed `kedro` and `kedro_datasets` to run this app locally"
            ) from e

        project_path = pathlib.Path(kedro_project_root).resolve()
        bootstrap_project(project_path)
        session = KedroSession.create(project_path)
        context = session.load_context()
        catalog = context.catalog

        # initializing a context & catalog is slow enough to be perceived; persist in session state
        st.session_state["KEDRO_CATALOG"] = catalog
    return st.session_state["KEDRO_CATALOG"]


def get_param(parameter: str) -> Any:
    """Get the parameter from the session state"""
    return st.session_state["params"][parameter]


class DataRobotPredictionError(Exception):
    """Raised if there are issues getting predictions from DataRobot"""


@st.cache_data(show_spinner=False)
def get_prediction_server_data(prediction_server_id: str) -> Dict[str, Any]:
    """Get prediction server data.

    Parameters
    ----------
    prediction_server_id : str
        The id of the prediction server

    Returns
    -------
    dict :
        The prediction server data
    """

    prediction_server = [
        i for i in dr.PredictionServer.list() if i.id == prediction_server_id
    ][0]
    return prediction_server.url, prediction_server.datarobot_key


def _raise_dataroboterror_for_status(response):
    """Raise DataRobotPredictionError if the request fails along with the response returned"""
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        err_msg = f"{response.status_code} Error: {response.text}"
        raise DataRobotPredictionError(err_msg)


@st.cache_data(show_spinner=False)
def make_datarobot_deployment_predictions(
    deployment_id: str,
    data: Dict[str, Any],
    max_explanations=None,
):
    """
    Make predictions on data provided using DataRobot deployment_id provided.
    See docs for details:
         https://app.datarobot.com/docs/predictions/api/dr-predapi.html

    Parameters
    ----------
    data : str
        If using CSV as input:
        Feature1,Feature2
        numeric_value,string

        Or if using JSON as input:
        [{"Feature1":numeric_value,"Feature2":"string"}]

    deployment_id : str
        The ID of the deployment to make predictions with.

    Returns
    -------
    Response schema:
        https://app.datarobot.com/docs/predictions/api/dr-predapi.html#response-schema

    Raises
    ------
    DataRobotPredictionError if there are issues getting predictions from DataRobot
    """
    print(f"Running prediction against deployment {deployment_id}")
    url = f"predApi/v1.0/deployments/{deployment_id}/predictions"
    api_key = get_param("api_token")
    prediction_server_id = get_param("prediction_server_id")

    prediction_server_url, datarobot_key = get_prediction_server_data(
        prediction_server_id
    )
    url = urljoin(prediction_server_url, url)

    headers = {
        "Content-Type": "text/plain; charset=UTF-8",
        "Authorization": f"Bearer {api_key}",
        "DataRobot-Key": datarobot_key,
    }

    params = (
        {}
        if max_explanations is None
        else {"maxExplanations": max_explanations, "maxNgramExplanations": "all"}
    )

    predictions_response = requests.post(
        url,
        data=data,
        headers=headers,
        params=params,
    )
    _raise_dataroboterror_for_status(predictions_response)

    return predictions_response.json()


def set_outcome_details(
    outcome_detail_list: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Convert outcome details into a dictionary"""

    return {
        i["prediction"]: {"label": i["label"], "description": i["description"]}
        for i in outcome_detail_list
    }


def create_qualitative_strength(strength: float):
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


def get_important_text_features(
    text_explanations: List[Dict[str, Any]],
    text: str,
    # n_selected=10,
    # use_downward_drivers=False,
) -> List[str]:
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
        start, end = ngram_index["startingIndex"], ngram_index["endingIndex"]
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
            qual_strength = create_qualitative_strength(ngram_texts[word])
            color = QUALITATIVE_STRENGTHS[qual_strength]["color"]
            word = html_style.format(color, word)
        all_words.append(word)
    text = " ".join(all_words)
    return text


def make_important_features_list(
    prediction_explanations: List[Dict[str, Any]],
) -> (str, Dict[str, float]):
    # Initialize an empty list to store response strings
    rsp = []

    # Loop through the filtered prediction explanations to build the response
    text_explanations = None
    for i in prediction_explanations:
        # Replace underscores in feature names with spaces
        feature = i["feature"].replace("_", " ")

        # Round feature values if they are integers or floats
        featureValue = (
            round(i["featureValue"], 0)
            if isinstance(i["featureValue"], (int, float))
            else i["featureValue"]
        )
        if (
            "perNgramTextExplanations" in i
            and i["perNgramTextExplanations"] is not None
            and i["feature"] == get_param("text_explanation_feature")
        ):
            text_explanations = get_important_text_features(
                i["perNgramTextExplanations"], i["featureValue"]
            )
            if i["qualitativeStrength"] not in QUALITATIVE_STRENGTHS:
                i["qualitativeStrength"] = create_qualitative_strength(i["strength"])
            explanation = (
                f"-{feature} {QUALITATIVE_STRENGTHS[i['qualitativeStrength']]['label']} "
                + get_param("target_probability_description")
            )

        else:
            if i["qualitativeStrength"] is None:
                i["qualitativeStrength"] = create_qualitative_strength(i["strength"])
            # Build explanation string
            explanation = (
                f"-{feature} of {featureValue} {QUALITATIVE_STRENGTHS[i['qualitativeStrength']]['label']} "
                + get_param("target_probability_description")
            )

            # Append the explanation to the response list
        rsp.append(explanation)

    return "\n\n".join(rsp), text_explanations


@st.cache_data(show_spinner=False)
def create_prompt(
    prediction_data,
    selected_record: str,
    number_of_explanations: int,
    tone: str,
    verbosity: str,
):
    email_prompt = get_param("email_prompt")
    target_description = get_param("target_probability_description")

    outcome_details = st.session_state.outcome_details

    predicted_label = prediction_data["prediction"]
    customer_predicted_label = outcome_details[predicted_label]["label"]
    outcome_description = outcome_details[predicted_label]["description"]

    prediction_explanations = [
        i for i in prediction_data["predictionExplanations"] if abs(i["strength"]) > 0
    ]
    rsp = []
    for i in prediction_explanations[:number_of_explanations]:
        if i["qualitativeStrength"] not in QUALITATIVE_STRENGTHS:
            i["qualitativeStrength"] = create_qualitative_strength(i["strength"])
        feature = i["feature"].replace("_", " ")
        featureValue = (
            int(i["featureValue"])
            if isinstance(i["featureValue"], (int, float))
            else i["featureValue"]
        )
        explanation = f"-{feature} of {featureValue} {QUALITATIVE_STRENGTHS[i['qualitativeStrength']]['label']} {target_description}"
        rsp.append(explanation)
    rsp = "\n\n".join(rsp)
    prompt = email_prompt.format(
        prediction_label=customer_predicted_label,
        selected_record=selected_record,
        outcome_description=outcome_description,
        tone=tone,
        verbosity=verbosity,
        rsp=rsp,
    )

    return prompt


def prepare_openai_request(
    prompt: str | List[str],
    model: str,
    temperature: float,
    request_id: str | List[str],
    number_of_explanations: int,
    tone: str,
    verbosity: str,
):
    prompt = [prompt] if isinstance(prompt, str) else prompt
    return pd.DataFrame(
        {
            get_param("prompt_feature_name"): prompt,
            "system_prompt": get_param("system_prompt"),
            "model": model,
            "temperature": temperature,
            get_param("association_id_column_name"): request_id,
            "numberOfExplanations": number_of_explanations,
            "tone": tone,
            "verbosity": verbosity,
        }
    )


@st.cache_data(show_spinner=False)
def get_llm_response(
    prediction: Dict[str, Any],
    selected_record: str,
    number_of_explanations: int,
    temperature: float,
    tone: str,
    verbosity: str,
    model: str,
):
    # Create prompt for GPT
    prompt = create_prompt(
        prediction_data=prediction["data"][0],
        selected_record=selected_record,
        number_of_explanations=number_of_explanations,
        tone=tone,
        verbosity=verbosity,
    )
    request_id = str(uuid.uuid4())

    # Get output
    request = prepare_openai_request(
        prompt,
        model=model,
        temperature=temperature,
        request_id=request_id,
        number_of_explanations=number_of_explanations,
        tone=tone,
        verbosity=verbosity,
    )

    response = response = make_datarobot_deployment_predictions(
        get_param("llm_deployment_id"),
        request.to_csv(index=False),
    )
    output = response["data"][0]["prediction"]
    return prompt, output, request_id


@st.cache_data(show_spinner=False)
def batch_email_responses(
    record_ids: List[str],
    predictions: List[Dict[str, Any]],
    number_of_explanations: int,
    temperature: float,
    tone: str,
    verbosity: str,
    model: str,
):
    prompts = []
    for i in range(len(record_ids)):
        selected_record = record_ids[i]

        prompt = create_prompt(
            prediction_data=predictions[i],
            selected_record=selected_record,
            number_of_explanations=number_of_explanations,
            tone=tone,
            verbosity=verbosity,
        )
        prompts.append(prompt)
    request_ids = [str(uuid.uuid4()) for _ in range(len(record_ids))]
    llm_request_data = prepare_openai_request(
        prompts,
        model=model,
        temperature=temperature,
        request_id=request_ids,
        number_of_explanations=number_of_explanations,
        tone=tone,
        verbosity=verbosity,
    )
    response = make_datarobot_deployment_predictions(
        get_param("llm_deployment_id"),
        llm_request_data.to_csv(index=False).encode('utf-8'),
    )
    emails = [i["prediction"] for i in response["data"]]

    outcome_details = st.session_state.outcome_details
    predicted_labels = []
    for prediction in predictions:
        predicted_label = prediction["prediction"]
        customer_predicted_label = outcome_details[predicted_label]["label"]
        predicted_labels.append(customer_predicted_label)

    return pd.DataFrame(
        {
            "record_id": record_ids,
            "label": predicted_labels,
            "email": emails,
        }
    )
