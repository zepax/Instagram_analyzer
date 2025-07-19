"""
Model serialization utilities.

This module provides functions for saving and loading ML models
to/from disk, including preprocessing components and metadata.
"""

import logging
import os
import pickle
from typing import Any, Dict, Optional

# Try to import joblib (preferred) or pickle
try:
    import joblib

    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Optional dependency for MLflow
try:
    import mlflow

    HAS_MLFLOW = True
except ImportError:
    HAS_MLFLOW = False


def save_pipeline(pipeline: Any, path: str, use_mlflow: bool = False) -> None:
    """
    Save a machine learning pipeline to disk.

    Args:
        pipeline: ML pipeline to save
        path: Path to save the pipeline
        use_mlflow: Whether to use MLflow for saving
    """
    logger = logging.getLogger(__name__)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    # Save using MLflow if requested and available
    if use_mlflow and HAS_MLFLOW:
        logger.info(f"Saving pipeline to MLflow at {path}")
        try:
            with mlflow.start_run(nested=True):
                # Log model parameters
                if hasattr(pipeline, "get_params"):
                    params = pipeline.get_params()
                    mlflow.log_params(params)

                # Save model
                mlflow.sklearn.log_model(pipeline, path)
        except Exception as e:
            logger.error("Error saving pipeline with MLflow: %s", e)
            # Fall back to joblib/pickle
            logger.info("Falling back to joblib/pickle")
            _save_with_joblib_or_pickle(pipeline, path)
    else:
        # Save with joblib or pickle
        _save_with_joblib_or_pickle(pipeline, path)


def _save_with_joblib_or_pickle(obj: Any, path: str) -> None:
    """
    Save an object using joblib or pickle.

    Args:
        obj: Object to save
        path: Path to save the object
    """
    logger = logging.getLogger(__name__)

    try:
        if HAS_JOBLIB:
            logger.info("Saving object with joblib to %s", path)
            joblib.dump(obj, path)
        else:
            logger.info("Saving object with pickle to %s", path)
            with open(path, "wb") as f:
                pickle.dump(obj, f)
    except Exception as e:
        logger.error("Error saving object: %s", e)
        raise


def load_pipeline(path: str, use_mlflow: bool = False) -> Any:
    """
    Load a machine learning pipeline from disk.

    Args:
        path: Path to load the pipeline from
        use_mlflow: Whether to use MLflow for loading

    Returns:
        Loaded ML pipeline
    """
    logger = logging.getLogger(__name__)

    # Load using MLflow if requested and available
    if use_mlflow and HAS_MLFLOW:
        logger.info(f"Loading pipeline from MLflow at {path}")
        try:
            return mlflow.sklearn.load_model(path)
        except Exception as e:
            logger.error("Error loading pipeline with MLflow: %s", e)
            # Fall back to joblib/pickle
            logger.info("Falling back to joblib/pickle")
            return _load_with_joblib_or_pickle(path)
    else:
        # Load with joblib or pickle
        return _load_with_joblib_or_pickle(path)


def _load_with_joblib_or_pickle(path: str) -> Any:
    """
    Load an object using joblib or pickle.

    Args:
        path: Path to load the object from

    Returns:
        Loaded object
    """
    logger = logging.getLogger(__name__)

    try:
        if HAS_JOBLIB:
            logger.info(f"Loading object with joblib from {path}")
            return joblib.load(path)
        else:
            logger.info(f"Loading object with pickle from {path}")
            # Security note: Only use pickle.load for trusted files from known sources
            # as it can execute arbitrary code
            with open(path, "rb") as f:
                # Validate the path to ensure it's from our trusted source
                if not os.path.abspath(path).startswith(
                    os.path.abspath(os.path.dirname(__file__))
                ):
                    raise ValueError(
                        "Security check: Only loading models from trusted locations"
                    )
                return pickle.load(f)
    except Exception as e:
        logger.error("Error loading object: %s", e)
        raise


def save_model_metadata(metadata: dict[str, Any], path: str) -> None:
    """
    Save model metadata to disk.

    Args:
        metadata: Model metadata
        path: Path to save the metadata
    """
    logger = logging.getLogger(__name__)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    try:
        if HAS_JOBLIB:
            logger.info("Saving model metadata with joblib to %s", path)
            joblib.dump(metadata, path)
        else:
            logger.info("Saving model metadata with pickle to %s", path)
            with open(path, "wb") as f:
                pickle.dump(metadata, f)
    except Exception as e:
        logger.error("Error saving model metadata: %s", e)
        raise


def load_model_metadata(path: str) -> dict[str, Any]:
    """
    Load model metadata from disk.

    Args:
        path: Path to load the metadata from

    Returns:
        Model metadata
    """
    logger = logging.getLogger(__name__)

    try:
        if HAS_JOBLIB:
            logger.info(f"Loading model metadata with joblib from {path}")
            return joblib.load(path)
        else:
            logger.info(f"Loading model metadata with pickle from {path}")
            # Security note: Only use pickle.load for trusted files from known sources
            # as it can execute arbitrary code
            with open(path, "rb") as f:
                # Validate the path to ensure it's from our trusted source
                if not os.path.abspath(path).startswith(
                    os.path.abspath(os.path.dirname(__file__))
                ):
                    raise ValueError(
                        "Security check: Only loading models from trusted locations"
                    )
                return pickle.load(f)
    except Exception as e:
        logger.error("Error loading model metadata: %s", e)
        raise
