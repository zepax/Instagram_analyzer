"""Conversation-related Pydantic models for Instagram direct messages."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator

from .user import User


class MessageType(Enum):
    """Types of Instagram messages."""
    TEXT = "text"
    PHOTO = "photo"
    AUDIO = "audio"
    VIDEO = "video"
    STORY_SHARE = "story_share"
    POST_SHARE = "post_share"
    REACTION = "reaction"
    STICKER = "sticker"
    GIF = "gif"
    CALL = "call"
    LIKE = "like"
    LOCATION = "location"
    PRODUCT = "product"
    REEL_SHARE = "reel_share"
    LINK = "link"
    VOICE_CLIP = "voice_clip"
    

class MessageStatus(Enum):
    """Message status indicators."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    UNSENT = "unsent"
    FAILED = "failed"


class ReactionType(Enum):
    """Instagram message reaction types."""
    HEART = "❤️"
    LAUGH = "😂"
    WOW = "😮"
    SAD = "😢"
    ANGRY = "😠"
    LIKE = "👍"
    DISLIKE = "👎"
    FIRE = "🔥"


class MessageReaction(BaseModel):
    """Represents a reaction to a message."""
    reaction: str = Field(..., description="The emoji reaction")
    actor: str = Field(..., description="Username of person who reacted")
    timestamp: Optional[datetime] = Field(None, description="When the reaction was added")


class MessageMedia(BaseModel):
    """Represents media attached to a message."""
    uri: str = Field(..., description="Path to the media file")
    media_type: MessageType = Field(..., description="Type of media")
    creation_timestamp: Optional[datetime] = Field(None, description="When media was created")
    width: Optional[int] = Field(None, description="Media width in pixels")
    height: Optional[int] = Field(None, description="Media height in pixels")
    duration: Optional[float] = Field(None, description="Duration for audio/video in seconds")
    


class ShareContent(BaseModel):
    """Represents shared content in a message."""
    link: Optional[str] = Field(None, description="URL of shared content")
    share_text: Optional[str] = Field(None, description="Text description of share")
    original_content_owner: Optional[str] = Field(None, description="Original content creator")
    media_type: Optional[str] = Field(None, description="Type of shared content")


class Message(BaseModel):
    """Represents a single Instagram direct message."""
    sender_name: str = Field(..., description="Name of the message sender")
    timestamp_ms: int = Field(..., description="Message timestamp in milliseconds")
    content: Optional[str] = Field(None, description="Text content of the message")
    message_type: MessageType = Field(MessageType.TEXT, description="Type of message")
    
    # Media attachments
    photos: List[MessageMedia] = Field(default_factory=list, description="Photo attachments")
    audio_files: List[MessageMedia] = Field(default_factory=list, description="Audio attachments")
    videos: List[MessageMedia] = Field(default_factory=list, description="Video attachments")
    gifs: List[MessageMedia] = Field(default_factory=list, description="GIF attachments")
    stickers: List[MessageMedia] = Field(default_factory=list, description="Sticker attachments")
    
    # Interactions
    reactions: List[MessageReaction] = Field(default_factory=list, description="Reactions to this message")
    share: Optional[ShareContent] = Field(None, description="Shared content information")
    
    # Metadata
    is_geoblocked_for_viewer: bool = Field(False, description="Whether message is geoblocked")
    is_unsent_image_by_messenger_kid_parent: bool = Field(False, description="Messenger Kids flag")
    
    # Derived fields
    timestamp: Optional[datetime] = Field(None, description="Parsed timestamp as datetime")
    message_id: Optional[str] = Field(None, description="Unique message identifier")
    thread_id: Optional[str] = Field(None, description="Thread this message belongs to")
    
    # Raw data preservation
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Raw message data")
    


class ConversationType(Enum):
    """Types of Instagram conversations."""
    DIRECT = "direct"  # 1-on-1 conversation
    GROUP = "group"    # Group conversation
    BROADCAST = "broadcast"  # Broadcast message


class Participant(BaseModel):
    """Represents a participant in a conversation."""
    name: str = Field(..., description="Display name of participant")
    username: Optional[str] = Field(None, description="Instagram username")
    is_self: bool = Field(False, description="Whether this is the account owner")
    join_timestamp: Optional[datetime] = Field(None, description="When they joined the conversation")
    leave_timestamp: Optional[datetime] = Field(None, description="When they left the conversation")


