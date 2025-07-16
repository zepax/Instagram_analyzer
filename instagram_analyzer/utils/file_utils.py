"""File utility functions."""

import json
import os
from pathlib import Path
from typing import Any, Optional, Dict
from glob import glob

from .retry_utils import safe_json_load, safe_file_operation


def validate_path(path: Path) -> bool:
    """Validate if path exists and is accessible.

    Args:
        path: Path to validate

    Returns:
        True if path is valid and accessible
    """
    try:
        if not (path.exists() and path.is_dir()):
            return False

        mode = path.stat().st_mode
        has_read = bool(mode & 0o400)
        has_execute = bool(mode & 0o100)
        return has_read and has_execute
    except Exception:
        return False


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes, 0 if file doesn't exist
    """
    try:
        return file_path.stat().st_size
    except Exception:
        return 0


@safe_json_load
def safe_json_load(file_path: Path) -> Optional[Dict[str, Any]]:
    """Safely load JSON file with error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data or None if loading fails
    """
    try:
        if not file_path.exists() or file_path.stat().st_size == 0:
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                return json.load(f)
        except Exception:
            return None
    except Exception:
        return None


def count_files_in_directory(directory: Path, pattern: str = "*") -> int:
    """Count files in directory matching pattern.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match files

    Returns:
        Number of matching files
    """
    try:
        return len(list(directory.glob(pattern)))
    except Exception:
        return 0


def get_directory_size(directory: Path) -> int:
    """Calculate total size of directory and all subdirectories.

    Args:
        directory: Directory to calculate size for

    Returns:
        Total size in bytes
    """
    total_size = 0
    try:
        for path in directory.rglob("*"):
            if path.is_file():
                total_size += path.stat().st_size
    except Exception:
        pass
    return total_size


def ensure_directory(directory: Path) -> bool:
    """Ensure directory exists, create if it doesn't.

    Args:
        directory: Directory path to ensure exists

    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


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
        # In your_instagram_activity
        data_root / "your_instagram_activity" / "media" / filename,
        data_root / "your_instagram_activity" / media_uri,
    ]

    # Check direct paths first
    for path in search_paths:
        if path.exists():
            return path

    # If not found, try searching with glob patterns

    # Search in stories subdirectories by year/month
    story_pattern = str(data_root / "media" / "stories" / "*" / filename)
    matches = glob(story_pattern)
    for match in matches:
        match_path = Path(match)
        if match_path.exists():
            return match_path

    # Search in posts subdirectories
    posts_pattern = str(data_root / "media" / "posts" / "*" / filename)
    matches = glob(posts_pattern)
    for match in matches:
        match_path = Path(match)
        if match_path.exists():
            return match_path

    # Search anywhere in the directory recursively as last resort
    all_pattern = str(data_root / "**" / filename)
    matches = glob(all_pattern, recursive=True)
    for match in matches:
        match_path = Path(match)
        if match_path.exists():
            return match_path

    return None
