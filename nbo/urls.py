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

import os
from urllib.parse import urlsplit


def get_deployment_url(deployment_id: str) -> str:
    """Translate deployment ID to GUI URL.

    Parameters
    ----------
    deployment_id : str
        DataRobot deployment id.
    endpoint: str
        DataRobot public API endpoint e.g. envir
    """
    parsed_dr_url = urlsplit(os.environ["DATAROBOT_ENDPOINT"])
    return f"{parsed_dr_url.scheme}://{parsed_dr_url.netloc}/console-nextgen/deployments/{deployment_id}/"


def get_project_url(project_id: str) -> str:
    """Translate project ID to GUI URL.

    Parameters
    ----------
    project_id : str
        DataRobot project id.
    endpoint: str
        DataRobot public API endpoint e.g. envir
    """
    parsed_dr_url = urlsplit(os.environ["DATAROBOT_ENDPOINT"])
    return (
        f"{parsed_dr_url.scheme}://{parsed_dr_url.netloc}/projects/{project_id}/models"
    )
