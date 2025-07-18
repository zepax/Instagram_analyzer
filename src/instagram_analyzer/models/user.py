"""User and profile models for Instagram data."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class User(BaseModel):
    """Represents a user in Instagram data."""

    username: str = Field(..., description="Instagram username")
    name: Optional[str] = Field(None, description="Display name")
    user_id: Optional[str] = Field(None, description="Instagram user ID")
    is_verified: bool = Field(False, description="Verification status")
    is_private: bool = Field(False, description="Account privacy setting")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lower()


class Profile(BaseModel):
    """Represents the account owner's profile information."""

    username: str = Field(..., description="Instagram username")
    name: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Profile biography")
    website: Optional[str] = Field(None, description="Website URL")
    email: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")

    # Profile stats
    followers_count: Optional[int] = Field(None, ge=0, description="Number of followers")
    following_count: Optional[int] = Field(None, ge=0, description="Number of following")
    posts_count: Optional[int] = Field(None, ge=0, description="Number of posts")

    # Account settings
    is_private: bool = Field(False, description="Account privacy setting")
    is_verified: bool = Field(False, description="Verification status")
    is_business: bool = Field(False, description="Business account status")

    # Dates
    date_joined: Optional[datetime] = Field(None, description="Account creation date")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")

    # Additional data from export
    profile_pic_url: Optional[str] = Field(None, description="Profile picture URL")
    external_url: Optional[str] = Field(None, description="External link in bio")
    category: Optional[str] = Field(None, description="Business category")

    # Raw data storage for unknown fields
    raw_data: dict[str, Any] = Field(default_factory=dict, description="Raw profile data")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip().lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Basic email validation."""
        if v and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    @property
    def engagement_rate(self) -> Optional[float]:
        """Calculate basic engagement rate if data is available."""
        if self.followers_count and self.followers_count > 0 and self.posts_count:
            # This is a simplified calculation
            return (self.posts_count / self.followers_count) * 100
        return None
