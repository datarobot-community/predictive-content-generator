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

import contextlib
import importlib
import logging
import os
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any

import datarobot as dr
import pytest
from datarobot.models.deployment.custom_metrics import CustomMetric
from pytest_mock import MockerFixture
from streamlit.testing.v1 import AppTest

from nbo.resources import CustomMetricIds, GenerativeDeployment

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def cd(new_dir: Path) -> Any:
    """Changes the current working directory to the given path and restores the old directory on exit."""
    prev_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prev_dir)


@pytest.fixture
def output_path() -> Any:
    output_dir = Path("../tests/output")
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
    # shutil.rmtree(output_dir)


@pytest.fixture
def application(pulumi_up: Any) -> Any:
    import nbo.predict
    import nbo.resources

    with cd(Path("frontend")):
        sys.path.append(".")
        importlib.reload(nbo.predict)
        importlib.reload(nbo.resources)
        yield AppTest.from_file("app.py", default_timeout=60)


@pytest.fixture
def app_prompt() -> str:
    return "Tell me about DataRobot"


@pytest.fixture
def app_post_prompt(application: AppTest, app_prompt: str, pulumi_up: Any) -> AppTest:
    logger.info(os.getcwd())
    at = application.run()
    at.button(key="FormSubmitter:customer_selection-Submit").click().run(timeout=120)
    return at


def test_generated_email(app_post_prompt: AppTest) -> None:
    email_content = app_post_prompt.text_area(key="generated_email").value
    logger.info(email_content)
    assert len(str(email_content)) > 0

    select = app_post_prompt.selectbox(key="selectbox-tone").select_index(2)
    logger.info(f"Selected: {select.value}")
    app_post_prompt.button(key="FormSubmitter:settings_selection-Apply").click().run(
        timeout=120
    )
    email_content_new = app_post_prompt.text_area(key="generated_email").value
    logger.info(email_content_new)
    assert email_content != email_content_new


def test_submit_feedback(app_post_prompt: AppTest) -> None:
    test_app = app_post_prompt
    now = datetime.now()

    user_feedback_custom_metric_id = CustomMetricIds().custom_metric_ids[
        "user_feedback"
    ]
    generative_deployment_id = GenerativeDeployment().id

    custom_metric = CustomMetric.get(
        deployment_id=generative_deployment_id,
        custom_metric_id=user_feedback_custom_metric_id,
    )

    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    feedback_count_before_click = custom_metric.get_summary(
        start=yesterday, end=tomorrow
    ).metric["sample_count"]
    if feedback_count_before_click is None:
        feedback_count_before_click = 0
    test_app.button(key="button-thumbsup").click().run()

    feedback_count_after_click = custom_metric.get_summary(
        start=yesterday, end=tomorrow
    ).metric["sample_count"]

    assert feedback_count_before_click + 1 == feedback_count_after_click


def test_batch_email(
    application: AppTest, mocker: MockerFixture, output_path: Path
) -> None:
    from nbo.resources import DatasetId

    dataset_id = DatasetId().id

    test_app = application.run()
    tab_1 = test_app.tabs[1]
    logger.info(os.getcwd())

    test_data = dr.Dataset.get(dataset_id).get_as_dataframe()[:2]  # type: ignore[attr-defined]

    test_data.columns = [c.replace(".", "_") for c in test_data.columns]  # type: ignore[assignment]

    test_data.to_csv(output_path / "test_data_batch.csv", index=False)

    with open(output_path / "test_data_batch.csv", "rb") as f:
        mocker.patch("streamlit.file_uploader", return_value=BytesIO(f.read()))

    tab_1.button[0].click().run(timeout=120)

    tab_1 = test_app.tabs[1]

    assert tab_1.dataframe[0].value.shape[0] == 2
