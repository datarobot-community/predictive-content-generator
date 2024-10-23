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

# mypy: ignore-errors

import datetime as dt
import logging
import uuid

import pytest

from nbo.resources import GenerativeDeployment
from nbo.schema import LLMRequest

logger = logging.getLogger(__name__)


@pytest.fixture
def generative_deployment_id():
    return GenerativeDeployment().id


def generate_association_id():
    return f"{uuid.uuid4().hex}_{dt.datetime.now()}"


def test_rag_deployment_prediction(
    pulumi_up, make_prediction, generative_deployment_id
):
    from nbo.credentials import AzureOpenAICredentials
    from nbo.predict import make_generative_deployment_predictions

    credentials = AzureOpenAICredentials()

    llm_input = LLMRequest(
        prompt="Write a short email to customer Rob",
        system_prompt="You are a helpful assistant.",
        association_id=generate_association_id(),
        model=credentials.azure_deployment,
        temperature=0,
        number_of_explanations=1,
        tone="Happy",
        verbosity="brief",
    )

    response = make_generative_deployment_predictions([llm_input])
    assert len(response[0].content) > 0 and "Rob" in response[0].content
