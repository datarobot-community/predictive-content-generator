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
from typing import Any, List, Optional

from openai import BaseModel
from pydantic import Field


class CVMethod(str, Enum):
    RandomCV = "RandomCV"
    StratifiedCV = "StratifiedCV"


class Metric(str, Enum):
    Accuracy = "Accuracy"
    AUC = "AUC"
    BalancedAccuracy = "Balanced Accuracy"
    FVEBinomial = "FVE Binomial"
    GiniNorm = "Gini Norm"
    KolmogorovSmirnov = "Kolmogorov-Smirnov"
    LogLoss = "LogLoss"
    RateAtTop5 = "Rate@Top5%"
    RateAtTop10 = "Rate@Top10%"
    TPR = "TPR"
    FPR = "FPR"
    TNR = "TNR"
    PPV = "PPV"
    NPV = "NPV"
    F1 = "F1"
    MCC = "MCC"
    FVEGamma = "FVE Gamma"
    FVEPoisson = "FVE Poisson"
    FVETweedie = "FVE Tweedie"
    GammaDeviance = "Gamma Deviance"
    MAE = "MAE"
    MAPE = "MAPE"
    PoissonDeviance = "Poisson Deviance"
    RSquared = "R Squared"
    RMSE = "RMSE"
    RMSLE = "RMSLE"
    TweedieDeviance = "Tweedie Deviance"


class ValidationType(str, Enum):
    CV = "CV"
    TVH = "TVH"


# Enumerated Values¶
# Property 	Value
# type 	[schedule, data_drift_decline, accuracy_decline, None]
class TriggerType(str, Enum):
    schedule = "schedule"
    data_drift_decline = "data_drift_decline"
    accuracy_decline = "accuracy_decline"
    trigger_none = "None"


class Action(str, Enum):
    CreateChallenger = "create_challenger"
    CreateModelPackage = "create_model_package"
    ModelReplacement = "model_replacement"


class FeatureListStrategy(str, Enum):
    InformativeFeatures = "informative_features"
    SameAsChampion = "same_as_champion"


class ModelSelectionStrategy(str, Enum):
    AutopilotRecommended = "autopilot_recommended"
    SameBlueprint = "same_blueprint"
    SameHyperparameters = "same_hyperparameters"


class ProjectOptionsStrategy(str, Enum):
    SameAsChampion = "same_as_champion"
    OverrideChampion = "override_champion"
    Custom = "custom"


class AutopilotMode(str, Enum):
    auto = "auto"
    quick = "quick"
    comprehensive = "comprehensive"


class AutopilotOptions(BaseModel):
    blendBestModels: bool = True
    mode: AutopilotMode = AutopilotMode.quick
    runLeakageRemovedFeatureList: bool = True
    scoringCodeOnly: bool = False
    shapOnlyMode: bool = False


class Periodicity(BaseModel):
    timeSteps: int = 0
    timeUnit: str = "MILLISECOND"


class Schedule(BaseModel):
    dayOfMonth: List[Any] = ["*"]
    dayOfWeek: List[Any] = ["*"]
    hour: List[Any] = ["*"]
    minute: List[Any] = ["*"]
    month: List[Any] = ["*"]


class Trigger(BaseModel):
    minIntervalBetweenRuns: Optional[str] = None
    schedule: Schedule = Field(default_factory=Schedule)
    statusDeclinesToFailing: bool = True
    statusDeclinesToWarning: bool = True
    statusStillInDecline: Optional[bool] = True
    type: TriggerType = TriggerType.schedule


class ProjectOptions(BaseModel):
    cvMethod: CVMethod = CVMethod.RandomCV
    holdoutPct: Optional[float] = None
    metric: Metric = Metric.Accuracy
    reps: Optional[int] = None
    validationPct: Optional[float] = None
    validationType: ValidationType = ValidationType.CV


class TimeSeriesOptions(BaseModel):
    calendarId: Optional[str] = None
    differencingMethod: str = "auto"
    exponentiallyWeightedMovingAlpha: Optional[int] = None
    periodicities: Optional[List[Periodicity]] = None
    treatAsExponential: Optional[str] = "auto"


class RetrainingPolicyCreate(BaseModel):
    action: Optional[Action] = Field(default_factory=lambda: Action.CreateChallenger)
    autopilotOptions: Optional[AutopilotOptions] = Field(
        default_factory=AutopilotOptions
    )
    description: str = Field(..., max_length=10000)
    featureListStrategy: Optional[FeatureListStrategy] = Field(
        default_factory=lambda: FeatureListStrategy.InformativeFeatures
    )
    modelSelectionStrategy: Optional[ModelSelectionStrategy] = Field(
        default_factory=lambda: ModelSelectionStrategy.AutopilotRecommended
    )
    name: str = Field(..., max_length=512)
    projectOptions: Optional[ProjectOptions] = Field(default_factory=ProjectOptions)
    projectOptionsStrategy: Optional[ProjectOptionsStrategy] = Field(
        default_factory=lambda: ProjectOptionsStrategy.SameAsChampion
    )
    timeSeriesOptions: Optional[TimeSeriesOptions] = None
    trigger: Optional[Trigger] = Field(default_factory=Trigger)
