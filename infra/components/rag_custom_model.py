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

from typing import List, Optional

import pulumi
import pulumi_datarobot as datarobot

from ..common.schema import (
    CustomModelArgs,
    DatasetArgs,
    LLMBlueprintArgs,
    PlaygroundArgs,
    VectorDatabaseArgs,
)


class RAGCustomModel(pulumi.ComponentResource):
    def __init__(
        self,
        resource_name: str,
        use_case: datarobot.UseCase,
        dataset_args: DatasetArgs,
        playground_args: PlaygroundArgs,
        vector_database_args: VectorDatabaseArgs,
        llm_blueprint_args: LLMBlueprintArgs,
        runtime_parameter_values: List[datarobot.CustomModelRuntimeParameterValueArgs],
        guard_configurations: List[datarobot.CustomModelGuardConfigurationArgs],
        custom_model_args: CustomModelArgs,
        opts: Optional[pulumi.ResourceOptions] = None,
    ):
        super().__init__("custom:datarobot:RAGCustomModel", resource_name, None, opts)

        self.playground = datarobot.Playground(
            use_case_id=use_case.id,
            **playground_args.model_dump(mode="json"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.vdb_dataset = datarobot.DatasetFromFile(
            use_case_ids=[use_case.id],
            **dataset_args.model_dump(mode="json"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.vector_database = datarobot.VectorDatabase(
            dataset_id=self.vdb_dataset.id,
            use_case_id=use_case.id,
            **vector_database_args.model_dump(mode="json"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.llm_blueprint = datarobot.LlmBlueprint(
            playground_id=self.playground.id,
            vector_database_id=self.vector_database.id,
            **llm_blueprint_args.model_dump(mode="json"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.custom_model = datarobot.CustomModel(
            source_llm_blueprint_id=self.llm_blueprint.id,
            runtime_parameter_values=runtime_parameter_values,
            guard_configurations=guard_configurations,
            **custom_model_args.model_dump(mode="json", exclude_none=True),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "playground_id": self.playground.id,
                "dataset_id": self.vdb_dataset.id,
                "vector_database_id": self.vector_database.id,
                "llm_blueprint_id": self.llm_blueprint.id,
                "id": self.custom_model.id,
                "version_id": self.custom_model.version_id,
            }
        )

    @property
    @pulumi.getter(name="versionId")
    def version_id(self) -> pulumi.Output[str]:
        """
        The ID of the latest Custom Model version.
        """
        return self.custom_model.version_id
