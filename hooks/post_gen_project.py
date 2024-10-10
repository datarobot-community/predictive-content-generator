# Copyright 2024 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import os
from pathlib import Path
import shutil
import stat
import subprocess


def remove_readonly(func, path, excinfo):
    """Handle windows permission error.

    https://stackoverflow.com/questions/1889597/deleting-read-only-directory-in-python/1889686#1889686
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def move_contents(src: Path, dst: Path):
    """Move the contents to destination and remove the source directory."""
    # Move the contents of the source directory to the destination directory
    for item in os.listdir(src):
        s = src / item
        d = dst / item
        shutil.move(s, d)

    # Remove the empty source directory
    os.rmdir(src)


DATAROBOTX_IDP_VERSION = "{{ cookiecutter.datarobotx_idp_version }}"

print("Copying latest datarobotx-idp source into project..\n")
subprocess.run(
    [
        "git",
        "clone",
        "--branch",
        DATAROBOTX_IDP_VERSION,
        "https://github.com/datarobot-community/datarobotx-idp.git",
    ],
    check=True,
)
shutil.copytree("datarobotx-idp/src/datarobotx", "src/datarobotx")
shutil.rmtree("datarobotx-idp")

conf_folder = Path("conf/base/")
include_folder = Path("include/")
use_case_type_enum = "{{ cookiecutter.use_case_type_enum }}"

(conf_folder / "globals.yml").unlink(missing_ok=True)
(conf_folder / "example-globals.yml").unlink(missing_ok=True)

if use_case_type_enum == "1":  # NBO
    move_contents(conf_folder / "nbo", conf_folder)
    shutil.rmtree(conf_folder / "fraud_monitoring", onerror=remove_readonly)
    shutil.rmtree(conf_folder / "underwriting", onerror=remove_readonly)
    os.remove(include_folder / "autopilot/fraud_monitoring_training.csv")
    os.remove(include_folder / "autopilot/underwriting_training.csv")

elif use_case_type_enum == "2":  # Underwriting
    move_contents(conf_folder / "underwriting", conf_folder)
    shutil.rmtree(conf_folder / "fraud_monitoring", onerror=remove_readonly)
    shutil.rmtree(conf_folder / "nbo", onerror=remove_readonly)
    os.remove(include_folder / "autopilot/fraud_monitoring_training.csv")
    os.remove(include_folder / "autopilot/nbo_training.csv")

elif use_case_type_enum == "3":  # Fraud Monitoring
    move_contents(conf_folder / "fraud_monitoring", conf_folder)
    shutil.rmtree(conf_folder / "nbo", onerror=remove_readonly)
    shutil.rmtree(conf_folder / "underwriting", onerror=remove_readonly)
    os.remove(include_folder / "autopilot/nbo_training.csv")
    os.remove(include_folder / "autopilot/underwriting_training.csv")
else:
    raise ValueError("Invalid use case type")


# Handle case when kedro new happens in a DataRobot codespace
if "DATAROBOT_DEFAULT_USE_CASE" in os.environ:
    import datarobot as dr
    import yaml

    parameters_yaml = Path("conf/base/parameters_automl_classifier.yml")
    use_case = dr.UseCase.get(os.environ["DATAROBOT_DEFAULT_USE_CASE"])

    with open(parameters_yaml, "r") as file:
        parameters = yaml.safe_load(file)
        parameters["automl_classifier"]["use_case"]["name"] = use_case.name
        parameters["automl_classifier"]["use_case"][
            "description"
        ] = use_case.description
    with open(parameters_yaml, "w") as file:
        yaml.dump(parameters, file)
