"""Tests for DataDetector."""

import json

from instagram_analyzer.parsers.data_detector import DataDetector


class TestDataDetector:
    """Test suite for DataDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = DataDetector()

    def test_init(self):
        """Test detector initialization."""
        assert self.detector.base_path is None

    def test_detect_structure_empty_directory(self, tmp_path):
        """Test structure detection in empty directory."""
        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is False
        assert result["export_type"] == "invalid"
        assert result["folders_found"] == []
        assert result["total_files"] == 0
        assert result["estimated_size"] == 0

    def test_detect_structure_nonexistent_directory(self, tmp_path):
        """Test structure detection with non-existent directory."""
        non_existent = tmp_path / "nonexistent"
        result = self.detector.detect_structure(non_existent)

        assert result["is_valid"] is False
        assert result["export_type"] == "unknown"
        assert result["folders_found"] == []

    def test_detect_structure_with_posts(self, tmp_path):
        """Test structure detection with posts file."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()

        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create valid posts file
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,
                "title": "Test post",
                "caption": "Test caption",
            }
        ]

        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert result["export_type"] == "content_export"
        assert len(result["post_files"]) == 1
        assert posts_file in result["post_files"]
        assert result["total_files"] == 1

    def test_detect_structure_with_stories(self, tmp_path):
        """Test structure detection with stories file."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()

        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create valid stories file
        stories_data = {
            "ig_stories": [
                {
                    "creation_timestamp": 1640995200,
                    "uri": "stories/story1.jpg",
                    "media_metadata": {},
                }
            ]
        }

        stories_file = media_dir / "stories.json"
        stories_file.write_text(json.dumps(stories_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["story_files"]) == 1
        assert stories_file in result["story_files"]

    def test_detect_structure_with_reels(self, tmp_path):
        """Test structure detection with reels file."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()

        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create valid reels file
        reels_data = [
            {
                "media": ["reel.mp4"],
                "creation_timestamp": 1640995200,
                "caption": "Test reel",
            }
        ]

        reels_file = media_dir / "reels.json"
        reels_file.write_text(json.dumps(reels_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["reel_files"]) == 1
        assert reels_file in result["reel_files"]

    def test_detect_structure_with_engagement_files(self, tmp_path):
        """Test structure detection with engagement files."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()

        # Create likes directory
        likes_dir = activity_dir / "likes"
        likes_dir.mkdir()

        # Create valid liked posts file
        liked_posts_data = {
            "likes_media_likes": [
                {
                    "timestamp": 1640995200,
                    "title": "Liked post",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "test"}
                    ],
                }
            ]
        }

        liked_posts_file = likes_dir / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        # Create comments directory
        comments_dir = activity_dir / "comments"
        comments_dir.mkdir()

        # Create valid post comments file
        post_comments_data = [
            {
                "string_map_data": {"Comment": {"value": "Nice post!"}},
                "timestamp": 1640995200,
            }
        ]

        post_comments_file = comments_dir / "post_comments_1.json"
        post_comments_file.write_text(json.dumps(post_comments_data))

        # Create some content to make it valid
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["engagement_files"]["liked_posts"]) == 1
        assert len(result["engagement_files"]["post_comments"]) == 1
        assert liked_posts_file in result["engagement_files"]["liked_posts"]
        assert post_comments_file in result["engagement_files"]["post_comments"]

    def test_detect_structure_with_profile_info(self, tmp_path):
        """Test structure detection with profile information."""
        # Create personal information directory
        personal_info_dir = tmp_path / "personal_information"
        personal_info_dir.mkdir()

        # Create profile file
        profile_data = {
            "profile_user": [
                {
                    "string_map_data": {
                        "Name": {"value": "Test User"},
                        "Username": {"value": "testuser"},
                    }
                }
            ]
        }

        profile_file = personal_info_dir / "personal_information.json"
        profile_file.write_text(json.dumps(profile_data))

        # Create content to make it valid
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["profile_files"]) == 1
        assert profile_file in result["profile_files"]

    def test_detect_structure_full_export(self, tmp_path):
        """Test detection of full export structure."""
        # Create multiple common directories
        for folder in ["content", "messages", "connections", "personal_information"]:
            (tmp_path / folder).mkdir()

        # Create some content
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert result["export_type"] == "full_export"
        assert len(result["folders_found"]) >= 4

    def test_json_file_handling_invalid_json(self, tmp_path):
        """Test handling of invalid JSON files."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create invalid JSON file
        invalid_file = media_dir / "posts_1.json"
        invalid_file.write_text("invalid json content")

        result = self.detector.detect_structure(tmp_path)

        # Should handle gracefully and not crash
        assert result["is_valid"] is False
        assert len(result["post_files"]) == 0

    def test_json_file_handling_missing_file(self, tmp_path):
        """Test handling of missing JSON files."""
        # Create Instagram structure but no files
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        result = self.detector.detect_structure(tmp_path)

        # Should handle gracefully
        assert result["is_valid"] is False
        assert len(result["post_files"]) == 0

    def test_categorize_file_skip_non_json(self, tmp_path):
        """Test that non-JSON files are skipped."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create non-JSON file
        txt_file = media_dir / "posts.txt"
        txt_file.write_text("test content")

        # Create valid JSON file to make structure valid
        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["post_files"]) == 1  # Only the JSON file
        assert txt_file not in result["post_files"]

    def test_categorize_file_skip_system_files(self, tmp_path):
        """Test that system files are skipped."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create system file
        system_file = media_dir / "posts.json:Zone.Identifier"
        system_file.write_text("system file")

        # Create valid JSON file to make structure valid
        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["post_files"]) == 1  # Only the JSON file
        assert system_file not in result["post_files"]

    def test_size_estimation(self, tmp_path):
        """Test that file size estimation works correctly."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create posts file with specific content
        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert result["estimated_size"] > 0
        assert result["total_files"] == 1

    def test_multiple_posts_files(self, tmp_path):
        """Test detection of multiple posts files."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create multiple posts files
        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]

        for i in range(3):
            posts_file = media_dir / f"posts_{i+1}.json"
            posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["post_files"]) == 3
        assert result["total_files"] == 3

    def test_mixed_content_types(self, tmp_path):
        """Test detection with mixed content types."""
        # Create Instagram structure
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        # Create posts file
        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        # Create stories file
        stories_data = {
            "ig_stories": [
                {"creation_timestamp": 1640995200, "uri": "stories/story1.jpg"}
            ]
        }
        stories_file = media_dir / "stories.json"
        stories_file.write_text(json.dumps(stories_data))

        # Create reels file
        reels_data = [{"media": ["reel.mp4"], "creation_timestamp": 1640995200}]
        reels_file = media_dir / "reels.json"
        reels_file.write_text(json.dumps(reels_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["is_valid"] is True
        assert len(result["post_files"]) == 1
        assert len(result["story_files"]) == 1
        assert len(result["reel_files"]) == 1
        assert result["total_files"] == 3

    def test_export_type_determination(self, tmp_path):
        """Test export type determination logic."""
        # Test content export
        activity_dir = tmp_path / "your_instagram_activity"
        activity_dir.mkdir()
        media_dir = activity_dir / "media"
        media_dir.mkdir()

        posts_data = [{"media": ["photo.jpg"], "creation_timestamp": 1640995200}]
        posts_file = media_dir / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        result = self.detector.detect_structure(tmp_path)

        assert result["export_type"] == "content_export"

        # Add more folders for full export
        for folder in ["messages", "connections", "personal_information"]:
            (tmp_path / folder).mkdir()

        result = self.detector.detect_structure(tmp_path)

        assert result["export_type"] == "full_export"
