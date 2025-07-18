"""Post, Story, and Reel models for Instagram content."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from .interaction import Comment, Like
from .media import Media, MediaType


class ContentType(str, Enum):
    """Types of Instagram content."""

    POST = "post"
    STORY = "story"
    REEL = "reel"
    IGTV = "igtv"
    LIVE = "live"


class Post(BaseModel):
    """Represents an Instagram post."""

    # Core content
    caption: Optional[str] = Field(None, description="Post caption text")
    media: list[Media] = Field(..., description="Media files in the post")
    timestamp: datetime = Field(..., description="When the post was published")

    # Post metadata
    post_id: Optional[str] = Field(None, description="Instagram post ID")
    content_type: ContentType = Field(ContentType.POST, description="Type of content")
    location: Optional[str] = Field(None, description="Location tag")

    # Engagement
    likes: list[Like] = Field(default_factory=list, description="Likes on the post")
    comments: list[Comment] = Field(
        default_factory=list, description="Comments on the post"
    )
    likes_count: int = Field(0, ge=0, description="Total number of likes")
    comments_count: int = Field(0, ge=0, description="Total number of comments")

    # Content analysis
    hashtags: list[str] = Field(default_factory=list, description="Hashtags in caption")
    mentions: list[str] = Field(default_factory=list, description="Mentioned users")

    # Privacy and settings
    is_sponsored: bool = Field(False, description="Whether this is a sponsored post")
    audience: Optional[str] = Field(None, description="Post audience setting")

    # Raw data storage
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw post data")

    @field_validator("media")
    @classmethod
    def validate_media(cls, v: list[Media]) -> list[Media]:
        """Validate that post has at least one media item."""
        if not v:
            raise ValueError("Post must have at least one media item")
        return v

    @property
    def media_count(self) -> int:
        """Number of media items in the post."""
        return len(self.media)

    @property
    def is_carousel(self) -> bool:
        """Check if post is a carousel (multiple media items)."""
        return len(self.media) > 1

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate (likes + comments)."""
        return self.likes_count + self.comments_count

    @property
    def has_video(self) -> bool:
        """Check if post contains video content."""
        return any(m.media_type in [MediaType.VIDEO, MediaType.REEL] for m in self.media)

    @property
    def caption_word_count(self) -> int:
        """Count words in caption."""
        if not self.caption:
            return 0
        return len(self.caption.split())


class Story(BaseModel):
    """Represents an Instagram story."""

    # Core content
    caption: Optional[str] = Field(None, description="Story caption text")
    media: Media = Field(..., description="Story media content")
    timestamp: datetime = Field(..., description="When the story was published")
    expires_at: Optional[datetime] = Field(None, description="When the story expires")

    @property
    def taken_at(self) -> datetime:
        """Alias for timestamp to provide a consistent API with other models."""
        return self.timestamp

    # Story metadata
    story_id: Optional[str] = Field(None, description="Instagram story ID")
    is_highlight: bool = Field(False, description="Whether story is saved as highlight")
    highlight_name: Optional[str] = Field(None, description="Highlight collection name")

    # Story features
    has_music: bool = Field(False, description="Whether story has music")
    has_stickers: bool = Field(False, description="Whether story has stickers")
    has_text: bool = Field(False, description="Whether story has text overlay")

    # Engagement
    views_count: int = Field(0, ge=0, description="Number of story views")
    replies_count: int = Field(0, ge=0, description="Number of story replies")

    # Raw data
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw story data")

    @property
    def is_expired(self) -> bool:
        """Check if story has expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        # Stories typically expire after 24 hours
        return (datetime.now() - self.timestamp).days >= 1


class Reel(BaseModel):
    """Represents an Instagram reel."""

    # Core content
    video: Media = Field(..., description="Reel video content")
    caption: Optional[str] = Field(None, description="Reel caption")
    timestamp: datetime = Field(..., description="When the reel was published")

    # Reel metadata
    reel_id: Optional[str] = Field(None, description="Instagram reel ID")
    audio_title: Optional[str] = Field(None, description="Audio track title")
    audio_artist: Optional[str] = Field(None, description="Audio track artist")

    # Reel features
    effects: list[str] = Field(default_factory=list, description="Applied effects")
    music_id: Optional[str] = Field(None, description="Music track ID")
    is_original_audio: bool = Field(False, description="Whether audio is original")

    # Engagement
    likes_count: int = Field(0, ge=0, description="Number of likes")
    comments_count: int = Field(0, ge=0, description="Number of comments")
    shares_count: int = Field(0, ge=0, description="Number of shares")
    plays_count: int = Field(0, ge=0, description="Number of plays")

    # Content analysis
    hashtags: list[str] = Field(default_factory=list, description="Hashtags in caption")
    mentions: list[str] = Field(default_factory=list, description="Mentioned users")

    # Raw data
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw reel data")

    @field_validator("video")
    @classmethod
    def validate_video(cls, v: Media) -> Media:
        """Validate that reel content is video."""
        if v.media_type not in [MediaType.VIDEO, MediaType.REEL]:
            raise ValueError("Reel must contain video content")
        return v

    @property
    def engagement_rate(self) -> float:
        """Calculate total engagement."""
        return self.likes_count + self.comments_count + self.shares_count

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get video duration in seconds."""
        return self.video.duration
