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

from pydantic import ValidationError

from nbo.credentials import AzureOpenAICredentials

from .common.schema import (
    CredentialArgs,
)
from .settings_main import project_name

try:
    credential = AzureOpenAICredentials()
    credential.test()
except ValidationError as e:
    raise ValueError(
        "Unable to load LLM credentials. "
        "Verify you have setup your environment variables as described in README.md."
    ) from e

credential_args = CredentialArgs(
    resource_name=f"Predictive Content Generator Credential [{project_name}]",
)
