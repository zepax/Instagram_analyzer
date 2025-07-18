# mypy: ignore-errors
"""
Engagement prediction model for Instagram Data Mining Platform.

This module provides engagement prediction capabilities using machine learning
to predict likes, comments, and other engagement metrics for social media content.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

from instagram_analyzer.cache import cached
from instagram_analyzer.ml.models.base import MLModel
from instagram_analyzer.ml.preprocessing.feature import FeatureEngineer


class EngagementPredictor(MLModel):
    """
    Engagement prediction model for social media content.

    This model predicts engagement metrics (likes, comments, shares) based on
    content features, timing, user behavior, and network characteristics.

    Attributes:
        algorithm: ML algorithm to use ('random_forest', 'gradient_boosting', etc.)
        features: List of feature groups to include
        target_metrics: List of target metrics to predict
        scaler: Feature scaler for numerical features
        encoders: Label encoders for categorical features
        models: Dictionary of trained models for each target metric
    """

    def __init__(
        self,
        algorithm: str = "random_forest",
        features: Optional[list[str]] = None,
        target_metrics: Optional[list[str]] = None,
        prediction_window_hours: int = 24,
        **kwargs,
    ):
        """
        Initialize the engagement predictor.

        Args:
            algorithm: ML algorithm ('random_forest', 'gradient_boosting', 'linear', 'ridge')
            features: List of feature groups to include
            target_metrics: List of metrics to predict
            prediction_window_hours: Time window for prediction
            **kwargs: Additional parameters for the model
        """
        super().__init__(
            model_type="engagement_prediction",
            model_name=f"engagement_{algorithm}",
            model_parameters={
                "algorithm": algorithm,
                "features": features,
                "target_metrics": target_metrics,
                "prediction_window_hours": prediction_window_hours,
                **kwargs,
            },
        )

        self.algorithm = algorithm
        self.features = features or ["temporal", "content", "user", "network"]
        self.target_metrics = target_metrics or ["likes", "comments"]
        self.prediction_window_hours = prediction_window_hours
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.feature_engineer = FeatureEngineer(
            include_derived=True, feature_groups=self.features
        )
        self.scaler = StandardScaler()
        self.encoders: dict[str, Any] = {}
        self.models = {}
        self.feature_names = []
        self.is_fitted = False

        # Initialize base models
        self._initialize_models(**kwargs)

    def _initialize_models(self, **kwargs) -> None:
        """Initialize ML models based on algorithm selection."""
        self.logger.info(
            f"Initializing engagement models with algorithm: {self.algorithm}"
        )

        model_params = kwargs.copy()

        if self.algorithm == "random_forest":
            base_model = RandomForestRegressor(
                n_estimators=model_params.get("n_estimators", 100),
                max_depth=model_params.get("max_depth", 10),
                min_samples_split=model_params.get("min_samples_split", 5),
                min_samples_leaf=model_params.get("min_samples_leaf", 2),
                random_state=model_params.get("random_state", 42),
                n_jobs=model_params.get("n_jobs", -1),
            )
        elif self.algorithm == "gradient_boosting":
            base_model = GradientBoostingRegressor(
                n_estimators=model_params.get("n_estimators", 100),
                learning_rate=model_params.get("learning_rate", 0.1),
                max_depth=model_params.get("max_depth", 6),
                min_samples_split=model_params.get("min_samples_split", 5),
                min_samples_leaf=model_params.get("min_samples_leaf", 2),
                random_state=model_params.get("random_state", 42),
            )
        elif self.algorithm == "ridge":
            base_model = Ridge(
                alpha=model_params.get("alpha", 1.0),
                random_state=model_params.get("random_state", 42),
            )
        else:  # Default to linear regression
            base_model = LinearRegression(
                n_jobs=model_params.get("n_jobs", -1),
            )

        # Create a separate model for each target metric
        for metric in self.target_metrics:
            self.models[metric] = base_model.__class__(**base_model.get_params())

    def fit(self, X: Any, y: Optional[Any] = None) -> "EngagementPredictor":
        """
        Fit the engagement prediction model.

        Args:
            X: Training data (posts, stories, etc.)
            y: Target engagement data (optional, can be extracted from X)

        Returns:
            self: The fitted model
        """
        self.logger.info("Starting engagement prediction model training")

        # Extract features
        features = self.feature_engineer.fit_transform(X)

        # Convert features to DataFrame
        feature_df = self._features_to_dataframe(features)

        # Extract target variables
        target_df = self._extract_targets(X, y)

        # Ensure we have the same number of samples
        min_samples = min(len(feature_df), len(target_df))
        feature_df = feature_df.iloc[:min_samples]
        target_df = target_df.iloc[:min_samples]

        if len(feature_df) == 0:
            raise ValueError("No valid training data available")

        # Preprocess features
        feature_df_processed = self._preprocess_features(feature_df, fit=True)

        # Train models for each target metric
        for metric in self.target_metrics:
            if metric in target_df.columns:
                self.logger.info(f"Training model for {metric}")

                # Handle missing values in targets
                valid_mask = ~target_df[metric].isna()
                X_train = feature_df_processed[valid_mask]
                y_train = target_df[metric][valid_mask]

                if len(X_train) > 0:
                    # Train the model
                    self.models[metric].fit(X_train, y_train)

                    # Log training performance
                    train_score = self.models[metric].score(X_train, y_train)
                    self.logger.info(f"Training R² for {metric}: {train_score:.4f}")
                else:
                    self.logger.warning(f"No valid training data for {metric}")

        self.is_fitted = True
        self.logger.info("Engagement prediction model training completed")
        return self

    @cached(ttl=1800, key_prefix="engagement_predict")
    def predict(self, X: Union[list[Any], Any]) -> dict[str, Union[list[float], float]]:
        """
        Predict engagement metrics for new data.

        Args:
            X: Input data for prediction

        Returns:
            Dictionary with predicted values for each target metric
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")

        self.logger.debug("Making engagement predictions")

        # Ensure X is a list
        if not isinstance(X, list):
            X = [X]

        # Extract features
        features = self.feature_engineer.transform(X)

        # Convert to DataFrame
        feature_df = self._features_to_dataframe(features)

        if len(feature_df) == 0:
            # Return empty predictions
            return {metric: [] for metric in self.target_metrics}

        # Preprocess features
        feature_df_processed = self._preprocess_features(feature_df, fit=False)

        # Make predictions for each metric
        predictions = {}
        for metric in self.target_metrics:
            if metric in self.models:
                try:
                    pred = self.models[metric].predict(feature_df_processed)
                    predictions[metric] = (
                        pred.tolist() if len(pred) > 1 else float(pred[0])
                    )
                except Exception as e:
                    self.logger.warning(f"Error predicting {metric}: {str(e)}")
                    predictions[metric] = [0.0] * len(feature_df_processed)

        return predictions

    def evaluate(self, X: Any, y: Optional[Any] = None) -> dict[str, dict[str, float]]:
        """
        Evaluate the model on test data.

        Args:
            X: Test data
            y: True target values (optional, can be extracted from X)

        Returns:
            Dictionary of evaluation metrics for each target
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")

        self.logger.info("Evaluating engagement prediction model")

        # Extract features and targets
        features = self.feature_engineer.transform(X)
        feature_df = self._features_to_dataframe(features)
        target_df = self._extract_targets(X, y)

        # Ensure same number of samples
        min_samples = min(len(feature_df), len(target_df))
        feature_df = feature_df.iloc[:min_samples]
        target_df = target_df.iloc[:min_samples]

        feature_df_processed = self._preprocess_features(feature_df, fit=False)

        evaluation_results = {}

        for metric in self.target_metrics:
            if metric in target_df.columns and metric in self.models:
                # Get valid samples
                valid_mask = ~target_df[metric].isna()
                X_test = feature_df_processed[valid_mask]
                y_true = target_df[metric][valid_mask]

                if len(X_test) > 0:
                    # Make predictions
                    y_pred = self.models[metric].predict(X_test)

                    # Calculate metrics
                    evaluation_results[metric] = {
                        "mae": mean_absolute_error(y_true, y_pred),
                        "mse": mean_squared_error(y_true, y_pred),
                        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
                        "r2": r2_score(y_true, y_pred),
                        "mean_actual": float(np.mean(y_true)),
                        "mean_predicted": float(np.mean(y_pred)),
                        "samples": len(X_test),
                    }
                else:
                    evaluation_results[metric] = {
                        "mae": float("inf"),
                        "mse": float("inf"),
                        "rmse": float("inf"),
                        "r2": 0.0,
                        "mean_actual": 0.0,
                        "mean_predicted": 0.0,
                        "samples": 0,
                    }

        self.logger.info(f"Evaluation complete: {evaluation_results}")
        return evaluation_results

    def get_feature_importance(self, metric: str) -> Optional[dict[str, float]]:
        """
        Get feature importance for a specific target metric.

        Args:
            metric: Target metric name

        Returns:
            Dictionary of feature names and their importance scores
        """
        if not self.is_fitted or metric not in self.models:
            return None

        model = self.models[metric]

        # Check if model has feature_importances_ attribute
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            return dict(zip(self.feature_names, importances))
        elif hasattr(model, "coef_"):
            # For linear models, use absolute coefficients
            importances = np.abs(model.coef_)
            return dict(zip(self.feature_names, importances))
        else:
            return None

    def _features_to_dataframe(self, features: dict[str, Any]) -> pd.DataFrame:
        """Convert feature dictionary to DataFrame."""
        data = {}

        # Flatten nested feature groups
        for group_name, group_features in features.items():
            if isinstance(group_features, dict):
                for feature_name, feature_values in group_features.items():
                    if isinstance(feature_values, list):
                        data[f"{group_name}_{feature_name}"] = feature_values
                    else:
                        data[f"{group_name}_{feature_name}"] = [feature_values]

        # Handle empty data
        if not data:
            return pd.DataFrame()

        # Ensure all lists have the same length
        max_length = max(len(v) if isinstance(v, list) else 1 for v in data.values())
        for key, values in data.items():
            if not isinstance(values, list):
                data[key] = [values] * max_length
            elif len(values) < max_length:
                # Pad with last value or None
                last_val = values[-1] if values else None
                data[key] = values + [last_val] * (max_length - len(values))

        df = pd.DataFrame(data)
        self.feature_names = list(df.columns)
        return df

    def _extract_targets(self, X: Any, y: Optional[Any] = None) -> pd.DataFrame:
        """Extract target engagement metrics from data."""
        if y is not None:
            # Use provided targets
            if isinstance(y, pd.DataFrame):
                return y
            elif isinstance(y, dict):
                return pd.DataFrame(y)
            else:
                return pd.DataFrame({"engagement": y})

        # Extract targets from X
        targets = []

        if isinstance(X, list):
            for item in X:
                target_row = {}

                # Extract likes
                if hasattr(item, "likes_count"):
                    target_row["likes"] = item.likes_count or 0
                elif hasattr(item, "likes") and isinstance(item.likes, list):
                    target_row["likes"] = len(item.likes)
                else:
                    target_row["likes"] = 0

                # Extract comments
                if hasattr(item, "comments_count"):
                    target_row["comments"] = item.comments_count or 0
                elif hasattr(item, "comments") and isinstance(item.comments, list):
                    target_row["comments"] = len(item.comments)
                else:
                    target_row["comments"] = 0

                # Extract shares (if available)
                if hasattr(item, "shares_count"):
                    target_row["shares"] = item.shares_count or 0
                else:
                    target_row["shares"] = 0

                targets.append(target_row)

        return pd.DataFrame(targets)

    def _preprocess_features(
        self, feature_df: pd.DataFrame, fit: bool = False
    ) -> pd.DataFrame:
        """Preprocess features for training/prediction."""
        df = feature_df.copy()

        # Handle categorical features
        categorical_columns = df.select_dtypes(include=["object"]).columns

        for col in categorical_columns:
            if col not in self.encoders:
                if fit:
                    self.encoders[col] = LabelEncoder()
                    # Fit and transform
                    df[col] = self.encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Use default encoding for unseen categories
                    df[col] = 0
            else:
                # Transform using existing encoder
                try:
                    df[col] = self.encoders[col].transform(df[col].astype(str))
                except ValueError:
                    # Handle unseen categories
                    df[col] = 0

        # Handle numerical features
        numerical_columns = df.select_dtypes(include=[np.number]).columns

        if fit:
            df[numerical_columns] = self.scaler.fit_transform(df[numerical_columns])
        else:
            df[numerical_columns] = self.scaler.transform(df[numerical_columns])

        # Fill any remaining NaN values
        df = df.fillna(0)

        return df

    def predict_optimal_timing(self, content_features: dict[str, Any]) -> dict[str, Any]:
        """
        Predict optimal posting timing for maximum engagement.

        Args:
            content_features: Features of the content to post

        Returns:
            Dictionary with optimal timing recommendations
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making timing predictions")

        # Generate predictions for different time slots
        hours = list(range(24))
        best_predictions = {}

        for metric in self.target_metrics:
            best_hour = 0
            best_score = 0

            for hour in hours:
                # Create feature vector with this hour
                test_features = content_features.copy()
                test_features["temporal_features"] = {
                    "hour_of_day": [hour],
                    "day_of_week": [1],  # Monday
                    "is_weekend": [False],
                    "is_business_hours": [9 <= hour <= 17],
                }

                # Predict engagement
                predictions = self.predict([test_features])
                score = predictions.get(metric, [0])[0] if predictions.get(metric) else 0

                if score > best_score:
                    best_score = score
                    best_hour = hour

            best_predictions[metric] = {
                "optimal_hour": best_hour,
                "predicted_engagement": best_score,
            }

        return best_predictions
