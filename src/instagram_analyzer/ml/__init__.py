"""
Machine Learning module for Instagram Data Mining Platform.

This package provides advanced data mining and machine learning capabilities
for analyzing social media data, including sentiment analysis, engagement prediction,
user segmentation, and anomaly detection.
"""

from instagram_analyzer.ml.config import MLConfig, get_config
from instagram_analyzer.ml.models import EngagementPredictor, SentimentAnalyzer
from instagram_analyzer.ml.pipeline import MLPipeline
from instagram_analyzer.ml.preprocessing.feature import FeatureEngineer
from instagram_analyzer.ml.preprocessing.text import TextPreprocessor

__all__ = [
    "MLPipeline",
    "SentimentAnalyzer",
    "EngagementPredictor",
    "FeatureEngineer",
    "TextPreprocessor",
    "get_config",
    "MLConfig",
]
