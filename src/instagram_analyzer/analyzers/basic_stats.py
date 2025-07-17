"""Basic statistics analyzer for Instagram data."""

from collections import Counter
from datetime import timedelta
from typing import Any, Dict, List, Optional

from ..models import Media, Post, Profile, Reel, Story, StoryInteraction
from ..utils import get_time_period_stats, group_dates_by_period


class BasicStatsAnalyzer:
    """Analyzer for basic Instagram statistics."""

    def analyze(
        self,
        posts: list[Post],
        stories: list[Story],
        reels: list[Reel],
        profile: Optional[Profile] = None,
        archived_posts: list[Post] = [],
        recently_deleted: list[Media] = [],
        story_interactions: list[StoryInteraction] = [],
    ) -> dict[str, Any]:
        """Analyze basic statistics from Instagram data.

        Args:
            posts: List of posts
            stories: List of stories
            reels: List of reels
            profile: Profile information
            archived_posts: List of archived posts
            recently_deleted: List of recently deleted media
            story_interactions: List of story interactions

        Returns:
            Dictionary containing basic statistics
        """
        stats = {}

        # Content counts
        stats.update(
            self._get_content_counts(
                posts, stories, reels, archived_posts, recently_deleted
            )
        )

        # Engagement stats
        stats.update(self._get_engagement_stats(posts, reels))

        # Time period analysis
        stats.update(self._get_time_analysis(posts, stories, reels, archived_posts))

        # Content analysis
        stats.update(self._get_content_analysis(posts, reels))

        # Story interaction analysis
        stats.update(self._get_story_interaction_stats(story_interactions))

        # Profile stats
        if profile:
            stats.update(self._get_profile_stats(profile))

        return stats

    def _get_content_counts(
        self,
        posts: list[Post],
        stories: list[Story],
        reels: list[Reel],
        archived_posts: list[Post],
        recently_deleted: list[Media],
    ) -> dict[str, int]:
        """Calculate content counts."""
        return {
            "total_posts": len(posts),
            "total_stories": len(stories),
            "total_reels": len(reels),
            "total_archived_posts": len(archived_posts),
            "total_recently_deleted": len(recently_deleted),
            "total_content": len(posts) + len(stories) + len(reels),
        }

    def _get_engagement_stats(
        self, posts: list[Post], reels: list[Reel]
    ) -> dict[str, Any]:
        """Calculate engagement statistics."""
        stats = {
            "total_likes": 0,
            "total_comments": 0,
            "average_likes_per_post": 0.0,
            "average_comments_per_post": 0.0,
            "most_liked_post_likes": 0,
            "most_commented_post_comments": 0,
            "engagement_rate": 0.0,
        }

        if not posts and not reels:
            return stats

        all_content = posts + reels
        likes_counts = [content.likes_count for content in all_content]
        comments_counts = [content.comments_count for content in all_content]

        stats["total_likes"] = sum(likes_counts)
        stats["total_comments"] = sum(comments_counts)

        if all_content:
            stats["average_likes_per_post"] = stats["total_likes"] / len(all_content)
            stats["average_comments_per_post"] = stats["total_comments"] / len(
                all_content
            )

        if likes_counts:
            stats["most_liked_post_likes"] = max(likes_counts)

        if comments_counts:
            stats["most_commented_post_comments"] = max(comments_counts)

        # Engagement rate calculation
        stats["engagement_rate"] = self._calculate_engagement_rate(all_content)

        return stats

    def _calculate_engagement_rate(self, content: list) -> float:
        """Calculate overall engagement rate."""
        if not content:
            return 0.0

        total_engagement = sum(item.likes_count + item.comments_count for item in content)

        return total_engagement / len(content) if content else 0.0

    def _get_time_analysis(
        self,
        posts: list[Post],
        stories: list[Story],
        reels: list[Reel],
        archived_posts: list[Post],
    ) -> dict[str, Any]:
        """Analyze content over time periods."""
        all_content = posts + stories + reels + archived_posts

        if not all_content:
            return {
                "total_posts": 0,
                "total_stories": 0,
                "total_reels": 0,
                "total_archived_posts": 0,
                "total_content": 0,
            }

        timestamps = [content.timestamp for content in all_content if content.timestamp]

        if not timestamps:
            return {
                "total_posts": 0,
                "total_stories": 0,
                "total_reels": 0,
                "total_archived_posts": 0,
                "total_content": 0,
            }

        # Daily, weekly, monthly analysis
        daily_activity = Counter(timestamp.date() for timestamp in timestamps)
        weekly_activity = Counter(
            (timestamp - timedelta(days=timestamp.weekday())).date()
            for timestamp in timestamps
        )
        monthly_activity = Counter(timestamp.replace(day=1) for timestamp in timestamps)

        return {
            "total_posts": len([p for p in posts if p.timestamp]),
            "total_stories": len([s for s in stories if s.timestamp]),
            "total_reels": len([r for r in reels if r.timestamp]),
            "total_archived_posts": len([ap for ap in archived_posts if ap.timestamp]),
            "daily_activity": {str(k): v for k, v in daily_activity.items()},
            "weekly_activity": {str(k): v for k, v in weekly_activity.items()},
            "monthly_activity": {str(k): v for k, v in monthly_activity.items()},
            "most_active_day": daily_activity.most_common(1),
            "most_active_week": weekly_activity.most_common(1),
            "most_active_month": monthly_activity.most_common(1),
        }

    def _get_content_analysis(
        self, posts: list[Post], reels: list[Reel]
    ) -> dict[str, Any]:
        """Analyze content properties like hashtags and mentions."""
        stats = {
            "top_hashtags": [],
            "top_mentions": [],
            "total_hashtags": 0,
            "unique_hashtags": 0,
        }

        all_content = posts + reels

        if not all_content:
            return stats

        # Hashtag analysis - first try the hashtags field, then parse from caption
        all_hashtags = []
        for item in all_content:
            # Use hashtags field if available
            if hasattr(item, "hashtags") and item.hashtags:
                all_hashtags.extend(item.hashtags)
            # Fallback to parsing from caption
            elif item.caption:
                hashtags_from_caption = [
                    word[1:] for word in item.caption.split() if word.startswith("#")
                ]
                all_hashtags.extend(hashtags_from_caption)

        if all_hashtags:
            hashtag_counts = Counter(all_hashtags)
            stats["top_hashtags"] = hashtag_counts.most_common(10)
            stats["total_hashtags"] = len(all_hashtags)
            stats["unique_hashtags"] = len(hashtag_counts)

        # Mention analysis
        all_mentions = []
        for item in all_content:
            if item.caption:
                all_mentions.extend(
                    [word for word in item.caption.split() if word.startswith("@")]
                )

        if all_mentions:
            stats["top_mentions"] = Counter(all_mentions).most_common(10)

        return stats

    def _get_story_interaction_stats(
        self, interactions: list[StoryInteraction]
    ) -> dict[str, Any]:
        """Analyze story interaction data."""
        if not interactions:
            return {
                "total_story_interactions": 0,
                "story_interaction_types": {},
                "top_story_interactors": [],
            }

        interaction_types = Counter(i.interaction_type for i in interactions)
        # Since story interactions are from the same user, we don't have usernames
        # We can show interaction titles instead
        top_titles = Counter(i.title for i in interactions if i.title).most_common(10)

        return {
            "total_story_interactions": len(interactions),
            "story_interaction_types": dict(interaction_types),
            "top_interaction_titles": top_titles,
        }

    def _get_profile_stats(self, profile: Profile) -> dict[str, Any]:
        """Extract statistics from profile data."""
        stats = {
            "profile_username": profile.username,
            "profile_name": profile.name,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "is_business": profile.is_business,
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "profile_posts_count": profile.posts_count,
            "bio_length": len(profile.bio) if profile.bio else 0,
            "has_website": bool(profile.website),
            "has_bio": bool(profile.bio),
            "profile_category": profile.category,
            "profile_is_business": profile.is_business,
        }

        # Follower/Following Ratio
        if (
            profile.following_count
            and profile.following_count > 0
            and profile.followers_count is not None
        ):
            stats["follower_following_ratio"] = (
                profile.followers_count / profile.following_count
            )
        else:
            stats["follower_following_ratio"] = profile.followers_count or 0

        return stats
