"""Temporal analysis for Instagram data."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from ..models import Post, Story, Reel
from ..utils import get_activity_hours, get_activity_days_of_week


class TemporalAnalyzer:
    """Analyzer for temporal patterns in Instagram data."""
    
    def analyze(self, posts: List[Post], stories: List[Story], 
                reels: List[Reel]) -> Dict[str, Any]:
        """Analyze temporal patterns in Instagram activity.
        
        Args:
            posts: List of posts
            stories: List of stories  
            reels: List of reels
            
        Returns:
            Dictionary containing temporal analysis results
        """
        all_content = posts + stories + reels
        
        if not all_content:
            return {}
        
        temporal_stats = {}
        
        # Hour-based analysis
        temporal_stats.update(self._analyze_hourly_patterns(all_content))
        
        # Day-based analysis
        temporal_stats.update(self._analyze_daily_patterns(all_content))
        
        # Monthly trends
        temporal_stats.update(self._analyze_monthly_trends(all_content))
        
        # Activity streaks
        temporal_stats.update(self._analyze_activity_streaks(all_content))
        
        # Peak activity periods
        temporal_stats.update(self._find_peak_periods(all_content))
        
        return temporal_stats
    
    def _analyze_hourly_patterns(self, content: List) -> Dict[str, Any]:
        """Analyze activity patterns by hour of day."""
        timestamps = [item.timestamp for item in content]
        hourly_activity = get_activity_hours(timestamps)
        
        # Find peak hours
        peak_hour = max(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (0, 0)
        quiet_hour = min(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (0, 0)
        
        # Calculate activity periods
        morning_posts = sum(hourly_activity.get(h, 0) for h in range(6, 12))
        afternoon_posts = sum(hourly_activity.get(h, 0) for h in range(12, 18))
        evening_posts = sum(hourly_activity.get(h, 0) for h in range(18, 24))
        night_posts = sum(hourly_activity.get(h, 0) for h in range(0, 6))
        
        total_posts = len(content)
        
        return {
            "hourly_activity": hourly_activity,
            "peak_hour": peak_hour[0],
            "peak_hour_posts": peak_hour[1],
            "quiet_hour": quiet_hour[0],
            "quiet_hour_posts": quiet_hour[1],
            "morning_activity_rate": (morning_posts / total_posts * 100) if total_posts else 0,
            "afternoon_activity_rate": (afternoon_posts / total_posts * 100) if total_posts else 0,
            "evening_activity_rate": (evening_posts / total_posts * 100) if total_posts else 0,
            "night_activity_rate": (night_posts / total_posts * 100) if total_posts else 0,
            "most_active_period": self._get_most_active_period(morning_posts, afternoon_posts, evening_posts, night_posts)
        }
    
    def _get_most_active_period(self, morning: int, afternoon: int, evening: int, night: int) -> str:
        """Determine most active time period."""
        periods = {"morning": morning, "afternoon": afternoon, "evening": evening, "night": night}
        return max(periods.items(), key=lambda x: x[1])[0]
    
    def _analyze_daily_patterns(self, content: List) -> Dict[str, Any]:
        """Analyze activity patterns by day of week."""
        timestamps = [item.timestamp for item in content]
        daily_activity = get_activity_days_of_week(timestamps)
        
        # Find peak days
        peak_day = max(daily_activity.items(), key=lambda x: x[1]) if daily_activity else ("", 0)
        quiet_day = min(daily_activity.items(), key=lambda x: x[1]) if daily_activity else ("", 0)
        
        # Weekend vs weekday analysis
        weekend_posts = daily_activity.get("Saturday", 0) + daily_activity.get("Sunday", 0)
        weekday_posts = sum(daily_activity.get(day, 0) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        total_posts = len(content)
        
        return {
            "daily_activity": daily_activity,
            "peak_day": peak_day[0],
            "peak_day_posts": peak_day[1],
            "quiet_day": quiet_day[0],
            "quiet_day_posts": quiet_day[1],
            "weekend_activity_rate": (weekend_posts / total_posts * 100) if total_posts else 0,
            "weekday_activity_rate": (weekday_posts / total_posts * 100) if total_posts else 0,
            "weekend_vs_weekday_ratio": (weekend_posts / weekday_posts) if weekday_posts else 0
        }
    
    def _analyze_monthly_trends(self, content: List) -> Dict[str, Any]:
        """Analyze monthly posting trends."""
        monthly_counts = defaultdict(int)
        yearly_counts = defaultdict(int)
        
        for item in content:
            month_key = item.timestamp.strftime("%Y-%m")
            year_key = item.timestamp.strftime("%Y")
            monthly_counts[month_key] += 1
            yearly_counts[year_key] += 1
        
        # Calculate trends
        monthly_trend = self._calculate_trend(monthly_counts)
        yearly_trend = self._calculate_trend(yearly_counts)
        
        # Find most/least active months
        most_active_month = max(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else ("", 0)
        least_active_month = min(monthly_counts.items(), key=lambda x: x[1]) if monthly_counts else ("", 0)
        
        return {
            "monthly_activity": dict(monthly_counts),
            "yearly_activity": dict(yearly_counts),
            "monthly_trend": monthly_trend,
            "yearly_trend": yearly_trend,
            "most_active_month": most_active_month[0],
            "most_active_month_posts": most_active_month[1],
            "least_active_month": least_active_month[0],
            "least_active_month_posts": least_active_month[1],
            "activity_variance": self._calculate_variance(list(monthly_counts.values()))
        }
    
    def _calculate_trend(self, time_series: Dict[str, int]) -> str:
        """Calculate trend direction in time series data."""
        if len(time_series) < 2:
            return "insufficient_data"
        
        values = list(time_series.values())
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half_avg > first_half_avg * 1.1:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calculate variance in activity levels."""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def _analyze_activity_streaks(self, content: List) -> Dict[str, Any]:
        """Analyze posting streaks and gaps."""
        if not content:
            return {}
        
        # Sort content by timestamp
        sorted_content = sorted(content, key=lambda x: x.timestamp)
        
        # Group by day
        daily_posts = defaultdict(int)
        for item in sorted_content:
            day_key = item.timestamp.strftime("%Y-%m-%d")
            daily_posts[day_key] += 1
        
        # Calculate streaks
        active_days = sorted(daily_posts.keys())
        longest_streak = self._find_longest_streak(active_days)
        longest_gap = self._find_longest_gap(active_days)
        
        return {
            "total_active_days": len(active_days),
            "longest_active_streak_days": longest_streak,
            "longest_inactive_gap_days": longest_gap,
            "average_posts_per_active_day": sum(daily_posts.values()) / len(daily_posts) if daily_posts else 0,
            "most_posts_single_day": max(daily_posts.values()) if daily_posts else 0
        }
    
    def _find_longest_streak(self, dates: List[str]) -> int:
        """Find longest consecutive posting streak."""
        if not dates:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i-1], "%Y-%m-%d")
            curr_date = datetime.strptime(dates[i], "%Y-%m-%d")
            
            if (curr_date - prev_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def _find_longest_gap(self, dates: List[str]) -> int:
        """Find longest gap between posts."""
        if len(dates) < 2:
            return 0
        
        max_gap = 0
        
        for i in range(1, len(dates)):
            prev_date = datetime.strptime(dates[i-1], "%Y-%m-%d")
            curr_date = datetime.strptime(dates[i], "%Y-%m-%d")
            gap = (curr_date - prev_date).days - 1  # -1 because we want gap days
            max_gap = max(max_gap, gap)
        
        return max_gap
    
    def _find_peak_periods(self, content: List) -> Dict[str, Any]:
        """Find peak activity periods."""
        if not content:
            return {}
        
        # Group by week
        weekly_counts = defaultdict(int)
        for item in content:
            # Get Monday of the week
            monday = item.timestamp - timedelta(days=item.timestamp.weekday())
            week_key = monday.strftime("%Y-%m-%d")
            weekly_counts[week_key] += 1
        
        # Find peak week
        peak_week = max(weekly_counts.items(), key=lambda x: x[1]) if weekly_counts else ("", 0)
        
        # Calculate activity intensity
        total_weeks = len(weekly_counts)
        average_weekly_posts = sum(weekly_counts.values()) / total_weeks if total_weeks else 0
        
        # Find weeks above average
        above_average_weeks = sum(1 for count in weekly_counts.values() if count > average_weekly_posts)
        
        return {
            "peak_week": peak_week[0],
            "peak_week_posts": peak_week[1],
            "average_weekly_posts": average_weekly_posts,
            "weeks_above_average": above_average_weeks,
            "activity_intensity_score": (above_average_weeks / total_weeks * 100) if total_weeks else 0
        }