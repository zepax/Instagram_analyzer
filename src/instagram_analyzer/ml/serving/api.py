"""
API integration for ML models.

This module provides utilities for exposing ML models through APIs
and handling API requests/responses.
"""

import json
import logging
from typing import Any, Dict, Optional


class ModelAPI:
    """
    API interface for ML models.

    This class provides methods for exposing ML models through an API
    and handling API requests/responses.

    Attributes:
        model: ML model to expose through the API
        version: API version
        name: API name
    """

    def __init__(
        self,
        model: Any,
        version: str = "v1",
        name: Optional[str] = None,
    ):
        """
        Initialize the model API.

        Args:
            model: ML model to expose through the API
            version: API version
            name: API name (if None, derived from model name)
        """
        self.model = model
        self.version = version
        self.name = name or self._derive_name()
        self.logger = logging.getLogger(__name__)

    def _derive_name(self) -> str:
        """
        Derive API name from model name.

        Returns:
            Derived API name
        """
        if hasattr(self.model, "model_name"):
            return f"{self.model.model_name}_api"
        elif hasattr(self.model, "__class__"):
            return f"{self.model.__class__.__name__.lower()}_api"
        else:
            return "model_api"

    def handle_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """
        Handle an API request.

        Args:
            request_data: Request data

        Returns:
            Response data
        """
        self.logger.info(f"Handling API request for {self.name}")

        try:
            # Extract inputs from request
            inputs = self._extract_inputs(request_data)

            # Make prediction
            prediction = self._make_prediction(inputs)

            # Format response
            response = self._format_response(prediction)

            return response

        except Exception as e:
            self.logger.error(f"Error handling API request: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
            }

    def _extract_inputs(self, request_data: dict[str, Any]) -> Any:
        """
        Extract model inputs from request data.

        Args:
            request_data: Request data

        Returns:
            Model inputs
        """
        # Default implementation assumes request_data has 'inputs' key
        if "inputs" in request_data:
            return request_data["inputs"]
        else:
            # If no 'inputs' key, use the entire request data
            return request_data

    def _make_prediction(self, inputs: Any) -> Any:
        """
        Make prediction using the model.

        Args:
            inputs: Model inputs

        Returns:
            Model prediction
        """
        # Call predict method on the model
        if hasattr(self.model, "predict"):
            return self.model.predict(inputs)
        else:
            raise AttributeError("Model does not have a 'predict' method")

    def _format_response(self, prediction: Any) -> dict[str, Any]:
        """
        Format prediction as API response.

        Args:
            prediction: Model prediction

        Returns:
            Formatted API response
        """
        # Convert numpy arrays to lists
        try:
            import numpy as np

            if isinstance(prediction, np.ndarray):
                prediction = prediction.tolist()
        except ImportError:
            pass

        # Convert basic types to JSON-serializable
        try:
            # Try to serialize the prediction to ensure it's JSON-serializable
            json.dumps(prediction)
            serializable_prediction = prediction
        except (TypeError, OverflowError):
            # If not serializable, convert to string
            serializable_prediction = str(prediction)

        # Format response
        return {
            "prediction": serializable_prediction,
            "model": self.name,
            "version": self.version,
            "status": "success",
        }
