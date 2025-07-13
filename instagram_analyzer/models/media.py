"""Media-related models for Instagram data."""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, validator


class MediaType(str, Enum):
    """Types of media content in Instagram."""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REEL = "reel"
    STORY = "story"


class Media(BaseModel):
    """Represents a media file in Instagram data."""
    
    uri: str = Field(..., description="URI or path to the media file")
    media_type: MediaType = Field(..., description="Type of media content")
    creation_timestamp: datetime = Field(..., description="When the media was created")
    taken_at: Optional[datetime] = Field(None, description="When the photo/video was taken")
    title: Optional[str] = Field(None, description="Media title or caption")
    
    # Technical details
    width: Optional[int] = Field(None, gt=0, description="Media width in pixels")
    height: Optional[int] = Field(None, gt=0, description="Media height in pixels")
    duration: Optional[float] = Field(None, gt=0, description="Video duration in seconds")
    file_size: Optional[int] = Field(None, gt=0, description="File size in bytes")
    
    # Instagram specific
    thumbnail_uri: Optional[str] = Field(None, description="Thumbnail URI for videos")
    ig_media_id: Optional[str] = Field(None, description="Instagram media ID")
    
    @validator('uri')
    def validate_uri(cls, v: str) -> str:
        """Validate URI format."""
        if not v or not v.strip():
            raise ValueError("URI cannot be empty")
        return v.strip()
    
    @validator('creation_timestamp', 'taken_at')
    def validate_timestamps(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate timestamp is not in the future."""
        if v and v > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
        return v
    
    @property
    def file_path(self) -> Optional[Path]:
        """Get Path object for local files."""
        if self.uri.startswith(('http://', 'https://')):
            return None
        return Path(self.uri)
    
    @property
    def is_local_file(self) -> bool:
        """Check if media is a local file."""
        return not self.uri.startswith(('http://', 'https://'))
    
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Calculate aspect ratio if dimensions are available."""
        if self.width and self.height:
            return self.width / self.height
        return None