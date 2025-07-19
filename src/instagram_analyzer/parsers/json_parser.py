"""JSON parser for Instagram data files."""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import Comment, Like, Post, Profile, Reel, Story, StoryInteraction, User
from ..models.media import Media, MediaType
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
            # Handle case where profile_user is a list
            if isinstance(profile_data, list) and profile_data:
                profile_data = profile_data[0]  # Take first item
        elif "account_information" in data:
            profile_data = data["account_information"]

        # Extract profile fields from string_map_data structure if present
        if "string_map_data" in profile_data:
            string_map = profile_data["string_map_data"]
            username = string_map.get("Username", {}).get("value", "")
            name = string_map.get("Name", {}).get("value", "")
            bio = string_map.get("Bio", {}).get("value", "")
            email = string_map.get("Email", {}).get("value", "")
            website = string_map.get("Website", {}).get("value", "")
            phone_number = string_map.get("Phone Number", {}).get("value", "")
            is_private = (
                string_map.get("Private Account", {}).get("value", "").lower() == "true"
            )
            is_verified = (
                string_map.get("Verified", {}).get("value", "").lower() == "true"
            )
        else:
            # Fallback to standard field names
            username = profile_data.get("username", "")
            name = profile_data.get("name") or profile_data.get("full_name", "")
            bio = profile_data.get("biography") or profile_data.get("bio", "")
            email = profile_data.get("email", "")
            website = profile_data.get("external_url") or profile_data.get("website", "")
            phone_number = profile_data.get("phone_number", "")
            is_private = profile_data.get("is_private", False)
            is_verified = profile_data.get("is_verified", False)

        return Profile(
            username=username,
            name=name,
            bio=bio,
            website=website,
            email=email,
            phone_number=phone_number,
            followers_count=profile_data.get("follower_count", 0),
            following_count=profile_data.get("following_count", 0),
            posts_count=profile_data.get("media_count", 0),
            is_private=is_private,
            is_verified=is_verified,
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

        if data is None:
            return posts

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

        if posts_data is None:
            return posts

        for post_data in posts_data:
            try:
                post = self._parse_single_post(post_data)
                if post:
                    posts.append(post)
            except Exception as e:
                import logging

                from instagram_analyzer.exceptions import InstagramAnalyzerError

                logging.warning("Error parsing post: %s", e)
                raise InstagramAnalyzerError(
                    f"Error parsing post: {e}", context={"post_data": post_data}
                ) from e

        return posts

    def parse_stories(self, data: Any) -> list[Story]:
        """Parse stories data from JSON.

        Args:
            data: Raw stories data from JSON

        Returns:
            List of Story model instances
        """
        stories = []

        if data is None:
            return stories

        # Handle different data formats
        stories_data = data
        if isinstance(data, dict):
            # Some exports wrap stories in a container
            if "ig_stories" in data:
                stories_data = data["ig_stories"]
            elif "stories" in data:
                stories_data = data["stories"]

        if stories_data is None:
            return stories

        for i, story_data in enumerate(stories_data):
            try:
                story = self._parse_single_story(story_data)
                if story:
                    stories.append(story)
            except Exception as e:
                import logging

                logging.warning(f"Error parsing story: {e}")
                continue

        return stories

        return stories

    def parse_reels(self, data: list[dict[str, Any]]) -> list[Reel]:
        """Parse reels data from JSON.

        Args:
            data: Raw reels data from JSON

        Returns:
            List of Reel model instances
        """
        reels = []

        if data is None:
            return reels

        # Handle different data formats
        reels_data = data
        if isinstance(data, dict):
            # Some exports wrap reels in a container
            if "reels" in data:
                reels_data = data["reels"]

        if reels_data is None:
            return reels

        for reel_data in reels_data:
            try:
                reel = self._parse_single_reel(reel_data)
                if reel:
                    reels.append(reel)
            except Exception as e:
                import logging

                logging.warning(f"Error parsing reel: {e}")
                continue

        return reels

    def parse_archived_posts(self, data: dict[str, Any]) -> list[Post]:
        """Parse archived posts data from JSON."""
        # Handle archived posts structure
        if isinstance(data, dict) and "ig_archived_post_media" in data:
            archived_data = data["ig_archived_post_media"]
        else:
            archived_data = data

        return self.parse_posts(archived_data)

    def parse_recently_deleted(self, data: dict[str, Any]) -> list[Media]:
        """Parse recently deleted media data from JSON."""
        media_list = []

        # Handle recently deleted structure
        if isinstance(data, dict) and "ig_recently_deleted_media" in data:
            deleted_data = data["ig_recently_deleted_media"]
        elif isinstance(data, dict) and "deleted_content" in data:
            deleted_data = data["deleted_content"]
        else:
            deleted_data = data

        for item_data in deleted_data:
            try:
                # Each item is like a post with multiple media
                if "media" in item_data and isinstance(item_data["media"], list):
                    for media_data in item_data["media"]:
                        media = self._parse_single_media(media_data)
                        if media:
                            media_list.append(media)
                else:
                    # Fallback: treat the item as a single media
                    media = self._parse_single_media(item_data)
                    if media:
                        media_list.append(media)
            except Exception as e:
                import logging

                logging.warning(f"Error parsing recently deleted media: {e}")
                continue

        return media_list

    def parse_story_interactions(
        self, data: list[dict[str, Any]], interaction_type: str
    ) -> list[StoryInteraction]:
        """Parse story interactions data from JSON."""
        interactions = []

        if data is None:
            return interactions

        interactions_data = data
        if isinstance(data, dict):
            if "story_activities" in data:
                interactions_data = data["story_activities"]
            elif "interactions" in data:
                interactions_data = data["interactions"]

        if interactions_data is None:
            return interactions

        for interaction_data in interactions_data:
            try:
                interaction = self._parse_single_story_interaction(
                    interaction_data, interaction_type
                )
                if interaction:
                    interactions.append(interaction)
            except Exception as e:
                import logging

                logging.warning(f"Error parsing story interaction: {e}")
                continue

        return interactions

    def parse_posts_from_file(self, file_path: str) -> list[Post]:
        """Parse posts from a JSON file, using streaming for large files."""
        path_obj = Path(file_path) if isinstance(file_path, str) else file_path
        if should_use_streaming(path_obj, self.streaming_parser.memory_threshold):
            return self.streaming_parser.parse(
                file_path, self.batch_processor.process_posts
            )
        else:
            data = safe_json_load(file_path)
            if data is None:
                return []
            return self.parse_posts(data)

    def parse_stories_from_file(self, file_path: str) -> list[Story]:
        """Parse stories from a JSON file, using streaming for large files."""
        path_obj = Path(file_path) if isinstance(file_path, str) else file_path
        if should_use_streaming(path_obj, self.streaming_parser.memory_threshold):
            result = self.streaming_parser.parse(
                file_path, self.batch_processor.process_stories
            )
            return result
        else:
            data = safe_json_load(file_path)
            if data is None:
                return []
            result = self.parse_stories(data)
            return result

    def parse_reels_from_file(self, file_path: str) -> list[Reel]:
        """Parse reels from a JSON file."""
        data = safe_json_load(file_path)
        if data is None:
            return []
        return self.parse_reels(data)

    def parse_archived_posts_from_file(self, file_path: str) -> list[Post]:
        """Parse archived posts from a JSON file."""
        data = safe_json_load(file_path)
        return self.parse_archived_posts(data)

    def parse_recently_deleted_from_file(self, file_path: str) -> list[Media]:
        """Parse recently deleted media from a JSON file."""
        data = safe_json_load(file_path)
        return self.parse_recently_deleted(data)

    def parse_media_from_file(self, file_path: str) -> list[Media]:
        """Parse generic media from a JSON file (for recently deleted)."""
        data = safe_json_load(file_path)
        return self.parse_recently_deleted(data)

    def parse_story_interactions_from_file(
        self, file_path: str, interaction_type: str
    ) -> list[StoryInteraction]:
        """Parse story interactions from a JSON file."""
        data = safe_json_load(file_path)
        if data is None:
            return []
        return self.parse_story_interactions(data, interaction_type)

    def _parse_single_post(self, data: dict[str, Any]) -> Optional[Post]:
        """Parse a single post from JSON data."""
        # Handle different post data formats
        post_data = data

        # Some exports wrap post data
        if "post" in data:
            post_data = data["post"]
        # Note: Don't reassign post_data when "media" exists,
        # let _extract_media handle the media list

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
        creation_timestamp = data.get("creation_timestamp")

        if not uri or not creation_timestamp:
            return None

        timestamp = self._parse_date(creation_timestamp)
        if not timestamp:
            return None

        # Extract media information
        try:
            media = Media(
                uri=uri,
                media_type=MediaType.IMAGE,  # Stories can be images or videos
                creation_timestamp=timestamp,
                taken_at=timestamp,
                title=data.get("title", ""),
                width=None,  # Will be set if available
                height=None,  # Will be set if available
                duration=None,  # Will be set if available
                file_size=None,  # Will be set if available
                thumbnail_uri="",  # Will be set if available
                ig_media_id=data.get("id", ""),
            )
        except Exception as e:
            import logging

            logging.warning(f"Error parsing media: {e}")
            return None

        try:
            story = Story(
                caption=data.get("caption"),  # Add caption field
                media=media,
                timestamp=timestamp,
                story_id=data.get("id"),
                expires_at=None,  # Instagram stories expire after 24h
                is_highlight=False,  # We'd need to check if it's in highlights
                highlight_name=None,
                has_music=False,  # Would need to analyze metadata
                has_stickers=False,  # Would need to analyze metadata
                has_text=bool(data.get("title", "")),  # Use title as text indicator
                views_count=0,  # Not available in export data
                replies_count=0,  # Not available in export data
                raw_data=data,
            )
            return story
        except Exception as e:
            import logging

            logging.warning(f"Error parsing story: {e}")
            return None

    def _parse_single_reel(self, data: dict[str, Any]) -> Optional[Reel]:
        """Parse a single reel from its JSON data."""
        uri = data.get("uri")
        taken_at = self._parse_date(
            data.get("taken_at") or data.get("creation_timestamp")
        )

        if not uri or not taken_at:
            return None

        return Reel(
            video=Media(
                uri=uri,
                creation_timestamp=taken_at.timestamp(),
                media_type=MediaType.REEL,
                title=data.get("title", ""),
            ),
            timestamp=taken_at,
            caption=data.get("caption", ""),
            raw_data=data,
        )

    def _parse_single_media(self, data: dict[str, Any]) -> Optional[Media]:
        """Parse a single media item from JSON data."""
        uri = data.get("uri", "")
        media_type = self._get_media_type_from_uri(uri)

        return Media(
            uri=uri,
            creation_timestamp=self._parse_date(
                data.get("creation_timestamp") or data.get("taken_at")
            ),
            media_type=media_type,
            title=data.get("title"),
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
            return MediaType.IMAGE

        path = Path(uri)
        ext = path.suffix.lower()

        if ext in [".jpg", ".jpeg", ".png", ".gif"]:
            return MediaType.IMAGE
        elif ext in [".mp4", ".mov", ".avi"]:
            return MediaType.VIDEO
        else:
            return MediaType.IMAGE

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

        # Check top level first
        for field in timestamp_fields:
            if field in data:
                return parse_instagram_date(data[field])

        # If not found at top level, try media list
        if "media" in data and isinstance(data["media"], list) and data["media"]:
            first_media = data["media"][0]
            for field in timestamp_fields:
                if field in first_media:
                    return parse_instagram_date(first_media[field])

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
            except Exception as e:
                import logging

                logging.warning(f"Error parsing comment: {e}")
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
            except Exception as e:
                import logging

                logging.warning(f"Error parsing like: {e}")
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
        if not engagement_data:
            return posts

        liked_posts = engagement_data.get("liked_posts", {})
        post_comments = engagement_data.get("post_comments", {})

        enriched_posts = []
        for post in posts:
            # Try to find a direct match using a URL-like key
            post_url = self._find_post_url(post)

            likes_count = 0
            comments_count = 0

            if post_url:
                if post_url in liked_posts:
                    likes_count = 1  # Assuming 1 like per entry
                if post_url in post_comments:
                    comments_count = len(post_comments[post_url])

            # Fallback to timestamp matching if no URL match
            if likes_count == 0 and comments_count == 0 and post.timestamp:
                engagement = self._find_engagement_by_timestamp(
                    post.timestamp, liked_posts, post_comments
                )
                likes_count = engagement["likes_count"]
                comments_count = engagement["comments_count"]

            # Fallback to media/caption matching if still no match
            if likes_count == 0 and comments_count == 0:
                engagement = self._find_engagement_by_media(
                    post.media, post.caption, liked_posts, post_comments
                )
                likes_count = engagement["likes_count"]
                comments_count = engagement["comments_count"]

            # Create a new Post object with updated engagement counts
            if likes_count > 0 or comments_count > 0:
                enriched_post = post.model_copy(
                    update={
                        "likes_count": likes_count,
                        "comments_count": comments_count,
                    }
                )
                enriched_posts.append(enriched_post)
            else:
                enriched_posts.append(post)

        return enriched_posts

    def _find_post_url(self, post: Post) -> Optional[str]:
        """Try to find a URL-like identifier for a post."""
        # Check for a URL in the raw data
        if post.raw_data and "uri" in post.raw_data:
            return post.raw_data["uri"]

        # Check media URIs
        for media in post.media:
            if media.uri:
                # A simple heuristic to check if it's a post URL
                if "/p/" in media.uri or "/reel/" in media.uri:
                    return media.uri

        return None
