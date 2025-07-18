"""Base models for Instagram data."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseModel(BaseModel):
    """Base model with common configurations."""

    class Config:
        extra = "ignore"
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Media(BaseModel):
    """Represents a media item (post, story, reel)."""

    uri: str
    creation_timestamp: int
    title: Optional[str] = None

    @property
    def timestamp(self) -> datetime:
        return datetime.fromtimestamp(self.creation_timestamp)


class StoryInteraction(BaseModel):
    """Represents a story interaction."""

    interaction_type: str
    data: list[dict[str, Any]]