class ConversationMetrics(BaseModel):
    """Metrics calculated for a conversation."""
    total_messages: int = Field(0, description="Total number of messages")
    total_participants: int = Field(0, description="Total number of participants")
    message_count_by_participant: Dict[str, int] = Field(default_factory=dict)
    date_range: Dict[str, Optional[datetime]] = Field(default_factory=dict)
    most_active_participant: Optional[str] = Field(None)
    avg_messages_per_day: float = Field(0.0)
    conversation_duration_days: int = Field(0)
    most_active_hour: Optional[int] = Field(None)
    most_active_day_of_week: Optional[str] = Field(None)
    emoji_usage: Dict[str, int] = Field(default_factory=dict)
    reaction_counts: Dict[str, int] = Field(default_factory=dict)
    media_counts: Dict[str, int] = Field(default_factory=dict)


class ConversationThread(BaseModel):
    """Represents a sequence of related messages (thread)."""
    thread_id: str = Field(..., description="Unique identifier for the thread")
    root_message_id: Optional[str] = Field(None, description="ID of the message that started the thread")
    messages: List[Message] = Field(default_factory=list, description="Messages in this thread")
    participants: List[str] = Field(default_factory=list, description="Participants in this thread")
    start_time: Optional[datetime] = Field(None, description="When the thread started")
    end_time: Optional[datetime] = Field(None, description="When the thread ended")
    topic: Optional[str] = Field(None, description="Inferred topic of the thread")
    duration_minutes: Optional[float] = Field(None, description="Thread duration in minutes")
    


class Conversation(BaseModel):
    """Represents a complete Instagram conversation."""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    title: str = Field(..., description="Conversation title or participant names")
    thread_path: str = Field(..., description="Path to conversation in export")
    conversation_type: ConversationType = Field(ConversationType.DIRECT, description="Type of conversation")
    
    # Participants
    participants: List[Participant] = Field(default_factory=list, description="Conversation participants")
    is_still_participant: bool = Field(True, description="Whether account owner is still in conversation")
    
    # Messages and threads
    messages: List[Message] = Field(default_factory=list, description="All messages in conversation")
    threads: List[ConversationThread] = Field(default_factory=list, description="Message threads")
    
    # Conversation features
    magic_words: List[str] = Field(default_factory=list, description="Magic words/triggers")
    joinable_mode: Optional[Dict[str, Any]] = Field(None, description="Group join settings")
    
    # Analytics
    metrics: Optional[ConversationMetrics] = Field(None, description="Calculated conversation metrics")
    
    # Temporal analysis
    activity_patterns: Dict[str, Any] = Field(default_factory=dict, description="Activity pattern analysis")
    peak_activity_periods: List[Dict[str, Any]] = Field(default_factory=list, description="Periods of high activity")
    
    # Content analysis
    dominant_message_types: List[str] = Field(default_factory=list, description="Most common message types")
    keyword_frequency: Dict[str, int] = Field(default_factory=dict, description="Frequency of keywords")
    sentiment_scores: Dict[str, float] = Field(default_factory=dict, description="Sentiment analysis by participant")
    
    # Privacy and security
    contains_sensitive_data: bool = Field(False, description="Whether conversation contains sensitive information")
    anonymization_applied: bool = Field(False, description="Whether data has been anonymized")
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict, description="Original conversation data")
    


class ConversationAnalysis(BaseModel):
    """Comprehensive analysis results for conversations."""
    total_conversations: int = Field(0, description="Total number of conversations")
    total_messages: int = Field(0, description="Total messages across all conversations")
    date_range: Dict[str, Optional[datetime]] = Field(default_factory=dict)
    
    # Conversation distribution
    conversation_types: Dict[str, int] = Field(default_factory=dict)
    most_active_conversations: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_sizes: Dict[int, int] = Field(default_factory=dict)  # by participant count
    
    # Participant analysis
    most_frequent_contacts: List[Dict[str, Any]] = Field(default_factory=list)
    group_vs_direct_ratio: Dict[str, float] = Field(default_factory=dict)
    unique_contacts: int = Field(0)
    
    # Temporal patterns
    messaging_by_hour: Dict[int, int] = Field(default_factory=dict)
    messaging_by_day: Dict[str, int] = Field(default_factory=dict)
    messaging_by_month: Dict[str, int] = Field(default_factory=dict)
    peak_messaging_periods: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Content analysis
    message_type_distribution: Dict[str, int] = Field(default_factory=dict)
    media_sharing_patterns: Dict[str, int] = Field(default_factory=dict)
    reaction_usage: Dict[str, int] = Field(default_factory=dict)
    popular_topics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Communication patterns
    response_time_analysis: Dict[str, float] = Field(default_factory=dict)
    conversation_length_distribution: Dict[str, int] = Field(default_factory=dict)
    thread_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Privacy insights
    conversations_with_sensitive_data: int = Field(0)
    anonymization_recommendations: List[str] = Field(default_factory=list)