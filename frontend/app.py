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

import logging
import sys

import datarobot as dr
import pandas as pd
import streamlit as st
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
    app_settings,
    batch_email_responses,
    color_texts,
    custom_metric_ids,
    generative_deployment_id,
    get_llm_response,
    make_important_features_list,
    pred_ai_deployment_id,
    set_outcome_details,
)

sys.path.append("..")
from nbo.predict import make_pred_ai_deployment_predictions
from nbo.resources import DatasetId

logger = logging.getLogger(__name__)

st.set_page_config(
    layout="wide",
    page_title=app_settings.page_title,
    page_icon="./datarobot_favicon.png",
)

with open("./style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)


# Set environment vars
CUSTOM_METRIC_IDS = custom_metric_ids
CUSTOM_METRIC_BASELINES = app_settings.custom_metric_baselines
DATASET_ID = DatasetId().id


@st.cache_data(show_spinner=False)
def get_dataset() -> pd.DataFrame:
    dataset = dr.Dataset.get(DATASET_ID)  # type: ignore[attr-defined]
    df = dataset.get_as_dataframe()
    df[app_settings.record_identifier["column_name"]] = df[
        app_settings.record_identifier["column_name"]
    ].astype(str)
    return df


def main() -> None:
    # Initialize DataRobot client and objects

    if "outcome_details" not in st.session_state:
        st.session_state["outcome_details"] = set_outcome_details(
            app_settings.outcome_details
        )

    # Get the data
    df = get_dataset()

    # Initialize session states
    if "model" not in st.session_state:
        st.session_state.model = app_settings.models[0]
    if "temperature" not in st.session_state:
        st.session_state.temperature = app_settings.default_temperature
    if "numberOfExplanations" not in st.session_state:
        st.session_state.numberOfExplanations = (
            app_settings.default_number_of_explanations
        )
    if "tone" not in st.session_state:
        st.session_state.tone = app_settings.tones[0]
    if "verbosity" not in st.session_state:
        st.session_state.verbosity = app_settings.verbosity[0]
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
                [model.name for model in app_settings.models],
                index=0,
                help="Model controls the underlying LLM selection.",
            )

            temperature = st.number_input(
                "Select a temperature value:",
                min_value=0.0,
                max_value=2.0,
                value=app_settings.default_temperature,
                step=0.1,
                help=(
                    "The temperature argument in OpenAI's GPT determines the "
                    "randomness of the model's output."
                ),
            )
            # Number input for selecting the number of explanations
            number_of_explanations = int(
                st.number_input(
                    label="Select the number of explanations:",
                    min_value=0,
                    max_value=10,
                    value=app_settings.default_number_of_explanations,
                    step=1,
                    help=(
                        "The number of explanations argument controls how "
                        "many prediction explanations we pass to our prompt."
                    ),
                )
            )

            # Dropdown for tone selection
            tone = st.selectbox(
                "Select a tone:",
                app_settings.tones,
                index=0,
                help="Tone controls the attitude of the email.",
                key="selectbox-tone",
            )

            # Dropdown for verbosity selection
            verbosity = st.selectbox(
                "Select a verbosity:",
                app_settings.verbosity,
                index=0,
                help="Verbosity helps to determine the length and wordiness of the email.",
            )

            # Apply button for the form
            new_settings_run = st.form_submit_button("Apply", type="primary")

            # Update session state variables upon form submission
            if new_settings_run:
                st.session_state.model = [
                    m for m in app_settings.models if m.name == model
                ][0]
                st.session_state.temperature = temperature
                st.session_state.numberOfExplanations = number_of_explanations
                st.session_state.tone = tone
                st.session_state.verbosity = verbosity

        # Monitoring settings section
        st.markdown("**Monitoring Settings:** ")

        # Sidebar caption with hyperlink
        st.caption(
            f"See [here](https://app.datarobot.com/console-nextgen/deployments/{generative_deployment_id}/overview) to view and update tracking data"
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
            f"<h1 style='text-align: center;'>{app_settings.page_title}</h1>",
            unsafe_allow_html=True,
        )
        st.write(app_settings.page_subtitle)

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

        record_id = app_settings.record_identifier["column_name"]
        record_display_name = app_settings.record_identifier["display_name"]

        # Extract unique customer names from the dataframe
        customers_list: list[str] = df[record_id].unique().tolist()

        # Customer selection form and dropdown
        with customer_selection_container:
            with st.form(key="customer_selection"):
                (
                    col1,
                    _,
                ) = st.columns([2, 6])
                # First column: Dropdown to select a customer
                with col1:
                    selected_record: str = str(
                        st.selectbox(
                            f"Select a {record_display_name}:", customers_list, index=0
                        )
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
                    df.loc[df[record_id] == str(selected_record), :]
                    .reset_index(drop=True)
                    .copy()
                )

                # Make a prediction using DataRobot's deployment API
                predictions = make_pred_ai_deployment_predictions(
                    prediction_row,
                    max_explanations=number_of_explanations,  # Number of explanations you want (if applicable)
                )
                prediction = predictions[0]
                # Extract the predicted label and its probability
                predicted_label = prediction.predicted_label
                customer_prediction_label = f"**Predicted Label:** {st.session_state['outcome_details'][predicted_label].label}"
                customer_prediction_probability = f"**Predicted Probability:** {max([v for k, v in prediction.class_probabilities.items()]) :.1%}"
                # Store the prediction information in the session state
                st.session_state.predicted_label = customer_prediction_label
                st.session_state.predicted_probability = customer_prediction_probability

                # Clear spinner once predictions are made
                st.empty()

                # Container to hold the email draft section
                with prediction_response_container:
                    # Add a bit of space for better layout
                    st.write("\n\n")
                    deployment = dr.Deployment.get(pred_ai_deployment_id)  # type: ignore[attr-defined]
                    project_id = deployment.model.get("project_id")  # type: ignore[union-attr]

                    # Informational expander
                    prediction_info_expander = st.expander(
                        f"Drafted an email for {selected_record}! Expand the container to get more info or check the model out [here](https://app.datarobot.com/projects/{project_id}/models).",
                        expanded=False,
                    )

                    with prediction_info_expander:
                        # Filter to prediction explanations that have strength greater than 0
                        prediction_explanations = prediction.explanations
                        rsp, text_explanations = make_important_features_list(
                            prediction_explanations=prediction_explanations,
                        )

                        st.info(
                            f"\n\n{customer_prediction_label}\n\n{customer_prediction_probability}\n\n**List of Prediction Explanations:**\n\n{rsp}"
                        )

                with text_response_container:
                    if text_explanation := app_settings.text_explanation_feature:
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
                    if predicted_label == app_settings.no_text_gen_label:
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
                        logger.info(
                            f"Incorporating {st.session_state.numberOfExplanations} prediction explanations into the prompt"
                        )
                        # Generate the email content based on the prediction
                        generation = get_llm_response(
                            prediction,
                            selected_record=selected_record,
                            number_of_explanations=st.session_state.numberOfExplanations,
                            temperature=st.session_state.temperature,
                            tone=st.session_state.tone,
                            verbosity=st.session_state.verbosity,
                            model=st.session_state.model.name,
                        )
                        st.session_state.unique_uuid = generation.association_id

                        # Display the generated email
                        st.subheader("Newly Generated Email:")
                        generated_email = st.text_area(
                            label="Email",
                            value=generation.content,
                            height=450,
                            label_visibility="collapsed",
                            key="generated_email",
                        )

                    with post_email_container:
                        # Create multiple columns for different components
                        _, _, c2, c3 = st.columns([10, 10, 1, 1])

                        # Button for positive feedback in the second column
                        with c2:
                            thumbs_up = st.button("👍🏻", key="button-thumbsup")

                        # Button for negative feedback in the third column
                        with c3:
                            thumbs_down = st.button("👎🏻", key="button-thumbsdown")

                        # Capture feedback when either button is clicked
                        if thumbs_up or thumbs_down:
                            # Report back to deployment
                            feedback = (
                                1.0 if thumbs_up else 0.0 if thumbs_down else None
                            )
                            user_feedback_id = CUSTOM_METRIC_IDS["user_feedback"]
                            user_feedback_metric_values = {user_feedback_id: feedback}
                            submit_metrics(
                                metric_scores=user_feedback_metric_values,
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
                        confidence = get_cosine_similarity(
                            generation.prompt_used, generated_email
                        )
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

                        input_cost = st.session_state.model.input_price_per_1k_tokens
                        output_cost = st.session_state.model.output_price_per_1k_tokens

                        # Count prompt tokens
                        num_prompt_tokens = get_num_tokens_from_string(
                            generation.prompt_used, "cl100k_base"
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
                                metric_scores=metric_values,
                                request_id=st.session_state.unique_uuid,
                            )

    with multiple_emails:
        csv = st.file_uploader(
            "Upload a csv:",
            type=["csv"],
            accept_multiple_files=False,
            label_visibility="visible",
        )
        st.session_state.csv = csv
        st.empty()
        st.write("\n\n")
        run_button, download_button = st.columns([1, 1])
        run = run_button.button("Generate Emails")
        if run and csv is not None:
            st.write("\n\n")
            st.session_state.bulk_generated = True
            scoring_data = pd.read_csv(csv)
            count = len(scoring_data)
            record_id = app_settings.record_identifier["column_name"]
            status_bar = st.empty()

            with st.spinner(f"Analyzing {count} records..."):
                predictions = make_pred_ai_deployment_predictions(
                    df=scoring_data,
                    max_explanations=st.session_state.numberOfExplanations,
                )

                status_bar.success("Predictions have been made! Generating emails...")

            # st.session_state.bulk_prediction_results = predictions

            with st.spinner(f"Generating emails for {count} records..."):
                emails = batch_email_responses(
                    record_ids=scoring_data[record_id].to_list(),
                    predictions=predictions,
                    number_of_explanations=st.session_state.numberOfExplanations,
                    temperature=st.session_state.temperature,
                    tone=st.session_state.tone,
                    verbosity=st.session_state.verbosity,
                    model=st.session_state.model.name,
                )

            st.session_state.bulk_prediction_results = emails.to_csv(index=False)
            status_bar.success(
                f"Finished! All {count} emails have been drafted and results have been saved."
            )

            st.dataframe(emails)
        elif run:
            status_bar.error("Please upload a csv file to generate emails.")  # type: ignore

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
        for plan in app_settings.outcome_details:
            with st.expander(plan.label):
                st.write(plan.description)


if __name__ == "__main__":
    main()