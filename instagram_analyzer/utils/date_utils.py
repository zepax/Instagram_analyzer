"""Date and time utility functions."""

from datetime import datetime, timezone
from typing import Union, Optional, Tuple
from dateutil import parser


def parse_instagram_date(date_value: Union[str, int, float]) -> Optional[datetime]:
    """Parse Instagram date from various formats.
    
    Instagram exports can contain dates in multiple formats:
    - Unix timestamps (seconds or milliseconds)
    - ISO format strings
    - Custom format strings
    
    Args:
        date_value: Date value to parse
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_value:
        return None
    
    try:
        # Handle numeric timestamps
        if isinstance(date_value, (int, float)):
            # Check if it's milliseconds (longer than typical unix timestamp)
            if date_value > 10**10:
                date_value = date_value / 1000
            
            return datetime.fromtimestamp(date_value, tz=timezone.utc)
        
        # Handle string dates
        elif isinstance(date_value, str):
            # Try to parse as ISO format first
            try:
                return parser.isoparse(date_value)
            except ValueError:
                pass
            
            # Try general date parsing
            try:
                return parser.parse(date_value)
            except ValueError:
                pass
            
            # Try as numeric string
            try:
                timestamp = float(date_value)
                if timestamp > 10**10:
                    timestamp = timestamp / 1000
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            except ValueError:
                pass
    
    except Exception:
        pass
    
    return None


def format_date_range(start_date: datetime, end_date: datetime) -> str:
    """Format a date range as a human-readable string.
    
    Args:
        start_date: Start of date range
        end_date: End of date range
        
    Returns:
        Formatted date range string
    """
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%d, %Y')}"
        else:
            return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
    else:
        return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"


def get_time_period_stats(dates: list) -> dict:
    """Calculate time period statistics from a list of dates.
    
    Args:
        dates: List of datetime objects
        
    Returns:
        Dictionary with time period statistics
    """
    if not dates:
        return {}
    
    dates = sorted(dates)
    start_date = dates[0]
    end_date = dates[-1]
    total_days = (end_date - start_date).days + 1
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_days": total_days,
        "total_entries": len(dates),
        "entries_per_day": len(dates) / total_days if total_days > 0 else 0,
        "date_range": format_date_range(start_date, end_date)
    }


def group_dates_by_period(dates: list, period: str = "month") -> dict:
    """Group dates by time period.
    
    Args:
        dates: List of datetime objects
        period: Time period to group by ("day", "week", "month", "year")
        
    Returns:
        Dictionary with period as key and count as value
    """
    if not dates:
        return {}
    
    groups = {}
    
    for date in dates:
        if period == "day":
            key = date.strftime("%Y-%m-%d")
        elif period == "week":
            # Get Monday of the week
            monday = date - datetime.timedelta(days=date.weekday())
            key = monday.strftime("%Y-%m-%d")
        elif period == "month":
            key = date.strftime("%Y-%m")
        elif period == "year":
            key = date.strftime("%Y")
        else:
            continue
        
        groups[key] = groups.get(key, 0) + 1
    
    return groups


def get_activity_hours(dates: list) -> dict:
    """Analyze activity by hour of day.
    
    Args:
        dates: List of datetime objects
        
    Returns:
        Dictionary with hour as key and count as value
    """
    if not dates:
        return {}
    
    hours = {}
    for date in dates:
        hour = date.hour
        hours[hour] = hours.get(hour, 0) + 1
    
    return hours


def get_activity_days_of_week(dates: list) -> dict:
    """Analyze activity by day of week.
    
    Args:
        dates: List of datetime objects
        
    Returns:
        Dictionary with day name as key and count as value
    """
    if not dates:
        return {}
    
    days = {}
    day_names = [
        "Monday", "Tuesday", "Wednesday", "Thursday", 
        "Friday", "Saturday", "Sunday"
    ]
    
    for date in dates:
        day_name = day_names[date.weekday()]
        days[day_name] = days.get(day_name, 0) + 1
    
    return days