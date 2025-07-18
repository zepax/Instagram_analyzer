# mypy: ignore-errors
"""
ML Pipeline orchestrator for Instagram Data Mining Platform.

This module provides the main orchestration for ML pipelines, combining
preprocessing, model training, evaluation, and serving into a unified workflow.
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union

from instagram_analyzer.cache import cached
from instagram_analyzer.utils.retry_utils import exponential_backoff


class MLPipeline:
    """
    Main ML pipeline orchestrator for the Instagram Data Mining Platform.

    This class handles the end-to-end machine learning workflow, including
    data preprocessing, model training, evaluation, and prediction.

    Attributes:
        preprocessor: Data preprocessing component or name
        model: ML model component
        evaluation_metrics: List of metrics for model evaluation
        logger: Logger instance for pipeline logging
    """

    def __init__(
        self,
        preprocessor: Optional[Union[str, Any]] = None,
        model: Optional[Any] = None,
        evaluation_metrics: Optional[list[str]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the ML Pipeline.

        Args:
            preprocessor: Preprocessing component or name of built-in preprocessor
            model: Machine learning model instance
            evaluation_metrics: List of metrics for evaluation
            logger: Custom logger, if None a default will be used
        """
        self.preprocessor = preprocessor
        self.model = model
        self.evaluation_metrics = evaluation_metrics or ["accuracy", "f1"]
        self.logger = logger or logging.getLogger(__name__)

        # Initialize pipeline components
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize pipeline components based on configuration."""
        # Initialize preprocessor if it's a string (built-in preprocessor name)
        if isinstance(self.preprocessor, str):
            self.logger.info(f"Initializing built-in preprocessor: {self.preprocessor}")
            self.preprocessor = self._get_preprocessor(self.preprocessor)

    def _get_preprocessor(self, name: str) -> Any:
        """Get a preprocessor by name."""
        # Import here to avoid circular imports
        from instagram_analyzer.ml.preprocessing import get_preprocessor

        return get_preprocessor(name)

    @exponential_backoff(max_retries=3)
    def fit(self, data: Any) -> "MLPipeline":
        """
        Fit the pipeline on training data.

        Args:
            data: Training data

        Returns:
            self: The fitted pipeline
        """
        self.logger.info("Starting ML pipeline training")

        # Preprocess data if preprocessor is available
        if self.preprocessor:
            self.logger.debug("Preprocessing training data")
            processed_data = self.preprocessor.fit_transform(data)
        else:
            processed_data = data

        # Train model if available
        if self.model:
            self.logger.debug("Training model")
            self.model.fit(processed_data)

        self.logger.info("ML pipeline training completed")
        return self

    @cached(ttl=1800, key_prefix="ml_predict")
    def predict(self, data: Any) -> Any:
        """
        Make predictions using the trained pipeline.

        Args:
            data: Input data for prediction

        Returns:
            Prediction results
        """
        self.logger.debug("Making predictions with ML pipeline")

        # Preprocess data if preprocessor is available
        if self.preprocessor:
            self.logger.debug("Preprocessing prediction data")
            processed_data = self.preprocessor.transform(data)
        else:
            processed_data = data

        # Make predictions if model is available
        if self.model:
            self.logger.debug("Running model prediction")
            predictions = self.model.predict(processed_data)
            return predictions

        return None

    def evaluate(self, data: Any, target: Any = None) -> dict[str, float]:
        """
        Evaluate the pipeline on test data.

        Args:
            data: Test data
            target: True target values (if separate from data)

        Returns:
            Dict of evaluation metrics
        """
        self.logger.info("Evaluating ML pipeline")

        # Import here to avoid circular imports
        from instagram_analyzer.ml.evaluation.metrics import calculate_metrics

        # Make predictions
        predictions = self.predict(data)

        # Extract targets if not provided separately
        if target is None and hasattr(data, "target"):
            target = data.target

        # Calculate metrics
        metrics = calculate_metrics(predictions, target, metrics=self.evaluation_metrics)

        self.logger.info(f"Evaluation complete: {metrics}")
        return metrics

    def save(self, path: str) -> None:
        """
        Save the pipeline to disk.

        Args:
            path: Path to save the pipeline
        """
        # Import here to avoid circular imports
        from instagram_analyzer.ml.serving.serialization import save_pipeline

        self.logger.info(f"Saving ML pipeline to {path}")
        save_pipeline(self, path)

    @classmethod
    def load(cls, path: str) -> "MLPipeline":
        """
        Load a pipeline from disk.

        Args:
            path: Path to load the pipeline from

        Returns:
            Loaded MLPipeline instance
        """
        # Import here to avoid circular imports
        from instagram_analyzer.ml.serving.serialization import load_pipeline

        logging.info(f"Loading ML pipeline from {path}")
        return load_pipeline(path)  # type: ignore

    def run(self, data: Any, **kwargs: Any) -> Any:
        """
        Run the complete pipeline on data.

        Args:
            data: Input data
            **kwargs: Additional keyword arguments

        Returns:
            Pipeline results
        """
        self.logger.info("Running complete ML pipeline")
        return self.predict(data)
