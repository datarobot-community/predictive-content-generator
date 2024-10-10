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

import glob
import pathlib
import re
import shutil


def remove_dev_snippet(file: pathlib.Path):
    with open(file, "r") as f:
        content = f.read()

    p = r"# <=== Begin dev snippet ===>.*# <=== End dev snippet ===>"
    content = re.sub(p, "", content, flags=re.DOTALL)

    with open(file, "w") as f:
        f.write(content)


# copy files and templatize key directories
shutil.copytree(
    "recipe-bob",
    "{{ cookiecutter.repo_name }}",
    ignore=shutil.ignore_patterns("pyproject.toml", "datarobotx", "data"),
    dirs_exist_ok=True,
)
shutil.move(
    "{{ cookiecutter.repo_name }}/src/recipe_bob",
    "{{ cookiecutter.repo_name }}/src/{{ cookiecutter.python_package }}",
)

# templatize conf files
for filename in glob.iglob("{{ cookiecutter.repo_name }}/conf/**/**", recursive=True):
    file = pathlib.Path(filename)
    if file.is_file():
        contents = file.read_text()
        file.write_text(
            file.read_text()
            .replace("${globals:project_name}", "{{ cookiecutter.project_name }}")
            .replace("recipe_bob", "{{ cookiecutter.python_package }}")
        )


shutil.copyfile("README.md", "{{ cookiecutter.repo_name }}/README.md")
shutil.copyfile("LICENSE.txt", "{{ cookiecutter.repo_name }}/LICENSE.txt")

shutil.move(
    "{{ cookiecutter.repo_name }}/conf/local/example-credentials.yml",
    "{{ cookiecutter.repo_name }}/conf/local/credentials.yml",
)

package_path = pathlib.Path(
    "{{ cookiecutter.repo_name }}/src/{{ cookiecutter.python_package }}"
)
remove_dev_snippet(package_path / "settings.py")
