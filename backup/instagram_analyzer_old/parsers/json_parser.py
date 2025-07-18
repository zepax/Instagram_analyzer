"""JSON parser for Instagram data files."""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import (
    Comment,
    Like,
    Media,
    MediaType,
    Post,
    Profile,
    Reel,
    Story,
    StoryInteraction,
    User,
)
from ..utils import parse_instagram_date, safe_json_load
from ..utils.streaming_parser import (
    BatchProcessor,
    StreamingJSONParser,
    should_use_streaming,
)


class JSONParser:
    """Parses Instagram JSON data files into structured models."""

    def __init__(self, memory_threshold: int = 50 * 1024 * 1024):
        """Initialize JSON parser with memory optimization.

        Args:
            memory_threshold: File size threshold for using streaming mode
        """
        self.streaming_parser = StreamingJSONParser(memory_threshold)
        self.batch_processor = BatchProcessor()

    def parse_profile(self, data: dict[str, Any]) -> Profile:
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
            raw_data=profile_data,
        )

    def parse_posts(self, data: list[dict[str, Any]]) -> list[Post]:
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

    def parse_stories(self, data: list[dict[str, Any]]) -> list[Story]:
        """Parse stories data from JSON.

        Args:
            data: Raw stories data from JSON

        Returns:
            List of Story model instances
        """
        stories = []

        # Handle different data formats
        stories_data = data
        if isinstance(data, dict):
            # Some exports wrap stories in a container
            if "ig_stories" in data:
                stories_data = data["ig_stories"]
            elif "stories" in data:
                stories_data = data["stories"]

        for story_data in stories_data:
            try:
                story = self._parse_single_story(story_data)
                if story:
                    stories.append(story)
            except Exception:
                # Skip invalid stories
                continue

        return stories

    def parse_reels(self, data: list[dict[str, Any]]) -> list[Reel]:
        """Parse reels data from JSON.

        Args:
            data: Raw reels data from JSON

        Returns:
            List of Reel model instances
        """
        reels = []

        # Handle different data formats
        reels_data = data
        if isinstance(data, dict):
            # Some exports wrap reels in a container
            if "reels" in data:
                reels_data = data["reels"]

        for reel_data in reels_data:
            try:
                reel = self._parse_single_reel(reel_data)
                if reel:
                    reels.append(reel)
            except Exception:
                # Skip invalid reels
                continue

        return reels

    def parse_archived_posts(self, data: list[dict[str, Any]]) -> list[Post]:
        """Parse archived posts data from JSON."""
        return self.parse_posts(data)

    def parse_recently_deleted(self, data: list[dict[str, Any]]) -> list[Media]:
        """Parse recently deleted media data from JSON."""
        media_list = []

        deleted_data = data
        if isinstance(data, dict) and "deleted_content" in data:
            deleted_data = data["deleted_content"]

        for media_data in deleted_data:
            try:
                media = self._parse_single_media(media_data)
                if media:
                    media_list.append(media)
            except Exception:
                continue

        return media_list

    def parse_story_interactions(
        self, data: list[dict[str, Any]], interaction_type: str
    ) -> list[StoryInteraction]:
        """Parse story interactions data from JSON."""
        interactions = []

        interactions_data = data
        if isinstance(data, dict):
            if "story_activities" in data:
                interactions_data = data["story_activities"]
            elif "interactions" in data:
                interactions_data = data["interactions"]

        for interaction_data in interactions_data:
            try:
                interaction = self._parse_single_story_interaction(
                    interaction_data, interaction_type
                )
                if interaction:
                    interactions.append(interaction)
            except Exception:
                continue

        return interactions

    def parse_posts_from_file(self, file_path: str) -> list[Post]:
        """Parse posts from a JSON file, using streaming for large files."""
        if should_use_streaming(file_path, self.streaming_parser.threshold):
            return self.streaming_parser.parse(
                file_path, self.batch_processor.process_posts
            )
        else:
            data = safe_json_load(file_path)
            return self.parse_posts(data)

    def parse_stories_from_file(self, file_path: str) -> list[Story]:
        """Parse stories from a JSON file, using streaming for large files."""
        if should_use_streaming(file_path, self.streaming_parser.threshold):
            return self.streaming_parser.parse(
                file_path, self.batch_processor.process_stories
            )
        else:
            data = safe_json_load(file_path)
            return self.parse_stories(data)

    def parse_reels_from_file(self, file_path: str) -> list[Reel]:
        """Parse reels from a JSON file."""
        data = safe_json_load(file_path)
        return self.parse_reels(data)

    def parse_archived_posts_from_file(self, file_path: str) -> list[Post]:
        """Parse archived posts from a JSON file."""
        data = safe_json_load(file_path)
        return self.parse_archived_posts(data)

    def parse_media_from_file(self, file_path: str) -> list[Media]:
        """Parse generic media from a JSON file (for recently deleted)."""
        data = safe_json_load(file_path)
        return self.parse_recently_deleted(data)

    def parse_story_interactions_from_file(
        self, file_path: str, interaction_type: str
    ) -> list[StoryInteraction]:
        """Parse story interactions from a JSON file."""
        data = safe_json_load(file_path)
        return self.parse_story_interactions(data, interaction_type)

    def _parse_single_post(self, data: dict[str, Any]) -> Optional[Post]:
        """Parse a single post from JSON data."""
        # Handle different post data formats
        post_data = data

        # Some exports wrap post data
        if "post" in data:
            post_data = data["post"]
        elif "media" in data:
            post_data = data["media"]

        # Extract media
        media_list = self._extract_media(post_data)
        if not media_list:
            return None

        # Extract timestamp
        timestamp = self._parse_timestamp(post_data)
        if not timestamp:
            return None

        # Parse comments
        comments = self._parse_comments(post_data.get("comments", []))

        # Parse likes
        likes = self._parse_likes(post_data.get("likes", []))

        # Extract hashtags and mentions from caption
        caption = post_data.get("caption") or post_data.get("title", "")
        hashtags = self._extract_hashtags(caption)
        mentions = self._extract_mentions(caption)

        likes_count = post_data.get("like_count", len(likes))
        comments_count = post_data.get("comment_count", len(comments))

        return Post(
            caption=caption,
            media=media_list,
            timestamp=timestamp,
            post_id=post_data.get("id") or post_data.get("pk"),
            location=(
                post_data.get("location", {}).get("name")
                if post_data.get("location")
                else None
            ),
            likes=likes,
            comments=comments,
            likes_count=likes_count,
            comments_count=comments_count,
            hashtags=hashtags,
            mentions=mentions,
            raw_data=post_data,
        )

    def _parse_single_story(self, data: dict[str, Any]) -> Optional[Story]:
        """Parse a single story from its JSON data."""
        uri = data.get("uri")
        taken_at = self._parse_date(
            data.get("taken_at") or data.get("creation_timestamp")
        )

        if not uri or not taken_at:
            return None

        return Story(
            media=Media(
                uri=uri,
                creation_timestamp=taken_at.timestamp(),
                media_type=MediaType.STORY,
                title=data.get("title", ""),
            ),
            taken_at=taken_at,
            caption=data.get("caption", ""),
            raw_data=data,
        )

    def _parse_single_reel(self, data: dict[str, Any]) -> Optional[Reel]:
        """Parse a single reel from its JSON data."""
        uri = data.get("uri")
        taken_at = self._parse_date(
            data.get("taken_at") or data.get("creation_timestamp")
        )

        if not uri or not taken_at:
            return None

        return Reel(
            media=Media(
                uri=uri,
                creation_timestamp=taken_at.timestamp(),
                media_type=MediaType.REEL,
                title=data.get("title", ""),
            ),
            taken_at=taken_at,
            caption=data.get("caption", ""),
            raw_data=data,
        )

    def _parse_single_media(self, data: dict[str, Any]) -> Optional[Media]:
        """Parse a single media item from JSON data."""
        uri = data.get("uri", "")
        media_type = self._get_media_type_from_uri(uri)

        return Media(
            uri=uri,
            timestamp=self._parse_date(
                data.get("creation_timestamp") or data.get("taken_at")
            ),
            media_type=media_type,
            title=data.get("title"),
            raw_data=data,
        )

    def _parse_single_story_interaction(
        self, data: dict[str, Any], interaction_type: str
    ) -> Optional[StoryInteraction]:
        """Parse a single story interaction from JSON data."""
        # Data is often a list of dicts with 'string_map_data'
        if "string_map_data" in data:
            interaction_data = data["string_map_data"]
        else:
            interaction_data = data

        # Extract username and timestamp
        username = ""
        for key in ["username", "author", "user"]:
            if key in interaction_data:
                username = interaction_data[key].get("value", "")
                break

        timestamp = None
        for key in ["time", "timestamp"]:
            if key in interaction_data:
                timestamp = self._parse_date(interaction_data[key].get("timestamp"))
                break

        return StoryInteraction(
            interaction_type=interaction_type,
            username=username,
            timestamp=timestamp,
            raw_data=data,
        )

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Safely parse date string into datetime object."""
        if not date_str:
            return None
        try:
            return parse_instagram_date(date_str)
        except (ValueError, TypeError):
            return None

    def _get_media_type_from_uri(self, uri: str) -> MediaType:
        """Determine media type from its URI."""
        if not uri:
            return MediaType.UNKNOWN

        path = Path(uri)
        ext = path.suffix.lower()

        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            return MediaType.IMAGE
        elif ext in [".mp4", ".mov", ".avi"]:
            return MediaType.VIDEO
        else:
            return MediaType.UNKNOWN

    def _extract_media(self, data: dict[str, Any]) -> list[Media]:
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

        # Handle cases where media is at the top level
        elif "uri" in data:
            media = self._create_media_from_data(data)
            if media:
                media_list.append(media)

        return media_list

    def _extract_single_media(
        self, data: dict[str, Any], media_type: Optional[MediaType] = None
    ) -> Optional[Media]:
        """Extract single media from data."""
        media_list = self._extract_media(data)
        if media_list:
            return media_list[0]
        return None

    def _create_media_from_data(self, data: dict[str, Any]) -> Optional[Media]:
        """Create Media object from data."""
        uri = data.get("uri")
        if not uri:
            return None

        # Determine media type
        media_type = self._get_media_type_from_uri(uri)

        return Media(
            uri=uri,
            media_type=media_type,
            creation_timestamp=self._parse_timestamp(data) or datetime.now(timezone.utc),
            title=data.get("title"),
            width=data.get("width"),
            height=data.get("height"),
            duration=data.get("duration"),
        )

    def _parse_timestamp(self, data: dict[str, Any]) -> Optional[datetime]:
        """Parse timestamp from various possible fields."""
        timestamp_fields = [
            "creation_timestamp",
            "timestamp",
            "taken_at",
            "created_at",
            "date_created",
        ]

        for field in timestamp_fields:
            if field in data:
                return parse_instagram_date(data[field])

        return None

    def _parse_comments(self, comments_data: list[dict[str, Any]]) -> list[Comment]:
        """Parse comments from data."""
        comments = []

        for comment_data in comments_data:
            try:
                # Handle different comment structures
                text = ""
                author_username = ""

                if "string_map_data" in comment_data:
                    # New format
                    string_map = comment_data["string_map_data"]
                    text = string_map.get("Comment", {}).get("value", "")
                    author_username = string_map.get("Author", {}).get("value", "")
                elif "text" in comment_data:
                    # Old format
                    text = comment_data["text"]
                    author_username = comment_data.get("user", {}).get("username", "")

                user = User(username=author_username)
                comment = Comment(
                    text=text,
                    timestamp=self._parse_timestamp(comment_data)
                    or datetime.now(timezone.utc),
                    author=user,
                    comment_id=comment_data.get("id"),
                    raw_data=comment_data,
                )
                comments.append(comment)
            except Exception:
                continue

        return comments

    def _parse_likes(self, likes_data: list[dict[str, Any]]) -> list[Like]:
        """Parse likes from data."""
        likes = []

        for like_data in likes_data:
            try:
                # Handle different like structures
                username = ""
                if "string_map_data" in like_data:
                    string_map = like_data["string_map_data"]
                    username = string_map.get("Author", {}).get("value", "")
                elif "username" in like_data:
                    username = like_data["username"]

                user = User(username=username)
                like = Like(
                    user=user,
                    timestamp=self._parse_timestamp(like_data)
                    or datetime.now(timezone.utc),
                    raw_data=like_data,
                )
                likes.append(like)
            except Exception:
                continue

        return likes

    def _extract_hashtags(self, text: str) -> list[str]:
        """Extract hashtags from text."""
        if not text:
            return []

        hashtags = [word for word in text.split() if word.startswith("#")]
        return hashtags

    def _extract_mentions(self, text: str) -> list[str]:
        """Extract mentions from text."""
        if not text:
            return []

        mentions = [word for word in text.split() if word.startswith("@")]
        return mentions

    def _find_engagement_by_timestamp(
        self,
        post_timestamp: datetime,
        liked_posts: dict[str, Any],
        post_comments: dict[str, Any],
    ) -> dict[str, int]:
        """Find engagement data by matching timestamps.

        Args:
            post_timestamp: Timestamp of the post
            liked_posts: Liked posts data
            post_comments: Post comments data

        Returns:
            Dictionary with likes_count and comments_count
        """
        likes_count = 0
        comments_count = 0

        # Look for likes with similar timestamps (within 1 hour)
        for url, like_data in liked_posts.items():
            if like_data.get("datetime"):
                time_diff = abs((post_timestamp - like_data["datetime"]).total_seconds())
                if time_diff <= 3600:  # Within 1 hour
                    likes_count += 1

        # Look for comments with similar timestamps
        for url, comments_list in post_comments.items():
            for comment in comments_list:
                if comment.get("datetime"):
                    time_diff = abs(
                        (post_timestamp - comment["datetime"]).total_seconds()
                    )
                    if time_diff <= 3600:  # Within 1 hour
                        comments_count += 1

        return {"likes_count": likes_count, "comments_count": comments_count}

    def _find_engagement_by_media(
        self,
        media_list: list[Media],
        caption: str,
        liked_posts: dict[str, Any],
        post_comments: dict[str, Any],
    ) -> dict[str, int]:
        """Find engagement data by matching media URIs or captions.

        Args:
            media_list: List of media objects
            caption: Post caption
            liked_posts: Liked posts data
            post_comments: Post comments data

        Returns:
            Dictionary with likes_count and comments_count
        """
        likes_count = 0
        comments_count = 0

        # Extract potential identifiers from media URIs
        media_identifiers = []
        for media in media_list:
            if media.uri:
                # Extract filename or ID from URI
                filename = Path(media.uri).name
                media_identifiers.append(filename)

        # Look for engagement data that might match these identifiers
        for url in liked_posts.keys():
            for identifier in media_identifiers:
                if identifier in url and len(identifier) > 5:  # Avoid short matches
                    likes_count += 1
                    break

        for url in post_comments.keys():
            for identifier in media_identifiers:
                if identifier in url and len(identifier) > 5:  # Avoid short matches
                    comments_count += len(post_comments[url])
                    break

        return {"likes_count": likes_count, "comments_count": comments_count}

    def _get_engagement_stats(
        self, posts: list[Post], engagement_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Get engagement statistics for posts."""
        stats = {
            "total_likes": 0,
            "total_comments": 0,
            "top_hashtags": [],
            "top_mentions": [],
        }

        from collections import Counter

        all_hashtags = []
        all_mentions = []

        for post in posts:
            all_hashtags.extend(post.hashtags)
            all_mentions.extend(post.mentions)
            stats["total_likes"] += post.likes_count
            stats["total_comments"] += post.comments_count

        stats["top_hashtags"] = Counter(all_hashtags).most_common(10)
        stats["top_mentions"] = Counter(all_mentions).most_common(10)

        return stats

    def enrich_posts_with_engagement(
        self, posts: list[Post], engagement_data: dict[str, Any]
    ) -> list[Post]:
        """Enrich posts with engagement data like comments and likes."""

        # Create a mapping from post ID to post
        post_map = {post.post_id: post for post in posts if post.post_id}

        # Process comments
        for comment_thread in engagement_data.get("post_comments", []):
            post_id = comment_thread.get("post_id")
            if post_id in post_map:
                # Assuming comments are not already parsed in the post
                # This logic can be improved to merge comments if needed
                post_map[post_id].comments.extend(comment_thread.get("comments", []))
                post_map[post_id].comments_count = len(post_map[post_id].comments)

        # Process likes (if available and structured by post)
        # This part is highly dependent on the structure of liked_posts.json
        # For now, we assume likes are already part of the post data if available

        return list(post_map.values())
