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

import os

import datarobot as dr
import pandas as pd
import streamlit as st
import yaml

from custom_metrics import (
    calculate_metrics,
    estimated_reading_time,
    flesch_reading_ease,
    get_cosine_similarity,
    get_num_tokens_from_string,
    get_sentiment,
    submit_metrics,
)
from helpers import (
    batch_email_responses,
    color_texts,
    get_kedro_catalog,
    get_llm_response,
    get_param,
    make_datarobot_deployment_predictions,
    make_important_features_list,
    set_outcome_details,
)


if "params" not in st.session_state:
    try:
        # in production, parameters are available in the working directory
        with open("app_parameters.yaml", "r") as f:
            st.session_state["params"] = yaml.safe_load(f)
        st.session_state["params"]["endpoint"] = os.environ["DATAROBOT_ENDPOINT"]
        st.session_state["params"]["api_token"] = os.environ["DATAROBOT_API_TOKEN"]

    except (FileNotFoundError, KeyError):
        # during local dev, parameters can be retrieved from the kedro catalog
        project_root = "../../"

        catalog = get_kedro_catalog(project_root)
        st.session_state["params"] = yaml.safe_load(
            catalog.load("deploy_streamlit_app.app_parameters").read_bytes()
        )
        st.session_state["params"]["endpoint"] = catalog.load(
            "params:credentials.datarobot.endpoint"
        )
        st.session_state["params"]["api_token"] = catalog.load(
            "params:credentials.datarobot.api_token"
        )

params = st.session_state["params"]

st.set_page_config(
    layout="wide",
    page_title=get_param("application_name"),
    page_icon="./datarobot_favicon.png",
)

