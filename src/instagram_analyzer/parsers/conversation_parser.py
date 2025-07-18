"""Specialized parser for Instagram conversation/message data."""

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..models.conversation import (
    Conversation,
    ConversationAnalysis,
    ConversationMetrics,
    ConversationThread,
    ConversationType,
    Message,
    MessageMedia,
    MessageReaction,
    MessageType,
    Participant,
    ShareContent,
)
from ..utils.date_utils import parse_instagram_date
from ..utils.text_utils import clean_instagram_text, extract_hashtags, extract_mentions


class ConversationParser:
    """Parses Instagram conversation JSON files into structured conversation models."""

    def __init__(self, data_root: Path):
        """Initialize parser with data root path."""
        self.data_root = data_root
        self.conversations = []
        self.analysis = None

    def parse_conversation_file(self, conversation_file: Path) -> Optional[Conversation]:
        """Parse a single conversation JSON file.

        Args:
            conversation_file: Path to the conversation JSON file

        Returns:
            Parsed Conversation object or None if parsing fails
        """
        try:
            with open(conversation_file, encoding="utf-8") as f:
                data = json.load(f)

            return self._parse_conversation_data(data, conversation_file)

        except Exception as e:
            print(f"Error parsing conversation file {conversation_file}: {e}")
            return None

    def _parse_conversation_data(
        self, data: dict[str, Any], file_path: Path
    ) -> Conversation:
        """Parse conversation data from JSON structure."""
        # Extract basic conversation info
        conversation_id = self._extract_conversation_id(data, file_path)
        title = data.get("title", "Untitled Conversation")
        thread_path = data.get("thread_path", str(file_path.parent.name))

        # Parse participants
        participants = self._parse_participants(data.get("participants", []))

        # Parse messages
        messages = self._parse_messages(data.get("messages", []), conversation_id)

        # Determine conversation type
        conv_type = (
            ConversationType.GROUP if len(participants) > 2 else ConversationType.DIRECT
        )

        # Calculate metrics
        metrics = self._calculate_conversation_metrics(messages, participants)

        # Create conversation object
        conversation = Conversation(
            conversation_id=conversation_id,
            title=clean_instagram_text(title),
            thread_path=thread_path,
            conversation_type=conv_type,
            participants=participants,
            messages=messages,
            is_still_participant=data.get("is_still_participant", True),
            magic_words=data.get("magic_words", []),
            joinable_mode=data.get("joinable_mode"),
            metrics=metrics,
            raw_data=data,
        )

        # Generate threads and additional analysis
        conversation.threads = self._generate_threads(messages)
        conversation.activity_patterns = self._analyze_activity_patterns(messages)
        conversation.dominant_message_types = self._analyze_message_types(messages)
        conversation.keyword_frequency = self._analyze_keywords(messages)

        return conversation

    def _extract_conversation_id(self, data: dict[str, Any], file_path: Path) -> str:
        """Extract conversation ID from data or file path."""
        # Try to get from thread_path first
        if "thread_path" in data:
            thread_path = data["thread_path"]
            if "/" in thread_path:
                return thread_path.split("/")[-1]

        # Fall back to directory name
        return file_path.parent.name

    def _parse_participants(
        self, participants_data: list[dict[str, Any]]
    ) -> list[Participant]:
        """Parse participant data."""
        participants = []

        for p_data in participants_data:
            name = clean_instagram_text(p_data.get("name", "Unknown"))

            # Try to extract username from name (if it contains @)
            username = None
            if "@" in name:
                username = name.split("@")[-1].strip()

            participant = Participant(
                name=name,
                username=username,
                is_self=name == "Flora Escobar",  # Detect self based on known name
            )

            participants.append(participant)

        return participants

    def _parse_messages(
        self, messages_data: list[dict[str, Any]], conversation_id: str
    ) -> list[Message]:
        """Parse messages from conversation data."""
        messages = []

        for msg_data in messages_data:
            try:
                message = self._parse_single_message(msg_data, conversation_id)
                if message:
                    messages.append(message)
            except Exception:
                # Skip invalid messages but continue processing
                continue

        # Sort messages by timestamp (oldest first)
        messages.sort(key=lambda m: m.timestamp_ms)

        return messages

    def _parse_single_message(
        self, msg_data: dict[str, Any], conversation_id: str
    ) -> Optional[Message]:
        """Parse a single message from JSON data."""
        # Extract basic message info
        sender_name = clean_instagram_text(msg_data.get("sender_name", "Unknown"))
        timestamp_ms = msg_data.get("timestamp_ms", 0)
        content = msg_data.get("content")

        if content:
            content = clean_instagram_text(content)

        # Parse reactions
        reactions = self._parse_reactions(msg_data.get("reactions", []))

        # Parse media attachments
        photos = self._parse_media_list(msg_data.get("photos", []), MessageType.PHOTO)
        audio_files = self._parse_media_list(
            msg_data.get("audio_files", []), MessageType.AUDIO
        )
        videos = self._parse_media_list(msg_data.get("videos", []), MessageType.VIDEO)
        gifs = self._parse_media_list(msg_data.get("gifs", []), MessageType.GIF)
        stickers = self._parse_media_list(
            msg_data.get("stickers", []), MessageType.STICKER
        )

        # Parse share content
        share = self._parse_share_content(msg_data.get("share"))

        # Generate message ID
        message_id = f"{conversation_id}_{timestamp_ms}"

        message = Message(
            sender_name=sender_name,
            timestamp_ms=timestamp_ms,
            content=content,
            photos=photos,
            audio_files=audio_files,
            videos=videos,
            gifs=gifs,
            stickers=stickers,
            reactions=reactions,
            share=share,
            is_geoblocked_for_viewer=msg_data.get("is_geoblocked_for_viewer", False),
            is_unsent_image_by_messenger_kid_parent=msg_data.get(
                "is_unsent_image_by_messenger_kid_parent", False
            ),
            message_id=message_id,
            thread_id=conversation_id,
            raw_data=msg_data,
        )

        return message

    def _parse_reactions(
        self, reactions_data: list[dict[str, Any]]
    ) -> list[MessageReaction]:
        """Parse message reactions."""
        reactions = []

        for r_data in reactions_data:
            reaction = MessageReaction(
                reaction=r_data.get("reaction", ""),
                actor=clean_instagram_text(r_data.get("actor", "")),
                timestamp=self._parse_timestamp(r_data.get("timestamp")),
            )
            reactions.append(reaction)

        return reactions

    def _parse_media_list(
        self, media_data: list[dict[str, Any]], media_type: MessageType
    ) -> list[MessageMedia]:
        """Parse list of media attachments."""
        media_list = []

        for m_data in media_data:
            uri = m_data.get("uri", "")
            creation_timestamp = self._parse_timestamp(m_data.get("creation_timestamp"))

            media = MessageMedia(
                uri=uri,
                media_type=media_type,
                creation_timestamp=creation_timestamp,
                width=m_data.get("width"),
                height=m_data.get("height"),
                duration=m_data.get("duration"),
            )
            media_list.append(media)

        return media_list

    def _parse_share_content(
        self, share_data: Optional[dict[str, Any]]
    ) -> Optional[ShareContent]:
        """Parse shared content information."""
        if not share_data:
            return None

        return ShareContent(
            link=share_data.get("link"),
            share_text=clean_instagram_text(share_data.get("share_text", "")),
            original_content_owner=share_data.get("original_content_owner"),
            media_type=share_data.get("media_type"),
        )

    def _parse_timestamp(self, timestamp: Any) -> Optional[datetime]:
        """Parse timestamp from various formats."""
        if not timestamp:
            return None

        try:
            if isinstance(timestamp, (int, float)):
                # Handle both seconds and milliseconds
                if timestamp > 1e10:  # Likely milliseconds
                    return datetime.fromtimestamp(timestamp / 1000)
                else:  # Likely seconds
                    return datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                return parse_instagram_date(timestamp)
        except Exception:
            pass

        return None

    def _calculate_conversation_metrics(
        self, messages: list[Message], participants: list[Participant]
    ) -> ConversationMetrics:
        """Calculate metrics for the conversation."""
        if not messages:
            return ConversationMetrics()

        # Basic counts
        total_messages = len(messages)
        total_participants = len(participants)

        # Message counts by participant
        message_count_by_participant = Counter(msg.sender_name for msg in messages)
        most_active_participant = (
            message_count_by_participant.most_common(1)[0][0]
            if message_count_by_participant
            else None
        )

        # Date range analysis
        timestamps = [msg.timestamp for msg in messages if msg.timestamp]
        if timestamps:
            start_date = min(timestamps)
            end_date = max(timestamps)
            duration_days = (end_date - start_date).days + 1
            avg_messages_per_day = (
                total_messages / duration_days if duration_days > 0 else 0
            )
        else:
            start_date = end_date = None
            duration_days = 0
            avg_messages_per_day = 0

        # Activity patterns
        hours = [msg.timestamp.hour for msg in messages if msg.timestamp]
        weekdays = [msg.timestamp.strftime("%A") for msg in messages if msg.timestamp]
        most_active_hour = Counter(hours).most_common(1)[0][0] if hours else None
        most_active_day = Counter(weekdays).most_common(1)[0][0] if weekdays else None

        # Content analysis
        emoji_usage = Counter()
        reaction_counts = Counter()
        media_counts = Counter()

        for msg in messages:
            # Count emojis in content
            if msg.content:
                for char in msg.content:
                    if ord(char) > 127:  # Simple emoji detection
                        emoji_usage[char] += 1

            # Count reactions
            for reaction in msg.reactions:
                reaction_counts[reaction.reaction] += 1

            # Count media types
            if msg.photos:
                media_counts["photos"] += len(msg.photos)
            if msg.audio_files:
                media_counts["audio"] += len(msg.audio_files)
            if msg.videos:
                media_counts["videos"] += len(msg.videos)
            if msg.gifs:
                media_counts["gifs"] += len(msg.gifs)

        return ConversationMetrics(
            total_messages=total_messages,
            total_participants=total_participants,
            message_count_by_participant=dict(message_count_by_participant),
            date_range={"start": start_date, "end": end_date},
            most_active_participant=most_active_participant,
            avg_messages_per_day=avg_messages_per_day,
            conversation_duration_days=duration_days,
            most_active_hour=most_active_hour,
            most_active_day_of_week=most_active_day,
            emoji_usage=dict(emoji_usage.most_common(20)),
            reaction_counts=dict(reaction_counts),
            media_counts=dict(media_counts),
        )

    def _generate_threads(self, messages: list[Message]) -> list[ConversationThread]:
        """Generate conversation threads based on message timing and content."""
        if not messages:
            return []

        threads = []
        current_thread = None
        thread_gap_minutes = 60  # 1 hour gap indicates new thread

        for i, message in enumerate(messages):
            # Start new thread if:
            # 1. It's the first message
            # 2. There's a significant time gap
            # 3. Topic appears to change (heuristic)

            start_new_thread = current_thread is None or (
                message.timestamp
                and current_thread.end_time
                and (message.timestamp - current_thread.end_time).total_seconds()
                > thread_gap_minutes * 60
            )

            if start_new_thread:
                if current_thread:
                    threads.append(current_thread)

                thread_id = f"thread_{len(threads)+1}"
                current_thread = ConversationThread(
                    thread_id=thread_id,
                    messages=[message],
                    participants=[message.sender_name],
                    start_time=message.timestamp,
                    end_time=message.timestamp,
                )
            else:
                # Add to current thread
                current_thread.messages.append(message)
                if message.sender_name not in current_thread.participants:
                    current_thread.participants.append(message.sender_name)
                if message.timestamp:
                    current_thread.end_time = message.timestamp

        # Add final thread
        if current_thread:
            threads.append(current_thread)

        # Calculate thread durations
        for thread in threads:
            if thread.start_time and thread.end_time:
                duration = (thread.end_time - thread.start_time).total_seconds() / 60
                thread.duration_minutes = duration

        return threads

    def _analyze_activity_patterns(self, messages: list[Message]) -> dict[str, Any]:
        """Analyze activity patterns in the conversation."""
        if not messages:
            return {}

        # Hourly distribution
        hourly_counts = Counter(msg.timestamp.hour for msg in messages if msg.timestamp)

        # Daily distribution
        daily_counts = Counter(
            msg.timestamp.strftime("%A") for msg in messages if msg.timestamp
        )

        # Monthly distribution
        monthly_counts = Counter(
            msg.timestamp.strftime("%Y-%m") for msg in messages if msg.timestamp
        )

        return {
            "hourly_distribution": dict(hourly_counts),
            "daily_distribution": dict(daily_counts),
            "monthly_distribution": dict(monthly_counts),
            "peak_hour": hourly_counts.most_common(1)[0][0] if hourly_counts else None,
            "peak_day": daily_counts.most_common(1)[0][0] if daily_counts else None,
        }

    def _analyze_message_types(self, messages: list[Message]) -> list[str]:
        """Analyze dominant message types in the conversation."""
        type_counts = Counter(msg.message_type.value for msg in messages)
        return [msg_type for msg_type, _ in type_counts.most_common(5)]

    def _analyze_keywords(self, messages: list[Message]) -> dict[str, int]:
        """Analyze keyword frequency in conversation content."""
        word_counts = Counter()

        for msg in messages:
            if msg.content:
                # Simple word extraction (could be enhanced with NLP)
                words = msg.content.lower().split()
                # Filter out common words and very short words
                filtered_words = [
                    word.strip(".,!?¿¡")
                    for word in words
                    if len(word) > 3
                    and word
                    not in {
                        "para",
                        "como",
                        "esta",
                        "pero",
                        "todo",
                        "muy",
                        "que",
                        "con",
                        "una",
                        "por",
                        "más",
                        "hola",
                        "the",
                        "and",
                        "you",
                        "for",
                        "are",
                        "not",
                        "this",
                        "that",
                    }
                ]
                word_counts.update(filtered_words)

        return dict(word_counts.most_common(50))

    def parse_all_conversations(self, conversations_dir: Path) -> list[Conversation]:
        """Parse all conversations in the messages/inbox directory.

        Args:
            conversations_dir: Path to the messages/inbox directory

        Returns:
            List of parsed Conversation objects
        """
        conversations = []

        if not conversations_dir.exists():
            print(f"Conversations directory not found: {conversations_dir}")
            return conversations

        # Find all conversation directories
        for conv_dir in conversations_dir.iterdir():
            if conv_dir.is_dir():
                # Look for message JSON files
                message_files = list(conv_dir.glob("message_*.json"))

                for message_file in message_files:
                    conversation = self.parse_conversation_file(message_file)
                    if conversation:
                        conversations.append(conversation)

        self.conversations = conversations
        return conversations

    def generate_conversation_analysis(
        self, conversations: Optional[list[Conversation]] = None
    ) -> ConversationAnalysis:
        """Generate comprehensive analysis of all conversations.

        Args:
            conversations: List of conversations to analyze, or None to use stored conversations

        Returns:
            ConversationAnalysis object with comprehensive insights
        """
        if conversations is None:
            conversations = self.conversations

        if not conversations:
            return ConversationAnalysis()

        # Basic statistics
        total_conversations = len(conversations)
        total_messages = sum(
            conv.metrics.total_messages if conv.metrics else 0 for conv in conversations
        )

        # Date range across all conversations
        all_dates = []
        for conv in conversations:
            if conv.metrics and conv.metrics.date_range:
                start = conv.metrics.date_range.get("start")
                end = conv.metrics.date_range.get("end")
                if start:
                    all_dates.append(start)
                if end:
                    all_dates.append(end)

        date_range = {}
        if all_dates:
            date_range = {"start": min(all_dates), "end": max(all_dates)}

        # Conversation type distribution
        conv_types = Counter(conv.conversation_type.value for conv in conversations)

        # Most active conversations
        most_active = sorted(
            [
                {
                    "title": conv.title,
                    "messages": conv.metrics.total_messages if conv.metrics else 0,
                    "id": conv.conversation_id,
                }
                for conv in conversations
            ],
            key=lambda x: x["messages"],
            reverse=True,
        )[:10]

        # Conversation sizes (by participant count)
        conv_sizes = Counter(len(conv.participants) for conv in conversations)

        # Contact frequency analysis
        contact_frequency = Counter()
        for conv in conversations:
            if conv.conversation_type == ConversationType.DIRECT:
                # Find the other participant (not self)
                other_participants = [p.name for p in conv.participants if not p.is_self]
                if other_participants:
                    contact_frequency[other_participants[0]] += (
                        conv.metrics.total_messages if conv.metrics else 0
                    )

        most_frequent_contacts = [
            {"name": name, "total_messages": count}
            for name, count in contact_frequency.most_common(20)
        ]

        # Group vs direct ratio
        group_count = len(
            [c for c in conversations if c.conversation_type == ConversationType.GROUP]
        )
        direct_count = len(
            [c for c in conversations if c.conversation_type == ConversationType.DIRECT]
        )

        group_vs_direct_ratio = {
            "group_percentage": (
                (group_count / total_conversations * 100)
                if total_conversations > 0
                else 0
            ),
            "direct_percentage": (
                (direct_count / total_conversations * 100)
                if total_conversations > 0
                else 0
            ),
        }

        # Unique contacts
        all_participants = set()
        for conv in conversations:
            for participant in conv.participants:
                if not participant.is_self:
                    all_participants.add(participant.name)
        unique_contacts = len(all_participants)

        # Temporal patterns aggregation
        all_hourly = Counter()
        all_daily = Counter()
        all_monthly = Counter()

        for conv in conversations:
            if conv.activity_patterns:
                hourly = conv.activity_patterns.get("hourly_distribution", {})
                daily = conv.activity_patterns.get("daily_distribution", {})
                monthly = conv.activity_patterns.get("monthly_distribution", {})

                all_hourly.update({int(k): v for k, v in hourly.items()})
                all_daily.update(daily)
                all_monthly.update(monthly)

        # Message type distribution
        all_message_types = Counter()
        for conv in conversations:
            all_message_types.update(conv.dominant_message_types)

        # Media sharing patterns
        media_patterns = Counter()
        for conv in conversations:
            if conv.metrics and conv.metrics.media_counts:
                media_patterns.update(conv.metrics.media_counts)

        # Reaction usage
        all_reactions = Counter()
        for conv in conversations:
            if conv.metrics and conv.metrics.reaction_counts:
                all_reactions.update(conv.metrics.reaction_counts)

        # Privacy analysis
        conversations_with_sensitive = len(
            [c for c in conversations if c.contains_sensitive_data]
        )

        analysis = ConversationAnalysis(
            total_conversations=total_conversations,
            total_messages=total_messages,
            date_range=date_range,
            conversation_types=dict(conv_types),
            most_active_conversations=most_active,
            conversation_sizes=dict(conv_sizes),
            most_frequent_contacts=most_frequent_contacts,
            group_vs_direct_ratio=group_vs_direct_ratio,
            unique_contacts=unique_contacts,
            messaging_by_hour=dict(all_hourly),
            messaging_by_day=dict(all_daily),
            messaging_by_month=dict(all_monthly),
            message_type_distribution=dict(all_message_types),
            media_sharing_patterns=dict(media_patterns),
            reaction_usage=dict(all_reactions),
            conversations_with_sensitive_data=conversations_with_sensitive,
        )

        self.analysis = analysis
        return analysis
