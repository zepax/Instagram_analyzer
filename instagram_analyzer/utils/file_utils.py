"""File utility functions."""

import json
from pathlib import Path
from typing import Any, Optional, Dict


def validate_path(path: Path) -> bool:
    """Validate if path exists and is accessible.
    
    Args:
        path: Path to validate
        
    Returns:
        True if path is valid and accessible
    """
    try:
        return path.exists() and path.is_dir()
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
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
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
        for path in directory.rglob('*'):
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