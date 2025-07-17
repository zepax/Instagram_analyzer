"""
Base model class for machine learning models.

This module provides a base class for all machine learning models
in the Instagram Data Mining Platform, ensuring consistent APIs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MLModel(ABC):
    """
    Abstract base class for all ML models.

    This class defines the standard interface for all machine learning models
    in the Instagram Data Mining Platform.

    Attributes:
        model_type: Type of the model
        model_name: Name of the model
        model_version: Version of the model
        model_parameters: Parameters of the model
    """

    def __init__(
        self,
        model_type: str,
        model_name: str,
        model_version: str = "0.1.0",
        model_parameters: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the ML model.

        Args:
            model_type: Type of the model (e.g., 'sentiment', 'engagement')
            model_name: Name of the model
            model_version: Version of the model
            model_parameters: Parameters of the model
        """
        self.model_type = model_type
        self.model_name = model_name
        self.model_version = model_version
        self.model_parameters = model_parameters or {}
        self._model = None

    @abstractmethod
    def fit(self, X: Any, y: Optional[Any] = None) -> "MLModel":
        """
        Fit the model on training data.

        Args:
            X: Training data features
            y: Training data targets

        Returns:
            self: The fitted model
        """
        pass

    @abstractmethod
    def predict(self, X: Any) -> Any:
        """
        Make predictions using the model.

        Args:
            X: Input data for prediction

        Returns:
            Prediction results
        """
        pass

    def get_params(self) -> dict[str, Any]:
        """
        Get the model parameters.

        Returns:
            Dictionary of model parameters
        """
        return {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "model_version": self.model_version,
            **self.model_parameters,
        }

    def set_params(self, **params) -> "MLModel":
        """
        Set the model parameters.

        Args:
            **params: Parameters to set

        Returns:
            self: The model with updated parameters
        """
        for key, value in params.items():
            if key in ["model_type", "model_name", "model_version"]:
                setattr(self, key, value)
            else:
                self.model_parameters[key] = value
        return self

    def __repr__(self) -> str:
        """
        Get a string representation of the model.

        Returns:
            String representation
        """
        return f"{self.__class__.__name__}(type={self.model_type}, name={self.model_name}, version={self.model_version})"
