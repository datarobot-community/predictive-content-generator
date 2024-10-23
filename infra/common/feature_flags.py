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

import pathlib
from typing import Dict, Iterable, List, Tuple

import datarobot as dr
import pulumi
import yaml


def get_statuses(flags: Iterable[str]) -> Dict[str, bool]:
    client = dr.client.get_client()
    flags_json = {"entitlements": [{"name": flag} for flag in flags]}
    response = client.post("entitlements/evaluate/", json=flags_json)
    return {
        flag_status["name"]: flag_status["value"]
        for flag_status in response.json()["entitlements"]
    }


def get_corrections(
    desired: Dict[str, bool], status: Dict[str, bool]
) -> List[Tuple[str, bool]]:
    return [
        (flag, desired[flag]) for flag in status.keys() if desired[flag] != status[flag]
    ]


def eval_feature_flags(
    desired: Dict[str, bool],
) -> Tuple[List[Tuple[str, bool]], List[str]]:
    invalid: List[str] = []
    try:
        status = get_statuses(desired.keys())
        return get_corrections(desired, status), invalid
    except dr.errors.ClientError as e:
        if e.status_code == 422:
            for _, value in e.json["errors"].items():
                invalid.append(value)
            desired = {k: v for k, v in desired.items() if k not in invalid}
            status = get_statuses(desired.keys())
            return get_corrections(desired, status), invalid
        else:
            raise e


def check_feature_flags(
    yaml_path: pathlib.Path, raise_corrections: bool = True
) -> None:
    """Find incorrect, and invalid feature flags

    Returns a list of feature flag corrections the user needs to make and
    a list of invalid feature flags.
    """
    with open(yaml_path) as f:
        desired = yaml.safe_load(f)
        desired = {k: bool(v) for k, v in desired.items()}
    corrections, invalid = eval_feature_flags(desired)
    for flag in invalid:
        correct_value = desired[flag]
        pulumi.warn(
            f"Feature flag '{flag}' is required to be {correct_value} but is no longer a valid DataRobot feature flag."
        )
    for flag, correct_value in corrections:
        pulumi.error(
            f"This app template requires that feature flag '{flag}' is set "
            f"to {correct_value}. Contact your DataRobot representative for "
            "assistance."
        )
    if len(corrections) and raise_corrections:
        raise pulumi.RunError("Please correct feature flag settings and run again.")
