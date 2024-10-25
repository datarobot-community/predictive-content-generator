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
import subprocess

import pulumi


def get_stack() -> str:
    """Retrieve the active pulumi stack

    Attempt to retrieve from the pulumi runtime
    If no stack selected, attempt to infer from an env var

    Allows subprocesses w/o access to the pulumi runtime to see the active stack even
    if `pulumi up -s` syntax is used with no selected stack.
    """
    try:
        stack = pulumi.get_stack()
        if stack != "stack":
            os.environ["PULUMI_STACK_CONTEXT"] = stack
            return stack
    except Exception:
        pass
    try:
        return os.environ["PULUMI_STACK_CONTEXT"]
    except KeyError:
        pass
    try:
        return subprocess.check_output(
            ["pulumi", "stack", "--show-name", "--non-interactive"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError:
        pass
    raise ValueError(
        (
            "Unable to retrieve the currently active stack. "
            "Verify you have selected created and selected a stack with `pulumi stack`."
        )
    )
