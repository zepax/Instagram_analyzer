# mypy: ignore-errors
"""
ML Configuration module for Instagram Data Mining Platform.

This module provides configuration settings, constants, and defaults
for machine learning components and pipelines.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class MLModelType(Enum):
    """Supported ML model types."""

    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    USER_SEGMENTATION = "user_segmentation"
    ANOMALY_DETECTION = "anomaly_detection"
    TOPIC_MODELING = "topic_modeling"
    NETWORK_ANALYSIS = "network_analysis"


class PreprocessorType(Enum):
    """Supported preprocessor types."""

    TEXT_STANDARD = "text_standard"
    TEXT_ADVANCED = "text_advanced"
    FEATURE_STANDARD = "feature_standard"
    FEATURE_ADVANCED = "feature_advanced"
    IMAGE_BASIC = "image_basic"
    IMAGE_ADVANCED = "image_advanced"


@dataclass
class MLConfig:
    """Base configuration for ML components."""

    # Model configuration
    model_type: str = "sentiment_analysis"
    model_name: str = "default"
    model_version: str = "1.0.0"

    # Training configuration
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 10
    validation_split: float = 0.2
    random_seed: int = 42

    # Feature configuration
    max_features: int = 10000
    sequence_length: int = 100

    # Evaluation configuration
    evaluation_metrics: list[str] = field(
        default_factory=lambda: ["accuracy", "precision", "recall", "f1"]
    )

    # Caching configuration
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour

    # Parallel processing
    n_jobs: int = -1  # Use all available cores

    # Output configuration
    output_dir: str = "output/ml"
    model_save_dir: str = "models"

    # Logging configuration
    log_level: str = "INFO"
    log_to_file: bool = True

    def __post_init__(self) -> None:
        """Post-initialization to create directories if needed."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.model_save_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class SentimentAnalysisConfig(MLConfig):
    """Configuration for sentiment analysis models."""

    model_type: str = "sentiment_analysis"

    # Model-specific settings
    sentiment_model: str = "textblob"  # textblob, vader, transformers
    language: str = "en"

    # TextBlob specific
    use_naive_bayes: bool = False

    # Transformers specific
    pretrained_model: str = "distilbert-base-uncased"
    max_length: int = 512

    # Output configuration
    include_confidence: bool = True
    include_emotion: bool = True
    emotion_model: str = "text2emotion"


@dataclass
class EngagementPredictionConfig(MLConfig):
    """Configuration for engagement prediction models."""

    model_type: str = "engagement_prediction"

    # Model-specific settings
    algorithm: str = "random_forest"  # random_forest, xgboost, lightgbm

    # Feature selection
    feature_groups: list[str] = field(
        default_factory=lambda: ["temporal", "content", "user", "network"]
    )

    # Target metrics
    prediction_targets: list[str] = field(
        default_factory=lambda: ["likes", "comments", "shares"]
    )

    # Time window for prediction
    prediction_window_hours: int = 24

    # Feature engineering
    include_lag_features: bool = True
    lag_periods: list[int] = field(default_factory=lambda: [1, 7, 30])


@dataclass
class UserSegmentationConfig(MLConfig):
    """Configuration for user segmentation models."""

    model_type: str = "user_segmentation"

    # Clustering settings
    n_clusters: int = 5
    algorithm: str = "kmeans"  # kmeans, dbscan, hierarchical

    # Feature selection
    feature_groups: list[str] = field(
        default_factory=lambda: [
            "activity_patterns",
            "engagement_behavior",
            "content_preferences",
            "temporal_patterns",
        ]
    )

    # Clustering parameters
    max_iterations: int = 300
    tolerance: float = 1e-4

    # DBSCAN specific
    eps: float = 0.5
    min_samples: int = 5

    # Segment naming
    auto_name_segments: bool = True
    segment_names: Optional[list[str]] = None


