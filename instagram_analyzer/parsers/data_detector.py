"""Data structure detection for Instagram exports."""

import json
from pathlib import Path
from typing import Dict, List, Any

from ..utils import safe_json_load


class DataDetector:
    """Detects and validates Instagram data export structure."""
    
    COMMON_FOLDERS = [
        "content",
        "messages", 
        "connections",
        "personal_information",
        "ads_and_businesses",
        "security_and_login_info",
        "preferences"
    ]
    
    CONTENT_FILES = [
        "posts_1.json",
        "stories.json", 
        "reels.json",
        "profile.json",
        "personal_information.json",
        "account_information.json"
    ]
    
    def detect_structure(self, data_path: Path) -> Dict[str, Any]:
        """Detect Instagram data export structure.
        
        Args:
            data_path: Path to data export directory
            
        Returns:
            Dictionary containing structure information
        """
        structure = {
            "is_valid": False,
            "export_type": "unknown",
            "folders_found": [],
            "post_files": [],
            "story_files": [],
            "reel_files": [],
            "profile_files": [],
            "message_files": [],
            "total_files": 0,
            "estimated_size": 0
        }
        
        if not data_path.exists() or not data_path.is_dir():
            return structure
        
        # Scan directory structure
        self._scan_directory(data_path, structure)
        
        # Validate structure
        structure["is_valid"] = self._validate_structure(structure)
        
        # Determine export type
        structure["export_type"] = self._determine_export_type(structure)
        
        return structure
    
    def _scan_directory(self, path: Path, structure: Dict[str, Any]) -> None:
        """Recursively scan directory for Instagram files."""
        for item in path.iterdir():
            if item.is_dir():
                structure["folders_found"].append(item.name)
                self._scan_directory(item, structure)
            
            elif item.is_file():
                structure["total_files"] += 1
                structure["estimated_size"] += item.stat().st_size
                
                # Categorize files
                self._categorize_file(item, structure)
    
    def _categorize_file(self, file_path: Path, structure: Dict[str, Any]) -> None:
        """Categorize file based on name and location."""
        filename = file_path.name.lower()
        parent_dir = file_path.parent.name.lower()
        
        # Profile/account information
        if any(name in filename for name in ["profile", "account", "personal_information"]):
            structure["profile_files"].append(file_path)
        
        # Posts
        elif "posts" in filename or ("content" in parent_dir and filename.endswith(".json")):
            # Validate it's actually a posts file
            if self._is_posts_file(file_path):
                structure["post_files"].append(file_path)
        
        # Stories
        elif "stories" in filename or "story" in filename:
            if self._is_stories_file(file_path):
                structure["story_files"].append(file_path)
        
        # Reels
        elif "reels" in filename or "reel" in filename:
            if self._is_reels_file(file_path):
                structure["reel_files"].append(file_path)
        
        # Messages
        elif "message" in filename or "messages" in parent_dir:
            structure["message_files"].append(file_path)
    
    def _is_posts_file(self, file_path: Path) -> bool:
        """Check if file contains posts data."""
        try:
            data = safe_json_load(file_path)
            if not data:
                return False
            
            # Check for common post data structures
            if isinstance(data, list):
                # Look for post-like objects
                for item in data[:5]:  # Check first 5 items
                    if isinstance(item, dict) and self._has_post_structure(item):
                        return True
            
            elif isinstance(data, dict):
                # Check if it's a wrapper containing posts
                for key in ["posts", "data", "items"]:
                    if key in data and isinstance(data[key], list):
                        for item in data[key][:5]:
                            if isinstance(item, dict) and self._has_post_structure(item):
                                return True
            
            return False
        except Exception:
            return False
    
    def _is_stories_file(self, file_path: Path) -> bool:
        """Check if file contains stories data."""
        try:
            data = safe_json_load(file_path)
            if not data:
                return False
            
            # Check for story data structure
            if isinstance(data, list):
                for item in data[:5]:
                    if isinstance(item, dict) and self._has_story_structure(item):
                        return True
            
            return False
        except Exception:
            return False
    
    def _is_reels_file(self, file_path: Path) -> bool:
        """Check if file contains reels data."""
        try:
            data = safe_json_load(file_path)
            if not data:
                return False
            
            # Check for reel data structure
            if isinstance(data, list):
                for item in data[:5]:
                    if isinstance(item, dict) and self._has_reel_structure(item):
                        return True
            
            return False
        except Exception:
            return False
    
    def _has_post_structure(self, item: Dict[str, Any]) -> bool:
        """Check if item has post-like structure."""
        post_indicators = [
            "media",
            "creation_timestamp", 
            "timestamp",
            "caption",
            "title"
        ]
        
        return any(indicator in item for indicator in post_indicators)
    
    def _has_story_structure(self, item: Dict[str, Any]) -> bool:
        """Check if item has story-like structure."""
        story_indicators = [
            "creation_timestamp",
            "timestamp", 
            "uri",
            "media_metadata"
        ]
        
        return any(indicator in item for indicator in story_indicators)
    
    def _has_reel_structure(self, item: Dict[str, Any]) -> bool:
        """Check if item has reel-like structure."""
        reel_indicators = [
            "media",
            "creation_timestamp",
            "timestamp",
            "caption"
        ]
        
        return any(indicator in item for indicator in reel_indicators)
    
    def _validate_structure(self, structure: Dict[str, Any]) -> bool:
        """Validate if structure looks like Instagram export."""
        # Must have some content files
        content_files = (
            len(structure["post_files"]) +
            len(structure["story_files"]) + 
            len(structure["reel_files"])
        )
        
        if content_files == 0:
            return False
        
        # Should have some common folders
        common_folders_found = sum(
            1 for folder in self.COMMON_FOLDERS 
            if folder in structure["folders_found"]
        )
        
        return common_folders_found >= 1
    
    def _determine_export_type(self, structure: Dict[str, Any]) -> str:
        """Determine type of Instagram export."""
        if not structure["is_valid"]:
            return "invalid"
        
        # Check for full export
        if len(structure["folders_found"]) >= 3:
            return "full_export"
        
        # Check for content-only export  
        if (structure["post_files"] or 
            structure["story_files"] or 
            structure["reel_files"]):
            return "content_export"
        
        return "partial_export"