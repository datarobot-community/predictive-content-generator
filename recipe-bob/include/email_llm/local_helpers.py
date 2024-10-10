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


def get_kedro_catalog(kedro_project_root: str):
    """Initialize a kedro data catalog (as a singleton)."""

    try:
        import pathlib
        from kedro.framework.session import KedroSession
        from kedro.framework.startup import bootstrap_project
    except ImportError as e:
        raise ImportError(
            "Please ensure you've installed `kedro` and `kedro_datasets` to run this app locally"
        ) from e

    project_path = pathlib.Path(kedro_project_root).resolve()
    bootstrap_project(project_path)
    session = KedroSession.create(project_path)
    context = session.load_context()
    return context.catalog