with open("./style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


# Set environment vars
RECORD_IDENTIFIER = params["record_identifier"]
CUSTOM_METRIC_IDS = params["custom_metric_ids"]
CUSTOM_METRIC_BASELINES = params["custom_metric_baselines"]


@st.cache_data(show_spinner=False)
def get_dataset(dataset_id):
    dataset = dr.Dataset.get(dataset_id)
    df = dataset.get_as_dataframe()
    return df


def main():
    # Initialize DataRobot client and objects
    if "DATAROBOT_CLIENT" not in st.session_state:
        st.session_state["DATAROBOT_CLIENT"] = dr.Client(
            token=get_param("api_token"), endpoint=get_param("endpoint")
        )
    if "oucome_details" not in st.session_state:
        st.session_state["outcome_details"] = set_outcome_details(
            get_param("outcome_details")
        )

    # Get the data
    df = get_dataset(dataset_id=get_param("dataset_id"))

    # Initialize session states
    if "model" not in st.session_state:
        st.session_state.model = get_param("models")[0]
    if "temperature" not in st.session_state:
        st.session_state.temperature = get_param("default_temperature")
    if "numberOfExplanations" not in st.session_state:
        st.session_state.numberOfExplanations = get_param(
            "default_number_of_explanations"
        )
    if "tone" not in st.session_state:
        st.session_state.tone = get_param("tones")[0]
    if "verbosity" not in st.session_state:
        st.session_state.verbosity = get_param("verbosity")[0]
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "predicted_label" not in st.session_state:
        st.session_state.predicted_label = ""
    if "predicted_probability" not in st.session_state:
        st.session_state.predicted_probability = ""
    if "unique_uuid" not in st.session_state:
        st.session_state.unique_uuid = ""
    if "bulk_generated" not in st.session_state:
        st.session_state.bulk_generated = False
        st.session_state.bulk_prediction_results = (
            pd.DataFrame().to_csv().encode("utf-8")
        )

    # Create the sidebar section
    with st.sidebar:
        # Sidebar title and description
        st.title("Email Settings")
        st.caption("Configure the settings used to create your email")

        # Horizontal line
        st.markdown("---")

        # Prompt settings section
        st.markdown("**Prompt Settings:** ")

        # Create a form for settings
        with st.form(key="settings_selection"):
            # Dropdown for model selection
            model = st.selectbox(
                "Select a model type:",
                [i["name"] for i in get_param("models")],
                index=1,
                help="Model controls the underlying LLM selection.",
            )

            temperature = st.number_input(
                "Select a temperature value:",
                min_value=0.0,
                max_value=2.0,
                value=get_param("default_temperature"),
                step=0.1,
                help=(
                    "The temperature argument in OpenAI's GPT determines the "
                    "randomness of the model's output."
                ),
            )
            # Number input for selecting the number of explanations
            number_of_explanations = st.number_input(
                label="Select the number of explanations:",
                min_value=0,
                max_value=10,
                value=get_param("default_number_of_explanations"),
                step=1,
                help=(
                    "The number of explanations argument controls how "
                    "many prediction explanations we pass to our prompt."
                ),
            )

            # Dropdown for tone selection
            tone = st.selectbox(
                "Select a tone:",
                get_param("tones"),
                index=0,
                help="Tone controls the attitude of the email.",
            )

            # Dropdown for verbosity selection
            verbosity = st.selectbox(
                "Select a verbosity:",
                get_param("verbosity"),
                index=0,
                help="Verbosity helps to determine the length and wordiness of the email.",
            )

            # Apply button for the form
            new_settings_run = st.form_submit_button("Apply", type="primary")

            # Update session state variables upon form submission
            if new_settings_run:
                st.session_state.model = [
                    i for i in get_param("models") if i["name"] == model
                ][0]
                st.session_state.temperature = temperature
                st.session_state.numberOfExplanations = number_of_explanations
                st.session_state.tone = tone
                st.session_state.verbosity = verbosity

        # Monitoring settings section
        st.markdown("**Monitoring Settings:** ")

        # Sidebar caption with hyperlink
        st.caption(
            f"See [here](https://app.datarobot.com/console-nextgen/deployments/{get_param('llm_deployment_id')}/overview) to view and update tracking data"
        )

    # Create our shared title container
    title_container = st.container()

    with title_container:
        (
            col1,
            _,
        ) = title_container.columns([1, 2])
        col1.image("./DataRobot.png", width=200)

        st.markdown(
            f"<h1 style='text-align: center;'>{get_param('page_title')}</h1>",
            unsafe_allow_html=True,
        )
        st.write(get_param("page_subtitle"))

        new_email, multiple_emails, outcome_information = st.tabs(
            ["New Draft", "Batch Emails", "Outcome Details"]
        )

    with new_email:
        # Create containers for different sections of the page
        customer_selection_container = st.container()
        prediction_response_container = st.container()
        text_response_container = st.container()
        email_draft_container = st.container()
        post_email_container = st.container()

        record_id = RECORD_IDENTIFIER["column_name"]
        record_display_name = RECORD_IDENTIFIER["display_name"]

        # Extract unique customer names from the dataframe
        customers_list = df[record_id].unique()

        # Customer selection form and dropdown
        with customer_selection_container:
            with st.form(key="customer_selection"):
                (
                    col1,
                    _,
                ) = st.columns([2, 6])
                # First column: Dropdown to select a customer
                with col1:
                    selected_record = st.selectbox(
                        f"Select a {record_display_name}:", customers_list, index=0
                    )
                    submitted = st.form_submit_button("Submit", type="secondary")

        # If the form has been submitted, or if a previous submission exists in session_state
        if submitted or st.session_state.submitted:
            # Set the 'submitted' session_state to True
            st.session_state.submitted = True

            # Spinner appears while the marketing email is being generated
            with st.spinner(
                f"Generating response and assessment metrics for {selected_record}..."
            ):
                # Filter the dataframe to get the row corresponding to the selected customer
                prediction_row = (
                    df.loc[df[record_id] == selected_record, :]
                    .reset_index(drop=True)
                    .copy()
                )

                # Make a prediction using DataRobot's deployment API
                prediction = make_datarobot_deployment_predictions(
                    get_param("deployment_id"),
                    prediction_row.to_csv(index=False),
                    max_explanations=number_of_explanations,  # Number of explanations you want (if applicable)
                )

                # Extract the predicted label and its probability
                predicted_label = prediction["data"][0]["prediction"]
                customer_prediction_label = f"**Predicted Label:** {st.session_state['outcome_details'][predicted_label]['label']}"
                customer_prediction_probability = f"**Predicted Probability:** {max(prediction['data'][0]['predictionValues'], key=lambda x: x['value'])['value'] :.1%}"
                # Store the prediction information in the session state
                st.session_state.predicted_label = customer_prediction_label
                st.session_state.predicted_probability = customer_prediction_probability

                # Clear spinner once predictions are made
                st.empty()

                # Container to hold the email draft section
                with prediction_response_container:
                    # Add a bit of space for better layout
                    st.write("\n\n")
                    deployment = dr.Deployment.get(get_param("deployment_id"))
                    project_id = deployment.model.get("project_id")

                    # Informational expander
                    prediction_info_expander = st.expander(
                        f"Drafted an email for {selected_record}! Expand the container to get more info or check the model out [here](https://app.datarobot.com/projects/{project_id}/models).",
                        expanded=False,
                    )

                    with prediction_info_expander:
                        # Filter to prediction explanations that have strength greater than 0
                        prediction_explanations = prediction["data"][0][
                            "predictionExplanations"
                        ]
                        rsp, text_explanations = make_important_features_list(
                            prediction_explanations=prediction_explanations,
                        )

                        st.info(
                            f"\n\n{customer_prediction_label}\n\n{customer_prediction_probability}\n\n**List of Prediction Explanations:**\n\n{rsp}"
                        )

                with text_response_container:
                    if text_explanation := get_param("text_explanation_feature"):
                        with st.expander(
                            "See the most important items in text feature "
                            f"`{text_explanation}` that influenced the "
                            f"prediction {customer_prediction_label}"
                        ):
                            if text_explanations:
                                st.markdown(
                                    color_texts(
                                        prediction_row.at[0, text_explanation],
                                        text_explanations,
                                    ),
                                    unsafe_allow_html=True,
                                )

                with email_draft_container:
                    # Add a bit of space for better layout
                    st.write("\n\n")
                    if predicted_label == get_param("no_text_gen_label"):
                        generated_email = (
                            "Our model predicted that you are better off not "
                            f"targeting {selected_record} with any email "
                            "offer. The best next step is to not take any "
                            "action."
                        )
                        st.error(generated_email)
                        st.stop()
                    else:
                        # Log the number of explanations to be used in the prompt
                        print(
                            f"Incorporating {st.session_state.numberOfExplanations} prediction explanations into the prompt"
                        )
                        # Generate the email content based on the prediction
                        prompt, generated_email, request_id = get_llm_response(
                            prediction,
                            selected_record=selected_record,
                            number_of_explanations=st.session_state.numberOfExplanations,
                            temperature=st.session_state.temperature,
                            tone=st.session_state.tone,
                            verbosity=st.session_state.verbosity,
                            model=st.session_state.model["name"],
                        )

                        st.session_state.unique_uuid = request_id

                        # Display the generated email
                        st.subheader("Newly Generated Email:")
                        generated_email = st.text_area(
                            label="Email",
                            value=generated_email,
                            height=450,
                            label_visibility="collapsed",
                        )

                    with post_email_container:
                        # Create multiple columns for different components
                        _, _, c2, c3 = st.columns([10, 10, 1, 1])

                        # Button for positive feedback in the second column
                        with c2:
                            thumbs_up = st.button("👍🏻")

                        # Button for negative feedback in the third column
                        with c3:
                            thumbs_down = st.button("👎🏻")

                        # Capture feedback when either button is clicked
                        if thumbs_up or thumbs_down:
                            # Report back to deployment
                            feedback = 1 if thumbs_up else 0 if thumbs_down else None
                            user_feedback_id = CUSTOM_METRIC_IDS["user_feedback"]
                            user_feedback_metric_values = {user_feedback_id: feedback}
                            submit_metrics(
                                st.session_state["DATAROBOT_CLIENT"],
                                get_param("llm_deployment_id"),
                                user_feedback_metric_values,
                                CUSTOM_METRIC_IDS,
                                request_id=st.session_state.unique_uuid,
                            )

                            st.toast(
                                "Your feedback has been successfully saved!", icon="🥳"
                            )

                        # Clear any Streamlit widgets that may be set to display below this
                        st.empty()
                        st.write("\n")

                        # Calculate a Flesch Readability Score
                        score, readability = flesch_reading_ease(generated_email)
                        score_baseline = CUSTOM_METRIC_BASELINES["readability_level"]

                        # Calcualte an estimated reading time
                        reading_time = estimated_reading_time(generated_email)
                        reading_time_baseline = CUSTOM_METRIC_BASELINES["reading_time"]

                        # Calculate polarity and sentiment
                        sentiment, reaction = get_sentiment(generated_email)
                        sentiment_baseline = CUSTOM_METRIC_BASELINES["sentiment"]

                        # Calcualte a confidence score
                        confidence = get_cosine_similarity(prompt, generated_email)
                        confidence_baseline = CUSTOM_METRIC_BASELINES["confidence"]

                        st.write("\n\n")
                        st.subheader("**Monitoring Metrics:** \n")
                        st.markdown("---")

                        # Add guard metrics
                        m1, _, m2, _, m3, _, m4 = st.columns([3, 1, 4, 1, 3, 1, 3])
                        m1.metric(
                            label="📖 Readability",
                            value=f"{readability}",
                            delta=f"{round((score-score_baseline)/score_baseline*100,0)}%",
                            delta_color="normal",
                        )
                        m2.metric(
                            label="⏱️ Reading Time",
                            value=f"{reading_time} seconds",
                            delta=f"{reading_time-reading_time_baseline} seconds",
                            delta_color="inverse",
                        )
                        m3.metric(
                            label="✍ Sentiment",
                            value=f"{reaction}",
                            delta=f"{round(sentiment-sentiment_baseline,2)}",
                            delta_color="normal",
                        )
                        m4.metric(
                            label="✅ Confidence",
                            value=f"{confidence :.1%}",
                            delta=f"{round((confidence-confidence_baseline)*100)}%",
                            delta_color="normal",
                        )

                        input_cost = st.session_state.model["input_price_per_1k_tokens"]
                        output_cost = st.session_state.model[
                            "output_price_per_1k_tokens"
                        ]

                        # Count prompt tokens
                        num_prompt_tokens = get_num_tokens_from_string(
                            prompt, "cl100k_base"
                        )

                        # Count response tokens
                        num_response_tokens = get_num_tokens_from_string(
                            generated_email, "cl100k_base"
                        )

                        total_cost = (num_prompt_tokens / 1000 * input_cost) + (
                            num_response_tokens / 1000 * output_cost
                        )

                        st.markdown("---")

                        # Compile response dictionary
                        response = {
                            "prompt_token_count": num_prompt_tokens,
                            "response_token_count": num_response_tokens,
                            "llm_cost": total_cost,
                            "readability_level": score,
                            "reading_time": reading_time,
                            "sentiment": sentiment,
                            "confidence": confidence,
                        }
                        # Calculate metrics
                        metric_values = calculate_metrics(CUSTOM_METRIC_IDS, response)

                        # Report back to deployment
                        if submitted:
                            submit_metrics(
                                st.session_state["DATAROBOT_CLIENT"],
                                get_param("llm_deployment_id"),
                                metric_values,
                                CUSTOM_METRIC_IDS,
                                request_id=st.session_state.unique_uuid,
                            )

    with multiple_emails:
        csv = st.file_uploader(
            "Upload a csv:",
            type=["csv"],
            accept_multiple_files=False,
            label_visibility="visible",
        )

        st.empty()
        st.write("\n\n")
        run_button, download_button = st.columns([1, 1])
        run = run_button.button("Generate Emails")
        if run and csv is not None:
            st.write("\n\n")
            st.session_state.bulk_generated = True
            scoring_data = pd.read_csv(csv)
            count = len(scoring_data)
            record_id = RECORD_IDENTIFIER["column_name"]
            status_bar = st.empty()

            with st.spinner(f"Analyzing {count} records..."):
                predictions = make_datarobot_deployment_predictions(
                    get_param("deployment_id"),
                    data=scoring_data.to_csv(index=False),
                    max_explanations=st.session_state.numberOfExplanations,
                )
                status_bar.success("Predictions have been made! Generating emails...")

            st.session_state.bulk_prediction_results = predictions

            with st.spinner(f"Generating emails for {count} records..."):
                emails = batch_email_responses(
                    record_ids=scoring_data[record_id].to_list(),
                    predictions=predictions["data"],
                    number_of_explanations=st.session_state.numberOfExplanations,
                    temperature=st.session_state.temperature,
                    tone=st.session_state.tone,
                    verbosity=st.session_state.verbosity,
                    model=st.session_state.model["name"],
                )

            st.session_state.bulk_prediction_results = emails.to_csv(index=False)
            status_bar.success(
                f"Finished! All {count} emails have been drafted and results have been saved."
            )
        elif run:
            status_bar.error("Please upload a csv file to generate emails.")

        download = download_button.download_button(
            "Download Results",
            data=st.session_state.bulk_prediction_results,
            file_name="emails.csv",
            disabled=not st.session_state.bulk_generated,
        )

        if download:
            st.success("Your download should start automatically.")

    with outcome_information:
        st.empty()
        st.write("**Below find more detailed background about possible outcomes:**")
        for plan in get_param("outcome_details"):
            with st.expander(plan["label"]):
                st.write(plan["description"])


if __name__ == "__main__":
    main()
