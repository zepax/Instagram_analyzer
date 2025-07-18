"""
Evaluation metrics for machine learning models.

This module provides functions for calculating metrics for model evaluation,
such as accuracy, precision, recall, F1 score, etc.
"""

import logging
from typing import Any, Dict, List, Optional, Union

# Try to import scikit-learn for metrics
try:
    import numpy as np
    from sklearn import metrics as sklearn_metrics

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def calculate_metrics(
    predictions: Any,
    targets: Any,
    metrics: Optional[list[str]] = None,
    problem_type: str = "classification",
) -> dict[str, float]:
    """
    Calculate evaluation metrics for model predictions.

    Args:
        predictions: Model predictions
        targets: True target values
        metrics: List of metrics to calculate (None for default metrics)
        problem_type: Type of problem ('classification', 'regression', etc.)

    Returns:
        Dictionary of metric names and values
    """
    logger = logging.getLogger(__name__)

    if not HAS_SKLEARN:
        logger.warning(
            "scikit-learn not found. Metrics calculation will be limited. "
            "Install with 'pip install scikit-learn'."
        )

    # Default metrics based on problem type
    if metrics is None:
        if problem_type == "classification":
            metrics = ["accuracy", "precision", "recall", "f1"]
        elif problem_type == "regression":
            metrics = ["mse", "rmse", "mae", "r2"]
        else:
            metrics = ["accuracy"]

    # Convert inputs to numpy arrays if possible
    try:
        if not isinstance(predictions, np.ndarray):
            predictions = np.array(predictions)
        if not isinstance(targets, np.ndarray):
            targets = np.array(targets)
    except (TypeError, ValueError, AttributeError):
        logger.warning("Could not convert inputs to numpy arrays.")

    results = {}

    # Calculate metrics
    for metric in metrics:
        try:
            if HAS_SKLEARN:
                value = _calculate_sklearn_metric(
                    predictions, targets, metric, problem_type
                )
            else:
                value = _calculate_basic_metric(
                    predictions, targets, metric, problem_type
                )

            results[metric] = value
        except Exception as e:
            logger.error(f"Error calculating metric {metric}: {str(e)}")
            results[metric] = float("nan")

    return results


def _calculate_sklearn_metric(
    predictions: np.ndarray, targets: np.ndarray, metric: str, problem_type: str
) -> float:
    """
    Calculate a metric using scikit-learn.

    Args:
        predictions: Model predictions
        targets: True target values
        metric: Name of the metric to calculate
        problem_type: Type of problem

    Returns:
        Metric value
    """
    # Classification metrics
    if problem_type == "classification":
        if metric == "accuracy":
            return float(sklearn_metrics.accuracy_score(targets, predictions))
        elif metric == "precision":
            return float(
                sklearn_metrics.precision_score(
                    targets, predictions, average="macro", zero_division=0
                )
            )
        elif metric == "recall":
            return float(
                sklearn_metrics.recall_score(
                    targets, predictions, average="macro", zero_division=0
                )
            )
        elif metric == "f1":
            return float(
                sklearn_metrics.f1_score(
                    targets, predictions, average="macro", zero_division=0
                )
            )
        elif metric == "auc":
            # For binary classification with probability predictions
            if predictions.ndim > 1 and predictions.shape[1] > 1:
                try:
                    # Use second column for positive class probability
                    return float(
                        sklearn_metrics.roc_auc_score(targets, predictions[:, 1])
                    )
                except (TypeError, ValueError, AttributeError):
                    return float("nan")
            else:
                try:
                    return float(sklearn_metrics.roc_auc_score(targets, predictions))
                except (TypeError, ValueError, AttributeError):
                    return float("nan")

    # Regression metrics
    elif problem_type == "regression":
        if metric == "mse":
            return float(sklearn_metrics.mean_squared_error(targets, predictions))
        elif metric == "rmse":
            return float(
                np.sqrt(sklearn_metrics.mean_squared_error(targets, predictions))
            )
        elif metric == "mae":
            return float(sklearn_metrics.mean_absolute_error(targets, predictions))
        elif metric == "r2":
            return float(sklearn_metrics.r2_score(targets, predictions))

    # Unknown metric
    return float("nan")


def _calculate_basic_metric(
    predictions: Any, targets: Any, metric: str, problem_type: str
) -> float:
    """
    Calculate a metric using basic numpy operations (without scikit-learn).

    Args:
        predictions: Model predictions
        targets: True target values
        metric: Name of the metric to calculate
        problem_type: Type of problem

    Returns:
        Metric value
    """
    # Try to convert inputs to numpy arrays
    try:
        import numpy as np

        predictions = np.array(predictions)
        targets = np.array(targets)
    except (TypeError, ValueError, AttributeError):
        # If numpy is not available or conversion fails, use lists
        if not isinstance(predictions, list):
            predictions = list(predictions)
        if not isinstance(targets, list):
            targets = list(targets)

    # Basic classification metrics
    if problem_type == "classification":
        if metric == "accuracy":
            # Calculate accuracy manually
            correct = sum(1 for p, t in zip(predictions, targets) if p == t)
            total = len(targets)
            return float(correct / total) if total > 0 else 0.0

    # Basic regression metrics
    elif problem_type == "regression":
        if metric == "mse":
            # Calculate mean squared error manually
            squared_errors = [(p - t) ** 2 for p, t in zip(predictions, targets)]
            return (
                float(sum(squared_errors) / len(targets))
                if len(targets) > 0
                else float("nan")
            )
        elif metric == "rmse":
            # Calculate root mean squared error manually
            squared_errors = [(p - t) ** 2 for p, t in zip(predictions, targets)]
            mse = sum(squared_errors) / len(targets) if len(targets) > 0 else float("nan")
            return float(mse**0.5)
        elif metric == "mae":
            # Calculate mean absolute error manually
            abs_errors = [abs(p - t) for p, t in zip(predictions, targets)]
            return (
                float(sum(abs_errors) / len(targets))
                if len(targets) > 0
                else float("nan")
            )

    # Unknown or unsupported metric
    return float("nan")
