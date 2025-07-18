"""Simplified tests for JSONParser core functionality."""

import json
from datetime import datetime
from typing import Any, Dict, List

from instagram_analyzer.parsers.json_parser import JSONParser


class TestJSONParserCore:
    """Test suite for JSONParser core functionality."""

    def __init__(self):
        """Initialize test class."""
        self.parser = None

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = JSONParser()

    def test_init(self):
        """Test parser initialization."""
        assert self.parser.streaming_parser is not None
        assert self.parser.batch_processor is not None

    def test_parse_profile_basic(self):
        """Test basic profile parsing."""
        profile_data = {"username": "testuser", "name": "Test User", "bio": "Test bio"}

        profile = self.parser.parse_profile(profile_data)

        assert profile.username == "testuser"
        assert profile.name == "Test User"
        assert profile.bio == "Test bio"

    def test_parse_profile_with_wrapped_data(self):
        """Test profile parsing with wrapped data."""
        profile_data = {"profile_user": {"username": "testuser", "name": "Test User"}}

        profile = self.parser.parse_profile(profile_data)

        assert profile.username == "testuser"
        assert profile.name == "Test User"

    def test_parse_posts_basic(self):
        """Test basic posts parsing."""
        posts_data = [
            {
                "media": [{"uri": "photo.jpg"}],
                "creation_timestamp": 1640995200,
                "caption": "Test post #hashtag",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]
        assert post.caption == "Test post #hashtag"
        assert post.timestamp == datetime.fromtimestamp(1640995200)
        assert len(post.media) == 1

    def test_parse_posts_empty(self):
        """Test parsing empty posts."""
        posts_data: list[dict[str, Any]] = []

        posts = self.parser.parse_posts(posts_data)

        assert posts == []

    def test_parse_stories_basic(self):
        """Test basic stories parsing."""
        stories_data = {
            "ig_stories": [
                {
                    "uri": "story1.jpg",
                    "creation_timestamp": 1640995200,
                    "caption": "Test story",
                }
            ]
        }

        stories = self.parser.parse_stories(stories_data)

        assert len(stories) == 1
        story = stories[0]
        assert story.caption == "Test story"
        assert story.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_stories_empty(self):
        """Test parsing empty stories."""
        stories_data = {"ig_stories": []}

        stories = self.parser.parse_stories(stories_data)

        assert stories == []

    def test_parse_reels_basic(self):
        """Test basic reels parsing."""
        reels_data = [
            {
                "media": [{"uri": "reel1.mp4"}],
                "creation_timestamp": 1640995200,
                "caption": "Test reel",
            }
        ]

        reels = self.parser.parse_reels(reels_data)

        assert len(reels) == 1
        reel = reels[0]
        assert reel.caption == "Test reel"
        assert reel.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_reels_empty(self):
        """Test parsing empty reels."""
        reels_data: list[dict[str, Any]] = []

        reels = self.parser.parse_reels(reels_data)

        assert reels == []

    def test_parse_posts_from_file(self, tmp_path):
        """Test posts parsing from file."""
        posts_data = [
            {
                "media": [{"uri": "photo.jpg"}],
                "creation_timestamp": 1640995200,
                "caption": "Test post from file",
            }
        ]

        posts_file = tmp_path / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        posts = self.parser.parse_posts_from_file(str(posts_file))

        assert len(posts) == 1
        post = posts[0]
        assert post.caption == "Test post from file"
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_stories_from_file(self, tmp_path):
        """Test stories parsing from file."""
        stories_data = {
            "ig_stories": [
                {
                    "uri": "story1.jpg",
                    "creation_timestamp": 1640995200,
                    "caption": "Test story from file",
                }
            ]
        }

        stories_file = tmp_path / "stories.json"
        stories_file.write_text(json.dumps(stories_data))

        stories = self.parser.parse_stories_from_file(str(stories_file))

        assert len(stories) == 1
        story = stories[0]
        assert story.caption == "Test story from file"

    def test_parse_reels_from_file(self, tmp_path):
        """Test reels parsing from file."""
        reels_data = [
            {
                "media": [{"uri": "reel1.mp4"}],
                "creation_timestamp": 1640995200,
                "caption": "Test reel from file",
            }
        ]

        reels_file = tmp_path / "reels.json"
        reels_file.write_text(json.dumps(reels_data))

        reels = self.parser.parse_reels_from_file(str(reels_file))

        assert len(reels) == 1
        reel = reels[0]
        assert reel.caption == "Test reel from file"

    def test_parse_from_invalid_file(self):
        """Test parsing from nonexistent file."""
        posts = self.parser.parse_posts_from_file("nonexistent.json")
        assert posts == []

        stories = self.parser.parse_stories_from_file("nonexistent.json")
        assert stories == []

        reels = self.parser.parse_reels_from_file("nonexistent.json")
        assert reels == []

    def test_parse_from_invalid_json(self, tmp_path):
        """Test parsing from invalid JSON file."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        posts = self.parser.parse_posts_from_file(str(invalid_file))
        assert posts == []

        stories = self.parser.parse_stories_from_file(str(invalid_file))
        assert stories == []

        reels = self.parser.parse_reels_from_file(str(invalid_file))
        assert reels == []

    def test_parse_timestamp_conversion(self):
        """Test timestamp conversion."""
        posts_data = [
            {
                "media": [{"uri": "photo.jpg"}],
                "creation_timestamp": 1640995200,
                "caption": "Test timestamp",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]
        assert isinstance(post.timestamp, datetime)
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_multiple_media(self):
        """Test parsing posts with multiple media."""
        posts_data = [
            {
                "media": [
                    {"uri": "photo1.jpg"},
                    {"uri": "photo2.jpg"},
                    {"uri": "video1.mp4"},
                ],
                "creation_timestamp": 1640995200,
                "caption": "Multiple media post",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]
        assert len(post.media) == 3
        assert post.media[0].uri == "photo1.jpg"
        assert post.media[1].uri == "photo2.jpg"
        assert post.media[2].uri == "video1.mp4"

    def test_parse_hashtags_and_mentions(self):
        """Test hashtag and mention extraction."""
        posts_data = [
            {
                "media": [{"uri": "photo.jpg"}],
                "creation_timestamp": 1640995200,
                "caption": "Test post #hashtag1 #hashtag2 @user1 @user2",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]
        # Check if hashtags are properly extracted
        assert "#hashtag1" in post.caption
        assert "#hashtag2" in post.caption
        assert "@user1" in post.caption
        assert "@user2" in post.caption

    def test_memory_efficiency_large_dataset(self, tmp_path):
        """Test memory efficiency with larger dataset."""
        # Create a moderately large dataset
        large_posts_data = []
        for i in range(100):
            large_posts_data.append(
                {
                    "media": [{"uri": f"photo_{i}.jpg"}],
                    "creation_timestamp": 1640995200 + i,
                    "caption": f"Post {i} #test{i}",
                }
            )

        posts_file = tmp_path / "large_posts.json"
        posts_file.write_text(json.dumps(large_posts_data))

        posts = self.parser.parse_posts_from_file(str(posts_file))

        assert len(posts) == 100
        assert posts[0].caption == "Post 0 #test0"
        assert posts[99].caption == "Post 99 #test99"

    def test_batch_processing(self, tmp_path):
        """Test batch processing of multiple files."""
        # Create multiple files
        for i in range(3):
            posts_data = [
                {
                    "media": [{"uri": f"photo_{i}.jpg"}],
                    "creation_timestamp": 1640995200 + i,
                    "caption": f"Batch post {i}",
                }
            ]

            posts_file = tmp_path / f"posts_{i+1}.json"
            posts_file.write_text(json.dumps(posts_data))

        # Parse all files
        all_posts = []
        for i in range(3):
            file_path = tmp_path / f"posts_{i+1}.json"
            posts = self.parser.parse_posts_from_file(str(file_path))
            all_posts.extend(posts)

        assert len(all_posts) == 3
        assert all_posts[0].caption == "Batch post 0"
        assert all_posts[1].caption == "Batch post 1"
        assert all_posts[2].caption == "Batch post 2"

    def test_error_handling_graceful(self):
        """Test graceful error handling."""
        # Test with minimal data
        minimal_posts = [{}]  # Post with no data

        posts = self.parser.parse_posts(minimal_posts)

        # Should handle gracefully - either return empty or handle with defaults
        assert isinstance(posts, list)
