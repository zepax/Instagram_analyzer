"""JSON parser for Instagram data files."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models import Post, Story, Reel, Profile, User, Media, MediaType, Comment, Like
from ..utils import parse_instagram_date


class JSONParser:
    """Parses Instagram JSON data files into structured models."""
    
    def parse_profile(self, data: Dict[str, Any]) -> Profile:
        """Parse profile data from JSON.
        
        Args:
            data: Raw profile data from JSON
            
        Returns:
            Profile model instance
        """
        # Handle different profile data formats
        profile_data = data
        
        # Some exports wrap profile data
        if "profile_user" in data:
            profile_data = data["profile_user"]
        elif "account_information" in data:
            profile_data = data["account_information"]
        
        return Profile(
            username=profile_data.get("username", ""),
            name=profile_data.get("name") or profile_data.get("full_name"),
            bio=profile_data.get("biography") or profile_data.get("bio"),
            website=profile_data.get("external_url") or profile_data.get("website"),
            email=profile_data.get("email"),
            phone_number=profile_data.get("phone_number"),
            followers_count=profile_data.get("follower_count", 0),
            following_count=profile_data.get("following_count", 0),
            posts_count=profile_data.get("media_count", 0),
            is_private=profile_data.get("is_private", False),
            is_verified=profile_data.get("is_verified", False),
            is_business=profile_data.get("is_business_account", False),
            date_joined=self._parse_date(profile_data.get("date_joined")),
            profile_pic_url=profile_data.get("profile_pic_url"),
            category=profile_data.get("category"),
            raw_data=profile_data
        )
    
    def parse_posts(self, data: List[Dict[str, Any]]) -> List[Post]:
        """Parse posts data from JSON.
        
        Args:
            data: Raw posts data from JSON
            
        Returns:
            List of Post model instances
        """
        posts = []
        
        # Handle different data formats
        posts_data = data
        if isinstance(data, dict):
            # Some exports wrap posts in a container
            if "posts" in data:
                posts_data = data["posts"]
            elif "data" in data:
                posts_data = data["data"]
            elif "items" in data:
                posts_data = data["items"]
        
        for post_data in posts_data:
            try:
                post = self._parse_single_post(post_data)
                if post:
                    posts.append(post)
            except Exception:
                # Skip invalid posts
                continue
        
        return posts
    
    def _parse_single_post(self, data: Dict[str, Any]) -> Optional[Post]:
        """Parse a single post from JSON data."""
        # Extract media
        media_list = self._extract_media(data)
        if not media_list:
            return None
        
        # Extract timestamp
        timestamp = self._parse_timestamp(data)
        if not timestamp:
            return None
        
        # Parse comments
        comments = self._parse_comments(data.get("comments", []))
        
        # Parse likes  
        likes = self._parse_likes(data.get("likes", []))
        
        # Extract hashtags and mentions from caption
        caption = data.get("caption") or data.get("title", "")
        hashtags = self._extract_hashtags(caption)
        mentions = self._extract_mentions(caption)
        
        likes_count = data.get("like_count", len(likes))
        comments_count = data.get("comment_count", len(comments))

        return Post(
            caption=caption,
            media=media_list,
            timestamp=timestamp,
            post_id=data.get("id") or data.get("pk"),
            location=data.get("location", {}).get("name") if data.get("location") else None,
            likes=likes,
            comments=comments,
            likes_count=likes_count,
            comments_count=comments_count,
            hashtags=hashtags,
            mentions=mentions,
            raw_data=data,
        )
    
    def parse_stories(self, data: List[Dict[str, Any]]) -> List[Story]:
        """Parse stories data from JSON.
        
        Args:
            data: Raw stories data from JSON
            
        Returns:
            List of Story model instances
        """
        stories = []
        
        for story_data in data:
            try:
                story = self._parse_single_story(story_data)
                if story:
                    stories.append(story)
            except Exception:
                continue
        
        return stories
    
    def _parse_single_story(self, data: Dict[str, Any]) -> Optional[Story]:
        """Parse a single story from JSON data."""
        # Extract media
        media = self._extract_single_media(data)
        if not media:
            return None
        
        # Extract timestamp
        timestamp = self._parse_timestamp(data)
        if not timestamp:
            return None
        
        return Story(
            media=media,
            timestamp=timestamp,
            story_id=data.get("id") or data.get("pk"),
            raw_data=data
        )
    
    def parse_reels(self, data: List[Dict[str, Any]]) -> List[Reel]:
        """Parse reels data from JSON.
        
        Args:
            data: Raw reels data from JSON
            
        Returns:
            List of Reel model instances
        """
        reels = []
        
        for reel_data in data:
            try:
                reel = self._parse_single_reel(reel_data)
                if reel:
                    reels.append(reel)
            except Exception:
                continue
        
        return reels
    
    def _parse_single_reel(self, data: Dict[str, Any]) -> Optional[Reel]:
        """Parse a single reel from JSON data."""
        # Extract video media
        media = self._extract_single_media(data, media_type=MediaType.VIDEO)
        if not media:
            return None
        
        # Extract timestamp
        timestamp = self._parse_timestamp(data)
        if not timestamp:
            return None
        
        # Extract caption and analyze
        caption = data.get("caption") or data.get("title", "")
        hashtags = self._extract_hashtags(caption)
        mentions = self._extract_mentions(caption)
        
        return Reel(
            video=media,
            caption=caption,
            timestamp=timestamp,
            reel_id=data.get("id") or data.get("pk"),
            likes_count=data.get("like_count", 0),
            comments_count=data.get("comment_count", 0),
            hashtags=hashtags,
            mentions=mentions,
            raw_data=data
        )
    
    def _extract_media(self, data: Dict[str, Any]) -> List[Media]:
        """Extract media list from post data."""
        media_list = []
        
        # Handle different media formats
        if "media" in data:
            media_data = data["media"]
            if isinstance(media_data, list):
                for item in media_data:
                    media = self._create_media_from_data(item)
                    if media:
                        media_list.append(media)
            elif isinstance(media_data, dict):
                media = self._create_media_from_data(media_data)
                if media:
                    media_list.append(media)
        
        # Handle direct URI
        elif "uri" in data:
            media = self._create_media_from_data(data)
            if media:
                media_list.append(media)
        
        return media_list
    
    def _extract_single_media(self, data: Dict[str, Any], 
                            media_type: Optional[MediaType] = None) -> Optional[Media]:
        """Extract single media from data."""
        media_list = self._extract_media(data)
        if media_list:
            return media_list[0]
        return None
    
    def _create_media_from_data(self, data: Dict[str, Any]) -> Optional[Media]:
        """Create Media object from data."""
        uri = data.get("uri")
        if not uri:
            return None
        
        # Determine media type
        media_type = MediaType.IMAGE  # default
        if "video" in uri.lower() or data.get("media_type") == "video":
            media_type = MediaType.VIDEO
        
        return Media(
            uri=uri,
            media_type=media_type,
            creation_timestamp=self._parse_timestamp(data) or datetime.now(),
            title=data.get("title"),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration")
        )
    
    def _parse_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Parse timestamp from various possible fields."""
        timestamp_fields = [
            "creation_timestamp",
            "timestamp", 
            "taken_at",
            "created_time"
        ]
        
        for field in timestamp_fields:
            if field in data:
                return parse_instagram_date(data[field])
        
        return None
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date value."""
        if not date_value:
            return None
        return parse_instagram_date(date_value)
    
    def _parse_comments(self, comments_data: List[Dict[str, Any]]) -> List[Comment]:
        """Parse comments from data."""
        comments = []
        
        for comment_data in comments_data:
            try:
                user = User(username=comment_data.get("user", {}).get("username", ""))
                comment = Comment(
                    text=comment_data.get("text", ""),
                    timestamp=self._parse_timestamp(comment_data) or datetime.now(),
                    author=user,
                    comment_id=comment_data.get("id"),
                    raw_data=comment_data
                )
                comments.append(comment)
            except Exception:
                continue
        
        return comments
    
    def _parse_likes(self, likes_data: List[Dict[str, Any]]) -> List[Like]:
        """Parse likes from data."""
        likes = []
        
        for like_data in likes_data:
            try:
                user = User(username=like_data.get("username", ""))
                like = Like(
                    user=user,
                    timestamp=self._parse_timestamp(like_data) or datetime.now(),
                    raw_data=like_data
                )
                likes.append(like)
            except Exception:
                continue
        
        return likes
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        if not text:
            return []
        
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions