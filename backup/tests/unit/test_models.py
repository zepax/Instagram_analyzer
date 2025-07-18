"""Test cases for Pydantic models."""

from datetime import datetime, timezone

import pytest

from instagram_analyzer.models import (
    Comment,
    ContentType,
    Like,
    Media,
    MediaType,
    Post,
    Profile,
    Reel,
    Story,
    User,
)


class TestMedia:
    """Test cases for Media model."""

    def test_media_creation(self):
        """Test basic media creation."""
        media = Media(
            uri="test_image.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        assert media.uri == "test_image.jpg"
        assert media.media_type == MediaType.IMAGE
        assert media.is_local_file is True

    def test_media_url(self):
        """Test media with URL."""
        media = Media(
            uri="https://example.com/image.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        assert media.is_local_file is False
        assert media.file_path is None

    def test_aspect_ratio(self):
        """Test aspect ratio calculation."""
        media = Media(
            uri="test.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
            width=1920,
            height=1080,
        )

        assert media.aspect_ratio == pytest.approx(1.777, rel=1e-3)


class TestUser:
    """Test cases for User model."""

    def test_user_creation(self):
        """Test basic user creation."""
        user = User(username="testuser")

        assert user.username == "testuser"
        assert user.is_verified is False
        assert user.is_private is False

    def test_username_normalization(self):
        """Test username is normalized to lowercase."""
        user = User(username="TestUser")
        assert user.username == "testuser"


class TestProfile:
    """Test cases for Profile model."""

    def test_profile_creation(self):
        """Test basic profile creation."""
        profile = Profile(username="testuser")

        assert profile.username == "testuser"
        assert profile.is_private is False
        assert profile.is_verified is False
        assert profile.is_business is False

    def test_engagement_rate_calculation(self):
        """Test engagement rate calculation."""
        profile = Profile(username="testuser", followers_count=1000, posts_count=50)

        assert profile.engagement_rate == 5.0  # 50/1000 * 100


class TestComment:
    """Test cases for Comment model."""

    def test_comment_creation(self):
        """Test basic comment creation."""
        user = User(username="commenter")
        comment = Comment(
            text="Great post!", timestamp=datetime.now(timezone.utc), author=user
        )

        assert comment.text == "Great post!"
        assert comment.word_count == 2
        assert comment.char_count == 11
        assert comment.is_reply is False


class TestPost:
    """Test cases for Post model."""

    def test_post_creation(self):
        """Test basic post creation."""
        media = Media(
            uri="test.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        post = Post(
            media=[media],
            timestamp=datetime.now(timezone.utc),
            caption="Test post caption",
        )

        assert len(post.media) == 1
        assert post.caption == "Test post caption"
        assert post.media_count == 1
        assert post.is_carousel is False

    def test_carousel_post(self):
        """Test carousel post detection."""
        media1 = Media(
            uri="test1.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )
        media2 = Media(
            uri="test2.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        post = Post(media=[media1, media2], timestamp=datetime.now(timezone.utc))

        assert post.is_carousel is True
        assert post.media_count == 2

    def test_video_post_detection(self):
        """Test video post detection."""
        media = Media(
            uri="test.mp4",
            media_type=MediaType.VIDEO,
            creation_timestamp=datetime.now(timezone.utc),
        )

        post = Post(media=[media], timestamp=datetime.now(timezone.utc))

        assert post.has_video is True


class TestStory:
    """Test cases for Story model."""

    def test_story_creation(self):
        """Test basic story creation."""
        media = Media(
            uri="story.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        story = Story(media=media, timestamp=datetime.now(timezone.utc))

        assert story.media.uri == "story.jpg"
        assert story.is_highlight is False


class TestReel:
    """Test cases for Reel model."""

    def test_reel_creation(self):
        """Test basic reel creation."""
        media = Media(
            uri="reel.mp4",
            media_type=MediaType.VIDEO,
            creation_timestamp=datetime.now(timezone.utc),
            duration=30.0,
        )

        reel = Reel(
            video=media, timestamp=datetime.now(timezone.utc), caption="Cool reel!"
        )

        assert reel.video.uri == "reel.mp4"
        assert reel.caption == "Cool reel!"
        assert reel.duration_seconds == 30.0

    def test_reel_validation(self):
        """Test reel validation requires video."""
        media = Media(
            uri="image.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )

        with pytest.raises(ValueError, match="Reel must contain video content"):
            Reel(video=media, timestamp=datetime.now(timezone.utc))
