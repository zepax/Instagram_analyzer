"""Base models for Instagram data."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    """Base model with common configurations."""

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: v.isoformat(),
        },
    )


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
