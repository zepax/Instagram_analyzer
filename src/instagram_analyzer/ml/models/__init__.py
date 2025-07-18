"""
Models module for the Instagram Data Mining Platform.

This package provides machine learning models for various tasks,
including sentiment analysis, engagement prediction, user segmentation,
and anomaly detection.
"""

from instagram_analyzer.ml.models.base import MLModel
from instagram_analyzer.ml.models.engagement import EngagementPredictor
from instagram_analyzer.ml.models.sentiment import SentimentAnalyzer

__all__ = ["MLModel", "SentimentAnalyzer", "EngagementPredictor"]
