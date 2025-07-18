"""Image processing utilities for Instagram media."""

import base64
import io
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


def get_image_thumbnail(
    image_path: Path, size: tuple[int, int] = (300, 300)
) -> Optional[str]:
    """Generate base64 encoded thumbnail for image display.

    Args:
        image_path: Path to the image file
        size: Thumbnail size (width, height)

    Returns:
        Base64 encoded image data URL or None if processing fails
    """
    try:
        if not image_path.exists():
            return None

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)

            # Encode to base64
            image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{image_data}"

    except Exception:
        return None


def get_image_info(image_path: Path) -> dict:
    """Get basic information about an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with image information
    """
    try:
        if not image_path.exists():
            return {}

        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "format": img.format,
                "size_mb": round(image_path.stat().st_size / (1024 * 1024), 2),
            }
    except Exception:
        return {}


def is_image_file(file_path: Path) -> bool:
    """Check if a file is an image.

    Args:
        file_path: Path to check

    Returns:
        True if file appears to be an image
    """
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    return file_path.suffix.lower() in image_extensions


def resolve_media_path(media_uri: str, data_root: Path) -> Optional[Path]:
    """Resolve media URI to actual file path.

    Args:
        media_uri: URI from Instagram data
        data_root: Root directory of Instagram export

    Returns:
        Resolved file path or None if not found
    """
    if not media_uri:
        return None

    # Extract filename from URI
    filename = Path(media_uri).name

    # Common locations where Instagram stores media
    search_paths = [
        # Direct path as specified
        data_root / media_uri,
        # In media directory
        data_root / "media" / filename,
        data_root / "media" / "posts" / filename,
        data_root / "media" / "stories" / filename,
        # In subdirectories by date (common Instagram pattern)
        data_root / "media" / "stories" / "*" / filename,
        data_root / "media" / "posts" / "*" / filename,
        # In your_instagram_activity
        data_root / "your_instagram_activity" / "media" / filename,
        data_root / "your_instagram_activity" / media_uri,
    ]

    # Check direct paths first
    for path in search_paths[:6]:  # Skip glob patterns initially
        if path.exists() and is_image_file(path):
            return path

    # If not found, try searching in date subdirectories
    from glob import glob

    # Search in stories subdirectories by year/month
    story_pattern = str(data_root / "media" / "stories" / "*" / filename)
    matches = glob(story_pattern)
    for match in matches:
        match_path = Path(match)
        if match_path.exists() and is_image_file(match_path):
            return match_path

    # Search in posts subdirectories
    posts_pattern = str(data_root / "media" / "posts" / "*" / filename)
    matches = glob(posts_pattern)
    for match in matches:
        match_path = Path(match)
        if match_path.exists() and is_image_file(match_path):
            return match_path

    # Search anywhere in the media directory
    all_media_pattern = str(data_root / "**" / filename)
    matches = glob(all_media_pattern, recursive=True)
    for match in matches:
        match_path = Path(match)
        if match_path.exists() and is_image_file(match_path):
            return match_path

    return None
