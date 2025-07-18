"""Test cases for analyzer modules."""

from datetime import datetime, timedelta, timezone

import pytest

from instagram_analyzer.analyzers import BasicStatsAnalyzer, TemporalAnalyzer
from instagram_analyzer.models import Media, MediaType, Post, Profile, Reel, Story, User


class TestBasicStatsAnalyzer:
    """Test cases for BasicStatsAnalyzer."""

    def setup_method(self):
        """Set up test data."""
        self.analyzer = BasicStatsAnalyzer()

        # Create test media
        self.media1 = Media(
            uri="test1.jpg",
            media_type=MediaType.IMAGE,
            creation_timestamp=datetime.now(timezone.utc),
        )
        self.media2 = Media(
            uri="test2.mp4",
            media_type=MediaType.VIDEO,
            creation_timestamp=datetime.now(timezone.utc),
        )

        # Create test posts
        self.posts = [
            Post(
                media=[self.media1],
                timestamp=datetime.now(timezone.utc),
                caption="Test post 1",
                likes_count=10,
                comments_count=2,
                hashtags=["test", "instagram"],
            ),
            Post(
                media=[self.media2],
                timestamp=datetime.now(timezone.utc) - timedelta(days=1),
                caption="Test post 2 #test #photo",
                likes_count=20,
                comments_count=5,
                hashtags=["test", "photo"],
            ),
        ]

        # Create test stories
        self.stories = [Story(media=self.media1, timestamp=datetime.now(timezone.utc))]

        # Create test reels
        self.reels = [
            Reel(
                video=self.media2,
                timestamp=datetime.now(timezone.utc),
                caption="Test reel",
                likes_count=30,
                comments_count=8,
            )
        ]

        # Create test profile
        self.profile = Profile(
            username="testuser",
            followers_count=1000,
            following_count=500,
            posts_count=100,
        )

    def test_content_counts(self):
        """Test content counting."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels, self.profile)

        assert stats["total_posts"] == 2
        assert stats["total_stories"] == 1
        assert stats["total_reels"] == 1
        assert stats["total_content"] == 4

    def test_engagement_stats(self):
        """Test engagement statistics."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels, self.profile)

        # Total likes: posts (10+20) + reels (30) = 60
        # Total comments: posts (2+5) + reels (8) = 15
        assert stats["total_likes"] == 60
        assert stats["total_comments"] == 15
        assert stats["average_likes_per_post"] == 20  # 60/3 (posts + reels)
        assert stats["average_comments_per_post"] == 5  # 15/3
        assert stats["most_liked_post_likes"] == 30
        assert stats["most_commented_post_comments"] == 8

    def test_hashtag_analysis(self):
        """Test hashtag analysis."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels, self.profile)

        assert stats["total_hashtags"] == 4  # test(2) + instagram(1) + photo(1)
        assert stats["unique_hashtags"] == 3  # test, instagram, photo
        assert ("test", 2) in stats["top_hashtags"]  # "test" appears twice

    def test_profile_stats(self):
        """Test profile statistics."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels, self.profile)

        assert stats["profile_username"] == "testuser"
        assert stats["followers_count"] == 1000
        assert stats["following_count"] == 500
        assert stats["profile_posts_count"] == 100


class TestTemporalAnalyzer:
    """Test cases for TemporalAnalyzer."""

    def setup_method(self):
        """Set up test data."""
        self.analyzer = TemporalAnalyzer()

        # Create test content with specific timestamps
        base_time = datetime(
            2021, 6, 15, 14, 30, 0, tzinfo=timezone.utc
        )  # Tuesday 2:30 PM

        self.media = Media(
            uri="test.jpg", media_type=MediaType.IMAGE, creation_timestamp=base_time
        )

        self.posts = [
            Post(
                media=[self.media],
                timestamp=base_time,  # Tuesday 2:30 PM
                likes_count=10,
                comments_count=2,
            ),
            Post(
                media=[self.media],
                timestamp=base_time + timedelta(hours=2),  # Tuesday 4:30 PM
                likes_count=15,
                comments_count=3,
            ),
            Post(
                media=[self.media],
                timestamp=base_time + timedelta(days=1, hours=-4),  # Wednesday 10:30 AM
                likes_count=8,
                comments_count=1,
            ),
        ]

        self.stories = []
        self.reels = []

    def test_hourly_patterns(self):
        """Test hourly activity analysis."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels)

        hourly_activity = stats["hourly_activity"]

        # Should have activity at hours 10, 14, and 16
        assert hourly_activity[10] == 1  # 10:30 AM post
        assert hourly_activity[14] == 1  # 2:30 PM post
        assert hourly_activity[16] == 1  # 4:30 PM post

        # Most active period should be afternoon (12-18)
        assert stats["most_active_period"] == "afternoon"

    def test_daily_patterns(self):
        """Test daily activity analysis."""
        stats = self.analyzer.analyze(self.posts, self.stories, self.reels)

        daily_activity = stats["daily_activity"]

        # Should have 2 posts on Tuesday, 1 on Wednesday
        assert daily_activity["Tuesday"] == 2
        assert daily_activity["Wednesday"] == 1

        assert stats["peak_day"] == "Tuesday"
        assert stats["peak_day_posts"] == 2

    def test_empty_content(self):
        """Test analyzer with empty content."""
        stats = self.analyzer.analyze([], [], [])

        assert stats == {}

    def test_activity_streaks(self):
        """Test activity streak calculation."""
        # Create posts on consecutive days
        base_time = datetime(2021, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        consecutive_posts = []
        for i in range(5):  # 5 consecutive days
            post = Post(
                media=[self.media],
                timestamp=base_time + timedelta(days=i),
                likes_count=10,
                comments_count=2,
            )
            consecutive_posts.append(post)

        stats = self.analyzer.analyze(consecutive_posts, [], [])

        assert stats["total_active_days"] == 5
        assert stats["longest_active_streak_days"] == 5
