"""Basic statistics analyzer for Instagram data."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter

from ..models import Post, Story, Reel, Profile
from ..utils import get_time_period_stats, group_dates_by_period


class BasicStatsAnalyzer:
    """Analyzer for basic Instagram statistics."""
    
    def analyze(self, posts: List[Post], stories: List[Story], 
                reels: List[Reel], profile: Optional[Profile] = None) -> Dict[str, Any]:
        """Analyze basic statistics from Instagram data.
        
        Args:
            posts: List of posts
            stories: List of stories
            reels: List of reels
            profile: Profile information
            
        Returns:
            Dictionary containing basic statistics
        """
        stats = {}
        
        # Content counts
        stats.update(self._get_content_counts(posts, stories, reels))
        
        # Engagement stats
        stats.update(self._get_engagement_stats(posts, reels))
        
        # Time period analysis
        stats.update(self._get_time_analysis(posts, stories, reels))
        
        # Content analysis
        stats.update(self._get_content_analysis(posts, reels))
        
        # Profile stats
        if profile:
            stats.update(self._get_profile_stats(profile))
        
        return stats
    
    def _get_content_counts(self, posts: List[Post], stories: List[Story], 
                           reels: List[Reel]) -> Dict[str, int]:
        """Calculate content counts."""
        return {
            "total_posts": len(posts),
            "total_stories": len(stories), 
            "total_reels": len(reels),
            "total_content": len(posts) + len(stories) + len(reels)
        }
    
    def _get_engagement_stats(self, posts: List[Post], reels: List[Reel]) -> Dict[str, Any]:
        """Calculate engagement statistics."""
        stats = {
            "total_likes": 0,
            "total_comments": 0,
            "average_likes_per_post": 0,
            "average_comments_per_post": 0,
            "most_liked_post_likes": 0,
            "most_commented_post_comments": 0
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
            stats["average_comments_per_post"] = stats["total_comments"] / len(all_content)
        
        if likes_counts:
            stats["most_liked_post_likes"] = max(likes_counts)
        
        if comments_counts:
            stats["most_commented_post_comments"] = max(comments_counts)
        
        # Engagement rate calculation
        stats["engagement_rate"] = self._calculate_engagement_rate(all_content)
        
        return stats
    
    def _calculate_engagement_rate(self, content: List) -> float:
        """Calculate overall engagement rate."""
        if not content:
            return 0.0
        
        total_engagement = sum(
            item.likes_count + item.comments_count 
            for item in content
        )
        
        return total_engagement / len(content) if content else 0.0
    
    def _get_time_analysis(self, posts: List[Post], stories: List[Story], 
                          reels: List[Reel]) -> Dict[str, Any]:
        """Analyze time-based patterns."""
        all_dates = []
        
        # Collect all timestamps
        for post in posts:
            all_dates.append(post.timestamp)
        for story in stories:
            all_dates.append(story.timestamp)
        for reel in reels:
            all_dates.append(reel.timestamp)
        
        if not all_dates:
            return {}
        
        # Basic time stats
        time_stats = get_time_period_stats(all_dates)
        
        # Monthly activity
        monthly_activity = group_dates_by_period(all_dates, "month")
        time_stats["monthly_activity"] = monthly_activity
        time_stats["most_active_month"] = max(monthly_activity.items(), key=lambda x: x[1]) if monthly_activity else None
        
        # Weekly activity  
        weekly_activity = group_dates_by_period(all_dates, "week")
        time_stats["weekly_activity"] = weekly_activity
        
        # Activity consistency
        time_stats["posting_consistency"] = self._calculate_consistency(all_dates)
        
        return time_stats
    
    def _calculate_consistency(self, dates: List[datetime]) -> Dict[str, Any]:
        """Calculate posting consistency metrics."""
        if len(dates) < 2:
            return {"consistency_score": 0, "average_gap_days": 0}
        
        sorted_dates = sorted(dates)
        gaps = []
        
        for i in range(1, len(sorted_dates)):
            gap = (sorted_dates[i] - sorted_dates[i-1]).days
            gaps.append(gap)
        
        average_gap = sum(gaps) / len(gaps)
        
        # Calculate consistency score (lower variance = higher consistency)
        if len(gaps) > 1:
            variance = sum((gap - average_gap) ** 2 for gap in gaps) / len(gaps)
            consistency_score = max(0, 100 - (variance / average_gap * 10))
        else:
            consistency_score = 100
        
        return {
            "consistency_score": round(consistency_score, 2),
            "average_gap_days": round(average_gap, 2),
            "median_gap_days": sorted(gaps)[len(gaps)//2] if gaps else 0
        }
    
    def _get_content_analysis(self, posts: List[Post], reels: List[Reel]) -> Dict[str, Any]:
        """Analyze content patterns."""
        stats = {}
        
        # Media type analysis
        media_types = {"image": 0, "video": 0, "carousel": 0}
        
        for post in posts:
            if post.is_carousel:
                media_types["carousel"] += 1
            elif post.has_video:
                media_types["video"] += 1
            else:
                media_types["image"] += 1
        
        # Reels are all video
        media_types["video"] += len(reels)
        
        stats["media_types"] = media_types
        
        # Caption analysis
        caption_stats = self._analyze_captions(posts, reels)
        stats.update(caption_stats)
        
        # Hashtag analysis
        hashtag_stats = self._analyze_hashtags(posts, reels)
        stats.update(hashtag_stats)
        
        return stats
    
    def _analyze_captions(self, posts: List[Post], reels: List[Reel]) -> Dict[str, Any]:
        """Analyze caption patterns."""
        all_content = posts + reels
        captions = [content.caption for content in all_content if content.caption]
        
        if not captions:
            return {
                "average_caption_length": 0,
                "posts_with_captions": 0,
                "caption_usage_rate": 0
            }
        
        # Length analysis
        caption_lengths = [len(caption) for caption in captions]
        word_counts = [len(caption.split()) for caption in captions]
        
        return {
            "average_caption_length": sum(caption_lengths) / len(caption_lengths),
            "average_word_count": sum(word_counts) / len(word_counts),
            "posts_with_captions": len(captions),
            "caption_usage_rate": len(captions) / len(all_content) * 100,
            "longest_caption_length": max(caption_lengths),
            "shortest_caption_length": min(caption_lengths)
        }
    
    def _analyze_hashtags(self, posts: List[Post], reels: List[Reel]) -> Dict[str, Any]:
        """Analyze hashtag usage patterns."""
        all_hashtags = []
        content_with_hashtags = 0
        
        for content in posts + reels:
            if content.hashtags:
                all_hashtags.extend(content.hashtags)
                content_with_hashtags += 1
        
        if not all_hashtags:
            return {
                "total_hashtags": 0,
                "unique_hashtags": 0,
                "average_hashtags_per_post": 0,
                "hashtag_usage_rate": 0,
                "top_hashtags": []
            }
        
        hashtag_counter = Counter(all_hashtags)
        total_content = len(posts) + len(reels)
        
        return {
            "total_hashtags": len(all_hashtags),
            "unique_hashtags": len(hashtag_counter),
            "average_hashtags_per_post": len(all_hashtags) / total_content,
            "hashtag_usage_rate": content_with_hashtags / total_content * 100,
            "top_hashtags": hashtag_counter.most_common(10),
            "hashtag_diversity": len(hashtag_counter) / len(all_hashtags) if all_hashtags else 0
        }
    
    def _get_profile_stats(self, profile: Profile) -> Dict[str, Any]:
        """Get profile-specific statistics."""
        return {
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
            "has_bio": bool(profile.bio)
        }