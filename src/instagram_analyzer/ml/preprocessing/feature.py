# mypy: ignore-errors
"""
Feature engineering utilities for ML preprocessing.

This module provides tools for feature extraction and engineering
from various types of data (text, images, etc.).
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from dateutil import parser as date_parser

from instagram_analyzer.models.conversation import Message
from instagram_analyzer.models.post import Post
from instagram_analyzer.utils.text_utils import extract_hashtags, extract_mentions


# flake8: noqa: C901
class FeatureEngineer:
    """
    Feature engineering class for machine learning.

    This class provides methods for extracting and transforming features
    from various types of data including posts, stories, conversations, and interactions.

    Attributes:
        include_derived: Whether to include derived features
        feature_groups: Groups of features to include
        feature_cache: Cache for computed features
    """

    def __init__(
        self,
        include_derived: bool = True,
        feature_groups: Optional[list[str]] = None,
    ):
        """
        Initialize the feature engineer.

        Args:
            include_derived: Whether to include derived features
            feature_groups: Groups of features to include (None for all)
        """
        self.include_derived = include_derived
        self.feature_groups = feature_groups or [
            "temporal",
            "content",
            "user",
            "network",
        ]
        self.feature_cache: dict[str, Any] = {}

    def fit(self, X: Any, y: Optional[Any] = None) -> "FeatureEngineer":
        """
        Fit the feature engineer on training data.

        Args:
            X: Training data
            y: Target values (ignored)

        Returns:
            self: The fitted feature engineer
        """
        return self

    def transform(self, X: Any) -> Any:
        """
        Transform data by extracting features.

        Args:
            X: Data to transform

        Returns:
            Extracted features
        """
        features = {}

        # Extract features based on data type and configured groups
        if "temporal" in self.feature_groups:
            temporal_features = self._extract_temporal_features(X)
            features.update(temporal_features)

        if "content" in self.feature_groups:
            content_features = self._extract_content_features(X)
            features.update(content_features)

        if "user" in self.feature_groups:
            user_features = self._extract_user_features(X)
            features.update(user_features)

        if "network" in self.feature_groups:
            network_features = self._extract_network_features(X)
            features.update(network_features)

        # Add derived features if requested
        if self.include_derived:
            derived_features = self._extract_derived_features(features)
            features.update(derived_features)

        return features

    def fit_transform(self, X: Any, y: Optional[Any] = None) -> Any:
        """
        Fit and transform data.

        Args:
            X: Data to transform
            y: Target values (ignored)

        Returns:
            Extracted features
        """
        return self.fit(X, y).transform(X)

    def _extract_temporal_features(self, data: Any) -> dict[str, Any]:
        """
        Extract temporal features from data.

        Args:
            data: Input data (posts, messages, etc.)

        Returns:
            Dictionary of temporal features
        """
        temporal_features: dict[str, list[Any]] = {
            "timestamp": [],
            "hour_of_day": [],
            "day_of_week": [],
            "month": [],
            "year": [],
            "is_weekend": [],
            "is_business_hours": [],
            "season": [],
            "time_since_last_post": [],
        }

        if isinstance(data, list):
            timestamps = []
            for item in data:
                if hasattr(item, "timestamp") and item.timestamp:
                    try:
                        if isinstance(item.timestamp, str):
                            dt = date_parser.parse(item.timestamp)
                        else:
                            dt = item.timestamp
                        timestamps.append(dt)
                    except (ValueError, TypeError):
                        timestamps.append(None)
                else:
                    timestamps.append(None)

            # Sort timestamps to calculate time differences
            valid_timestamps = [ts for ts in timestamps if ts is not None]
            valid_timestamps.sort()

            for i, item in enumerate(data):
                timestamp = timestamps[i]
                if timestamp:
                    temporal_features["timestamp"].append(timestamp)
                    temporal_features["hour_of_day"].append(timestamp.hour)
                    temporal_features["day_of_week"].append(timestamp.weekday())
                    temporal_features["month"].append(timestamp.month)
                    temporal_features["year"].append(timestamp.year)
                    temporal_features["is_weekend"].append(timestamp.weekday() >= 5)
                    temporal_features["is_business_hours"].append(
                        9 <= timestamp.hour <= 17
                    )

                    # Season calculation (Northern Hemisphere)
                    month = timestamp.month
                    if month in [12, 1, 2]:
                        season = "winter"
                    elif month in [3, 4, 5]:
                        season = "spring"
                    elif month in [6, 7, 8]:
                        season = "summer"
                    else:
                        season = "autumn"
                    temporal_features["season"].append(season)

                    # Time since last post
                    if i > 0 and i - 1 < len(valid_timestamps):
                        time_diff = (
                            timestamp - valid_timestamps[i - 1]
                        ).total_seconds() / 3600  # hours
                        temporal_features["time_since_last_post"].append(time_diff)
                    else:
                        temporal_features["time_since_last_post"].append(0)
                else:
                    # Fill with defaults for missing timestamps
                    for key in temporal_features:
                        if key != "timestamp":
                            temporal_features[key].append(None)
                        else:
                            temporal_features[key].append(None)

        return {"temporal_features": temporal_features}

    def _extract_content_features(self, data: Any) -> dict[str, Any]:
        """
        Extract content features from data.

        Args:
            data: Input data (posts, messages, stories, etc.)

        Returns:
            Dictionary of content features
        """
        content_features: dict[str, list[Any]] = {
            "text_length": [],
            "word_count": [],
            "has_media": [],
            "media_type": [],
            "media_count": [],
            "hashtag_count": [],
            "mention_count": [],
            "emoji_count": [],
            "url_count": [],
            "sentiment_polarity": [],
            "has_question": [],
            "has_exclamation": [],
            "language_detected": [],
            "readability_score": [],
        }

        if isinstance(data, list):
            for item in data:
                # Extract text content
                text = ""
                if hasattr(item, "caption") and item.caption:
                    text = item.caption
                elif hasattr(item, "text") and item.text:
                    text = item.text
                elif hasattr(item, "content") and item.content:
                    text = item.content

                # Text analysis
                content_features["text_length"].append(len(text))
                content_features["word_count"].append(len(text.split()) if text else 0)

                # Hashtags and mentions
                hashtags = extract_hashtags(text) if text else []
                mentions = extract_mentions(text) if text else []
                content_features["hashtag_count"].append(len(hashtags))
                content_features["mention_count"].append(len(mentions))

                # Emojis (simple count of characters in emoji range)
                emoji_count = len(
                    re.findall(
                        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270]",
                        text,
                    )
                )
                content_features["emoji_count"].append(emoji_count)

                # URLs
                url_count = len(
                    re.findall(
                        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                        text,
                    )
                )
                content_features["url_count"].append(url_count)

                # Question and exclamation marks
                content_features["has_question"].append("?" in text)
                content_features["has_exclamation"].append("!" in text)

                # Media analysis
                has_media = False
                media_type = "none"
                media_count = 0

                if hasattr(item, "media") and item.media:
                    if isinstance(item.media, list):
                        media_count = len(item.media)
                        has_media = media_count > 0
                        if has_media:
                            # Determine dominant media type
                            types = [
                                (
                                    m.media_type.value
                                    if hasattr(m, "media_type")
                                    else "unknown"
                                )
                                for m in item.media
                            ]
                            media_type = (
                                max(set(types), key=types.count) if types else "unknown"
                            )
                    else:
                        has_media = True
                        media_count = 1
                        media_type = (
                            item.media.media_type.value
                            if hasattr(item.media, "media_type")
                            else "unknown"
                        )

                content_features["has_media"].append(has_media)
                content_features["media_type"].append(media_type)
                content_features["media_count"].append(media_count)

                # Simple sentiment using TextBlob if available
                try:
                    from textblob import TextBlob

                    blob = TextBlob(text) if text else TextBlob("")
                    content_features["sentiment_polarity"].append(blob.sentiment.polarity)
                except ImportError:
                    content_features["sentiment_polarity"].append(0.0)

                # Language detection (simplified)
                lang = "unknown"
                if text:
                    # Simple heuristic based on common words
                    if any(
                        word in text.lower()
                        for word in ["the", "and", "is", "in", "to", "of", "a"]
                    ):
                        lang = "english"
                    elif any(
                        word in text.lower()
                        for word in ["el", "la", "y", "es", "en", "de", "un", "una"]
                    ):
                        lang = "spanish"
                content_features["language_detected"].append(lang)

                # Simple readability score (average word length)
                words = text.split() if text else []
                avg_word_length = (
                    sum(len(word) for word in words) / len(words) if words else 0
                )
                content_features["readability_score"].append(avg_word_length)

        return {"content_features": content_features}

    def _extract_user_features(self, data: Any) -> dict[str, Any]:
        """
        Extract user features from data.

        Args:
            data: Input data (posts, conversations, interactions)

        Returns:
            Dictionary of user features
        """
        user_features: dict[str, list[Any]] = {
            "activity_level": [],
            "response_rate": [],
            "engagement_history": [],
            "avg_likes_per_post": [],
            "avg_comments_per_post": [],
            "posting_frequency": [],
            "content_diversity": [],
            "interaction_pattern": [],
            "response_time_hours": [],
            "conversation_length": [],
            "emoji_usage_rate": [],
        }

        if isinstance(data, list):
            # Calculate user-level aggregations
            total_posts = len(data)
            total_likes = 0
            total_comments = 0
            media_types = []
            posting_times = []
            response_times = []
            emoji_counts = []

            for item in data:
                # Engagement metrics
                likes = 0
                comments = 0

                if hasattr(item, "likes_count"):
                    likes = item.likes_count or 0
                elif hasattr(item, "likes") and isinstance(item.likes, list):
                    likes = len(item.likes)

                if hasattr(item, "comments_count"):
                    comments = item.comments_count or 0
                elif hasattr(item, "comments") and isinstance(item.comments, list):
                    comments = len(item.comments)

                total_likes += likes
                total_comments += comments

                # Media diversity
                if hasattr(item, "media") and item.media:
                    if isinstance(item.media, list):
                        for media in item.media:
                            if hasattr(media, "media_type"):
                                media_types.append(media.media_type.value)
                    else:
                        if hasattr(item.media, "media_type"):
                            media_types.append(item.media.media_type.value)

                # Posting times
                if hasattr(item, "timestamp") and item.timestamp:
                    try:
                        if isinstance(item.timestamp, str):
                            dt = date_parser.parse(item.timestamp)
                        else:
                            dt = item.timestamp
                        posting_times.append(dt)
                    except (ValueError, TypeError, AttributeError):
                        pass

                # Text analysis for emojis
                text = ""
                if hasattr(item, "caption") and item.caption:
                    text = item.caption
                elif hasattr(item, "text") and item.text:
                    text = item.text

                emoji_count = len(
                    re.findall(
                        r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002700-\U000027BF\U0001F900-\U0001F9FF\U0001F018-\U0001F270]",
                        text,
                    )
                )
                emoji_counts.append(emoji_count)

                # Response times (for conversations)
                if hasattr(item, "messages") and item.messages:
                    messages = item.messages
                    for i in range(1, len(messages)):
                        try:
                            if hasattr(messages[i], "timestamp") and hasattr(
                                messages[i - 1], "timestamp"
                            ):
                                curr_time = (
                                    date_parser.parse(messages[i].timestamp)
                                    if isinstance(messages[i].timestamp, str)
                                    else messages[i].timestamp
                                )
                                prev_time = (
                                    date_parser.parse(messages[i - 1].timestamp)
                                    if isinstance(messages[i - 1].timestamp, str)
                                    else messages[i - 1].timestamp
                                )
                                diff_hours = (
                                    curr_time - prev_time
                                ).total_seconds() / 3600
                                response_times.append(diff_hours)
                        except (ValueError, TypeError, AttributeError):
                            pass

            # Calculate aggregated features for all items
            for i in range(total_posts):
                user_features["activity_level"].append(total_posts)
                user_features["avg_likes_per_post"].append(
                    total_likes / total_posts if total_posts > 0 else 0
                )
                user_features["avg_comments_per_post"].append(
                    total_comments / total_posts if total_posts > 0 else 0
                )

                # Posting frequency (posts per day)
                if posting_times and len(posting_times) > 1:
                    time_span = (max(posting_times) - min(posting_times)).days
                    frequency = total_posts / max(time_span, 1)
                    user_features["posting_frequency"].append(frequency)
                else:
                    user_features["posting_frequency"].append(0)

                # Content diversity (unique media types)
                unique_media_types = len(set(media_types)) if media_types else 0
                user_features["content_diversity"].append(unique_media_types)

                # Response rate (simplified as engagement rate)
                engagement_rate = (total_likes + total_comments) / max(total_posts, 1)
                user_features["response_rate"].append(engagement_rate)
                user_features["engagement_history"].append(engagement_rate)

                # Interaction pattern (active vs passive based on posting vs engagement)
                if total_posts > 0:
                    interaction_ratio = (total_likes + total_comments) / total_posts
                    pattern = "active" if interaction_ratio > 10 else "passive"
                else:
                    pattern = "unknown"
                user_features["interaction_pattern"].append(pattern)

                # Average response time
                avg_response_time = (
                    sum(response_times) / len(response_times) if response_times else 0
                )
                user_features["response_time_hours"].append(avg_response_time)

                # Conversation length (for conversation data)
                avg_conv_length = total_posts  # Simplified
                user_features["conversation_length"].append(avg_conv_length)

                # Emoji usage rate
                total_emojis = sum(emoji_counts)
                emoji_rate = total_emojis / max(total_posts, 1)
                user_features["emoji_usage_rate"].append(emoji_rate)

        return {"user_features": user_features}

    def _extract_network_features(self, data: Any) -> dict[str, Any]:
        """
        Extract network features from data.

        Args:
            data: Input data (posts, conversations, interactions)

        Returns:
            Dictionary of network features
        """
        network_features: dict[str, list[Any]] = {
            "centrality": [],
            "influence": [],
            "community": [],
            "degree_centrality": [],
            "betweenness_centrality": [],
            "closeness_centrality": [],
            "pagerank": [],
            "clustering_coefficient": [],
            "connection_count": [],
            "mutual_connections": [],
            "conversation_partners": [],
        }

        if isinstance(data, list):
            # Build a simple network graph from interactions
            user_interactions: dict[str, set[str]] = {}
            all_users = set()

            for item in data:
                # Extract user interactions from conversations
                if hasattr(item, "messages") and item.messages:
                    participants = set()
                    for message in item.messages:
                        if hasattr(message, "sender_name"):
                            participants.add(message.sender_name)

                    # Create edges between all participants
                    participants_list = list(participants)
                    for i, user1 in enumerate(participants_list):
                        all_users.add(user1)
                        if user1 not in user_interactions:
                            user_interactions[user1] = set()

                        for j, user2 in enumerate(participants_list):
                            if i != j:
                                user_interactions[user1].add(user2)
                                all_users.add(user2)

                # Extract interactions from posts (likes, comments)
                elif hasattr(item, "likes") or hasattr(item, "comments"):
                    item_owner = getattr(item, "user", "unknown_user")
                    all_users.add(item_owner)

                    if item_owner not in user_interactions:
                        user_interactions[item_owner] = set()

                    # Add likes as interactions
                    if hasattr(item, "likes") and isinstance(item.likes, list):
                        for like in item.likes:
                            liker = getattr(
                                like, "username", getattr(like, "user", "unknown")
                            )
                            all_users.add(liker)
                            user_interactions[item_owner].add(liker)

                            if liker not in user_interactions:
                                user_interactions[liker] = set()
                            user_interactions[liker].add(item_owner)

                    # Add comments as interactions
                    if hasattr(item, "comments") and isinstance(item.comments, list):
                        for comment in item.comments:
                            commenter = getattr(
                                comment, "username", getattr(comment, "user", "unknown")
                            )
                            all_users.add(commenter)
                            user_interactions[item_owner].add(commenter)

                            if commenter not in user_interactions:
                                user_interactions[commenter] = set()
                            user_interactions[commenter].add(item_owner)

            # Calculate network metrics for each item
            for i, item in enumerate(data):
                # Get the main user for this item
                main_user = getattr(item, "user", "unknown_user")
                if hasattr(item, "messages") and item.messages and item.messages:
                    # For conversations, use the first sender
                    main_user = getattr(item.messages[0], "sender_name", "unknown_user")

                # Calculate simple network metrics
                connections = user_interactions.get(main_user, set())
                connection_count = len(connections)

                # Degree centrality (normalized by total possible connections)
                total_users = len(all_users)
                degree_centrality = connection_count / max(total_users - 1, 1)

                # Simple influence metric (number of connections)
                influence = connection_count

                # Clustering coefficient (simplified)
                if connection_count > 1:
                    # Count how many of user's connections are connected to each other
                    connected_pairs = 0
                    total_pairs = 0
                    connections_list = list(connections)

                    for j, conn1 in enumerate(connections_list):
                        for k, conn2 in enumerate(connections_list):
                            if j < k:
                                total_pairs += 1
                                if conn2 in user_interactions.get(conn1, set()):
                                    connected_pairs += 1

                    clustering_coeff = connected_pairs / max(total_pairs, 1)
                else:
                    clustering_coeff = 0

                # Mutual connections (simplified as average connection count of connections)
                if connections:
                    mutual_count = sum(
                        len(user_interactions.get(conn, set())) for conn in connections
                    ) / len(connections)
                else:
                    mutual_count = 0

                # Conversation partners (unique people interacted with)
                conv_partners = len(connections)

                # PageRank (simplified - based on connection quality)
                pagerank_score = influence / max(total_users, 1)

                # Community detection (simplified - group by connection density)
                if connection_count > 5:
                    community = "high_connected"
                elif connection_count > 2:
                    community = "medium_connected"
                elif connection_count > 0:
                    community = "low_connected"
                else:
                    community = "isolated"

                # Betweenness and closeness centrality (simplified approximations)
                betweenness = (
                    influence * clustering_coeff
                )  # Users who connect different groups
                closeness = 1 / (1 + connection_count) if connection_count > 0 else 0

                # Add features for this item
                network_features["centrality"].append(degree_centrality)
                network_features["influence"].append(influence)
                network_features["community"].append(community)
                network_features["degree_centrality"].append(degree_centrality)
                network_features["betweenness_centrality"].append(betweenness)
                network_features["closeness_centrality"].append(closeness)
                network_features["pagerank"].append(pagerank_score)
                network_features["clustering_coefficient"].append(clustering_coeff)
                network_features["connection_count"].append(connection_count)
                network_features["mutual_connections"].append(mutual_count)
                network_features["conversation_partners"].append(conv_partners)

        return {"network_features": network_features}

    def _extract_derived_features(self, features: dict[str, Any]) -> dict[str, Any]:
        """
        Extract derived features from existing features.

        Args:
            features: Existing features dictionary

        Returns:
            Dictionary of derived features
        """
        derived_features: dict[str, list[Any]] = {
            "engagement_score": [],
            "content_quality": [],
            "user_segment": [],
            "virality_potential": [],
            "interaction_quality": [],
            "optimal_posting_time": [],
            "content_category": [],
            "user_type": [],
            "influence_level": [],
            "community_role": [],
        }

        # Extract individual feature groups
        temporal_features = features.get("temporal_features", {})
        content_features = features.get("content_features", {})
        user_features = features.get("user_features", {})
        network_features = features.get("network_features", {})

        # Determine the number of items
        n_items = 0
        for feature_group in [
            temporal_features,
            content_features,
            user_features,
            network_features,
        ]:
            for feature_list in feature_group.values():
                if isinstance(feature_list, list) and len(feature_list) > n_items:
                    n_items = len(feature_list)
                    break

        for i in range(n_items):
            # Engagement Score (combination of likes, comments, and content quality)
            avg_likes = self._get_feature_value(user_features, "avg_likes_per_post", i, 0)
            avg_comments = self._get_feature_value(
                user_features, "avg_comments_per_post", i, 0
            )
            text_length = self._get_feature_value(content_features, "text_length", i, 0)
            has_media = self._get_feature_value(content_features, "has_media", i, False)

            engagement_score = (avg_likes * 0.6 + avg_comments * 1.5) * (
                1.2 if has_media else 1.0
            )
            if text_length > 100:  # Longer content bonus
                engagement_score *= 1.1
            derived_features["engagement_score"].append(engagement_score)

            # Content Quality (based on text features and engagement)
            word_count = self._get_feature_value(content_features, "word_count", i, 0)
            hashtag_count = self._get_feature_value(
                content_features, "hashtag_count", i, 0
            )
            emoji_count = self._get_feature_value(content_features, "emoji_count", i, 0)
            sentiment = self._get_feature_value(
                content_features, "sentiment_polarity", i, 0
            )

            quality_score = 0
            if 10 <= word_count <= 150:  # Optimal length
                quality_score += 2
            if 1 <= hashtag_count <= 5:  # Optimal hashtag count
                quality_score += 1
            if emoji_count > 0:  # Has emojis
                quality_score += 0.5
            if abs(sentiment) > 0.1:  # Clear sentiment
                quality_score += 1

            derived_features["content_quality"].append(quality_score)

            # User Segment (based on activity and engagement patterns)
            activity_level = self._get_feature_value(
                user_features, "activity_level", i, 0
            )
            posting_frequency = self._get_feature_value(
                user_features, "posting_frequency", i, 0
            )
            response_rate = self._get_feature_value(user_features, "response_rate", i, 0)

            if activity_level > 100 and posting_frequency > 1:
                user_segment = "power_user"
            elif activity_level > 50 and response_rate > 10:
                user_segment = "active_user"
            elif activity_level > 10:
                user_segment = "regular_user"
            else:
                user_segment = "casual_user"

            derived_features["user_segment"].append(user_segment)

            # Virality Potential (combination of content and network factors)
            connection_count = self._get_feature_value(
                network_features, "connection_count", i, 0
            )
            influence = self._get_feature_value(network_features, "influence", i, 0)
            hour_of_day = self._get_feature_value(temporal_features, "hour_of_day", i, 12)
            is_weekend = self._get_feature_value(
                temporal_features, "is_weekend", i, False
            )

            virality_score = (
                engagement_score * 0.4 + quality_score * 0.3 + influence * 0.2
            )

            # Time bonus (peak hours)
            if hour_of_day in [9, 10, 11, 19, 20, 21]:  # Peak engagement hours
                virality_score *= 1.2
            if is_weekend:  # Weekend bonus
                virality_score *= 1.1

            derived_features["virality_potential"].append(virality_score)

            # Interaction Quality (depth vs breadth of interactions)
            emoji_usage = self._get_feature_value(user_features, "emoji_usage_rate", i, 0)
            response_time = self._get_feature_value(
                user_features, "response_time_hours", i, 24
            )

            interaction_quality = 0
            if avg_comments > avg_likes * 0.1:  # Good comment ratio
                interaction_quality += 2
            if emoji_usage > 1:  # Uses emojis
                interaction_quality += 1.0
            if response_time < 2:  # Quick responder
                interaction_quality += 1

            derived_features["interaction_quality"].append(interaction_quality)

            # Optimal Posting Time (based on historical patterns)
            if hour_of_day in [8, 9, 10]:
                optimal_time = "morning"
            elif hour_of_day in [12, 13, 14]:
                optimal_time = "afternoon"
            elif hour_of_day in [19, 20, 21]:
                optimal_time = "evening"
            else:
                optimal_time = "off_peak"

            derived_features["optimal_posting_time"].append(optimal_time)

            # Content Category (based on content characteristics)
            media_type = self._get_feature_value(
                content_features, "media_type", i, "none"
            )
            has_question = self._get_feature_value(
                content_features, "has_question", i, False
            )
            has_exclamation = self._get_feature_value(
                content_features, "has_exclamation", i, False
            )

            if media_type == "video":
                content_category = "video_content"
            elif media_type == "photo":
                content_category = "photo_content"
            elif has_question:
                content_category = "interactive_content"
            elif has_exclamation:
                content_category = "expressive_content"
            else:
                content_category = "text_content"

            derived_features["content_category"].append(content_category)

            # User Type (based on behavior patterns)
            content_diversity = self._get_feature_value(
                user_features, "content_diversity", i, 0
            )
            interaction_pattern = self._get_feature_value(
                user_features, "interaction_pattern", i, "unknown"
            )

            if content_diversity > 2 and interaction_pattern == "active":
                user_type = "content_creator"
            elif response_rate > 20:
                user_type = "community_builder"
            elif connection_count > 50:
                user_type = "social_connector"
            else:
                user_type = "content_consumer"

            derived_features["user_type"].append(user_type)

            # Influence Level (normalized influence score)
            if influence > 100:
                influence_level = "high"
            elif influence > 20:
                influence_level = "medium"
            elif influence > 5:
                influence_level = "low"
            else:
                influence_level = "minimal"

            derived_features["influence_level"].append(influence_level)

            # Community Role (based on network position)
            centrality = self._get_feature_value(network_features, "centrality", i, 0)
            clustering_coeff = self._get_feature_value(
                network_features, "clustering_coefficient", i, 0
            )

            if centrality > 0.1 and clustering_coeff > 0.5:
                community_role = "hub"
            elif centrality > 0.05:
                community_role = "connector"
            elif clustering_coeff > 0.7:
                community_role = "cluster_member"
            else:
                community_role = "peripheral"

            derived_features["community_role"].append(community_role)

        return {"derived_features": derived_features}

    def _get_feature_value(
        self, feature_group: dict, feature_name: str, index: int, default: Any
    ) -> Any:
        """
        Safely get a feature value with fallback to default.

        Args:
            feature_group: Dictionary containing feature lists
            feature_name: Name of the feature
            index: Index to retrieve
            default: Default value if feature is missing or index is out of bounds

        Returns:
            Feature value or default
        """
        if feature_name not in feature_group:
            return default

        feature_list = feature_group[feature_name]
        if not isinstance(feature_list, list) or index >= len(feature_list):
            return default

        value = feature_list[index]
        return value if value is not None else default
