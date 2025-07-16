"""Advanced HTML exporter for Instagram analysis reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
import base64

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
            "analyzer_version": "0.1.0",
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
        elif anonymize:
            metadata.update({"username": "User***", "display_name": "Anonymous User"})

        return metadata

    def _get_overview_stats(self, analyzer) -> Dict[str, Any]:
        """Get overview statistics."""
        posts = analyzer.posts
        stories = analyzer.stories
        reels = analyzer.reels

        if not posts:
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

        # Engagement totals
        total_likes = sum(p.likes_count for p in posts)
        total_comments = sum(p.comments_count for p in posts)

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
                    round(total_likes / len(posts), 1) if posts else 0
                ),
                "avg_comments_per_post": (
                    round(total_comments / len(posts), 1) if posts else 0
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
        """Render the HTML template with data."""
        template = self.template

        # Replace template variables
        template = template.replace(
            "{{METADATA}}", json.dumps(data["metadata"], default=str)
        )
        template = template.replace(
            "{{OVERVIEW}}", json.dumps(data["overview"], default=str)
        )
        template = template.replace(
            "{{TEMPORAL}}", json.dumps(data["temporal_analysis"], default=str)
        )
        template = template.replace(
            "{{ENGAGEMENT}}", json.dumps(data["engagement_analysis"], default=str)
        )
        template = template.replace(
            "{{CONTENT}}", json.dumps(data["content_analysis"], default=str)
        )
        template = template.replace("{{POSTS}}", json.dumps(data["posts"], default=str))
        template = template.replace(
            "{{CHARTS}}", json.dumps(data["charts_data"], default=str)
        )

        return template

    def _get_template(self) -> str:
        """Get the HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #4a4a4a;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .nav-menu {
            background: rgba(255, 255, 255, 0.8);
            padding: 10px 20px;
            display: flex;
            gap: 15px;
            justify-content: center;
            border-radius: 10px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .nav-menu a {
            color: #4a4a4a;
            text-decoration: none;
            font-weight: 500;
        }

        .nav-menu a:hover {
            color: #764ba2;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .section h2 {
            color: #4a4a4a;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        .stat-number {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }
        
        .posts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .post-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            background: #fafafa;
        }
        
        .post-media {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }
        
        .media-thumbnail {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            object-fit: cover;
            border: 2px solid #e0e0e0;
        }
        
        .media-placeholder {
            width: 60px;
            height: 60px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f0f0f0;
            font-size: 0.7em;
            font-weight: bold;
            color: #666;
        }
        
        .post-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }
        
        .post-header {
            padding: 15px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .post-content {
            padding: 15px;
        }
        
        .post-stats {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .hashtags {
            margin-top: 10px;
        }
        
        .hashtag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }
        
        .top-hashtags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        
        .top-hashtag {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: 500;
        }
        
        .engagement-list {
            list-style: none;
        }
        
        .engagement-item {
            background: #f8f9ff;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .posts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📸 Instagram Analysis Report</h1>
            <div id="metadata-info">
                <div class="loading">Loading report data...</div>
            </div>
        </div>

        <nav class="nav-menu">
            <a href="#overview">Overview</a>
            <a href="#temporal">Activity</a>
            <a href="#engagement">Engagement</a>
            <a href="#content">Content</a>
            <a href="#posts">Posts</a>
        </nav>

        <!-- Overview Stats -->
        <div class="section" id="overview">
            <h2>📊 Overview Statistics</h2>
            <div id="overview-stats">
                <div class="loading">Loading statistics...</div>
            </div>
        </div>

        <!-- Temporal Analysis -->
        <div class="section" id="temporal">
            <h2>📅 Activity Over Time</h2>
            <div id="temporal-analysis">
                <div class="loading">Loading temporal analysis...</div>
            </div>
        </div>

        <!-- Engagement Analysis -->
        <div class="section" id="engagement">
            <h2>💝 Engagement Analysis</h2>
            <div id="engagement-analysis">
                <div class="loading">Loading engagement data...</div>
            </div>
        </div>

        <!-- Content Analysis -->
        <div class="section" id="content">
            <h2>🔍 Content Analysis</h2>
            <div id="content-analysis">
                <div class="loading">Loading content analysis...</div>
            </div>
        </div>

        <!-- Posts Gallery -->
        <div class="section" id="posts">
            <h2>📷 Recent Posts</h2>
            <div id="posts-gallery">
                <div class="loading">Loading posts...</div>
            </div>
        </div>
    </div>

    <script>
        // Data will be injected here
        const metadata = {{METADATA}};
        const overview = {{OVERVIEW}};
        const temporal = {{TEMPORAL}};
        const engagement = {{ENGAGEMENT}};
        const content = {{CONTENT}};
        const posts = {{POSTS}};
        const charts = {{CHARTS}};
        
        // Render metadata
        function renderMetadata() {
            const container = document.getElementById('metadata-info');
            container.innerHTML = `
                <p><strong>Generated:</strong> ${metadata.generated_at}</p>
                ${metadata.username ? `<p><strong>Account:</strong> @${metadata.username}</p>` : ''}
                <p><strong>Version:</strong> Instagram Analyzer v${metadata.analyzer_version}</p>
            `;
        }
        
        // Render overview stats
        function renderOverview() {
            const container = document.getElementById('overview-stats');
            
            if (!overview.has_data) {
                container.innerHTML = '<p>No data available</p>';
                return;
            }
            
            const stats = overview.content_counts;
            const dates = overview.date_range;
            const engagement = overview.engagement_totals;
            
            container.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">${stats.posts}</div>
                        <div class="stat-label">Posts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${stats.total_media}</div>
                        <div class="stat-label">Total Media</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${engagement.likes}</div>
                        <div class="stat-label">Total Likes</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${engagement.comments}</div>
                        <div class="stat-label">Total Comments</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${dates.years_active}</div>
                        <div class="stat-label">Years Active</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">${engagement.avg_likes_per_post}</div>
                        <div class="stat-label">Avg Likes/Post</div>
                    </div>
                </div>
                <p><strong>Active Period:</strong> ${dates.start} to ${dates.end} (${dates.active_days} days)</p>
            `;
        }
        
        // Render temporal analysis
        function renderTemporal() {
            const container = document.getElementById('temporal-analysis');
            
            if (!temporal.has_data) {
                container.innerHTML = '<p>No temporal data available</p>';
                return;
            }
            
            container.innerHTML = `
                <div class="stats-grid">
                    <div>
                        <h3>Most Active Periods</h3>
                        <ul>
                            ${temporal.most_active.year ? `<li><strong>Year:</strong> ${temporal.most_active.year}</li>` : ''}
                            ${temporal.most_active.month ? `<li><strong>Month:</strong> ${temporal.most_active.month}</li>` : ''}
                            ${temporal.most_active.weekday ? `<li><strong>Day:</strong> ${temporal.most_active.weekday}</li>` : ''}
                            ${temporal.most_active.hour ? `<li><strong>Hour:</strong> ${temporal.most_active.hour}</li>` : ''}
                        </ul>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="monthly-chart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="weekday-chart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="hourly-chart"></canvas>
                </div>
            `;

            // Create charts
            createMonthlyChart();
            createWeekdayChart();
            createHourlyChart();
        }
        
        // Render engagement analysis
        function renderEngagement() {
            const container = document.getElementById('engagement-analysis');
            
            if (!engagement.has_data) {
                container.innerHTML = '<p>No engagement data available</p>';
                return;
            }
            
            const dist = engagement.distribution;
            
            container.innerHTML = `
                <div class="stats-grid">
                    <div>
                        <h3>Engagement Distribution</h3>
                        <ul>
                            <li><strong>Average Likes:</strong> ${dist.avg_likes}</li>
                            <li><strong>Median Likes:</strong> ${dist.median_likes}</li>
                            <li><strong>Max Likes:</strong> ${dist.max_likes}</li>
                            <li><strong>Average Comments:</strong> ${dist.avg_comments}</li>
                            <li><strong>Max Comments:</strong> ${dist.max_comments}</li>
                        </ul>
                    </div>
                </div>
                <div>
                    <h3>Top Performing Posts</h3>
                    <h4>Most Liked</h4>
                    <ul class="engagement-list">
                        ${engagement.top_posts.most_liked.map(post => `
                            <li class="engagement-item">
                                <strong>${post.likes} likes, ${post.comments} comments</strong><br>
                                ${post.caption}<br>
                                <small>${post.date} • ${post.media_count} media</small>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Render content analysis
        function renderContent() {
            const container = document.getElementById('content-analysis');
            
            if (!content.has_data) {
                container.innerHTML = '<p>No content analysis available</p>';
                return;
            }
            
            const hashtags = content.hashtags;
            const captions = content.captions;
            const media = content.media_types;
            
            container.innerHTML = `
                <div class="stats-grid">
                    <div>
                        <h3>Hashtag Usage</h3>
                        <ul>
                            <li><strong>Unique Hashtags:</strong> ${hashtags.total_unique}</li>
                            <li><strong>Total Usage:</strong> ${hashtags.total_usage}</li>
                            <li><strong>Usage Rate:</strong> ${hashtags.usage_rate}%</li>
                            <li><strong>Avg per Post:</strong> ${hashtags.avg_per_post}</li>
                        </ul>
                    </div>
                    <div>
                        <h3>Caption Stats</h3>
                        <ul>
                            <li><strong>Posts with Captions:</strong> ${captions.posts_with_captions}</li>
                            <li><strong>Usage Rate:</strong> ${captions.usage_rate}%</li>
                            <li><strong>Avg Length:</strong> ${captions.avg_length} chars</li>
                            <li><strong>Longest:</strong> ${captions.longest} chars</li>
                        </ul>
                    </div>
                    <div>
                        <h3>Media Types</h3>
                        <ul>
                            <li><strong>Image Only:</strong> ${media.image_only}</li>
                            <li><strong>Contains Video:</strong> ${media.contains_video}</li>
                            <li><strong>Carousel:</strong> ${media.carousel}</li>
                            <li><strong>Single Media:</strong> ${media.single_media}</li>
                        </ul>
                    </div>
                </div>
                <div>
                    <h3>Top Hashtags</h3>
                    <div class="top-hashtags">
                        ${hashtags.top_hashtags.map(([tag, count]) => `
                            <span class="top-hashtag">#${tag} (${count})</span>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Render posts gallery
        function renderPosts() {
            const container = document.getElementById('posts-gallery');
            
            if (!posts || posts.length === 0) {
                container.innerHTML = '<p>No posts available</p>';
                return;
            }
            
            container.innerHTML = `
                <div class="posts-grid">
                    ${posts.map(post => `
                        <div class="post-card">
                            <div class="post-header">
                                <small>${post.date}</small>
                            </div>
                            <div class="post-content">
                                <p>${post.caption}</p>
                                <div class="post-stats">
                                    <span>❤️ ${post.likes}</span>
                                    <span>💬 ${post.comments}</span>
                                    <span>📸 ${post.media_count}</span>
                                </div>
                                ${post.media.length > 0 ? `
                                    <div class="post-media">
                                        ${post.media.map(media => 
                                            media.thumbnail ? 
                                            `<img src="${media.thumbnail}" class="media-thumbnail" alt="Post media" title="${media.title || 'Image'}">` : 
                                            `<div class="media-placeholder" title="${media.type} - ${media.title || 'No preview'}">${media.type.toUpperCase()}</div>`
                                        ).join('')}
                                    </div>
                                ` : ''}
                                ${post.hashtags.length > 0 ? `
                                    <div class="hashtags">
                                        ${post.hashtags.map(tag => `<span class="hashtag">#${tag}</span>`).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        // Create monthly activity chart
        function createMonthlyChart() {
            const ctx = document.getElementById('monthly-chart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: charts.monthly_activity.labels,
                    datasets: [{
                        label: 'Posts per Month',
                        data: charts.monthly_activity.data,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Monthly Posting Activity'
                        }
                    }
                }
            });
        }
        
        // Create weekday activity chart
        function createWeekdayChart() {
            const ctx = document.getElementById('weekday-chart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: charts.weekday_activity.labels,
                    datasets: [{
                        label: 'Posts per Day',
                        data: charts.weekday_activity.data,
                        backgroundColor: '#764ba2'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Posts by Day of Week'
                        }
                    }
                }
            });
        }

        // Create hourly activity chart
        function createHourlyChart() {
            const ctx = document.getElementById('hourly-chart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: charts.hourly_activity.labels,
                    datasets: [{
                        label: 'Posts per Hour',
                        data: charts.hourly_activity.data,
                        backgroundColor: '#ff8c00'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Hourly Posting Activity'
                        }
                    }
                }
            });
        }
        
        // Initialize the report
        document.addEventListener('DOMContentLoaded', function() {
            renderMetadata();
            renderOverview();
            renderTemporal();
            renderEngagement();
            renderContent();
            renderPosts();
        });
    </script>
</body>
</html>"""
