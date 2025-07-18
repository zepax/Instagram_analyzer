"""Advanced HTML exporter for Instagram analysis reports."""

import base64
import json
from collections import Counter
from datetime import datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment

from .. import __version__
from ..analyzers.network_analysis import NetworkAnalyzer
from ..models import Post, Profile, Reel, Story, StoryInteraction
from ..utils import (
    clean_instagram_text,
    get_image_thumbnail,
    resolve_media_path,
    safe_html_escape,
    truncate_text,
)


class HTMLExporter:
    """Export Instagram analysis to professional HTML reports."""

    def __init__(self):
        pass

    def export(self, analyzer, output_path: Path, anonymize: bool = False) -> Path:
        """Export analysis to HTML report.

        Args:
            analyzer: InstagramAnalyzer instance with loaded data
            output_path: Directory to save the report
            anonymize: Whether to anonymize sensitive data

        Returns:
            Path to the generated HTML file
        """
        # Generate analysis data
        report_data = self._generate_report_data(analyzer, anonymize)

        # Generate HTML content
        html_content = self._render_template(report_data)

        # Save to file
        report_file = output_path / "instagram_analysis.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return report_file

    def _generate_report_data(self, analyzer, anonymize: bool) -> dict[str, Any]:
        """Generate comprehensive report data."""
        data = {
            "metadata": self._get_metadata(analyzer, anonymize),
            "overview": self._get_overview_stats(analyzer, anonymize),
            "temporal_analysis": self._get_temporal_analysis(analyzer),
            "engagement_analysis": self._get_engagement_analysis(analyzer),
            "content_analysis": self._get_content_analysis(analyzer),
            "posts": self._get_posts_data(analyzer, anonymize),
            "stories": self._get_stories_data(analyzer, anonymize),
            "reels": self._get_reels_data(analyzer, anonymize),
            "charts_data": self._get_charts_data(analyzer),
            "network_graph": self._get_network_graph_data(analyzer),
            "additional_content": self._get_additional_content_data(analyzer),
            "story_interactions": self._get_story_interactions_data(analyzer, anonymize),
        }

        return data

    def _get_metadata(self, analyzer, anonymize: bool) -> dict[str, Any]:
        """Get report metadata."""
        metadata = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": len(analyzer.posts),
            "total_stories": len(analyzer.stories),
            "total_reels": len(analyzer.reels),
            "total_archived": len(analyzer.archived_posts),
            "total_deleted": len(analyzer.recently_deleted),
            "total_story_interactions": len(analyzer.story_interactions),
            "analyzer_version": __version__,
        }

        if analyzer.profile and not anonymize:
            metadata.update(
                {
                    "username": analyzer.profile.username,
                    "display_name": analyzer.profile.name,
                    "is_verified": analyzer.profile.is_verified,
                    "is_private": analyzer.profile.is_private,
                }
            )
        elif anonymize and analyzer.profile:
            metadata.update({"username": "User***", "display_name": "Anonymous User"})
        elif anonymize and not analyzer.profile:
            metadata.update(
                {
                    "username": "No profile data available",
                    "display_name": "No profile data available",
                }
            )
        elif not analyzer.profile:
            metadata.update(
                {
                    "username": "No profile data available",
                    "display_name": "No profile data available",
                }
            )

        return metadata

    def _get_overview_stats(self, analyzer, anonymize: bool) -> dict[str, Any]:
        """Get overview statistics."""
        overview = {}

        # Basic counts
        overview["total_posts"] = len(analyzer.posts)
        overview["total_stories"] = len(analyzer.stories)
        overview["total_reels"] = len(analyzer.reels)
        overview["total_archived"] = len(analyzer.archived_posts)
        overview["total_deleted"] = len(analyzer.recently_deleted)
        overview["total_story_interactions"] = len(analyzer.story_interactions)

        if not overview["total_posts"] and not overview["total_reels"]:
            return {"has_data": False}

        # Date range
        all_dates = [p.timestamp for p in analyzer.posts if p.timestamp]
        if all_dates:
            start_date = min(all_dates)
            end_date = max(all_dates)
            active_days = (end_date - start_date).days + 1
        else:
            start_date = end_date = None
            active_days = 0

        # Content counts
        total_media = sum(len(p.media) for p in analyzer.posts)
        carousel_posts = sum(1 for p in analyzer.posts if len(p.media) > 1)
        video_posts = sum(
            1
            for p in analyzer.posts
            if any(m.media_type.value == "video" for m in p.media)
        )

        # Engagement totals (include reels)
        total_likes = sum(p.likes_count for p in analyzer.posts) + sum(
            r.likes_count for r in analyzer.reels
        )
        total_comments = sum(p.comments_count for p in analyzer.posts) + sum(
            r.comments_count for r in analyzer.reels
        )
        total_items = len(analyzer.posts) + len(analyzer.reels)

        # Top content
        top_posts = sorted(
            analyzer.posts, key=lambda p: p.likes_count + p.comments_count, reverse=True
        )[:5]
        overview["top_posts"] = [
            self._format_post_for_report(p, analyzer, anonymize) for p in top_posts
        ]

        # Recently deleted summary
        overview["recently_deleted_count"] = len(analyzer.recently_deleted)
        overview["deleted_last_30_days"] = sum(
            1
            for item in analyzer.recently_deleted
            if item.timestamp
            and item.timestamp > datetime.now(item.timestamp.tzinfo) - timedelta(days=30)
        )

        # Story interactions summary
        overview["story_interactions_count"] = len(analyzer.story_interactions)
        if analyzer.story_interactions:
            interaction_types = Counter(
                i.interaction_type for i in analyzer.story_interactions
            )
            overview["story_interaction_types"] = interaction_types.most_common()

        return overview

    def _get_temporal_analysis(self, analyzer) -> dict[str, Any]:
        """Get temporal analysis data."""
        posts = analyzer.posts
        if not posts:
            return {"has_data": False}

        # Posts by year
        posts_by_year = Counter()
        posts_by_month = Counter()
        posts_by_weekday = Counter()
        posts_by_hour = Counter()

        for post in posts:
            if post.timestamp:
                posts_by_year[post.timestamp.year] += 1
                posts_by_month[post.timestamp.strftime("%Y-%m")] += 1
                posts_by_weekday[post.timestamp.strftime("%A")] += 1
                posts_by_hour[post.timestamp.hour] += 1

        # Most active periods
        most_active_year = posts_by_year.most_common(1)[0] if posts_by_year else None
        most_active_month = posts_by_month.most_common(1)[0] if posts_by_month else None
        most_active_weekday = (
            posts_by_weekday.most_common(1)[0] if posts_by_weekday else None
        )
        most_active_hour = posts_by_hour.most_common(1)[0] if posts_by_hour else None

        return {
            "has_data": True,
            "by_year": dict(posts_by_year.most_common()),
            "by_month": dict(posts_by_month.most_common(12)),
            "by_weekday": dict(posts_by_weekday),
            "by_hour": dict(posts_by_hour),
            "most_active": {
                "year": (
                    f"{most_active_year[0]} ({most_active_year[1]} posts)"
                    if most_active_year
                    else None
                ),
                "month": (
                    f"{most_active_month[0]} ({most_active_month[1]} posts)"
                    if most_active_month
                    else None
                ),
                "weekday": (
                    f"{most_active_weekday[0]} ({most_active_weekday[1]} posts)"
                    if most_active_weekday
                    else None
                ),
                "hour": (
                    f"{most_active_hour[0]}:00 ({most_active_hour[1]} posts)"
                    if most_active_hour
                    else None
                ),
            },
        }

    def _get_engagement_analysis(self, analyzer) -> dict[str, Any]:
        """Get engagement analysis data."""
        posts = analyzer.posts
        if not posts:
            return {"has_data": False}

        # Sort posts by engagement
        posts_by_likes = sorted(posts, key=lambda p: p.likes_count, reverse=True)
        posts_by_comments = sorted(posts, key=lambda p: p.comments_count, reverse=True)

        # Top performing posts
        top_liked = posts_by_likes[:5]
        top_commented = posts_by_comments[:5]

        # Engagement distribution
        likes_counts = [p.likes_count for p in posts]
        comments_counts = [p.comments_count for p in posts]

        return {
            "has_data": True,
            "top_posts": {
                "most_liked": [
                    {
                        "caption": safe_html_escape(
                            truncate_text(p.caption or "No caption", 100)
                        ),
                        "likes": p.likes_count,
                        "comments": p.comments_count,
                        "date": (
                            p.timestamp.strftime("%Y-%m-%d") if p.timestamp else "Unknown"
                        ),
                        "media_count": len(p.media),
                    }
                    for p in top_liked
                ],
                "most_commented": [
                    {
                        "caption": safe_html_escape(
                            truncate_text(p.caption or "No caption", 100)
                        ),
                        "likes": p.likes_count,
                        "comments": p.comments_count,
                        "date": (
                            p.timestamp.strftime("%Y-%m-%d") if p.timestamp else "Unknown"
                        ),
                        "media_count": len(p.media),
                    }
                    for p in top_commented
                ],
            },
            "distribution": {
                "avg_likes": (
                    round(sum(likes_counts) / len(likes_counts), 1) if likes_counts else 0
                ),
                "median_likes": (
                    sorted(likes_counts)[len(likes_counts) // 2] if likes_counts else 0
                ),
                "max_likes": max(likes_counts) if likes_counts else 0,
                "avg_comments": (
                    round(sum(comments_counts) / len(comments_counts), 1)
                    if comments_counts
                    else 0
                ),
                "median_comments": (
                    sorted(comments_counts)[len(comments_counts) // 2]
                    if comments_counts
                    else 0
                ),
                "max_comments": max(comments_counts) if comments_counts else 0,
            },
        }

    def _get_content_analysis(self, analyzer) -> dict[str, Any]:
        """Get content analysis data."""
        content_data = {}

        # Top locations
        locations = [
            p.location["name"]
            for p in analyzer.posts
            if p.location and "name" in p.location
        ]
        location_counter = Counter(locations)
        top_locations = location_counter.most_common(10)

        # Hashtag analysis
        all_hashtags = []
        posts_with_hashtags = 0
        for post in analyzer.posts:
            if post.hashtags:
                all_hashtags.extend(post.hashtags)
                posts_with_hashtags += 1

        hashtag_counter = Counter(all_hashtags)
        top_hashtags = hashtag_counter.most_common(20)

        # Caption analysis
        captions = [p.caption for p in analyzer.posts if p.caption]
        avg_caption_length = (
            sum(len(c) for c in captions) / len(captions) if captions else 0
        )

        # Media type analysis
        image_posts = sum(
            1
            for p in analyzer.posts
            if all(m.media_type.value == "image" for m in p.media)
        )
        video_posts = sum(
            1
            for p in analyzer.posts
            if any(m.media_type.value == "video" for m in p.media)
        )
        carousel_posts = sum(1 for p in analyzer.posts if len(p.media) > 1)

        # Content analysis
        all_content = analyzer.posts + analyzer.reels
        hashtags = []
        mentions = []
        for item in all_content:
            if item.caption:
                hashtags.extend([w for w in item.caption.split() if w.startswith("#")])
                mentions.extend([w for w in item.caption.split() if w.startswith("@")])

        content_data["top_hashtags"] = Counter(hashtags).most_common(10)
        content_data["top_mentions"] = Counter(mentions).most_common(10)

        # Media type distribution
        media_types = Counter(
            m.media_type.value for p in analyzer.posts if p.media for m in p.media
        )
        content_data["media_type_distribution"] = media_types.most_common()

        return {
            "has_data": True,
            "hashtags": {
                "total_unique": len(hashtag_counter),
                "total_usage": len(all_hashtags),
                "posts_with_hashtags": posts_with_hashtags,
                "usage_rate": (
                    round(posts_with_hashtags / len(analyzer.posts) * 100, 1)
                    if analyzer.posts
                    else 0
                ),
                "top_hashtags": top_hashtags,
                "avg_per_post": (
                    round(len(all_hashtags) / len(analyzer.posts), 1)
                    if analyzer.posts
                    else 0
                ),
            },
            "captions": {
                "posts_with_captions": len(captions),
                "usage_rate": (
                    round(len(captions) / len(analyzer.posts) * 100, 1)
                    if analyzer.posts
                    else 0
                ),
                "avg_length": round(avg_caption_length),
                "longest": max(len(c) for c in captions) if captions else 0,
            },
            "media_types": {
                "image_only": image_posts,
                "contains_video": video_posts,
                "carousel": carousel_posts,
                "single_media": len(analyzer.posts) - carousel_posts,
            },
            "locations": {
                "total_unique": len(location_counter),
                "top_locations": top_locations,
            },
        }

    def _get_posts_data(self, analyzer, anonymize: bool) -> list[dict[str, Any]]:
        """Get formatted posts data."""
        return [
            self._format_post_for_report(p, analyzer, anonymize)
            for p in sorted(analyzer.posts, key=lambda x: x.timestamp, reverse=True)
        ]

    def _get_stories_data(self, analyzer, anonymize: bool) -> list[dict[str, Any]]:
        """Get formatted stories data."""
        return [
            self._format_story_for_report(s, analyzer, anonymize)
            for s in sorted(analyzer.stories, key=lambda x: x.taken_at, reverse=True)
        ]

    def _get_reels_data(self, analyzer, anonymize: bool) -> list[dict[str, Any]]:
        """Get formatted reels data."""
        return [
            self._format_reel_for_report(r, analyzer, anonymize)
            for r in sorted(analyzer.reels, key=lambda x: x.taken_at, reverse=True)
        ]

    def _get_additional_content_data(self, analyzer) -> dict[str, Any]:
        """Get data for archived and recently deleted content."""

        # Archived posts
        archived_posts = [
            self._format_post_for_report(
                p, analyzer, False
            )  # Anonymization not needed for internal data
            for p in sorted(
                analyzer.archived_posts, key=lambda x: x.timestamp, reverse=True
            )
        ]

        # Recently deleted content
        recently_deleted = [
            {
                "uri": item.uri,
                "timestamp": (
                    item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    if item.timestamp
                    else "N/A"
                ),
                "media_type": item.media_type.value,
                "title": item.title,
                "thumbnail": (
                    get_image_thumbnail(
                        resolve_media_path(item.uri, analyzer.data_path), (100, 100)
                    )
                    if item.media_type == "IMAGE"
                    else None
                ),
            }
            for item in sorted(
                analyzer.recently_deleted, key=lambda x: x.timestamp, reverse=True
            )
        ]

        return {"archived_posts": archived_posts, "recently_deleted": recently_deleted}

    def _get_story_interactions_data(self, analyzer, anonymize: bool) -> dict[str, Any]:
        """Get formatted story interactions data."""
        if not analyzer.story_interactions:
            return {"interactions": [], "summary": {}}

        interactions = [
            self._format_interaction_for_report(i, anonymize)
            for i in sorted(
                analyzer.story_interactions, key=lambda x: x.timestamp, reverse=True
            )
        ]

        summary = {
            "total": len(interactions),
            "types": Counter(
                i.interaction_type for i in analyzer.story_interactions
            ).most_common(),
            "top_interactors": Counter(
                i.username for i in analyzer.story_interactions if i.username
            ).most_common(10),
        }

        return {"interactions": interactions, "summary": summary}

    def _get_charts_data(self, analyzer) -> dict[str, Any]:
        """Get data for generating charts."""
        charts_data = {}
        # Monthly activity data
        monthly_data = Counter()
        for post in analyzer.posts:
            if post.timestamp:
                month_key = post.timestamp.strftime("%Y-%m")
                monthly_data[month_key] += 1

        # Weekday activity
        weekday_data = Counter()
        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for post in analyzer.posts:
            if post.timestamp:
                weekday_data[post.timestamp.strftime("%A")] += 1

        # Hour activity
        hourly_data = Counter()
        for post in analyzer.posts:
            if post.timestamp:
                hourly_data[post.timestamp.hour] += 1

        # Posts over time
        posts_over_time = Counter(
            p.timestamp.strftime("%Y-%m") for p in analyzer.posts if p.timestamp
        )
        if posts_over_time:
            sorted_months = sorted(posts_over_time.keys())
            charts_data["posts_over_time"] = {
                "labels": sorted_months,
                "data": [posts_over_time[m] for m in sorted_months],
            }

        # Engagement by weekday
        engagement_by_weekday = {i: {"likes": 0, "comments": 0} for i in range(7)}
        for post in analyzer.posts:
            if post.timestamp:
                weekday = post.timestamp.weekday()
                engagement_by_weekday[weekday]["likes"] += post.likes_count
                engagement_by_weekday[weekday]["comments"] += post.comments_count
        charts_data["engagement_by_weekday"] = {
            "labels": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ],
            "likes": [engagement_by_weekday[i]["likes"] for i in range(7)],
            "comments": [engagement_by_weekday[i]["comments"] for i in range(7)],
        }

        # Story interactions over time
        interactions_over_time = Counter(
            i.timestamp.strftime("%Y-%m")
            for i in analyzer.story_interactions
            if i.timestamp
        )
        if interactions_over_time:
            sorted_months = sorted(interactions_over_time.keys())
            charts_data["interactions_over_time"] = {
                "labels": sorted_months,
                "data": [interactions_over_time[m] for m in sorted_months],
            }

        return charts_data

    def _get_network_graph_data(self, analyzer) -> Optional[dict[str, Any]]:
        """Get data for network graph visualization."""
        if not analyzer.profile or not analyzer.posts:
            return {"nodes": [], "links": []}

        network = NetworkAnalyzer(analyzer.profile.username)
        return network.analyze(analyzer.posts)

    def _render_template(self, data: dict[str, Any]) -> str:
        """Render the HTML template with data."""
        import json

        # Get the template content
        template_content = self._get_template()

        # Replace placeholders with actual data
        replacements = {
            "{{ METADATA }}": json.dumps(data.get("metadata", {})),
            "{{ OVERVIEW }}": json.dumps(data.get("overview", {})),
            "{{ TEMPORAL }}": json.dumps(data.get("temporal_analysis", {})),
            "{{ ENGAGEMENT }}": json.dumps(data.get("engagement_analysis", {})),
            "{{ CONTENT }}": json.dumps(data.get("content_analysis", {})),
            "{{ POSTS }}": json.dumps(data.get("posts", [])),
            "{{ STORIES }}": json.dumps(data.get("stories", [])),
            "{{ REELS }}": json.dumps(data.get("reels", [])),
            "{{ ADDITIONAL_CONTENT }}": json.dumps(data.get("additional_content", {})),
            "{{ STORY_INTERACTIONS }}": json.dumps(data.get("story_interactions", {})),
            "{{ CHARTS }}": json.dumps(data.get("charts_data", {})),
            "{{ NETWORK }}": json.dumps(data.get("network_graph", {})),
        }

        for placeholder, value in replacements.items():
            template_content = template_content.replace(placeholder, value)

        return template_content

    def _get_template(self) -> str:
        """Return the HTML report template contents."""
        template_path = resources.files("instagram_analyzer.templates").joinpath(
            "report.html"
        )
        return template_path.read_text(encoding="utf-8")

    def _format_post_for_report(
        self, post: Post, analyzer, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single post for the report."""
        data = {
            "id": post.id,
            "uri": post.uri,
            "shortcode": post.shortcode,
            "timestamp": (
                post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if post.timestamp else "N/A"
            ),
            "likes": post.likes_count,
            "comments": post.comments_count,
            "media_count": len(post.media),
            "caption": safe_html_escape(truncate_text(post.caption, 100)),
            "full_caption": safe_html_escape(post.caption),
            "hashtags": post.hashtags or [],
            "mentions": post.mentions or [],
            "media": [],
        }

        # Add media info (limit to first 5 items for performance)
        for media in post.media[:5]:
            media_info = {
                "uri": media.uri,
                "type": media.media_type.value,
                "title": media.title or "",
            }

            # Try to generate thumbnail for images
            if media.media_type.value == "image":
                media_path = resolve_media_path(media.uri, analyzer.data_path)
                if media_path:
                    thumbnail = get_image_thumbnail(media_path)
                    if thumbnail:
                        media_info["thumbnail"] = thumbnail

            data["media"].append(media_info)

        # Anonymize user data if required
        if anonymize:
            data["username"] = "anonymous"
            data["profile_picture"] = None
        else:
            data["username"] = post.owner.username
            data["profile_picture"] = post.owner.profile_picture_url

        return data

    def _format_story_for_report(
        self, story: Story, analyzer, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single story for the report."""
        data = {
            "taken_at": (
                story.taken_at.strftime("%Y-%m-%d %H:%M:%S") if story.taken_at else "N/A"
            ),
            "caption": clean_instagram_text(story.caption) if story.caption else "",
            "media_uri": story.media.uri if story.media else "",
            "media_type": story.media.media_type.value if story.media else "unknown",
        }

        # Add thumbnail for images
        if story.media and story.media.media_type.value == "IMAGE":
            thumbnail_path = resolve_media_path(story.media.uri, analyzer.data_path)
            data["thumbnail"] = get_image_thumbnail(thumbnail_path, (150, 150))

        return data

    def _format_reel_for_report(
        self, reel: Reel, analyzer, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single reel for the report."""
        data = {
            "taken_at": (
                reel.taken_at.strftime("%Y-%m-%d %H:%M:%S") if reel.taken_at else "N/A"
            ),
            "caption": clean_instagram_text(reel.caption) if reel.caption else "",
            "media_uri": reel.media.uri if reel.media else "",
            "media_type": reel.media.media_type.value if reel.media else "unknown",
            "likes_count": getattr(reel, "likes_count", 0),
            "comments_count": getattr(reel, "comments_count", 0),
        }

        # Add thumbnail for videos (first frame) or images
        if reel.media:
            thumbnail_path = resolve_media_path(reel.media.uri, analyzer.data_path)
            data["thumbnail"] = get_image_thumbnail(thumbnail_path, (150, 150))

        return data

    def _format_interaction_for_report(
        self, interaction: StoryInteraction, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single story interaction for the report."""
        return {
            "type": interaction.interaction_type,
            "username": "anonymous" if anonymize else interaction.username,
            "timestamp": (
                interaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if interaction.timestamp
                else "N/A"
            ),
        }
