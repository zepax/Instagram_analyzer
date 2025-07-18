"""Parser for Instagram engagement data from separate files."""

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from ..utils import parse_instagram_date, safe_json_load


class EngagementParser:
    """Parses Instagram engagement data from separate files."""

    def __init__(self):
        """Initialize engagement parser."""
        self.liked_posts_cache: dict[str, Any] = {}
        self.post_comments_cache: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.reel_comments_cache: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def parse_engagement_files(
        self, engagement_files: dict[str, list[Path]]
    ) -> dict[str, Any]:
        """Parse all engagement files and return engagement data.

        Args:
            engagement_files: Dictionary with lists of engagement file paths

        Returns:
            Dictionary containing engagement data
        """
        engagement_data = {
            "liked_posts": {},
            "post_comments": defaultdict(list),
            "reel_comments": defaultdict(list),
            "total_likes_given": 0,
            "total_comments_made": 0,
        }

        # Parse liked posts
        for file_path in engagement_files.get("liked_posts", []):
            likes_data = self._parse_liked_posts(file_path)
            for item in likes_data:
                if "href" in item:
                    self.liked_posts_cache[item["href"]] = item
                    engagement_data["liked_posts"][item["href"]] = item
            engagement_data["total_likes_given"] += len(likes_data)

        # Parse post comments
        for file_path in engagement_files.get("post_comments", []):
            comments_data = self._parse_post_comments(file_path)
            for item in comments_data:
                post_url = item.get("post_url", "unknown_post")
                self.post_comments_cache[post_url].append(item)
                engagement_data["post_comments"][post_url].append(item)
            engagement_data["total_comments_made"] += len(comments_data)

        # Parse reel comments
        for file_path in engagement_files.get("reel_comments", []):
            comments_data = self._parse_reel_comments(file_path)
            for item in comments_data:
                reel_url = item.get("href", "unknown_reel")
                self.reel_comments_cache[reel_url].append(item)
                engagement_data["reel_comments"][reel_url].append(item)
            engagement_data["total_comments_made"] += len(comments_data)

        return engagement_data

    def _parse_liked_posts(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse liked posts file.

        Args:
            file_path: Path to liked_posts.json file

        Returns:
            List of like data dicts
        """
        liked_posts = []
        data = safe_json_load(file_path)
        if not data:
            return liked_posts
        likes_data = (
            data.get("liked_posts")
            or data.get("likes_media_likes")
            or data.get("media_likes")
            or []
        )
        for like_entry in likes_data:
            title = like_entry.get("title", "")
            string_list_data = like_entry.get("string_list_data", [])
            for like_data in string_list_data:
                href = like_data.get("href", "")
                timestamp = like_data.get("timestamp", like_entry.get("timestamp", None))
                if href:
                    liked_posts.append(
                        {
                            "title": title,
                            "href": href,
                            "timestamp": timestamp,
                            "datetime": (
                                parse_instagram_date(timestamp) if timestamp else None
                            ),
                        }
                    )
        return liked_posts

    def _extract_post_url_from_href(self, url: str) -> str:
        """Extracts the canonical post/reel URL from a given href, removing query params."""
        if not isinstance(url, str) or not url:
            return url
        if "/p/" in url:
            return url.split("?", 1)[0]
        if "/reel/" in url:
            return url.split("?", 1)[0]
        return url

    def _parse_post_comments(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse post comments file.

        Args:
            file_path: Path to post_comments.json file

        Returns:
            List of post comments data
        """
        post_comments = []
        data = safe_json_load(file_path)

        if not isinstance(data, list):
            return post_comments

        for comment_entry in data:
            media_list_data = comment_entry.get("media_list_data", [])
            post_url = ""
            if media_list_data:
                post_url = media_list_data[0].get("uri", "")

            string_map = comment_entry.get("string_map_data", {})
            comment_text = string_map.get("Comment", {}).get("value", "")
            timestamp = string_map.get("Time", {}).get("timestamp", 0)

            # Use post_url if available, otherwise fallback
            post_url = (
                post_url
                if post_url
                else string_map.get("Media Owner", {}).get("value", "unknown_post")
            )

            post_comments.append(
                {
                    "post_url": post_url,
                    "text": comment_text,
                    "timestamp": timestamp,
                    "datetime": parse_instagram_date(timestamp),
                }
            )

        return post_comments

    def _parse_reel_comments(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse reel comments file.

        Args:
            file_path: Path to reels_comments.json file

        Returns:
            List of reel comments data
        """
        reel_comments = []
        data = safe_json_load(file_path)

        if not data:
            return reel_comments

        # Handle different data structures
        comments_data = data.get("comments_reels_comments", [])
        if not comments_data:
            # Try alternative structure
            comments_data = data.get("reels_comments", [])

        for comment_entry in comments_data:
            title = comment_entry.get("title", "")
            string_list_data = comment_entry.get("string_list_data", [])

            for comment_data in string_list_data:
                href = comment_data.get("href", "")
                value = comment_data.get("value", "")
                timestamp = comment_data.get("timestamp", 0)

                if href:
                    reel_comments.append(
                        {
                            "title": title,
                            "href": href,
                            "text": value,
                            "timestamp": timestamp,
                            "datetime": parse_instagram_date(timestamp),
                        }
                    )

        return reel_comments

    def get_engagement_counts(self, post_urls: set[str]) -> dict[str, dict[str, int]]:
        """Get like and comment counts for a set of post URLs.

        Args:
            post_urls: Set of post URLs to get engagement for

        Returns:
            Dictionary mapping post URLs to engagement counts
        """
        engagement_counts = {}
        for url in post_urls:
            # Count likes
            likes_count = 1 if url in self.liked_posts_cache else 0

            # Count comments
            comments_count = len(self.post_comments_cache.get(url, []))

            engagement_counts[url] = {
                "likes_count": likes_count,
                "comments_count": comments_count,
                "total_engagement": likes_count + comments_count,
            }

        return engagement_counts

    def extract_post_id_from_url(self, url: str) -> str:
        """Extract post ID from Instagram URL.

        Args:
            url: Instagram post URL

        Returns:
            Post ID or original URL if extraction fails
        """
        try:
            # URLs typically look like: https://www.instagram.com/p/POST_ID/
            if "/p/" in url:
                return url.split("/p/")[1].split("/")[0]
            elif "/reel/" in url:
                return url.split("/reel/")[1].split("/")[0]
            return url
        except Exception:
            return url

    def clear_cache(self):
        """Clear engagement data cache."""
        self.liked_posts_cache.clear()
        self.post_comments_cache.clear()
        self.reel_comments_cache.clear()
