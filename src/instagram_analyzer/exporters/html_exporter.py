"""Advanced HTML exporter for Instagram analysis reports."""

import json
import logging
import os
import shutil
from collections import Counter
from datetime import datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .. import __version__
from ..analyzers.network_analysis import NetworkAnalyzer
from ..models import Post, Reel, Story, StoryInteraction
from ..utils import (
    clean_instagram_text,
    get_image_thumbnail,
    resolve_media_path,
    safe_html_escape,
    truncate_text,
)


class HTMLExporter:
    """Export Instagram analysis to professional HTML reports."""

    def __init__(self) -> None:
        """Initialize HTML exporter."""
        pass

    def export(
        self,
        analyzer: Any,
        output_path: Path,
        anonymize: bool = False,
        show_progress: bool = False,
        compact: bool = False,
        max_items: int = 100,
    ) -> Path:
        """Export analysis to HTML report.

        Args:
            analyzer: InstagramAnalyzer instance with loaded data
            output_path: Directory to save the report
            anonymize: Whether to anonymize sensitive data
            show_progress: Whether to show progress bars
            compact: Whether to generate a compact report (smaller file size)
            max_items: Maximum number of items to include per section

        Returns:
            Path to the generated HTML file
        """
        if show_progress:
            console = Console()
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(complete_style="green", finished_style="green"),
                TextColumn("{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                main_task = progress.add_task("Generating HTML report", total=100)

                # Set compact mode flag on analyzer for media processing
                analyzer._compact_mode = compact

                # Generate analysis data
                progress.update(main_task, description="Collecting analysis data...")
                report_data = self._generate_report_data(
                    analyzer, anonymize, compact, max_items
                )
                progress.update(main_task, advance=60)

                # Generate HTML content
                progress.update(main_task, description="Rendering HTML template...")
                html_content = self._render_template(report_data)
                progress.update(main_task, advance=30)

                # Save to file
                progress.update(main_task, description="Writing HTML file...")
                report_file = output_path / "instagram_analysis.html"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                progress.update(main_task, advance=10)

                progress.update(main_task, description="HTML report complete!")
                return report_file
        else:
            # Set compact mode flag on analyzer for media processing
            analyzer._compact_mode = compact

            # Generate analysis data
            report_data = self._generate_report_data(
                analyzer, anonymize, compact, max_items
            )

            # Generate HTML content
            html_content = self._render_template(report_data)

            # Save to file
            report_file = output_path / "instagram_analysis.html"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(html_content)

            return report_file

    def _generate_report_data(
        self,
        analyzer: Any,
        anonymize: bool,
        compact: bool = False,
        max_items: int = 100,
    ) -> dict[str, Any]:
        """Generate comprehensive report data."""
        data = {
            "metadata": self._get_metadata(analyzer, anonymize),
            "overview": self._get_overview_stats(analyzer, anonymize),
            "temporal_analysis": self._get_temporal_analysis(analyzer),
            "engagement_analysis": self._get_engagement_analysis(analyzer),
            "content_analysis": self._get_content_analysis(analyzer),
            "posts": self._get_posts_data(
                analyzer, anonymize, max_items if compact else None
            ),
            "stories": self._get_stories_data(
                analyzer, anonymize, max_items if compact else None
            ),
            "reels": self._get_reels_data(
                analyzer, anonymize, max_items if compact else None
            ),
            "charts_data": self._get_charts_data(analyzer),
            "network_graph": (
                self._get_network_graph_data(analyzer)
                if not compact
                else {"nodes": [], "links": []}
            ),
            "additional_content": self._get_additional_content_data(
                analyzer, max_items if compact else None
            ),
            "story_interactions": self._get_story_interactions_data(
                analyzer, anonymize, max_items if compact else None
            ),
        }

        return data

    def _get_metadata(self, analyzer: Any, anonymize: bool) -> dict[str, Any]:
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

    def _get_overview_stats(self, analyzer: Any, anonymize: bool) -> dict[str, Any]:
        """Get overview statistics."""
        overview: dict[str, Any] = {}

        # Basic counts
        overview["total_posts"] = len(analyzer.posts)
        overview["total_stories"] = len(analyzer.stories)
        overview["total_reels"] = len(analyzer.reels)
        overview["total_archived"] = len(analyzer.archived_posts)
        overview["total_deleted"] = len(analyzer.recently_deleted)
        overview["total_story_interactions"] = len(analyzer.story_interactions)

        if not overview["total_posts"] and not overview["total_reels"]:
            return {"has_data": False}

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

        # Engagement totals
        total_likes = sum(post.likes_count for post in analyzer.posts)
        total_comments = sum(post.comments_count for post in analyzer.posts)
        overview["engagement_totals"] = {"likes": total_likes, "comments": total_comments}

        return overview

    def _get_temporal_analysis(self, analyzer: Any) -> dict[str, Any]:
        """Get temporal analysis data."""
        posts = analyzer.posts
        if not posts:
            return {"has_data": False}

        # Posts by year
        posts_by_year: Counter[int] = Counter()
        posts_by_month: Counter[str] = Counter()
        posts_by_weekday: Counter[str] = Counter()
        posts_by_hour: Counter[int] = Counter()

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

    def _get_engagement_analysis(self, analyzer: Any) -> dict[str, Any]:
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

        # Engagement distribution - ensure numeric values
        likes_counts = [
            (
                int(p.likes_count)
                if isinstance(p.likes_count, (int, str)) and str(p.likes_count).isdigit()
                else 0
            )
            for p in posts
        ]
        comments_counts = [
            (
                int(p.comments_count)
                if isinstance(p.comments_count, (int, str))
                and str(p.comments_count).isdigit()
                else 0
            )
            for p in posts
        ]

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

    def _get_content_analysis(self, analyzer: Any) -> dict[str, Any]:
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
            sum(len(str(c)) for c in captions) / len(captions) if captions else 0
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
                    round(
                        int(posts_with_hashtags) / len(analyzer.posts) * 100, 1
                    )
                    if isinstance(posts_with_hashtags, (int, float)) or (
                        isinstance(posts_with_hashtags, str) and posts_with_hashtags.isdigit()
                    )
                    else 0
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

    def _get_posts_data(
        self, analyzer: Any, anonymize: bool, max_items: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Get formatted posts data."""
        sorted_posts = sorted(analyzer.posts, key=lambda x: x.timestamp, reverse=True)
        if max_items:
            sorted_posts = sorted_posts[:max_items]
        return [
            self._format_post_for_report(p, analyzer, anonymize) for p in sorted_posts
        ]

    def _get_stories_data(
        self, analyzer: Any, anonymize: bool, max_items: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Get formatted stories data."""
        sorted_stories = sorted(analyzer.stories, key=lambda x: x.taken_at, reverse=True)
        if max_items:
            sorted_stories = sorted_stories[:max_items]
        return [
            self._format_story_for_report(s, analyzer, anonymize) for s in sorted_stories
        ]

    def _get_reels_data(
        self, analyzer: Any, anonymize: bool, max_items: Optional[int] = None
    ) -> list[dict[str, Any]]:
        """Get formatted reels data."""
        sorted_reels = sorted(analyzer.reels, key=lambda x: x.taken_at, reverse=True)
        if max_items:
            sorted_reels = sorted_reels[:max_items]
        return [
            self._format_reel_for_report(r, analyzer, anonymize) for r in sorted_reels
        ]

    def _get_additional_content_data(
        self, analyzer: Any, max_items: Optional[int] = None
    ) -> dict[str, Any]:
        """Get data for archived and recently deleted content with relative media paths."""
        # Archived posts
        archived_posts = []
        sorted_archived = sorted(
            analyzer.archived_posts, key=lambda x: x.timestamp, reverse=True
        )
        if max_items:
            sorted_archived = sorted_archived[:max_items]
        for p in sorted_archived:
            post_data = self._format_post_for_report(p, analyzer, False)
            # Make all media paths relative if present
            for media in post_data.get("media", []):
                if "uri" in media and media["uri"]:
                    try:
                        html_dir = (
                            analyzer.output_path
                            if hasattr(analyzer, "output_path")
                            else Path(".")
                        )
                        if not hasattr(analyzer, "output_path") and hasattr(
                            analyzer, "report_file"
                        ):
                            html_dir = Path(analyzer.report_file).parent
                        img_path = Path(media["uri"])
                        if not img_path.is_absolute():
                            img_path = (analyzer.data_path / img_path).resolve()
                        rel_path = os.path.relpath(str(img_path), str(html_dir))
                        media["uri"] = rel_path
                    except (ValueError, OSError) as e:
                        logging.warning(f"Could not convert image path: {e}")
                if "thumbnail" in media and media["thumbnail"]:
                    try:
                        html_dir = (
                            analyzer.output_path
                            if hasattr(analyzer, "output_path")
                            else Path(".")
                        )
                        if not hasattr(analyzer, "output_path") and hasattr(
                            analyzer, "report_file"
                        ):
                            html_dir = Path(analyzer.report_file).parent
                        thumb_path = Path(media["thumbnail"])
                        if not thumb_path.is_absolute():
                            thumb_path = (analyzer.data_path / thumb_path).resolve()
                        rel_path = os.path.relpath(str(thumb_path), str(html_dir))
                        media["thumbnail"] = rel_path
                    except (ValueError, OSError) as e:
                        logging.warning(f"Could not convert thumbnail path: {e}")
            archived_posts.append(post_data)

        # Recently deleted content
        recently_deleted = []
        sorted_deleted = sorted(
            analyzer.recently_deleted, key=lambda x: x.timestamp, reverse=True
        )
        if max_items:
            sorted_deleted = sorted_deleted[:max_items]
        for item in sorted_deleted:
            media_path = resolve_media_path(item.uri, analyzer.data_path)
            thumb = (
                get_image_thumbnail(media_path, (100, 100))
                if item.media_type.value == "IMAGE" and media_path
                else None
            )
            # Make uri and thumbnail always relative to output_dir
            uri_val = item.uri
            if uri_val:
                try:
                    html_dir = (
                        analyzer.output_path
                        if hasattr(analyzer, "output_path")
                        else Path(".")
                    )
                    if not hasattr(analyzer, "output_path") and hasattr(
                        analyzer, "report_file"
                    ):
                        html_dir = Path(analyzer.report_file).parent
                    uri_path = Path(uri_val)
                    if not uri_path.is_absolute():
                        uri_path = (analyzer.data_path / uri_path).resolve()
                    rel_path = os.path.relpath(str(uri_path), str(html_dir))
                    uri_val = rel_path
                except (ValueError, OSError) as e:
                    logging.warning(f"Could not convert URI path: {e}")
            if thumb:
                try:
                    html_dir = (
                        analyzer.output_path
                        if hasattr(analyzer, "output_path")
                        else Path(".")
                    )
                    if not hasattr(analyzer, "output_path") and hasattr(
                        analyzer, "report_file"
                    ):
                        html_dir = Path(analyzer.report_file).parent
                    thumb_path = Path(thumb)
                    if not thumb_path.is_absolute():
                        thumb_path = (analyzer.data_path / thumb_path).resolve()
                    rel_path = os.path.relpath(str(thumb_path), str(html_dir))
                    thumb = rel_path
                except (ValueError, OSError) as e:
                    logging.warning(f"Could not convert thumbnail path: {e}")
            recently_deleted.append(
                {
                    "uri": uri_val,
                    "timestamp": (
                        item.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                        if item.timestamp
                        else "N/A"
                    ),
                    "media_type": item.media_type.value,
                    "title": item.title,
                    "thumbnail": thumb,
                }
            )

        return {"archived_posts": archived_posts, "recently_deleted": recently_deleted}

    def _get_story_interactions_data(
        self, analyzer: Any, anonymize: bool, max_items: Optional[int] = None
    ) -> dict[str, Any]:
        """Get formatted story interactions data."""
        if not analyzer.story_interactions:
            return {"interactions": [], "summary": {}}

        sorted_interactions = sorted(
            analyzer.story_interactions, key=lambda x: x.timestamp, reverse=True
        )
        if max_items:
            sorted_interactions = sorted_interactions[:max_items]
        interactions = [
            self._format_interaction_for_report(i, anonymize) for i in sorted_interactions
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

    def _get_charts_data(self, analyzer: Any) -> dict[str, Any]:
        """Get data for generating charts."""
        charts_data = {}
        # Monthly activity data
        monthly_data: Counter[str] = Counter()
        for post in analyzer.posts:
            if post.timestamp:
                month_key = post.timestamp.strftime("%Y-%m")
                monthly_data[month_key] += 1
        sorted_months = sorted(monthly_data.keys())
        charts_data["monthly_activity"] = {
            "labels": sorted_months,
            "data": [monthly_data[m] for m in sorted_months],
        }

        # Weekday activity
        weekday_data: Counter[str] = Counter()
        for post in analyzer.posts:
            if post.timestamp:
                weekday_data[post.timestamp.strftime("%A")] += 1
        weekday_labels = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        charts_data["weekday_activity"] = {
            "labels": weekday_labels,
            "data": [weekday_data.get(day, 0) for day in weekday_labels],
        }

        # Hour activity
        hourly_data: Counter[int] = Counter()
        for post in analyzer.posts:
            if post.timestamp:
                hourly_data[post.timestamp.hour] += 1
        hour_labels = [str(h) for h in range(24)]
        charts_data["hourly_activity"] = {
            "labels": hour_labels,
            "data": [hourly_data.get(h, 0) for h in range(24)],
        }

        # Engagement by weekday (se mantiene igual)
        engagement_by_weekday = {i: {"likes": 0, "comments": 0} for i in range(7)}
        for post in analyzer.posts:
            if post.timestamp:
                weekday = post.timestamp.weekday()
                engagement_by_weekday[weekday]["likes"] += post.likes_count
                engagement_by_weekday[weekday]["comments"] += post.comments_count
        charts_data["engagement_by_weekday"] = {
            "labels": weekday_labels,
            "likes": [engagement_by_weekday[i]["likes"] for i in range(7)],
            "comments": [engagement_by_weekday[i]["comments"] for i in range(7)],
        }

        # Story interactions over time (se mantiene igual)
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

    def _get_network_graph_data(self, analyzer: Any) -> Optional[dict[str, Any]]:
        """Get data for network graph visualization."""
        if not analyzer.profile or not analyzer.posts:
            return {"nodes": [], "links": []}

        network = NetworkAnalyzer(analyzer.profile.username)
        return network.analyze(analyzer.posts)

    def _render_template(self, data: dict[str, Any]) -> str:
        """Render the HTML template with data."""
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
        self, post: Post, analyzer: Any, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single post for the report."""
        data = {
            "id": getattr(post, "id", ""),
            "uri": getattr(post, "uri", ""),
            "shortcode": getattr(post, "shortcode", ""),
            "timestamp": (
                post.timestamp.strftime("%Y-%m-%d %H:%M:%S") if post.timestamp else "N/A"
            ),
            "likes": post.likes_count,
            "comments": post.comments_count,
            "media_count": len(post.media),
            "caption": safe_html_escape(truncate_text(post.caption or "", 100)),
            "full_caption": safe_html_escape(post.caption or ""),
            "hashtags": post.hashtags or [],
            "mentions": post.mentions or [],
            "media": [],
        }

        # Add media info (limit to first 3 items for compact mode, 5 for normal)
        media_limit = (
            3 if hasattr(analyzer, "_compact_mode") and analyzer._compact_mode else 5
        )
        media_list = []
        for media in post.media[:media_limit]:
            media_info = {
                "uri": media.uri,
                "type": media.media_type.value,
                "title": media.title or "",
            }

            # Generar ruta relativa real desde el HTML generado hasta la imagen
            if media_info["uri"]:
                if str(media_info["uri"]).startswith("data:image/"):
                    pass
                else:
                    try:
                        # Determinar la ubicación del HTML generado
                        # El output_path se pasa al export, lo usamos aquí
                        html_dir = (
                            analyzer.output_path
                            if hasattr(analyzer, "output_path")
                            else Path(".")
                        )
                        # Si analyzer no tiene output_path, intentar deducirlo
                        if not hasattr(analyzer, "output_path") and hasattr(
                            analyzer, "report_file"
                        ):
                            html_dir = Path(analyzer.report_file).parent
                        img_path = Path(media_info["uri"])
                        # Si la ruta no es absoluta, hazla absoluta respecto al data_path
                        if not img_path.is_absolute():
                            img_path = (analyzer.data_path / img_path).resolve()
                        rel_path = os.path.relpath(str(img_path), str(html_dir))
                        media_info["uri"] = rel_path
                    except (OSError, ValueError, TypeError) as e:
                        logging.debug(f"Could not resolve media path: {e}")
                        pass

            # Try to generate thumbnail for images
            if media.media_type.value == "image":
                media_path = resolve_media_path(media.uri, analyzer.data_path)
                if media_path:
                    thumbnail = get_image_thumbnail(media_path)
                    # Make thumbnail with "../" prefix
                    if thumbnail and not str(thumbnail).startswith("data:image/"):
                        try:
                            thumb_path = Path(thumbnail)
                            if not str(thumb_path).startswith("../"):
                                media_info["thumbnail"] = "../" + str(thumb_path)
                            else:
                                media_info["thumbnail"] = str(thumb_path)
                        except (OSError, ValueError) as e:
                            logging.debug(f"Could not create thumbnail: {e}")
                            pass  # No ponemos una imagen de marcador de posición

            media_list.append(media_info)

        data["media"] = media_list

        # Anonymize user data if required
        if anonymize:
            data["username"] = "anonymous"
            data["profile_picture"] = None
        else:
            owner = getattr(post, "owner", {})
            data["username"] = owner.get("username", "unknown")
            data["profile_picture"] = owner.get("profile_picture_url", None)

        return data

    def _format_story_for_report(
        self, story: Story, analyzer: Any, anonymize: bool
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

        # Generar ruta relativa real desde el HTML generado hasta la imagen de la historia
        if data["media_uri"]:
            try:
                html_dir = (
                    analyzer.output_path
                    if hasattr(analyzer, "output_path")
                    else Path(".")
                )
                if not hasattr(analyzer, "output_path") and hasattr(
                    analyzer, "report_file"
                ):
                    html_dir = Path(analyzer.report_file).parent
                img_path = Path(data["media_uri"])
                if not img_path.is_absolute():
                    img_path = (analyzer.data_path / img_path).resolve()
                rel_path = os.path.relpath(str(img_path), str(html_dir))
                data["media_uri"] = rel_path
            except Exception:
                pass

        # Add thumbnail for images
        if story.media and story.media.media_type.value == "IMAGE":
            thumbnail_path = resolve_media_path(story.media.uri, analyzer.data_path)
            if thumbnail_path:
                thumbnail = get_image_thumbnail(thumbnail_path, (150, 150))
                # Make thumbnail with "../" prefix
                if thumbnail and not str(thumbnail).startswith("data:image/"):
                    try:
                        thumb_path = Path(thumbnail)
                        if not str(thumb_path).startswith("../"):
                            data["thumbnail"] = "../" + str(thumb_path)
                        else:
                            data["thumbnail"] = str(thumb_path)
                    except Exception:
                        pass  # No ponemos una imagen de marcador de posición

        return data

    def _format_reel_for_report(
        self, reel: Reel, analyzer: Any, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single reel for the report."""
        taken_at = getattr(reel, "taken_at", None)
        reel_media = getattr(reel, "media", None)

        data = {
            "taken_at": (taken_at.strftime("%Y-%m-%d %H:%M:%S") if taken_at else "N/A"),
            "caption": clean_instagram_text(reel.caption) if reel.caption else "",
            "media_uri": reel_media.uri if reel_media else "",
            "media_type": (reel_media.media_type.value if reel_media else "unknown"),
            "likes_count": getattr(reel, "likes_count", 0),
            "comments_count": getattr(reel, "comments_count", 0),
        }

        # Generar ruta relativa real desde el HTML generado hasta la imagen del reel
        if data["media_uri"]:
            try:
                html_dir = (
                    analyzer.output_path
                    if hasattr(analyzer, "output_path")
                    else Path(".")
                )
                if not hasattr(analyzer, "output_path") and hasattr(
                    analyzer, "report_file"
                ):
                    html_dir = Path(analyzer.report_file).parent
                img_path = Path(data["media_uri"])
                if not img_path.is_absolute():
                    img_path = (analyzer.data_path / img_path).resolve()
                rel_path = os.path.relpath(str(img_path), str(html_dir))
                data["media_uri"] = rel_path
            except Exception:
                pass

        # Add thumbnail for videos (first frame) or images
        if reel_media:
            thumbnail_path = resolve_media_path(reel_media.uri, analyzer.data_path)
            if thumbnail_path:
                thumbnail = get_image_thumbnail(thumbnail_path, (150, 150))
                # Make thumbnail with "../" prefix
                if thumbnail and not str(thumbnail).startswith("data:image/"):
                    try:
                        thumb_path = Path(thumbnail)
                        if not str(thumb_path).startswith("../"):
                            data["thumbnail"] = "../" + str(thumb_path)
                        else:
                            data["thumbnail"] = str(thumb_path)
                    except Exception:
                        pass  # No ponemos una imagen de marcador de posición

        return data

    def _format_interaction_for_report(
        self, interaction: StoryInteraction, anonymize: bool
    ) -> dict[str, Any]:
        """Format a single story interaction for the report."""
        username = getattr(interaction, "username", "unknown")
        return {
            "type": interaction.interaction_type,
            "username": "anonymous" if anonymize else username,
            "timestamp": (
                interaction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                if interaction.timestamp
                else "N/A"
            ),
        }
