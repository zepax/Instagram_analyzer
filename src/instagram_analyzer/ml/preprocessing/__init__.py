"""
Preprocessing module for Instagram Data Mining Platform.

This package provides tools and utilities for preprocessing data
before applying machine learning models.
"""

from typing import Any, Dict, Optional, Union

try:
    from instagram_analyzer.ml.preprocessing.feature import FeatureEngineer
    from instagram_analyzer.ml.preprocessing.image import ImagePreprocessor
    from instagram_analyzer.ml.preprocessing.text import TextPreprocessor

    __all__ = [
        "TextPreprocessor",
        "ImagePreprocessor",
        "FeatureEngineer",
        "get_preprocessor",
    ]
except ImportError:
    # Handle case where modules aren't fully installed yet
    pass


def get_preprocessor(name: str) -> Any:
    """
    Get a preprocessor by name.

    Args:
        name: Name of the preprocessor

    Returns:
        Preprocessor instance

    Raises:
        ValueError: If the preprocessor name is not recognized
    """
    preprocessors = {
        "text_standard": get_text_preprocessor,
        "image_standard": get_image_preprocessor,
        "feature_standard": get_feature_preprocessor,
    }

    if name not in preprocessors:
        raise ValueError(f"Unknown preprocessor: {name}")

    return preprocessors[name]()


def get_text_preprocessor() -> Any:
    """Get standard text preprocessor."""
    from instagram_analyzer.ml.preprocessing.text import TextPreprocessor

    return TextPreprocessor()


def get_image_preprocessor() -> Any:
    """Get standard image preprocessor."""
    from instagram_analyzer.ml.preprocessing.image import ImagePreprocessor

    return ImagePreprocessor()


def get_feature_preprocessor() -> Any:
    """Get standard feature preprocessor."""
    from instagram_analyzer.ml.preprocessing.feature import FeatureEngineer

    return FeatureEngineer()


__all__ = ["get_preprocessor"]
