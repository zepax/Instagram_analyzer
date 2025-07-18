"""Tests for EngagementParser core functionality."""

import json
from typing import Any, Dict, List

from instagram_analyzer.parsers.engagement_parser import EngagementParser


class TestEngagementParser:
    """Test suite for EngagementParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EngagementParser()

    def test_init(self):
        """Test parser initialization."""
        assert self.parser is not None

    def test_parse_liked_posts_basic(self, tmp_path):
        """Test parsing liked posts from JSON data."""
        liked_posts_data = {
            "likes_media_likes": [
                {
                    "title": "Test Post",
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/p/test123/",
                            "timestamp": 1672574400,
                        }
                    ],
                }
            ]
        }

        # Create JSON file
        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        # Parse
        liked_posts = self.parser._parse_liked_posts(liked_posts_file)

        assert len(liked_posts) == 1
        assert liked_posts[0]["title"] == "Test Post"

    def test_parse_liked_posts_empty(self, tmp_path):
        """Test parsing empty liked posts."""
        liked_posts_data = {"likes_media_likes": []}

        # Create JSON file
        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        # Parse
        liked_posts = self.parser._parse_liked_posts(liked_posts_file)

        assert liked_posts == []

    def test_parse_post_comments_basic(self, tmp_path):
        """Test parsing post comments from JSON data."""
        comments_data = [
            {
                "media_list_data": [{"uri": "https://www.instagram.com/p/test123/"}],
                "string_map_data": {
                    "Comment": {"value": "Test comment text"},
                    "Time": {"timestamp": 1672574400},
                },
            }
        ]

        # Create JSON file
        comments_file = tmp_path / "comments.json"
        comments_file.write_text(json.dumps(comments_data))

        # Parse
        comments = self.parser._parse_post_comments(comments_file)

        assert len(comments) == 1
        assert comments[0]["text"] == "Test comment text"

    def test_parse_post_comments_empty(self, tmp_path):
        """Test parsing empty post comments."""
        comments_data = []

        # Create JSON file
        comments_file = tmp_path / "comments.json"
        comments_file.write_text(json.dumps(comments_data))

        # Parse
        comments = self.parser._parse_post_comments(comments_file)

        assert comments == []

    def test_parse_reel_comments_basic(self, tmp_path):
        """Test parsing reel comments from JSON data."""
        reel_comments_data = {
            "comments_reels_comments": [
                {
                    "title": "Test Reel Comment",
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/reel/test123/",
                            "value": "Great reel!",
                            "timestamp": 1672574400,
                        }
                    ],
                }
            ]
        }

        # Create JSON file
        reel_comments_file = tmp_path / "reel_comments.json"
        reel_comments_file.write_text(json.dumps(reel_comments_data))

        # Parse
        reel_comments = self.parser._parse_reel_comments(reel_comments_file)

        assert len(reel_comments) == 1
        assert reel_comments[0]["title"] == "Test Reel Comment"

    def test_parse_reel_comments_empty(self, tmp_path):
        """Test parsing empty reel comments."""
        reel_comments_data = {"comments_reels_comments": []}

        # Create JSON file
        reel_comments_file = tmp_path / "reel_comments.json"
        reel_comments_file.write_text(json.dumps(reel_comments_data))

        # Parse
        reel_comments = self.parser._parse_reel_comments(reel_comments_file)

        assert reel_comments == []

    def test_parse_from_nonexistent_file(self):
        """Test parsing from nonexistent file."""
        from pathlib import Path

        liked_posts = self.parser._parse_liked_posts(Path("nonexistent.json"))
        assert liked_posts == []

        comments = self.parser._parse_post_comments(Path("nonexistent.json"))
        assert comments == []

        reel_comments = self.parser._parse_reel_comments(Path("nonexistent.json"))
        assert reel_comments == []

    def test_parse_from_invalid_json(self, tmp_path):
        """Test parsing from invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        # Should handle gracefully
        liked_posts = self.parser._parse_liked_posts(invalid_file)
        assert liked_posts == []

        comments = self.parser._parse_post_comments(invalid_file)
        assert comments == []

        reel_comments = self.parser._parse_reel_comments(invalid_file)
        assert reel_comments == []

    def test_parse_with_missing_fields(self, tmp_path):
        """Test parsing data with missing fields."""
        incomplete_data = {
            "likes_media_likes": [
                {
                    "title": "Incomplete Post"
                    # Missing string_map_data
                }
            ]
        }

        # Create JSON file
        liked_posts_file = tmp_path / "incomplete.json"
        liked_posts_file.write_text(json.dumps(incomplete_data))

        # Parse - should handle gracefully
        liked_posts = self.parser._parse_liked_posts(liked_posts_file)

        # Should still return data or handle gracefully
        assert isinstance(liked_posts, list)

    def test_parse_multiple_entries(self, tmp_path):
        """Test parsing multiple entries."""
        multiple_data = {
            "likes_media_likes": [
                {
                    "title": "Post 1",
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/p/test123/",
                            "timestamp": 1672574400,
                        }
                    ],
                },
                {
                    "title": "Post 2",
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/p/test456/",
                            "timestamp": 1672660800,
                        }
                    ],
                },
            ]
        }

        # Create JSON file
        liked_posts_file = tmp_path / "multiple.json"
        liked_posts_file.write_text(json.dumps(multiple_data))

        # Parse
        liked_posts = self.parser._parse_liked_posts(liked_posts_file)

        assert len(liked_posts) == 2
        assert liked_posts[0]["title"] == "Post 1"
        assert liked_posts[1]["title"] == "Post 2"

    def test_parse_with_complex_data(self, tmp_path):
        """Test parsing with more complex data structure."""
        complex_data = {
            "likes_media_likes": [
                {
                    "title": "Complex Post",
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/p/test123/",
                            "timestamp": 1672574400,
                        }
                    ],
                    "media": [{"uri": "photo.jpg", "creation_timestamp": 1640995200}],
                }
            ]
        }

        # Create JSON file
        liked_posts_file = tmp_path / "complex.json"
        liked_posts_file.write_text(json.dumps(complex_data))

        # Parse
        liked_posts = self.parser._parse_liked_posts(liked_posts_file)

        assert len(liked_posts) == 1
        assert liked_posts[0]["title"] == "Complex Post"

    def test_error_handling_graceful(self, tmp_path):
        """Test graceful error handling."""
        # Test with malformed data
        malformed_data = {"invalid_key": "invalid_value"}

        # Create JSON file
        malformed_file = tmp_path / "malformed.json"
        malformed_file.write_text(json.dumps(malformed_data))

        # Should handle gracefully
        liked_posts = self.parser._parse_liked_posts(malformed_file)
        assert isinstance(liked_posts, list)

        comments = self.parser._parse_post_comments(malformed_file)
        assert isinstance(comments, list)

        reel_comments = self.parser._parse_reel_comments(malformed_file)
        assert isinstance(reel_comments, list)
