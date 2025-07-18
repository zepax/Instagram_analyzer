"""
Serving module for Instagram Data Mining Platform.

This package provides tools and utilities for serving and deploying
machine learning models.
"""

from instagram_analyzer.ml.serving.api import ModelAPI
from instagram_analyzer.ml.serving.serialization import load_pipeline, save_pipeline

__all__ = ["ModelAPI", "save_pipeline", "load_pipeline"]
