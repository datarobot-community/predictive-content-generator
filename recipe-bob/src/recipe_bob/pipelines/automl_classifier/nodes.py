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


def ensure_deployment_settings(
    endpoint: str,
    token: str,
    deployment_id: str,
) -> None:
    """Ensure deployment settings are properly configured.

    Parameters
    ----------
    prediction_interval: int
        The prediction interval to set for the deployment

    """
    import datarobot as dr

    dr.Client(endpoint=endpoint, token=token)

    deployment = dr.Deployment.get(deployment_id)
    deployment.update_predictions_data_collection_settings(enabled=True)
    deployment.update_drift_tracking_settings(target_drift_enabled=True)


def get_or_create_registered_model_with_threshold(
    endpoint, token, project_id, model_id, registered_model_name, **kwargs
) -> None:
    import datarobot as dr
    from datarobotx.idp.registered_model_versions import (
        get_or_create_registered_leaderboard_model_version,
    )

    dr.Client(endpoint=endpoint, token=token)

    try:
        model = dr.Model.get(project_id, model_id)
        prediction_threshold = model.get_roc_curve(
            source="validation"
        ).get_best_f1_threshold()
    except Exception:
        prediction_threshold = None

    return get_or_create_registered_leaderboard_model_version(
        endpoint,
        token,
        model_id=model_id,
        registered_model_name=registered_model_name,
        prediction_threshold=prediction_threshold,
        **kwargs,
    )
