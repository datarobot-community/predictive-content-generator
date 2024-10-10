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

from typing import Any, Dict


def get_update_or_create_custom_metrics(
    endpoint: str, token: str, deployment_id: str, custom_metrics: Dict[str, Any]
) -> Dict[str, str]:
    """Get, update or create requested custom metrics on a DR deployment.

    Parameters
    ----------
    deployment_id : str
        DataRobot id for the deployment which will hold the metrics
    custom_metrics : dict of dict
        Dictionary of custom metric specifications aligned to the
        POST deployments/{deployment_id}/customMetrics/ route. Each key in the
        dictionary should be associated with a single custom metric specification.

    Returns
    -------
    dict of str
        Dictionary of resulting custom metric ids aligned to the keys in the provided
        custom_metrics dictionary.
    """
    from datarobotx.idp.custom_metrics import get_update_or_create_custom_metric

    custom_metric_ids = {}
    for metric in custom_metrics:
        custom_metric_ids[metric] = get_update_or_create_custom_metric(
            endpoint=endpoint,
            token=token,
            deployment_id=deployment_id,
            **custom_metrics[metric],
        )
    return custom_metric_ids


def ensure_deployment_settings(
    endpoint: str, token: str, deployment_id: str, association_id_column_name: str
) -> None:
    """Ensure deployment settings are properly configured.

    Turns on data collection, drift tracking, etc.

    Parameters
    ----------
    deployment_id : str
        DataRobot id of the LLM deployment
    association_id : str
        The name of the column to use as the association id
    """

    import datarobot as dr

    dr.Client(endpoint=endpoint, token=token)
    rag_deployment = dr.Deployment.get(deployment_id)

    rag_deployment.update_predictions_data_collection_settings(enabled=True)
    rag_deployment.update_association_id_settings(
        column_names=[association_id_column_name], required_in_prediction_requests=True
    )
