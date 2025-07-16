"""Text processing utilities for Instagram data."""

import re
import html
from typing import Optional


def clean_instagram_text(text: Optional[str]) -> str:
    """Clean and fix text from Instagram exports.
    
    Instagram exports sometimes have encoding issues with emojis and special characters.
    This function attempts to fix common encoding problems.
    
    Args:
        text: Raw text from Instagram export
        
    Returns:
        Cleaned text with proper encoding
    """
    if not text:
        return ""
    
    # Handle cases where text is already a string
    if isinstance(text, str):
        # Try to fix common encoding issues
        try:
            # Handle HTML entities
            text = html.unescape(text)
            
            # Fix common mojibake patterns for emojis
            # These are common patterns when UTF-8 emojis are incorrectly encoded
            emoji_fixes = {
                'ð\x9f\x92\x8d': '💍',  # ring emoji
                'ð\x9f¤\x8d': '🤍',    # white heart emoji
                'ð\x9f\x98\x8d': '😍',  # heart eyes emoji
                'ð\x9f\x98\x98': '😘',  # kiss emoji
                'ð\x9f\x98\x80': '😀',  # grinning emoji
                'ð\x9f\x98\x82': '😂',  # crying laughing emoji
                'ð\x9f\x99\x8f': '🙏',  # prayer hands emoji
                'ð\x9f\x92\x95': '💕',  # two hearts emoji
                'ð\x9f\x94¥': '🔥',    # fire emoji
                'ð\x9f\x8c\x9f': '🌟',  # star emoji
                'â\x9d\xa4ï¸\x8f': '❤️', # red heart emoji
                'â\x9c\xa8': '✨',      # sparkles emoji
            }
            
            for broken, fixed in emoji_fixes.items():
                text = text.replace(broken, fixed)
            
            # Remove any remaining invalid UTF-8 sequences
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Clean up any remaining mojibake patterns
            text = re.sub(r'[ð\x9f]+[\x80-\xbf]*', '', text)
            text = re.sub(r'â[\x80-\xbf]*', '', text)
            
            # Normalize whitespace
            text = ' '.join(text.split())
            
        except Exception:
            # If all else fails, keep only ASCII characters
            text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()


def extract_hashtags(text: str) -> list:
    """Extract hashtags from text with better Unicode support.
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List of hashtags (without the # symbol)
    """
    if not text:
        return []
    
    # Clean the text first
    text = clean_instagram_text(text)
    
    # Extract hashtags - support Unicode characters
    hashtag_pattern = r'#(\w+(?:\w+)*)'
    hashtags = re.findall(hashtag_pattern, text, re.UNICODE)
    
    return hashtags


def extract_mentions(text: str) -> list:
    """Extract mentions from text with better Unicode support.
    
    Args:
        text: Text to extract mentions from
        
    Returns:
        List of usernames (without the @ symbol)
    """
    if not text:
        return []
    
    # Clean the text first
    text = clean_instagram_text(text)
    
    # Extract mentions - Instagram usernames are ASCII only
    mention_pattern = r'@([a-zA-Z0-9_.]+)'
    mentions = re.findall(mention_pattern, text)
    
    return mentions


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to a maximum length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    
    text = clean_instagram_text(text)
    
    if len(text) <= max_length:
        return text
    
    # Find the last space before the max length to avoid cutting words
    truncate_pos = text.rfind(' ', 0, max_length - 3)
    if truncate_pos == -1:
        truncate_pos = max_length - 3
    
    return text[:truncate_pos] + '...'


def safe_html_escape(text: str) -> str:
    """Safely escape HTML while preserving emojis.
    
    Args:
        text: Text to escape
        
    Returns:
        HTML-safe text
    """
    if not text:
        return ""
    
    # Clean the text first
    text = clean_instagram_text(text)
    
    # Escape HTML characters but preserve emojis
    text = html.escape(text, quote=False)
    
    return text