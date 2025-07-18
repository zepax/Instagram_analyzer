"""
Text preprocessing utilities for ML module.

This module provides tools for text preprocessing, including tokenization,
stemming, lemmatization, and other NLP-related operations.
"""

import logging
import string
from typing import Any, Optional, Union

import nltk

logger = logging.getLogger(__name__)
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download required NLTK resources
try:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
except (OSError, ConnectionError) as e:
    # Fail with logging, will fallback to handle in class methods
    logging.warning("Failed to download NLTK resources: %s", e)


class TextPreprocessor:
    """Text preprocessing class for NLP tasks.

    This class provides methods for cleaning, tokenizing, and transforming text
    data for use in machine learning models.

    Attributes:
        language: Language for stopwords and tokenization
        remove_stopwords: Whether to remove stopwords
        remove_punctuation: Whether to remove punctuation
        lowercase: Whether to convert text to lowercase
        stemming: Whether to apply stemming
        lemmatization: Whether to apply lemmatization
    """

    def __init__(
        self,
        language: str = "english",
        remove_stopwords: bool = True,
        remove_punctuation: bool = True,
        lowercase: bool = True,
        stemming: bool = False,
        lemmatization: bool = True,
    ):
        """
        Initialize the text preprocessor.

        Args:
            language: Language for stopwords and tokenization
            remove_stopwords: Whether to remove stopwords
            remove_punctuation: Whether to remove punctuation
            lowercase: Whether to convert text to lowercase
            stemming: Whether to apply stemming
            lemmatization: Whether to apply lemmatization
        """
        self.language = language
        self.remove_stopwords = remove_stopwords
        self.remove_punctuation = remove_punctuation
        self.lowercase = lowercase
        self.stemming = stemming
        self.lemmatization = lemmatization

        # Initialize components
        try:
            self.stop_words = (
                set(stopwords.words(language)) if remove_stopwords else set()
            )
        except (LookupError, ImportError, OSError) as e:
            logger.warning(f"Could not load stopwords for {language}: {e}")
            self.stop_words = set()

        self.stemmer = PorterStemmer() if stemming else None
        self.lemmatizer = WordNetLemmatizer() if lemmatization else None

    def fit(self, X: Any, y: Optional[Any] = None) -> "TextPreprocessor":
        """
        Fit the preprocessor on training data (no-op for this preprocessor).

        Args:
            X: Training data
            y: Target values (ignored)

        Returns:
            self: The fitted preprocessor
        """
        return self

    def transform(self, X: Union[str, list[str]]) -> Union[str, list[str]]:
        """
        Transform text data.

        Args:
            X: Text data to transform (string or list of strings)

        Returns:
            Transformed text data
        """
        if isinstance(X, str):
            return self._process_text(X)
        elif isinstance(X, list):
            return [self._process_text(text) for text in X]
        else:
            raise ValueError(f"Input must be string or list of strings, got {type(X)}")

    def fit_transform(
        self, X: Union[str, list[str]], y: Optional[Any] = None
    ) -> Union[str, list[str]]:
        """
        Fit and transform text data.

        Args:
            X: Text data to transform
            y: Target values (ignored)

        Returns:
            Transformed text data
        """
        return self.fit(X, y).transform(X)

    def _process_text(self, text: str) -> str:
        """
        Process a single text string.

        Args:
            text: Text to process

        Returns:
            Processed text
        """
        if not isinstance(text, str):
            return ""

        # Lowercase if requested
        if self.lowercase:
            text = text.lower()

        # Tokenize the text
        tokens = word_tokenize(text)

        # Remove stopwords if requested
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]

        # Remove punctuation if requested
        if self.remove_punctuation:
            tokens = [token for token in tokens if token not in string.punctuation]

        # Apply stemming if requested
        if self.stemming and self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]

        # Apply lemmatization if requested
        if self.lemmatization and self.lemmatizer:
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

        # Join tokens back into a string
        return " ".join(tokens)

    def get_feature_names(self) -> list[str]:
        """
        Get feature names (compatibility with scikit-learn).

        Returns:
            Empty list (not applicable for this preprocessor)
        """
        return []
