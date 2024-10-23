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

from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ChunkSizeEnum(str, Enum):
    auto = "auto"
    fixed = "fixed"
    dynamic = "dynamic"


# class ChunkSizeFixed(int):
#     int = Field(..., ge=20, le=41943040)


class BatchPredictionJobRemapping(BaseModel):
    pass


class BatchPredictionJobCSVSettings(BaseModel):
    delimiter: str = ","
    encoding: str = "utf-8"
    quotechar: str = '"'


class AzureIntake(BaseModel):
    type: Literal["azure"]


class BigQueryIntake(BaseModel):
    type: Literal["bigQuery"]


class DataStageIntake(BaseModel):
    type: Literal["dataStage"]


class Catalog(BaseModel):
    type: Literal["dataset"]
    datasetId: str


class DSS(BaseModel):
    type: Literal["dss"]


class FileSystemIntake(BaseModel):
    type: Literal["fileSystem"]


class GCPIntake(BaseModel):
    type: Literal["gcp"]


class HTTPIntake(BaseModel):
    type: Literal["http"]


class JDBCIntake(BaseModel):
    catalog: Optional[str] = None
    credentialId: Optional[str] = None
    dataStoreId: str
    fetchSize: Optional[int] = Field(default=1, ge=1, le=1000000)
    query: Optional[str] = None
    db_schema: Optional[str] = Field(default=None, alias="schema")
    table: Optional[str] = None
    type: Literal["jdbc"]


class LocalFileIntake(BaseModel):
    type: Literal["localFile"]


class S3Intake(BaseModel):
    type: Literal["s3"]


class SnowflakeIntake(BaseModel):
    type: Literal["snowflake"]


class SynapseIntake(BaseModel):
    type: Literal["synapse"]


class AzureOutput(BaseModel):
    type: Literal["azure"]
    credentialId: str
    url: str
    format: str = "csv"
    partitionColumns: List[str] = []


class BigQueryOutput(BaseModel):
    type: Literal["bigQuery"]


class FileSystemOutput(BaseModel):
    type: Literal["fileSystem"]


class GCPOutput(BaseModel):
    type: Literal["gcp"]


class HTTPOutput(BaseModel):
    type: Literal["http"]


class JDBCOutput(BaseModel):
    catalog: Optional[str] = None
    commitInterval: int = Field(default=600, ge=0, le=86400)
    createTableIfNotExists: bool = False
    credentialId: Optional[Union[str, None]] = None
    dataStoreId: str
    db_schema: Optional[str] = Field(default=None, alias="schema")
    statementType: str
    table: str
    type: Literal["jdbc"]
    updateColumns: Optional[List[str]] = Field(default_factory=list)
    whereColumns: Optional[List[str]] = Field(default_factory=list)


class LocalFileOutput(BaseModel):
    type: Literal["localFile"]


class S3Output(BaseModel):
    type: Literal["s3"]


class SnowflakeOutput(BaseModel):
    type: Literal["snowflake"]


class SynapseOutput(BaseModel):
    type: Literal["synapse"]


class Tableau(BaseModel):
    type: Literal["tableau"]


class BatchPredictionJobPredictionInstance(BaseModel):
    apiKey: str
    datarobotKey: str
    hostName: str
    sslEnabled: bool = True


class Schedule(BaseModel):
    dayOfMonth: List[Union[int, str]] = ["*"]
    dayOfWeek: List[Union[int, str]] = ["*"]
    hour: List[Union[int, str]] = ["*"]
    minute: List[Union[int, str]] = ["*"]
    month: List[Union[int, str]] = ["*"]


class BatchJobTimeSeriesSettingsForecast(BaseModel):
    type: Literal["forecast"]
    forecastPoint: str
    relaxKnownInAdvanceFeaturesCheck: bool = False


class BatchPredictionJobTimeSeriesSettingsForecastWithPolicy(BaseModel):
    type: Literal["forecastWithPolicy"]


class BatchJobTimeSeriesSettingsHistorical(BaseModel):
    type: Literal["historical"]


class BatchPredictionJobDefinitionsCreate(BaseModel):
    abortOnError: bool = True
    chunkSize: Union[ChunkSizeEnum, int] = Field(default=ChunkSizeEnum.auto)
    columnNamesRemapping: List[BatchPredictionJobRemapping] = Field(
        default_factory=list
    )
    csvSettings: BatchPredictionJobCSVSettings = Field(
        default_factory=BatchPredictionJobCSVSettings
    )
    deploymentId: str
    disableRowLevelErrorHandling: bool = False
    enabled: bool = True
    explanationAlgorithm: Optional[str] = None
    explanationClassNames: Optional[List[str]] = None
    explanationNumTopClasses: Optional[int] = Field(default=None, ge=1, le=10)
    includePredictionStatus: bool = False
    includeProbabilities: bool = True
    includeProbabilitiesClasses: List[str] = []
    intake_settings: Union[
        AzureIntake,
        BigQueryIntake,
        DataStageIntake,
        Catalog,
        DSS,
        FileSystemIntake,
        GCPIntake,
        HTTPIntake,
        JDBCIntake,
        LocalFileIntake,
        S3Intake,
        SnowflakeIntake,
        SynapseIntake,
    ] = Field(..., discriminator="type")
    maxExplanations: int = Field(default=0, ge=0, le=100)
    modelId: Optional[str] = None
    modelPackageId: Optional[str] = None
    monitoringBatchPrefix: Optional[str] = None
    num_concurrent: int = Field(default=1, ge=1)
    output_settings: Union[
        AzureOutput,
        BigQueryOutput,
        FileSystemOutput,
        GCPOutput,
        HTTPOutput,
        JDBCOutput,
        LocalFileOutput,
        S3Output,
        SnowflakeOutput,
        SynapseOutput,
        Tableau,
    ] = Field(discriminator="type")
    passthroughColumns: Optional[List[str]] = None
    passthroughColumnsSet: str = "all"
    pinnedModelId: Optional[str] = None
    predictionInstance: Optional[BatchPredictionJobPredictionInstance] = None
    predictionThreshold: Optional[float] = Field(default=None, ge=0, le=1)
    predictionWarningEnabled: Optional[bool] = None
    skipDriftTracking: bool = False
    thresholdHigh: Optional[float] = None
    thresholdLow: Optional[float] = None
    timeseriesSettings: Optional[
        Optional[
            Union[
                BatchJobTimeSeriesSettingsForecast,
                BatchPredictionJobTimeSeriesSettingsForecastWithPolicy,
                BatchJobTimeSeriesSettingsHistorical,
            ]
        ]
    ] = None
