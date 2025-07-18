"""Tests for EngagementParser."""

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from instagram_analyzer.exceptions import JSONParsingError, ParsingError
from instagram_analyzer.parsers.engagement_parser import EngagementParser


class TestEngagementParser:
    """Test suite for EngagementParser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = EngagementParser()

    def test_init(self):
        """Test parser initialization."""
        assert isinstance(self.parser.liked_posts_cache, dict)
        assert isinstance(self.parser.post_comments_cache, defaultdict)
        assert isinstance(self.parser.reel_comments_cache, defaultdict)

    def test_parse_engagement_files_empty(self):
        """Test parsing with empty engagement files."""
        result = self.parser.parse_engagement_files({})

        assert result["liked_posts"] == {}
        assert result["post_comments"] == defaultdict(list)
        assert result["reel_comments"] == defaultdict(list)
        assert result["total_likes_given"] == 0
        assert result["total_comments_made"] == 0

    def test_parse_engagement_files_with_likes(self, tmp_path):
        """Test parsing engagement files with liked posts."""
        # Create test liked posts file
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post 1",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test1", "value": "test1"}
                    ],
                    "timestamp": 1640995200,
                },
                {
                    "title": "Test Post 2",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test2", "value": "test2"}
                    ],
                    "timestamp": 1640995300,
                },
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        engagement_files = {"liked_posts": [liked_posts_file]}
        result = self.parser.parse_engagement_files(engagement_files)

        assert len(result["liked_posts"]) == 2
        assert result["total_likes_given"] == 2
        assert "https://instagram.com/p/test1" in result["liked_posts"]
        assert "https://instagram.com/p/test2" in result["liked_posts"]

    def test_parse_engagement_files_with_comments(self, tmp_path):
        """Test parsing engagement files with post comments."""
        # Create test post comments file
        post_comments_data = {
            "post_comments": [
                {
                    "title": "Test Comment 1",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test1", "value": "Nice post!"}
                    ],
                    "timestamp": 1640995200,
                },
                {
                    "title": "Test Comment 2",
                    "string_list_data": [
                        {
                            "href": "https://instagram.com/p/test1",
                            "value": "Great content!",
                        }
                    ],
                    "timestamp": 1640995300,
                },
            ]
        }

        post_comments_file = tmp_path / "post_comments_1.json"
        post_comments_file.write_text(json.dumps(post_comments_data))

        engagement_files = {"post_comments": [post_comments_file]}
        result = self.parser.parse_engagement_files(engagement_files)

        assert len(result["post_comments"]) == 1
        assert len(result["post_comments"]["https://instagram.com/p/test1"]) == 2
        assert result["total_comments_made"] == 2

    def test_parse_engagement_files_with_reel_comments(self, tmp_path):
        """Test parsing engagement files with reel comments."""
        # Create test reel comments file
        reel_comments_data = {
            "reel_comments": [
                {
                    "title": "Test Reel Comment",
                    "string_list_data": [
                        {
                            "href": "https://instagram.com/reel/test1",
                            "value": "Cool reel!",
                        }
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        reel_comments_file = tmp_path / "reels_comments.json"
        reel_comments_file.write_text(json.dumps(reel_comments_data))

        engagement_files = {"reel_comments": [reel_comments_file]}
        result = self.parser.parse_engagement_files(engagement_files)

        assert len(result["reel_comments"]) == 1
        assert len(result["reel_comments"]["https://instagram.com/reel/test1"]) == 1
        assert result["total_comments_made"] == 1

    def test_parse_liked_posts_success(self, tmp_path):
        """Test successful parsing of liked posts file."""
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "test"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        result = self.parser._parse_liked_posts(liked_posts_file)

        assert len(result) == 1
        assert "https://instagram.com/p/test" in result
        assert result["https://instagram.com/p/test"]["timestamp"] == 1640995200

    def test_parse_liked_posts_missing_file(self, tmp_path):
        """Test parsing of non-existent liked posts file."""
        non_existent_file = tmp_path / "nonexistent.json"
        result = self.parser._parse_liked_posts(non_existent_file)
        assert result == {}

    def test_parse_liked_posts_invalid_json(self, tmp_path):
        """Test parsing of invalid JSON in liked posts file."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        result = self.parser._parse_liked_posts(invalid_file)
        assert result == {}

    def test_parse_liked_posts_missing_key(self, tmp_path):
        """Test parsing of liked posts file missing 'liked_posts' key."""
        data = {"other_key": "value"}

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(data))

        result = self.parser._parse_liked_posts(liked_posts_file)
        assert result == {}

    def test_parse_post_comments_success(self, tmp_path):
        """Test successful parsing of post comments file."""
        post_comments_data = {
            "post_comments": [
                {
                    "title": "Test Comment",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "Nice!"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        post_comments_file = tmp_path / "post_comments_1.json"
        post_comments_file.write_text(json.dumps(post_comments_data))

        result = self.parser._parse_post_comments(post_comments_file)

        assert len(result) == 1
        assert "https://instagram.com/p/test" in result
        assert len(result["https://instagram.com/p/test"]) == 1
        assert result["https://instagram.com/p/test"][0]["text"] == "Nice!"

    def test_parse_post_comments_missing_file(self, tmp_path):
        """Test parsing of non-existent post comments file."""
        non_existent_file = tmp_path / "nonexistent.json"
        result = self.parser._parse_post_comments(non_existent_file)
        assert result == {}

    def test_parse_post_comments_invalid_json(self, tmp_path):
        """Test parsing of invalid JSON in post comments file."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        result = self.parser._parse_post_comments(invalid_file)
        assert result == {}

    def test_parse_reel_comments_success(self, tmp_path):
        """Test successful parsing of reel comments file."""
        reel_comments_data = {
            "reel_comments": [
                {
                    "title": "Test Reel Comment",
                    "string_list_data": [
                        {"href": "https://instagram.com/reel/test", "value": "Cool!"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        reel_comments_file = tmp_path / "reels_comments.json"
        reel_comments_file.write_text(json.dumps(reel_comments_data))

        result = self.parser._parse_reel_comments(reel_comments_file)

        assert len(result) == 1
        assert "https://instagram.com/reel/test" in result
        assert len(result["https://instagram.com/reel/test"]) == 1
        assert result["https://instagram.com/reel/test"][0]["text"] == "Cool!"

    def test_parse_reel_comments_missing_file(self, tmp_path):
        """Test parsing of non-existent reel comments file."""
        non_existent_file = tmp_path / "nonexistent.json"
        result = self.parser._parse_reel_comments(non_existent_file)
        assert result == {}

    def test_parse_reel_comments_invalid_json(self, tmp_path):
        """Test parsing of invalid JSON in reel comments file."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        result = self.parser._parse_reel_comments(invalid_file)
        assert result == {}

    def test_extract_post_url_from_href(self):
        """Test URL extraction from href."""
        # Test Instagram post URL
        url = "https://instagram.com/p/ABC123"
        result = self.parser._extract_post_url_from_href(url)
        assert result == "https://instagram.com/p/ABC123"

        # Test Instagram reel URL
        url = "https://instagram.com/reel/XYZ789"
        result = self.parser._extract_post_url_from_href(url)
        assert result == "https://instagram.com/reel/XYZ789"

        # Test URL with parameters
        url = "https://instagram.com/p/ABC123?utm_source=test"
        result = self.parser._extract_post_url_from_href(url)
        assert result == "https://instagram.com/p/ABC123"

    def test_extract_post_url_from_href_invalid(self):
        """Test URL extraction from invalid href."""
        # Test invalid URL
        url = "not-a-url"
        result = self.parser._extract_post_url_from_href(url)
        assert result == "not-a-url"

        # Test empty URL
        url = ""
        result = self.parser._extract_post_url_from_href(url)
        assert result == ""

    def test_cache_functionality(self, tmp_path):
        """Test that cache is properly updated."""
        # Create test data
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "test"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        # Parse and check cache
        engagement_files = {"liked_posts": [liked_posts_file]}
        self.parser.parse_engagement_files(engagement_files)

        assert len(self.parser.liked_posts_cache) == 1
        assert "https://instagram.com/p/test" in self.parser.liked_posts_cache

    def test_multiple_files_same_type(self, tmp_path):
        """Test parsing multiple files of the same type."""
        # Create two liked posts files
        liked_posts_data1 = {
            "liked_posts": [
                {
                    "title": "Test Post 1",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test1", "value": "test1"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        liked_posts_data2 = {
            "liked_posts": [
                {
                    "title": "Test Post 2",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test2", "value": "test2"}
                    ],
                    "timestamp": 1640995300,
                }
            ]
        }

        liked_posts_file1 = tmp_path / "liked_posts_1.json"
        liked_posts_file1.write_text(json.dumps(liked_posts_data1))

        liked_posts_file2 = tmp_path / "liked_posts_2.json"
        liked_posts_file2.write_text(json.dumps(liked_posts_data2))

        engagement_files = {"liked_posts": [liked_posts_file1, liked_posts_file2]}
        result = self.parser.parse_engagement_files(engagement_files)

        assert len(result["liked_posts"]) == 2
        assert result["total_likes_given"] == 2
        assert "https://instagram.com/p/test1" in result["liked_posts"]
        assert "https://instagram.com/p/test2" in result["liked_posts"]

    def test_mixed_engagement_files(self, tmp_path):
        """Test parsing mixed engagement files."""
        # Create liked posts file
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "test"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        # Create post comments file
        post_comments_data = {
            "post_comments": [
                {
                    "title": "Test Comment",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "Nice!"}
                    ],
                    "timestamp": 1640995200,
                }
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        post_comments_file = tmp_path / "post_comments_1.json"
        post_comments_file.write_text(json.dumps(post_comments_data))

        engagement_files = {
            "liked_posts": [liked_posts_file],
            "post_comments": [post_comments_file],
        }
        result = self.parser.parse_engagement_files(engagement_files)

        assert len(result["liked_posts"]) == 1
        assert len(result["post_comments"]) == 1
        assert result["total_likes_given"] == 1
        assert result["total_comments_made"] == 1

    def test_edge_case_empty_string_list_data(self, tmp_path):
        """Test parsing with empty string_list_data."""
        liked_posts_data = {
            "liked_posts": [
                {"title": "Test Post", "string_list_data": [], "timestamp": 1640995200}
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        result = self.parser._parse_liked_posts(liked_posts_file)
        assert result == {}

    def test_edge_case_missing_href(self, tmp_path):
        """Test parsing with missing href in string_list_data."""
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post",
                    "string_list_data": [{"value": "test"}],
                    "timestamp": 1640995200,
                }
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        result = self.parser._parse_liked_posts(liked_posts_file)
        assert result == {}

    def test_edge_case_missing_timestamp(self, tmp_path):
        """Test parsing with missing timestamp."""
        liked_posts_data = {
            "liked_posts": [
                {
                    "title": "Test Post",
                    "string_list_data": [
                        {"href": "https://instagram.com/p/test", "value": "test"}
                    ],
                }
            ]
        }

        liked_posts_file = tmp_path / "liked_posts.json"
        liked_posts_file.write_text(json.dumps(liked_posts_data))

        result = self.parser._parse_liked_posts(liked_posts_file)
        assert len(result) == 1
        assert result["https://instagram.com/p/test"]["timestamp"] is None
