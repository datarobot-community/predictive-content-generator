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

import json
import subprocess
from typing import Any, Dict, Mapping, Tuple, Type, Union

from pydantic import AliasChoices, Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pydantic_settings.sources import parse_env_vars

from nbo.schema import AppDataScienceSettings


class PulumiSettingsSource(EnvSettingsSource):
    """Pulumi stack outputs as a pydantic settings source."""

    _PULUMI_OUTPUTS: Dict[str, str] = {}
    _PULUMI_CALLED: bool = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.read_pulumi_outputs()
        super().__init__(*args, **kwargs)

    def read_pulumi_outputs(self) -> None:
        try:
            raw_outputs = json.loads(
                subprocess.check_output(
                    ["pulumi", "stack", "output", "-j"],
                    text=True,
                ).strip()
            )
            self._PULUMI_OUTPUTS = {
                k: v if isinstance(v, str) else json.dumps(v)
                for k, v in raw_outputs.items()
            }
        except BaseException:
            self._PULUMI_OUTPUTS = {}

    def _load_env_vars(self) -> Mapping[str, Union[str, None]]:
        return parse_env_vars(
            self._PULUMI_OUTPUTS,
            self.case_sensitive,
            self.env_ignore_empty,
            self.env_parse_none_str,
        )


class DynamicSettings(BaseSettings):
    """Settings that come from pulumi stack outputs or DR runtime parameters"""

    model_config = SettingsConfigDict(extra="ignore", populate_by_name=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            PulumiSettingsSource(settings_cls),
            env_settings,
        )


generative_deployment_env_name: str = "GENERATIVE_DEPLOYMENT_ID"


class GenerativeDeployment(DynamicSettings):
    id: str = Field(
        validation_alias=AliasChoices(
            "MLOPS_RUNTIME_PARAM_" + generative_deployment_env_name,
            generative_deployment_env_name,
        )
    )


pred_ai_deployment_env_name: str = "PRED_AI_DEPLOYMENT_ID"


class PredAIDeployment(DynamicSettings):
    id: str = Field(
        validation_alias=AliasChoices(
            "MLOPS_RUNTIME_PARAM_" + pred_ai_deployment_env_name,
            pred_ai_deployment_env_name,
        )
    )


app_settings_env_name: str = "NBO_APP_SETTINGS"


class AppEnvSettings(DynamicSettings):
    settings: AppDataScienceSettings = Field(
        validation_alias=AliasChoices(
            "MLOPS_RUNTIME_PARAM_" + app_settings_env_name,
            app_settings_env_name,
        )
    )


custom_metric_id_env_name: str = "CUSTOM_METRIC_IDS"


class CustomMetricIds(DynamicSettings):
    custom_metric_ids: dict[str, str] = Field(
        validation_alias=AliasChoices(
            "MLOPS_RUNTIME_PARAM_" + custom_metric_id_env_name,
            custom_metric_id_env_name,
        )
    )


dataset_id_env_name: str = "DATASET_ID"


class DatasetId(DynamicSettings):
    id: str = Field(
        validation_alias=AliasChoices(
            "MLOPS_RUNTIME_PARAM_" + dataset_id_env_name,
            dataset_id_env_name,
        )
    )


app_env_name: str = "DATAROBOT_APPLICATION_ID"