@dataclass
class AnomalyDetectionConfig(MLConfig):
    """Configuration for anomaly detection models."""

    model_type: str = "anomaly_detection"

    # Algorithm settings
    algorithm: str = (
        "isolation_forest"  # isolation_forest, one_class_svm, local_outlier_factor
    )
    contamination: float = 0.05  # Expected proportion of anomalies

    # Feature selection
    feature_groups: list[str] = field(
        default_factory=lambda: ["temporal", "engagement", "content"]
    )

    # Time series specific
    window_size: int = 24  # Hours
    detection_threshold: float = 0.8

    # Isolation Forest specific
    n_estimators: int = 100
    max_samples: Union[int, str] = "auto"

    # One-Class SVM specific
    kernel: str = "rbf"
    gamma: str = "scale"
    nu: float = 0.05


# Default configurations for each model type
DEFAULT_CONFIGS: dict[str, MLConfig] = {
    "sentiment_analysis": SentimentAnalysisConfig(),
    "engagement_prediction": EngagementPredictionConfig(),
    "user_segmentation": UserSegmentationConfig(),
    "anomaly_detection": AnomalyDetectionConfig(),
}


def get_config(model_type: str, **kwargs) -> MLConfig:
    """
    Get configuration for a specific model type.

    Args:
        model_type: Type of ML model
        **kwargs: Additional configuration parameters to override

    Returns:
        MLConfig instance for the specified model type

    Raises:
        ValueError: If model_type is not supported
    """
    if model_type not in DEFAULT_CONFIGS:
        raise ValueError(f"Unsupported model type: {model_type}")

    config = DEFAULT_CONFIGS[model_type]

    # Override with any provided kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    return config


def get_preprocessor_config(preprocessor_type: str) -> dict[str, Any]:
    """
    Get configuration for a specific preprocessor type.

    Args:
        preprocessor_type: Type of preprocessor

    Returns:
        Dict with preprocessor configuration

    Raises:
        ValueError: If preprocessor_type is not supported
    """
    configs = {
        "text_standard": {
            "lowercase": True,
            "remove_punctuation": True,
            "remove_stopwords": True,
            "lemmatize": True,
            "max_features": 10000,
            "ngram_range": (1, 2),
        },
        "text_advanced": {
            "lowercase": True,
            "remove_punctuation": False,
            "remove_stopwords": True,
            "lemmatize": True,
            "stemming": False,
            "max_features": 50000,
            "ngram_range": (1, 3),
            "use_tfidf": True,
            "include_emojis": True,
            "normalize_unicode": True,
        },
        "feature_standard": {
            "scale_features": True,
            "handle_missing": "median",
            "feature_selection": True,
            "select_k_best": 1000,
        },
        "feature_advanced": {
            "scale_features": True,
            "handle_missing": "iterative",
            "feature_selection": True,
            "select_k_best": 5000,
            "polynomial_features": True,
            "interaction_features": True,
            "feature_engineering": True,
        },
    }

    if preprocessor_type not in configs:
        raise ValueError(f"Unsupported preprocessor type: {preprocessor_type}")

    return configs[preprocessor_type]


# Model registry for dynamic loading
MODEL_REGISTRY: dict[str, str] = {
    "sentiment_analysis": "instagram_analyzer.ml.models.sentiment.SentimentAnalyzer",
    "engagement_prediction": "instagram_analyzer.ml.models.engagement.EngagementPredictor",
    "user_segmentation": "instagram_analyzer.ml.models.clustering.UserSegmentation",
    "anomaly_detection": "instagram_analyzer.ml.models.anomaly.AnomalyDetector",
}

# Preprocessor registry for dynamic loading
PREPROCESSOR_REGISTRY: dict[str, str] = {
    "text_standard": "instagram_analyzer.ml.preprocessing.text.StandardTextPreprocessor",
    "text_advanced": "instagram_analyzer.ml.preprocessing.text.AdvancedTextPreprocessor",
    "feature_standard": "instagram_analyzer.ml.preprocessing.feature.StandardFeaturePreprocessor",
    "feature_advanced": "instagram_analyzer.ml.preprocessing.feature.AdvancedFeaturePreprocessor",
}
