"""Interaction models for Instagram data (comments, likes, follows)."""

from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field, validator

from .user import User


class Comment(BaseModel):
    """Represents a comment on Instagram content."""
    
    text: str = Field(..., description="Comment text content")
    timestamp: datetime = Field(..., description="When the comment was made")
    author: User = Field(..., description="Comment author")
    
    # Comment metadata
    comment_id: Optional[str] = Field(None, description="Instagram comment ID")
    parent_comment_id: Optional[str] = Field(None, description="Parent comment ID for replies")
    is_reply: bool = Field(False, description="Whether this is a reply to another comment")
    
    # Engagement
    likes_count: int = Field(0, ge=0, description="Number of likes on this comment")
    replies_count: int = Field(0, ge=0, description="Number of replies to this comment")
    
    # Content analysis
    mentions: List[str] = Field(default_factory=list, description="Mentioned usernames")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags in comment")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw comment data")
    
    @validator('text')
    def validate_text(cls, v: str) -> str:
        """Validate comment text."""
        if not v or not v.strip():
            raise ValueError("Comment text cannot be empty")
        return v.strip()
    
    @property
    def word_count(self) -> int:
        """Count words in comment."""
        return len(self.text.split())
    
    @property
    def char_count(self) -> int:
        """Count characters in comment."""
        return len(self.text)


class Like(BaseModel):
    """Represents a like on Instagram content."""
    
    user: User = Field(..., description="User who liked the content")
    timestamp: datetime = Field(..., description="When the like was made")
    
    # Metadata
    like_id: Optional[str] = Field(None, description="Instagram like ID")
    content_type: Optional[str] = Field(None, description="Type of content liked")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw like data")


class Follow(BaseModel):
    """Represents a follow relationship."""
    
    user: User = Field(..., description="The user being followed/unfollowed")
    timestamp: datetime = Field(..., description="When the follow action occurred")
    action: str = Field(..., description="Type of action (follow/unfollow)")
    
    # Metadata
    follow_id: Optional[str] = Field(None, description="Instagram follow ID")
    is_mutual: bool = Field(False, description="Whether the follow is mutual")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw follow data")
    
    @validator('action')
    def validate_action(cls, v: str) -> str:
        """Validate follow action type."""
        valid_actions = ['follow', 'unfollow', 'follow_request_sent', 'follow_request_cancelled']
        if v.lower() not in valid_actions:
            raise ValueError(f"Invalid action. Must be one of: {valid_actions}")
        return v.lower()


class DirectMessage(BaseModel):
    """Represents a direct message."""
    
    sender: User = Field(..., description="Message sender")
    recipient: User = Field(..., description="Message recipient")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="When the message was sent")
    
    # Message metadata
    message_id: Optional[str] = Field(None, description="Instagram message ID")
    conversation_id: Optional[str] = Field(None, description="Conversation thread ID")
    message_type: str = Field("text", description="Type of message (text, media, etc.)")
    
    # Status
    is_read: bool = Field(False, description="Whether the message was read")
    is_deleted: bool = Field(False, description="Whether the message was deleted")
    
    # Media attachments
    media_uris: List[str] = Field(default_factory=list, description="Attached media URIs")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw message data")
    
    @validator('content')
    def validate_content(cls, v: str) -> str:
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        return v.strip()