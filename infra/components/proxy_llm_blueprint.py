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

from typing import Any, Optional

import pulumi
import pulumi_datarobot as datarobot

from infra.common.schema import LLMSettings, VectorDatabaseSettings


class ProxyLLMBlueprint(pulumi.ComponentResource):
    def __init__(
        self,
        resource_name: str,
        proxy_llm_deployment_id: pulumi.Output[str],
        use_case_id: pulumi.Output[str],
        playground_id: pulumi.Output[str],
        llm_id: str,
        llm_settings: LLMSettings,
        vector_database_settings: VectorDatabaseSettings | None = None,
        vector_database_id: pulumi.Output[str] | None = None,
        opts: Optional[pulumi.ResourceOptions] = None,
        chat_model_name: str | pulumi.Output[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            "custom:datarobot:ProxyLLMBlueprint", resource_name, None, opts
        )
        self.llm_validation = datarobot.CustomModelLlmValidation(
            resource_name=f"{resource_name}-validation",
            chat_model_id=chat_model_name,
            deployment_id=proxy_llm_deployment_id,
            use_case_id=use_case_id,
            opts=pulumi.ResourceOptions(replace_on_changes=["*"], parent=self),
        )
        if isinstance(llm_settings, dict):
            llm_settings = LLMSettings(**llm_settings)
        if isinstance(vector_database_settings, dict):
            vector_database_settings = VectorDatabaseSettings(
                **vector_database_settings
            )
        self.llm_blueprint = datarobot.LlmBlueprint(
            resource_name=resource_name,
            custom_model_llm_settings=datarobot.LlmBlueprintCustomModelLlmSettingsArgs(
                system_prompt=llm_settings.system_prompt,
                validation_id=self.llm_validation.id,
            ),
            llm_id=llm_id,
            playground_id=playground_id,
            vector_database_id=vector_database_id,
            vector_database_settings=vector_database_settings.model_dump()
            if vector_database_settings is not None
            else None,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "llm_validation_id": self.llm_validation.id,
                "id": self.llm_blueprint.id,
            }
        )

    @property
    @pulumi.getter(name="id")
    def id(self) -> pulumi.Output[str]:
        """
        The ID of the latest Custom Model version.
        """
        return self.llm_blueprint.id
