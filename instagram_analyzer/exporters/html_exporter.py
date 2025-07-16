"""Advanced HTML exporter for Instagram analysis reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import base64
from importlib import resources
from jinja2 import Environment

from .. import __version__
from ..models import Post, Story, Reel, Profile
from ..utils import (
    get_image_thumbnail,
    resolve_media_path,
    clean_instagram_text,
    truncate_text,
    safe_html_escape,
)


class HTMLExporter:
    """Export Instagram analysis to professional HTML reports."""

    def __init__(self):
        self.template = self._get_template()

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

    def _generate_report_data(self, analyzer, anonymize: bool) -> Dict[str, Any]:
        """Generate comprehensive report data."""
        data = {
            "metadata": self._get_metadata(analyzer, anonymize),
            "overview": self._get_overview_stats(analyzer),
            "temporal_analysis": self._get_temporal_analysis(analyzer),
            "engagement_analysis": self._get_engagement_analysis(analyzer),
            "content_analysis": self._get_content_analysis(analyzer),
            "posts": self._get_posts_data(analyzer, anonymize),
            "charts_data": self._get_charts_data(analyzer),
        }

        return data

    def _get_metadata(self, analyzer, anonymize: bool) -> Dict[str, Any]:
        """Get report metadata."""
        metadata = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_posts": len(analyzer.posts),
            "total_stories": len(analyzer.stories),
            "total_reels": len(analyzer.reels),
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

    def _get_overview_stats(self, analyzer) -> Dict[str, Any]:
        """Get overview statistics."""
        posts = analyzer.posts
        stories = analyzer.stories
        reels = analyzer.reels

        if not posts and not reels:
            return {"has_data": False}

        # Date range
        all_dates = [p.timestamp for p in posts if p.timestamp]
        if all_dates:
            start_date = min(all_dates)
            end_date = max(all_dates)
            active_days = (end_date - start_date).days + 1
        else:
            start_date = end_date = None
            active_days = 0

        # Content counts
        total_media = sum(len(p.media) for p in posts)
        carousel_posts = sum(1 for p in posts if len(p.media) > 1)
        video_posts = sum(
            1 for p in posts if any(m.media_type.value == "video" for m in p.media)
        )

        # Engagement totals (include reels)
        total_likes = sum(p.likes_count for p in posts) + sum(
            r.likes_count for r in reels
        )
        total_comments = sum(p.comments_count for p in posts) + sum(
            r.comments_count for r in reels
        )
        total_items = len(posts) + len(reels)


        return {
            "has_data": True,
            "content_counts": {
                "posts": len(posts),
                "stories": len(stories),
                "reels": len(reels),
                "total_media": total_media,
                "carousel_posts": carousel_posts,
                "video_posts": video_posts,
            },
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d") if start_date else None,
                "end": end_date.strftime("%Y-%m-%d") if end_date else None,
                "active_days": active_days,
                "years_active": (
                    round(active_days / 365.25, 1) if active_days > 0 else 0
                ),
            },
            "engagement_totals": {
                "likes": total_likes,
                "comments": total_comments,
                "avg_likes_per_post": (
                    round(total_likes / total_items, 1) if total_items else 0
                ),
                "avg_comments_per_post": (
                    round(total_comments / total_items, 1) if total_items else 0

                ),
            },
        }

    def _get_temporal_analysis(self, analyzer) -> Dict[str, Any]:
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

    def _get_engagement_analysis(self, analyzer) -> Dict[str, Any]:
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
                            p.timestamp.strftime("%Y-%m-%d")
                            if p.timestamp
                            else "Unknown"
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
                            p.timestamp.strftime("%Y-%m-%d")
                            if p.timestamp
                            else "Unknown"
                        ),
                        "media_count": len(p.media),
                    }
                    for p in top_commented
                ],
            },
            "distribution": {
                "avg_likes": round(sum(likes_counts) / len(likes_counts), 1),
                "median_likes": sorted(likes_counts)[len(likes_counts) // 2],
                "max_likes": max(likes_counts),
                "avg_comments": round(sum(comments_counts) / len(comments_counts), 1),
                "median_comments": sorted(comments_counts)[len(comments_counts) // 2],
                "max_comments": max(comments_counts),
            },
        }

    def _get_content_analysis(self, analyzer) -> Dict[str, Any]:
        """Get content analysis data."""
        posts = analyzer.posts
        if not posts:
            return {"has_data": False}

        # Hashtag analysis
        all_hashtags = []
        posts_with_hashtags = 0
        for post in posts:
            if post.hashtags:
                all_hashtags.extend(post.hashtags)
                posts_with_hashtags += 1

        hashtag_counter = Counter(all_hashtags)
        top_hashtags = hashtag_counter.most_common(20)

        # Caption analysis
        captions = [p.caption for p in posts if p.caption]
        avg_caption_length = (
            sum(len(c) for c in captions) / len(captions) if captions else 0
        )

        # Media type analysis
        image_posts = sum(
            1 for p in posts if all(m.media_type.value == "image" for m in p.media)
        )
        video_posts = sum(
            1 for p in posts if any(m.media_type.value == "video" for m in p.media)
        )
        carousel_posts = sum(1 for p in posts if len(p.media) > 1)

        return {
            "has_data": True,
            "hashtags": {
                "total_unique": len(hashtag_counter),
                "total_usage": len(all_hashtags),
                "posts_with_hashtags": posts_with_hashtags,
                "usage_rate": round(posts_with_hashtags / len(posts) * 100, 1),
                "top_hashtags": top_hashtags,
                "avg_per_post": round(len(all_hashtags) / len(posts), 1),
            },
            "captions": {
                "posts_with_captions": len(captions),
                "usage_rate": round(len(captions) / len(posts) * 100, 1),
                "avg_length": round(avg_caption_length),
                "longest": max(len(c) for c in captions) if captions else 0,
            },
            "media_types": {
                "image_only": image_posts,
                "contains_video": video_posts,
                "carousel": carousel_posts,
                "single_media": len(posts) - carousel_posts,
            },
        }

    def _get_posts_data(self, analyzer, anonymize: bool) -> List[Dict[str, Any]]:
        """Get posts data for gallery."""
        posts = analyzer.posts
        if not posts:
            return []

        # Sort by date, most recent first
        sorted_posts = sorted(
            posts, key=lambda p: p.timestamp or datetime.min, reverse=True
        )

        posts_data = []
        for post in sorted_posts[:50]:  # Limit to 50 most recent posts
            cleaned_caption = (
                clean_instagram_text(post.caption) if post.caption else "No caption"
            )
            post_data = {
                "caption": safe_html_escape(truncate_text(cleaned_caption, 200)),
                "full_caption": safe_html_escape(cleaned_caption),
                "date": (
                    post.timestamp.strftime("%Y-%m-%d %H:%M")
                    if post.timestamp
                    else "Unknown date"
                ),
                "likes": post.likes_count,
                "comments": post.comments_count,
                "media_count": len(post.media),
                "hashtags": (
                    post.hashtags[:10] if post.hashtags else []
                ),  # Limit hashtags
                "mentions": (
                    post.mentions[:10] if post.mentions else []
                ),  # Limit mentions
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

                post_data["media"].append(media_info)

            posts_data.append(post_data)

        return posts_data

    def _get_charts_data(self, analyzer) -> Dict[str, Any]:
        """Get data for charts and visualizations."""
        posts = analyzer.posts
        if not posts:
            return {}

        # Monthly activity data
        monthly_data = Counter()
        for post in posts:
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
        for post in posts:
            if post.timestamp:
                weekday_data[post.timestamp.strftime("%A")] += 1

        # Hour activity
        hourly_data = Counter()
        for post in posts:
            if post.timestamp:
                hourly_data[post.timestamp.hour] += 1

        return {
            "monthly_activity": {
                "labels": sorted(monthly_data.keys()),
                "data": [monthly_data[month] for month in sorted(monthly_data.keys())],
            },
            "weekday_activity": {
                "labels": weekday_order,
                "data": [weekday_data[day] for day in weekday_order],
            },
            "hourly_activity": {
                "labels": list(range(24)),
                "data": [hourly_data[hour] for hour in range(24)],
            },
        }

    def _render_template(self, data: Dict[str, Any]) -> str:
        """Render the HTML template with data using Jinja2."""
        env = Environment(autoescape=False)
        tmpl = env.from_string(self.template)
        context = {
            "METADATA": json.dumps(data["metadata"], default=str),
            "OVERVIEW": json.dumps(data["overview"], default=str),
            "TEMPORAL": json.dumps(data["temporal_analysis"], default=str),
            "ENGAGEMENT": json.dumps(data["engagement_analysis"], default=str),
            "CONTENT": json.dumps(data["content_analysis"], default=str),
            "POSTS": json.dumps(data["posts"], default=str),
            "CHARTS": json.dumps(data["charts_data"], default=str),
        }

        return tmpl.render(context)

    def _get_template(self) -> str:
        """Return the HTML report template contents."""
        template_path = resources.files("instagram_analyzer.templates").joinpath(
            "report.html"
        )
        return template_path.read_text(encoding="utf-8")
