"""
Image preprocessing utilities for ML module.

This module provides tools for image preprocessing, including resizing,
normalization, and feature extraction.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

# Optional imports for image processing
try:
    import numpy as np
    from PIL import Image

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class ImagePreprocessor:
    """
    Image preprocessing class for computer vision tasks.

    This class provides methods for transforming image data
    for use in machine learning models.

    Attributes:
        target_size: Target size for resized images (width, height)
        normalize: Whether to normalize pixel values
        grayscale: Whether to convert images to grayscale
        data_format: Format of image data ('channels_last' or 'channels_first')
    """

    def __init__(
        self,
        target_size: tuple[int, int] = (224, 224),
        normalize: bool = True,
        grayscale: bool = False,
        data_format: str = "channels_last",
    ):
        """
        Initialize the image preprocessor.

        Args:
            target_size: Target size for resized images (width, height)
            normalize: Whether to normalize pixel values
            grayscale: Whether to convert images to grayscale
            data_format: Format of image data ('channels_last' or 'channels_first')
        """
        self.target_size = target_size
        self.normalize = normalize
        self.grayscale = grayscale
        self.data_format = data_format
        self.logger = logging.getLogger(__name__)

        # Check for required dependencies
        if not HAS_PILLOW:
            self.logger.warning(
                "PIL/Pillow not found. Image preprocessing will not work. "
                "Install with 'pip install pillow'."
            )

    def fit(self, X: Any, y: Optional[Any] = None) -> "ImagePreprocessor":
        """
        Fit the preprocessor on training data (no-op for this preprocessor).

        Args:
            X: Training data
            y: Target values (ignored)

        Returns:
            self: The fitted preprocessor
        """
        return self

    def transform(
        self, X: Union[str, list[str], np.ndarray, list[np.ndarray]]
    ) -> np.ndarray:
        """
        Transform image data.

        Args:
            X: Image data (file paths, PIL images, or numpy arrays)

        Returns:
            Transformed image data as numpy arrays
        """
        if not HAS_PILLOW:
            self.logger.error("Cannot transform images: PIL/Pillow not installed.")
            # Return empty array or raise exception
            if isinstance(X, list):
                return np.array([])
            else:
                return np.array([])

        # Handle different input types
        if isinstance(X, str):
            return self._process_single_image(X)
        elif isinstance(X, list):
            return np.array([self._process_single_image(img) for img in X])
        elif isinstance(X, np.ndarray):
            if X.ndim == 3:  # Single image
                return self._preprocess_array(X)
            elif X.ndim == 4:  # Batch of images
                return np.array([self._preprocess_array(img) for img in X])
            else:
                raise ValueError(f"Invalid numpy array shape: {X.shape}")
        else:
            raise ValueError(f"Unsupported image data type: {type(X)}")

    def fit_transform(self, X: Any, y: Optional[Any] = None) -> np.ndarray:
        """
        Fit and transform image data.

        Args:
            X: Image data
            y: Target values (ignored)

        Returns:
            Transformed image data
        """
        return self.fit(X, y).transform(X)

    def _process_single_image(self, img_path: str) -> np.ndarray:
        """
        Process a single image from file path.

        Args:
            img_path: Path to image file

        Returns:
            Processed image as numpy array
        """
        try:
            # Load image
            with Image.open(img_path) as img:
                # Convert to grayscale if requested
                if self.grayscale:
                    img = img.convert("L")

                # Resize image
                img = img.resize(self.target_size, Image.LANCZOS)

                # Convert to numpy array
                img_array = np.array(img)

                # Add channel dimension for grayscale
                if self.grayscale:
                    img_array = img_array[..., np.newaxis]

                # Preprocess array (normalize, etc.)
                return self._preprocess_array(img_array)

        except Exception as e:
            self.logger.error(f"Error processing image {img_path}: {str(e)}")
            # Return empty array with correct shape
            if self.grayscale:
                return np.zeros((*self.target_size, 1))
            else:
                return np.zeros((*self.target_size, 3))

    def _preprocess_array(self, img_array: np.ndarray) -> np.ndarray:
        """
        Preprocess image array.

        Args:
            img_array: Image as numpy array

        Returns:
            Preprocessed image array
        """
        # Normalize if requested
        if self.normalize:
            img_array = img_array.astype(np.float32) / 255.0

        # Adjust data format if needed
        if self.data_format == "channels_first":
            if img_array.ndim == 3:
                img_array = np.transpose(img_array, (2, 0, 1))

        return img_array
