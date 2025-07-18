"""
Sentiment analysis model for Instagram Data Mining Platform.

This module provides sentiment analysis capabilities for text data,
using various NLP techniques and pre-trained models.
"""

import logging
from typing import Any, Dict, List, Optional, Union

import spacy
from textblob import TextBlob

from instagram_analyzer.ml.models.base import MLModel


class SentimentAnalyzer(MLModel):
    """
    Sentiment analysis model for text data.

    This model analyzes sentiment in text data using various NLP techniques,
    including pre-trained models and rule-based approaches.

    Attributes:
        model_type: Type of sentiment model to use
        language: Language of the text data
        include_emotions: Whether to include emotion classification
    """

    def __init__(
        self,
        model_type: str = "default",
        language: str = "english",
        include_emotions: bool = False,
        **kwargs,
    ):
        """
        Initialize the sentiment analyzer.

        Args:
            model_type: Type of model to use ('default', 'transformer', etc.)
            language: Language of the text data
            include_emotions: Whether to include emotion classification
            **kwargs: Additional parameters for the model
        """
        super().__init__(
            model_type="sentiment",
            model_name=f"sentiment_{model_type}",
            model_parameters={
                "language": language,
                "include_emotions": include_emotions,
                **kwargs,
            },
        )

        self.model_impl = model_type
        self.language = language
        self.include_emotions = include_emotions
        self.logger = logging.getLogger(__name__)

        # Initialize model based on type
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize the appropriate sentiment model based on configuration."""
        self.logger.info(f"Initializing sentiment model: {self.model_impl}")

        if self.model_impl == "spacy":
            # Initialize spaCy model
            try:
                # Try to load Spanish model first, then English
                model_names = ["es_core_news_sm", "en_core_web_sm"]
                self._spacy_nlp = None

                for model_name in model_names:
                    try:
                        self._spacy_nlp = spacy.load(model_name)
                        self.logger.info(f"spaCy model {model_name} loaded successfully")
                        break
                    except OSError:
                        continue

                if self._spacy_nlp is None:
                    # Fallback to basic model
                    self._spacy_nlp = spacy.blank(
                        "es" if self.language == "spanish" else "en"
                    )
                    self.logger.warning("Using blank spaCy model - limited functionality")

                self._model = "spacy"

            except Exception as e:
                self.logger.warning(
                    f"Error initializing spaCy: {str(e)}. Falling back to TextBlob"
                )
                self._model = None
                self._spacy_nlp = None

        elif self.model_impl == "transformer":
            # Import and initialize transformer model
            try:
                from transformers import pipeline

                self._model = pipeline("sentiment-analysis")
                self.logger.info("Transformer model initialized successfully")
            except ImportError:
                self.logger.warning(
                    "Transformers library not found, falling back to TextBlob"
                )
                self._model = None
        else:
            # Default to TextBlob
            self._model = None
            self._spacy_nlp = None
            self.logger.info("Using TextBlob for sentiment analysis")

    def fit(self, X: Any, y: Optional[Any] = None) -> "SentimentAnalyzer":
        """
        Fit the sentiment model (no-op for pre-trained models).

        Args:
            X: Training data
            y: Target values (ignored for pre-trained models)

        Returns:
            self: The fitted model
        """
        # Most sentiment models are pre-trained, so fit is a no-op
        return self

    def predict(
        self, X: Union[str, list[str]]
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """
        Predict sentiment for text data.

        Args:
            X: Text data (string or list of strings)

        Returns:
            Sentiment predictions with polarity, subjectivity, and optionally emotions
        """
        if isinstance(X, str):
            return self._analyze_text(X)
        elif isinstance(X, list):
            return [self._analyze_text(text) for text in X]
        else:
            raise ValueError(f"Input must be string or list of strings, got {type(X)}")

    def _analyze_text(self, text: str) -> dict[str, Any]:
        """
        Analyze sentiment in a single text.

        Args:
            text: Text to analyze

        Returns:
            Sentiment analysis results
        """
        if not isinstance(text, str) or not text.strip():
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "emotion": None if self.include_emotions else None,
                "confidence": 0.0,
                "entities": [],
                "language": None,
            }

        if self.model_impl == "spacy" and self._spacy_nlp is not None:
            # Use spaCy model for advanced analysis
            try:
                doc = self._spacy_nlp(text)

                # Extract entities
                entities = [
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start,
                        "end": ent.end,
                    }
                    for ent in doc.ents
                ]

                # Language detection (if available)
                detected_lang = getattr(doc, "lang_", None)

                # Use TextBlob for sentiment (spaCy doesn't have built-in sentiment)
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                subjectivity = blob.sentiment.subjectivity

                # Enhanced emotion detection using spaCy tokens
                emotion = self._get_emotion_spacy(doc) if self.include_emotions else None

                return {
                    "polarity": polarity,
                    "subjectivity": subjectivity,
                    "emotion": emotion,
                    "confidence": abs(polarity) * 0.7
                    + 0.3,  # Higher confidence with spaCy
                    "entities": entities,
                    "language": detected_lang,
                    "tokens": len(doc),
                    "sentences": len(list(doc.sents)),
                }

            except Exception as e:
                self.logger.warning(
                    f"Error in spaCy analysis: {str(e)}. Falling back to TextBlob."
                )

        elif self.model_impl == "transformer" and self._model is not None:
            # Use transformer model
            try:
                result = self._model(text)[0]

                # Map to common format
                label = result["label"].lower()
                score = result["score"]

                polarity = 0.0
                if "positive" in label:
                    polarity = score
                elif "negative" in label:
                    polarity = -score

                return {
                    "polarity": polarity,
                    "subjectivity": 0.5,  # Transformers don't provide subjectivity
                    "emotion": label if self.include_emotions else None,
                    "confidence": score,
                    "entities": [],
                    "language": None,
                }
            except Exception as e:
                self.logger.warning(
                    f"Error in transformer model: {str(e)}. Falling back to TextBlob."
                )

        # Default to TextBlob
        try:
            blob = TextBlob(text)

            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
                "emotion": self._get_emotion(text) if self.include_emotions else None,
                "confidence": abs(blob.sentiment.polarity) * 0.5 + 0.5,
                "entities": [],
                "language": None,
            }
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "emotion": None,
                "confidence": 0.0,
                "entities": [],
                "language": None,
            }

    def _get_emotion(self, text: str) -> Optional[str]:
        """
        Get emotion from text (simple rule-based implementation).

        Args:
            text: Text to analyze

        Returns:
            Detected emotion or None
        """
        # Simple rule-based emotion detection
        text = text.lower()

        emotion_keywords = {
            "joy": [
                "happy",
                "joy",
                "delighted",
                "glad",
                "pleased",
                "😊",
                "😄",
                "🙂",
                "love",
            ],
            "sadness": ["sad", "unhappy", "depressed", "miserable", "😢", "😭", "😞"],
            "anger": ["angry", "mad", "furious", "rage", "😠", "😡", "🤬"],
            "fear": ["afraid", "scared", "frightened", "terrified", "😨", "😱"],
            "surprise": ["surprised", "amazed", "astonished", "😲", "😯", "😮"],
            "disgust": ["disgusted", "revolted", "🤢", "🤮"],
        }

        # Count occurrences of emotion keywords
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            emotion_scores[emotion] = score

        # Return emotion with highest score, or None if no emotions detected
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return None

        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    def _get_emotion_spacy(self, doc) -> Optional[str]:
        """
        Get emotion from spaCy doc using advanced NLP features.

        Args:
            doc: spaCy Doc object

        Returns:
            Detected emotion or None
        """
        # Enhanced emotion detection using lemmatized tokens and POS tags
        emotion_keywords = {
            "joy": {
                "lemmas": [
                    "feliz",
                    "alegre",
                    "contento",
                    "emocionado",
                    "happy",
                    "joy",
                    "delight",
                    "pleased",
                    "love",
                ],
                "emojis": ["😊", "😄", "🙂", "❤️", "💕", "🥰", "😍"],
                "pos_boost": ["ADJ", "NOUN"],  # Boost if these POS tags
            },
            "sadness": {
                "lemmas": [
                    "triste",
                    "deprimido",
                    "sad",
                    "unhappy",
                    "depressed",
                    "miserable",
                ],
                "emojis": ["😢", "😭", "😞", "💔", "😔"],
                "pos_boost": ["ADJ", "VERB"],
            },
            "anger": {
                "lemmas": [
                    "enojado",
                    "furioso",
                    "molesto",
                    "angry",
                    "mad",
                    "furious",
                    "rage",
                ],
                "emojis": ["😠", "😡", "🤬", "💢"],
                "pos_boost": ["ADJ", "VERB"],
            },
            "fear": {
                "lemmas": [
                    "asustado",
                    "temeroso",
                    "afraid",
                    "scared",
                    "frightened",
                    "terrified",
                ],
                "emojis": ["😨", "😱", "😰"],
                "pos_boost": ["ADJ", "VERB"],
            },
            "surprise": {
                "lemmas": [
                    "sorprendido",
                    "asombrado",
                    "surprised",
                    "amazed",
                    "astonished",
                ],
                "emojis": ["😲", "😯", "😮", "🤯"],
                "pos_boost": ["ADJ", "VERB"],
            },
            "disgust": {
                "lemmas": ["asqueado", "disgusted", "revolted"],
                "emojis": ["🤢", "🤮", "😷"],
                "pos_boost": ["ADJ", "VERB"],
            },
        }

        emotion_scores = {}
        text_lower = doc.text.lower()

        for emotion, keywords in emotion_keywords.items():
            score = 0

            # Check lemmatized tokens
            for token in doc:
                if token.lemma_.lower() in keywords["lemmas"]:
                    score += 2  # Base score for lemma match
                    # Boost score based on POS tag
                    if token.pos_ in keywords.get("pos_boost", []):
                        score += 1

            # Check emojis in original text
            for emoji in keywords["emojis"]:
                score += text_lower.count(emoji) * 3  # Higher weight for emojis

            emotion_scores[emotion] = score

        # Return emotion with highest score, or None if no emotions detected
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return None

        return max(emotion_scores.items(), key=lambda x: x[1])[0]

    def analyze_conversations(
        self, conversations: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Analyze sentiment in conversation data.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            List of conversations with sentiment analysis results
        """
        results = []

        for conversation in conversations:
            # Extract text from conversation
            if "messages" in conversation:
                messages = conversation["messages"]
                message_sentiments = [
                    self._analyze_text(msg.get("text", "")) for msg in messages
                ]

                # Calculate conversation-level sentiment
                if message_sentiments:
                    avg_polarity = sum(s["polarity"] for s in message_sentiments) / len(
                        message_sentiments
                    )
                    avg_subjectivity = sum(
                        s["subjectivity"] for s in message_sentiments
                    ) / len(message_sentiments)

                    # Count emotions
                    emotions = [s["emotion"] for s in message_sentiments if s["emotion"]]
                    dominant_emotion = (
                        max(set(emotions), key=emotions.count) if emotions else None
                    )

                    conversation_sentiment = {
                        "polarity": avg_polarity,
                        "subjectivity": avg_subjectivity,
                        "dominant_emotion": dominant_emotion,
                        "message_sentiments": message_sentiments,
                    }
                else:
                    conversation_sentiment = {
                        "polarity": 0.0,
                        "subjectivity": 0.0,
                        "dominant_emotion": None,
                        "message_sentiments": [],
                    }

                # Add sentiment to conversation
                conversation_with_sentiment = {
                    **conversation,
                    "sentiment": conversation_sentiment,
                }
                results.append(conversation_with_sentiment)
            else:
                # If no messages, just pass through the conversation
                results.append(conversation)

        return results
