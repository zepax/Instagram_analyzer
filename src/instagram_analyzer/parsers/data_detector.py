"""Data structure detection for Instagram exports."""

import json
from pathlib import Path
from typing import Any, Dict

from ..utils import safe_json_load


class DataDetector:
    """Detects and validates Instagram data export structure."""

    base_path: Path = Path()

    COMMON_FOLDERS = [
        "content",
        "messages",
        "connections",
        "personal_information",
        "ads_and_businesses",
        "security_and_login_info",
        "preferences",
    ]

    CONTENT_FILES = [
        "posts_1.json",
        "stories.json",
        "reels.json",
        "profile.json",
        "personal_information.json",
        "account_information.json",
    ]

    ENGAGEMENT_FILES = [
        "liked_posts.json",
        "post_comments_1.json",
        "post_comments_2.json",
        "reels_comments.json",
    ]

    def __init__(self):
        # Base path for relative path calculations
        self.base_path = None

    def detect_structure(self, data_path: Path) -> dict[str, Any]:
        """Detect Instagram data export structure.

        Args:
            data_path: Path to data export directory

        Returns:
            Dictionary containing structure information
        """
        self.base_path = data_path  # Store base path for relative path calculations
        structure = {
            "is_valid": False,
            "export_type": "unknown",
            "folders_found": [],
            "post_files": [],
            "story_files": [],
            "reel_files": [],
            "profile_files": [],
            "message_files": [],
            "archived_post_files": [],
            "recently_deleted_files": [],
            "story_interaction_files": {},
            "engagement_files": {
                "liked_posts": [],
                "post_comments": [],
                "reel_comments": [],
            },
            "total_files": 0,
            "estimated_size": 0,
        }

        if not data_path.exists() or not data_path.is_dir():
            # Only set "unknown" for nonexistent paths, not for empty directories
            if not data_path.exists():
                structure["export_type"] = "unknown"
            return structure

        # Scan directory structure
        self._scan_directory(data_path, structure)

        # Validate structure
        structure["is_valid"] = self._validate_structure(structure)

        # Determine export type
        structure["export_type"] = self._determine_export_type(structure)

        return structure

    def _scan_directory(self, path: Path, structure: dict[str, Any]) -> None:
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

    def _categorize_file(self, file_path: Path, structure: dict[str, Any]) -> None:
        """Categorize file based on name and location."""
        filename = file_path.name.lower()

        # Skip non-JSON files and system files
        if not filename.endswith(".json") or "zone.identifier" in filename:
            return

        # Use relative path parts for precise matching
        try:
            path_parts = [p.lower() for p in file_path.relative_to(self.base_path).parts]

        except (ValueError, AttributeError):
            # Fallback for safety
            path_parts = [p.lower() for p in file_path.parts]
            print(
                f"WARNING: Could not determine relative path for {file_path}. Using full path."
            )

        # --- Profile Information ---
        if path_parts == ["personal_information", "personal_information.json"]:

            structure["profile_files"].append(file_path)
            return

        # --- Content Files (Posts, Stories, Reels) ---
        if path_parts == ["your_instagram_activity", "media", "posts_1.json"]:
            if self._is_posts_file(file_path):

                structure["post_files"].append(file_path)
                return
        elif path_parts == ["your_instagram_activity", "media", "stories.json"]:
            if self._is_stories_file(file_path):

                structure["story_files"].append(file_path)
                return
        elif path_parts == ["your_instagram_activity", "media", "reels.json"]:
            if self._is_reels_file(file_path):

                structure["reel_files"].append(file_path)
                return

        # --- Archived and Deleted Content ---
        if path_parts == ["your_instagram_activity", "media", "archived_posts.json"]:

            structure["archived_post_files"].append(file_path)
            return
        elif path_parts == [
            "your_instagram_activity",
            "media",
            "recently_deleted_content.json",
        ]:

            structure["recently_deleted_files"].append(file_path)
            return

        # --- Story Interactions ---
        if path_parts[:-1] == ["your_instagram_activity", "story_interactions"]:
            interaction_type = file_path.stem

            if interaction_type not in structure["story_interaction_files"]:
                structure["story_interaction_files"][interaction_type] = []
            structure["story_interaction_files"][interaction_type].append(file_path)
            return

        # --- Engagement Files ---
        if path_parts == ["your_instagram_activity", "likes", "liked_posts.json"]:
            if self._is_engagement_file(file_path, "liked_posts"):

                structure["engagement_files"]["liked_posts"].append(file_path)
                return
        elif (
            path_parts[:-1] == ["your_instagram_activity", "comments"]
            and "post_comments" in filename
        ):
            if self._is_engagement_file(file_path, "post_comments"):

                structure["engagement_files"]["post_comments"].append(file_path)
                return
        elif (
            path_parts[:-1] == ["your_instagram_activity", "comments"]
            and "reels_comments" in filename
        ):
            if self._is_engagement_file(file_path, "reel_comments"):

                structure["engagement_files"]["reel_comments"].append(file_path)
                return

        # --- Fallback for older/different structures ---

        # Generic Profile check
        if any(name in filename for name in ["profile.json", "account_information.json"]):
            if file_path not in structure["profile_files"]:
                structure["profile_files"].append(file_path)
            return

        # Generic Content check
        if "posts" in filename:
            if (
                self._is_posts_file(file_path)
                and file_path not in structure["post_files"]
            ):
                structure["post_files"].append(file_path)
                return
        if "stories" in filename:
            if (
                self._is_stories_file(file_path)
                and file_path not in structure["story_files"]
            ):
                structure["story_files"].append(file_path)
                return
        if "reels" in filename:
            if (
                self._is_reels_file(file_path)
                and file_path not in structure["reel_files"]
            ):
                structure["reel_files"].append(file_path)
                return

        # Archived and deleted content (fallback)
        if "archived" in filename:
            structure["archived_post_files"].append(file_path)
            return
        if "recently_deleted" in filename or "deleted_content" in filename:
            structure["recently_deleted_files"].append(file_path)
            return

        # Messages
        if "message" in filename:
            # A simple check for message files, can be refined if needed
            if "messages" in file_path.parent.name:
                structure["message_files"].append(file_path)
                return

    def _is_engagement_file(self, file_path: Path, engagement_type: str) -> bool:
        """Check if file contains engagement data."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Check different engagement file structures
            if engagement_type == "liked_posts":
                # Check for likes_media_likes or media_likes structure
                return isinstance(data, dict) and any(
                    key in data for key in ["likes_media_likes", "media_likes"]
                )
            elif engagement_type == "post_comments":
                # Check for a list of comments, checking the first item is enough
                return (
                    isinstance(data, list)
                    and data
                    and "string_map_data" in data[0]  # check if not empty
                    and "Comment" in data[0]["string_map_data"]
                )
            elif engagement_type == "reel_comments":
                # Check for reel comments structure
                return isinstance(data, dict) and any(
                    key in data
                    for key in ["comments_reels_comments", "reels_comments", "comments"]
                )

            return False
        except (json.JSONDecodeError, FileNotFoundError, UnicodeDecodeError):
            return False

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
            if isinstance(data, dict):
                # It's a dictionary, check for a key that contains a list of stories
                for key in [
                    "ig_stories",
                    "stories",
                    "story_activities",
                    "reel_activities",
                ]:
                    if key in data and isinstance(data[key], list):
                        for item in data[key][:5]:
                            if isinstance(item, dict) and self._has_story_structure(item):
                                return True
            elif isinstance(data, list):
                # It's a list of stories directly
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

            elif isinstance(data, dict):
                # Check if it's a wrapper containing reels
                for key in ["reels", "data", "items"]:
                    if key in data and isinstance(data[key], list):
                        for item in data[key][:5]:
                            if isinstance(item, dict) and self._has_reel_structure(item):
                                return True

            return False
        except Exception:
            return False

    def _has_post_structure(self, item: dict[str, Any]) -> bool:
        """Check if item has post-like structure."""
        post_indicators = [
            "media",
            "creation_timestamp",
            "timestamp",
            "caption",
            "title",
        ]

        return any(indicator in item for indicator in post_indicators)

    def _has_story_structure(self, item: dict[str, Any]) -> bool:
        """Check if item has story-like structure."""
        story_indicators = ["creation_timestamp", "timestamp", "uri", "media_metadata"]

        return any(indicator in item for indicator in story_indicators)

    def _has_reel_structure(self, item: dict[str, Any]) -> bool:
        """Check if item has reel-like structure."""
        reel_indicators = ["media", "creation_timestamp", "timestamp", "caption"]

        return any(indicator in item for indicator in reel_indicators)

    def _validate_structure(self, structure: dict[str, Any]) -> bool:
        """Validate if structure looks like Instagram export."""
        # Must have some content files
        content_files = (
            len(structure["post_files"])
            + len(structure["story_files"])
            + len(structure["reel_files"])
        )

        if content_files == 0:
            # No content files, check if there's profile or engagement data
            if (
                len(structure["profile_files"]) > 0
                or len(structure["engagement_files"]["liked_posts"]) > 0
                or len(structure["engagement_files"]["post_comments"]) > 0
                or len(structure["engagement_files"]["reel_comments"]) > 0
            ):
                return True
            return False

        # If we have content files, it's a valid Instagram export
        return True

    def _determine_export_type(self, structure: dict[str, Any]) -> str:
        """Determine type of Instagram export."""
        # Special case for nonexistent paths - use "unknown" status
        if not self.base_path.exists():
            return "unknown"

        # For empty directory, return invalid
        if len(structure["folders_found"]) == 0 and structure["total_files"] == 0:
            return "invalid"

        if not structure["is_valid"]:
            return "invalid"

        # Check for full export
        if len(structure["folders_found"]) >= 3:
            return "full_export"

        # Check for content-only export
        if structure["post_files"] or structure["story_files"] or structure["reel_files"]:
            return "content_export"

        return "partial_export"
