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
from pathlib import Path

from datarobot_pulumi_utils.pulumi.stack import get_stack
from datarobot_pulumi_utils.schema.exec_envs import RuntimeEnvironments

project_name = get_stack()

runtime_environment_moderations = RuntimeEnvironments.PYTHON_312_MODERATIONS.value

default_prediction_server_id = os.getenv("DATAROBOT_PREDICTION_ENVIRONMENT_ID", None)
prediction_environment_resource_name = (
    f"Predictive Content Generator Prediction Environment [{project_name}]"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.absolute()

model_training_nb = PROJECT_ROOT / "notebooks" / "train_model_nbo.ipynb"
model_training_output_ds_settings = (
    PROJECT_ROOT / "frontend" / f"app_settings.{project_name}.yaml"
)
model_training_output_infra_settings = (
    PROJECT_ROOT / "notebooks" / f"app_infra_settings.{project_name}.yaml"
)
