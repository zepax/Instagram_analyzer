"""Tests for JSONParser enrichment methods."""

import json
from datetime import datetime
from typing import Any, Dict, List

from instagram_analyzer.parsers.json_parser import JSONParser


class TestJSONParserEnrichment:
    """Test suite for JSONParser enrichment methods."""

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

    def test_parse_profile_basic(self, tmp_path):
        """Test basic profile parsing."""
        # Create profile data
        profile_data = {
            "profile_user": [
                {
                    "string_map_data": {
                        "Name": {"value": "Test User"},
                        "Username": {"value": "testuser"},
                        "Email": {"value": "test@example.com"},
                        "Bio": {"value": "Test bio"},
                    }
                }
            ]
        }

        # Create profile file
        profile_file = tmp_path / "profile.json"
        profile_file.write_text(json.dumps(profile_data))

        # Parse profile
        profile = self.parser.parse_profile(profile_data)

        assert profile.username == "testuser"
        assert profile.name == "Test User"
        assert profile.email == "test@example.com"
        assert profile.bio == "Test bio"

    def test_parse_profile_missing_fields(self):
        """Test profile parsing with missing fields."""
        profile_data = {
            "profile_user": [{"string_map_data": {"Username": {"value": "testuser"}}}]
        }

        profile = self.parser.parse_profile(profile_data)

        assert profile.username == "testuser"
        assert profile.name is None
        assert profile.email is None
        assert profile.bio is None

    def test_parse_profile_empty_data(self):
        """Test profile parsing with empty data."""
        profile_data: dict[str, Any] = {}

        profile = self.parser.parse_profile(profile_data)

        assert profile.username is None
        assert profile.name is None
        assert profile.email is None
        assert profile.bio is None

    def test_parse_posts_with_enrichment(self, tmp_path):
        """Test posts parsing with enrichment data."""
        # Create posts data
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,
                "title": "Test post",
                "caption": "Test caption #hashtag @mention",
                "location": "Test Location",
            }
        ]

        # Parse posts
        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        assert post.caption == "Test caption #hashtag @mention"
        assert post.location == "Test Location"
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_posts_with_media_enrichment(self):
        """Test posts parsing with media enrichment."""
        posts_data = [
            {
                "media": [
                    {
                        "uri": "photo.jpg",
                        "creation_timestamp": 1640995200,
                        "media_metadata": {
                            "photo_metadata": {
                                "exif_data": [
                                    {"camera_make": "iPhone", "camera_model": "iPhone 13"}
                                ]
                            }
                        },
                    }
                ],
                "creation_timestamp": 1640995200,
                "title": "Test post with media",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        assert len(post.media) == 1
        media = post.media[0]

        assert media.uri == "photo.jpg"
        assert media.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_stories_with_enrichment(self):
        """Test stories parsing with enrichment data."""
        stories_data = {
            "ig_stories": [
                {
                    "uri": "story1.jpg",
                    "creation_timestamp": 1640995200,
                    "caption": "Test story",
                    "media_metadata": {
                        "photo_metadata": {"exif_data": [{"taken_timestamp": 1640995200}]}
                    },
                }
            ]
        }

        stories = self.parser.parse_stories(stories_data)

        assert len(stories) == 1
        story = stories[0]

        assert story.uri == "story1.jpg"
        assert story.caption == "Test story"
        assert story.taken_at == datetime.fromtimestamp(1640995200)

    def test_parse_reels_with_enrichment(self):
        """Test reels parsing with enrichment data."""
        reels_data = [
            {
                "media": [
                    {
                        "uri": "reel1.mp4",
                        "creation_timestamp": 1640995200,
                        "media_metadata": {
                            "video_metadata": {"duration": 30.5, "quality": "1080p"}
                        },
                    }
                ],
                "creation_timestamp": 1640995200,
                "caption": "Test reel #reels",
                "title": "My Reel",
            }
        ]

        reels = self.parser.parse_reels(reels_data)

        assert len(reels) == 1
        reel = reels[0]

        assert reel.caption == "Test reel #reels"
        assert reel.timestamp == datetime.fromtimestamp(1640995200)
        assert len(reel.media) == 1

    def test_parse_story_interactions_with_enrichment(self):
        """Test story interactions parsing with enrichment."""
        interactions_data = [
            {
                "string_map_data": {
                    "Username": {"value": "testuser"},
                    "Story Type": {"value": "Story"},
                },
                "timestamp": 1640995200,
                "title": "testuser viewed your story",
            }
        ]

        interactions = self.parser.parse_story_interactions(interactions_data)

        assert len(interactions) == 1
        interaction = interactions[0]

        assert interaction.username == "testuser"
        assert interaction.interaction_type == "view"
        assert interaction.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_archived_posts_with_enrichment(self):
        """Test archived posts parsing with enrichment."""
        archived_data = {
            "archived_posts": [
                {
                    "media": ["archived_photo.jpg"],
                    "creation_timestamp": 1640995200,
                    "caption": "Archived post",
                    "title": "Archived Post",
                    "archived_timestamp": 1641081600,
                }
            ]
        }

        archived_posts = self.parser.parse_archived_posts(archived_data)

        assert len(archived_posts) == 1
        post = archived_posts[0]

        assert post.caption == "Archived post"
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_recently_deleted_with_enrichment(self):
        """Test recently deleted parsing with enrichment."""
        deleted_data = {
            "recently_deleted_media": [
                {
                    "uri": "deleted_photo.jpg",
                    "creation_timestamp": 1640995200,
                    "deletion_timestamp": 1641081600,
                    "media_type": "IMAGE",
                    "title": "Deleted Photo",
                }
            ]
        }

        deleted_items = self.parser.parse_recently_deleted(deleted_data)

        assert len(deleted_items) == 1
        item = deleted_items[0]

        assert item.uri == "deleted_photo.jpg"
        assert item.timestamp == datetime.fromtimestamp(1640995200)
        assert item.media_type.value == "IMAGE"

    def test_parse_posts_from_file_basic(self, tmp_path):
        """Test posts parsing from file."""
        # Create posts file
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,
                "title": "Test post",
            }
        ]

        posts_file = tmp_path / "posts_1.json"
        posts_file.write_text(json.dumps(posts_data))

        # Parse posts
        posts = self.parser.parse_posts_from_file(str(posts_file))

        assert len(posts) == 1
        post = posts[0]
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_parse_stories_from_file_basic(self, tmp_path):
        """Test stories parsing from file."""
        # Create stories file
        stories_data = {
            "ig_stories": [{"uri": "story1.jpg", "creation_timestamp": 1640995200}]
        }

        stories_file = tmp_path / "stories.json"
        stories_file.write_text(json.dumps(stories_data))

        # Parse stories
        stories = self.parser.parse_stories_from_file(str(stories_file))

        assert len(stories) == 1
        story = stories[0]
        assert story.media.uri == "story1.jpg"

    def test_parse_with_invalid_json(self, tmp_path):
        """Test parsing with invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("invalid json content")

        # Should handle gracefully
        posts = self.parser.parse_posts_from_file(str(invalid_file))
        assert posts == []

        stories = self.parser.parse_stories_from_file(str(invalid_file))
        assert stories == []

    def test_parse_with_missing_file(self):
        """Test parsing with missing file."""
        # Should handle gracefully
        posts = self.parser.parse_posts_from_file("nonexistent.json")
        assert posts == []

        stories = self.parser.parse_stories_from_file("nonexistent.json")
        assert stories == []

    def test_parse_with_empty_data(self):
        """Test parsing with empty data structures."""
        # Empty posts
        posts = self.parser.parse_posts([])
        assert posts == []

        # Empty stories
        stories = self.parser.parse_stories({"ig_stories": []})
        assert stories == []

        # Empty reels
        reels = self.parser.parse_reels([])
        assert reels == []

    def test_parse_with_malformed_data(self):
        """Test parsing with malformed data structures."""
        # Malformed posts
        malformed_posts = [
            {
                "invalid_field": "value"
                # Missing required fields
            }
        ]

        # Should handle gracefully
        posts = self.parser.parse_posts(malformed_posts)
        # May return empty list or objects with default values
        assert isinstance(posts, list)

        # Malformed stories
        malformed_stories = {
            "ig_stories": [
                {
                    "invalid_field": "value"
                    # Missing required fields
                }
            ]
        }

        stories = self.parser.parse_stories(malformed_stories)
        assert isinstance(stories, list)

    def test_hashtag_extraction(self):
        """Test hashtag extraction from captions."""
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,
                "caption": "Test post #hashtag1 #hashtag2 #test",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        # Check if hashtags are extracted properly
        expected_hashtags = ["hashtag1", "hashtag2", "test"]
        assert all(hashtag in post.hashtags for hashtag in expected_hashtags)

    def test_mention_extraction(self):
        """Test mention extraction from captions."""
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,
                "caption": "Test post @user1 @user2 @testuser",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        # Check if mentions are extracted properly
        expected_mentions = ["user1", "user2", "testuser"]
        assert all(mention in post.mentions for mention in expected_mentions)

    def test_media_type_detection(self):
        """Test media type detection."""
        posts_data = [
            {
                "media": [
                    {"uri": "photo.jpg", "creation_timestamp": 1640995200},
                    {"uri": "video.mp4", "creation_timestamp": 1640995200},
                ],
                "creation_timestamp": 1640995200,
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        assert len(post.media) == 2

        # Check media types
        photo_media = next(m for m in post.media if m.uri == "photo.jpg")
        video_media = next(m for m in post.media if m.uri == "video.mp4")

        assert photo_media.media_type.value == "IMAGE"
        assert video_media.media_type.value == "VIDEO"

    def test_timestamp_conversion(self):
        """Test timestamp conversion to datetime objects."""
        posts_data = [
            {
                "media": ["photo.jpg"],
                "creation_timestamp": 1640995200,  # Unix timestamp
                "title": "Test post",
            }
        ]

        posts = self.parser.parse_posts(posts_data)

        assert len(posts) == 1
        post = posts[0]

        assert isinstance(post.timestamp, datetime)
        assert post.timestamp == datetime.fromtimestamp(1640995200)

    def test_batch_processing(self, tmp_path):
        """Test batch processing of multiple files."""
        # Create multiple posts files
        for i in range(3):
            posts_data = [
                {
                    "media": [f"photo_{i}.jpg"],
                    "creation_timestamp": 1640995200 + i,
                    "title": f"Test post {i}",
                }
            ]

            posts_file = tmp_path / f"posts_{i+1}.json"
            posts_file.write_text(json.dumps(posts_data))

        # Get all posts files
        posts_files = list(tmp_path.glob("posts_*.json"))

        # Parse all files
        all_posts = []
        for file in posts_files:
            posts = self.parser.parse_posts_from_file(str(file))
            all_posts.extend(posts)

        assert len(all_posts) == 3

        # Check that all posts are unique
        timestamps = [post.timestamp for post in all_posts]
        assert len(set(timestamps)) == 3

    def test_error_handling_and_logging(self):
        """Test error handling with invalid data."""
        # Test with invalid data that should trigger error handling
        invalid_data = []  # Empty list should be handled gracefully

        posts = self.parser.parse_posts(invalid_data)

        # Should handle gracefully
        assert posts == []

    def test_memory_efficiency(self, tmp_path):
        """Test memory efficiency with large datasets."""
        # Create a large posts file
        large_posts_data = []
        for i in range(1000):
            large_posts_data.append(
                {
                    "media": [f"photo_{i}.jpg"],
                    "creation_timestamp": 1640995200 + i,
                    "title": f"Test post {i}",
                    "caption": f"Caption {i} #test{i}",
                }
            )

        posts_file = tmp_path / "large_posts.json"
        posts_file.write_text(json.dumps(large_posts_data))

        # Parse large file
        posts = self.parser.parse_posts_from_file(str(posts_file))

        assert len(posts) == 1000

        # Verify data integrity
        assert posts[0].caption == "Caption 0 #test0"
        assert posts[999].caption == "Caption 999 #test999"
