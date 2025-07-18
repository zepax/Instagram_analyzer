"""Advanced conversation analysis algorithms and thread reconstruction."""

import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..models.conversation import (
    Conversation,
    ConversationAnalysis,
    ConversationMetrics,
    ConversationThread,
    Message,
    MessageType,
)
from ..parsers.conversation_parser import ConversationParser


class ThreadReconstructionEngine:
    """Reconstructs conversation threads using advanced algorithms."""

    def __init__(
        self,
        time_gap_threshold_minutes: int = 60,
        topic_similarity_threshold: float = 0.3,
        min_thread_messages: int = 2,
    ):
        """Initialize thread reconstruction parameters.

        Args:
            time_gap_threshold_minutes: Time gap to consider for new thread
            topic_similarity_threshold: Similarity threshold for topic continuity
            min_thread_messages: Minimum messages required for a thread
        """
        self.time_gap_threshold = timedelta(minutes=time_gap_threshold_minutes)
        self.topic_threshold = topic_similarity_threshold
        self.min_thread_messages = min_thread_messages

    def reconstruct_threads(self, messages: list[Message]) -> list[ConversationThread]:
        """Reconstruct conversation threads using multiple algorithms.

        Args:
            messages: List of messages to analyze

        Returns:
            List of reconstructed conversation threads
        """
        if not messages:
            return []

        # Sort messages by timestamp
        sorted_messages = sorted(messages, key=lambda m: m.timestamp_ms)

        # Apply different threading algorithms
        time_based_threads = self._time_based_threading(sorted_messages)
        topic_based_threads = self._topic_based_threading(sorted_messages)
        interaction_based_threads = self._interaction_based_threading(sorted_messages)

        # Merge and optimize threads
        final_threads = self._merge_and_optimize_threads(
            time_based_threads, topic_based_threads, interaction_based_threads
        )

        # Post-process threads
        return self._post_process_threads(final_threads)

    def _time_based_threading(self, messages: list[Message]) -> list[ConversationThread]:
        """Create threads based on temporal gaps."""
        threads: list[ConversationThread] = []
        current_thread = None

        for message in messages:
            if current_thread is None or (
                message.timestamp
                and current_thread.end_time
                and message.timestamp - current_thread.end_time > self.time_gap_threshold
            ):
                # Start new thread
                if (
                    current_thread
                    and len(current_thread.messages) >= self.min_thread_messages
                ):
                    threads.append(current_thread)

                current_thread = ConversationThread(
                    thread_id=f"time_thread_{len(threads) + 1}",
                    messages=[message],
                    participants=[message.sender_name],
                    start_time=message.timestamp,
                    end_time=message.timestamp,
                )
            else:
                # Add to current thread
                if current_thread:
                    current_thread.messages.append(message)
                    if message.sender_name not in current_thread.participants:
                        current_thread.participants.append(message.sender_name)
                    if message.timestamp:
                        current_thread.end_time = message.timestamp

        # Add final thread
        if current_thread and len(current_thread.messages) >= self.min_thread_messages:
            threads.append(current_thread)

        return threads

    def _topic_based_threading(self, messages: list[Message]) -> list[ConversationThread]:
        """Create threads based on topic similarity."""
        threads: list[ConversationThread] = []

        # Extract topics/keywords from messages
        message_topics = []
        for msg in messages:
            topics = self._extract_message_topics(msg)
            message_topics.append(topics)

        # Group messages by topic similarity
        current_thread = None
        current_topics = set()

        for i, message in enumerate(messages):
            msg_topics = message_topics[i]

            # Calculate topic similarity with current thread
            if current_thread and current_topics:
                similarity = len(msg_topics.intersection(current_topics)) / len(
                    msg_topics.union(current_topics)
                )
            else:
                similarity = 0

            if similarity < self.topic_threshold or current_thread is None:
                # Start new thread
                if (
                    current_thread
                    and len(current_thread.messages) >= self.min_thread_messages
                ):
                    threads.append(current_thread)

                current_thread = ConversationThread(
                    thread_id=f"topic_thread_{len(threads) + 1}",
                    messages=[message],
                    participants=[message.sender_name],
                    start_time=message.timestamp,
                    end_time=message.timestamp,
                    topic=", ".join(list(msg_topics)[:3]),  # First 3 topics
                )
                current_topics = msg_topics.copy()
            else:
                # Add to current thread
                if current_thread:
                    current_thread.messages.append(message)
                    if message.sender_name not in current_thread.participants:
                        current_thread.participants.append(message.sender_name)
                    if message.timestamp:
                        current_thread.end_time = message.timestamp
                    current_topics.update(msg_topics)

        # Add final thread
        if current_thread and len(current_thread.messages) >= self.min_thread_messages:
            threads.append(current_thread)

        return threads

    def _interaction_based_threading(
        self, messages: list[Message]
    ) -> list[ConversationThread]:
        """Create threads based on interaction patterns (replies, reactions)."""
        threads: list[ConversationThread] = []

        # Look for interaction patterns
        reply_chains = self._detect_reply_chains(messages)
        reaction_groups = self._detect_reaction_groups(messages)

        # Convert interaction patterns to threads
        for chain in reply_chains:
            if len(chain) >= self.min_thread_messages:
                thread = ConversationThread(
                    thread_id=f"reply_thread_{len(threads) + 1}",
                    messages=chain,
                    participants=list({msg.sender_name for msg in chain}),
                    start_time=min(msg.timestamp for msg in chain if msg.timestamp),
                    end_time=max(msg.timestamp for msg in chain if msg.timestamp),
                )
                threads.append(thread)

        for group in reaction_groups:
            if len(group) >= self.min_thread_messages:
                thread = ConversationThread(
                    thread_id=f"reaction_thread_{len(threads) + 1}",
                    messages=group,
                    participants=list({msg.sender_name for msg in group}),
                    start_time=min(msg.timestamp for msg in group if msg.timestamp),
                    end_time=max(msg.timestamp for msg in group if msg.timestamp),
                )
                threads.append(thread)

        return threads

    def _extract_message_topics(self, message: Message) -> Set[str]:
        """Extract topics/keywords from a message."""
        topics = set()

        if message.content:
            # Extract hashtags
            hashtags = re.findall(r"#\w+", message.content.lower())
            topics.update(hashtags)

            # Extract mentions
            mentions = re.findall(r"@\w+", message.content.lower())
            topics.update(mentions)

            # Extract significant words (simple approach)
            words = re.findall(r"\b\w{4,}\b", message.content.lower())
            # Filter common words
            stop_words = {
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
                "jaja",
                "jajaja",
            }
            significant_words = [w for w in words if w not in stop_words]
            topics.update(significant_words[:5])  # Top 5 words

        # Add message type as topic
        topics.add(f"type_{message.message_type.value}")

        return topics

    def _detect_reply_chains(self, messages: list[Message]) -> list[list[Message]]:
        """Detect reply chains in messages."""
        chains = []

        # Simple heuristic: messages close in time with alternating senders
        for i in range(len(messages) - 1):
            current_msg = messages[i]

            # Look for rapid back-and-forth
            chain = [current_msg]
            last_sender = current_msg.sender_name

            for j in range(
                i + 1, min(i + 10, len(messages))
            ):  # Look ahead max 10 messages
                next_msg = messages[j]

                # Check if it's a potential reply
                if (
                    next_msg.timestamp
                    and current_msg.timestamp
                    and (next_msg.timestamp - current_msg.timestamp).total_seconds() < 300
                    and next_msg.sender_name != last_sender  # 5 minutes
                ):
                    chain.append(next_msg)
                    last_sender = next_msg.sender_name
                    current_msg = next_msg
                else:
                    break

            if len(chain) >= 3:  # At least 3 messages for a chain
                chains.append(chain)

        return chains

    def _detect_reaction_groups(self, messages: list[Message]) -> list[list[Message]]:
        """Detect groups of messages with reactions."""
        groups = []

        # Find messages with reactions and group nearby messages
        for i, msg in enumerate(messages):
            if msg.reactions:
                group = [msg]

                # Look at surrounding messages
                start_idx = max(0, i - 5)
                end_idx = min(len(messages), i + 6)

                for j in range(start_idx, end_idx):
                    if j != i:
                        other_msg = messages[j]
                        if (
                            other_msg.timestamp
                            and msg.timestamp
                            and abs((other_msg.timestamp - msg.timestamp).total_seconds())
                            < 600
                        ):  # 10 minutes
                            group.append(other_msg)

                if len(group) >= self.min_thread_messages:
                    groups.append(sorted(group, key=lambda m: m.timestamp_ms))

        return groups

    def _merge_and_optimize_threads(
        self, *thread_lists: list[ConversationThread]
    ) -> list[ConversationThread]:
        """Merge and optimize threads from different algorithms."""
        all_threads = []
        for thread_list in thread_lists:
            all_threads.extend(thread_list)

        if not all_threads:
            return []

        # Remove duplicate threads and merge overlapping ones
        merged_threads = []
        used_messages: set[str] = set()

        # Sort threads by start time
        sorted_threads = sorted(all_threads, key=lambda t: t.start_time or datetime.min)

        for thread in sorted_threads:
            thread_message_ids = {
                msg.message_id for msg in thread.messages if msg.message_id
            }

            # Check if thread overlaps significantly with already used messages
            overlap = len(thread_message_ids.intersection(used_messages))
            overlap_ratio = overlap / len(thread_message_ids) if thread_message_ids else 0

            if overlap_ratio < 0.5:  # Less than 50% overlap
                merged_threads.append(thread)
                used_messages.update(thread_message_ids)

        return merged_threads

    def _post_process_threads(
        self, threads: list[ConversationThread]
    ) -> list[ConversationThread]:
        """Post-process threads to add additional metadata."""
        for i, thread in enumerate(threads):
            # Update thread ID
            thread.thread_id = f"thread_{i + 1}"

            # Calculate duration
            if thread.start_time and thread.end_time:
                duration = (thread.end_time - thread.start_time).total_seconds() / 60
                thread.duration_minutes = duration

            # Infer topic if not set
            if not thread.topic:
                thread.topic = self._infer_thread_topic(thread.messages)

        return threads

    def _infer_thread_topic(self, messages: list[Message]) -> str:
        """Infer topic from thread messages."""
        all_topics = set()

        for msg in messages:
            msg_topics = self._extract_message_topics(msg)
            all_topics.update(msg_topics)

        # Remove type topics for better readability
        content_topics = [t for t in all_topics if not t.startswith("type_")]

        return (
            ", ".join(list(content_topics)[:3])
            if content_topics
            else "General conversation"
        )


class ConversationAnalyzer:
    """Advanced conversation analyzer with thread reconstruction."""

    def __init__(self, data_root: Path):
        """Initialize analyzer with data root path."""
        self.data_root = data_root
        self.parser = ConversationParser(data_root)
        self.thread_engine = ThreadReconstructionEngine()
        self.conversations: list[Conversation] = []
        self.analysis = None

    def load_conversations(
        self, conversations_dir: Optional[Path] = None
    ) -> list[Conversation]:
        """Load and parse all conversations.

        Args:
            conversations_dir: Path to conversations directory, defaults to data_root/messages/inbox

        Returns:
            List of parsed conversations
        """
        if conversations_dir is None:
            conversations_dir = (
                self.data_root / "your_instagram_activity" / "messages" / "inbox"
            )

        self.conversations = self.parser.parse_all_conversations(conversations_dir)

        # Enhance conversations with advanced thread reconstruction
        for conversation in self.conversations:
            conversation.threads = self.thread_engine.reconstruct_threads(
                conversation.messages
            )

        return self.conversations

    def analyze_conversation_patterns(self) -> ConversationAnalysis:
        """Perform comprehensive conversation pattern analysis."""
        if not self.conversations:
            raise ValueError("No conversations loaded. Call load_conversations() first.")

        # Generate base analysis
        analysis = self.parser.generate_conversation_analysis(self.conversations)

        # Enhance with advanced analytics
        analysis = self._enhance_analysis_with_advanced_metrics(analysis)

        self.analysis = analysis
        return analysis

    def _enhance_analysis_with_advanced_metrics(
        self, analysis: ConversationAnalysis
    ) -> ConversationAnalysis:
        """Enhance analysis with advanced conversation metrics."""

        # Response time analysis
        response_times = self._calculate_response_times()
        analysis.response_time_analysis = response_times

        # Conversation length distribution
        length_dist = self._analyze_conversation_lengths()
        analysis.conversation_length_distribution = length_dist

        # Thread analysis
        thread_analysis = self._analyze_threads()
        analysis.thread_analysis = thread_analysis

        # Peak messaging periods
        peak_periods = self._identify_peak_periods()
        analysis.peak_messaging_periods = peak_periods

        # Popular topics analysis
        popular_topics = self._analyze_popular_topics()
        analysis.popular_topics = popular_topics

        return analysis

    def _calculate_response_times(self) -> dict[str, float]:
        """Calculate response time statistics across conversations."""
        all_response_times = []

        for conv in self.conversations:
            if len(conv.messages) < 2:
                continue

            # Calculate response times between consecutive messages from different senders
            for i in range(1, len(conv.messages)):
                current_msg = conv.messages[i]
                prev_msg = conv.messages[i - 1]

                if (
                    current_msg.sender_name != prev_msg.sender_name
                    and current_msg.timestamp
                    and prev_msg.timestamp
                ):
                    response_time = (
                        current_msg.timestamp - prev_msg.timestamp
                    ).total_seconds() / 60
                    if response_time <= 1440:  # Within 24 hours
                        all_response_times.append(response_time)

        if not all_response_times:
            return {}

        return {
            "avg_response_time_minutes": statistics.mean(all_response_times),
            "median_response_time_minutes": statistics.median(all_response_times),
            "fast_response_percentage": len([t for t in all_response_times if t <= 5])
            / len(all_response_times)
            * 100,
            "slow_response_percentage": len([t for t in all_response_times if t >= 60])
            / len(all_response_times)
            * 100,
        }

    def _analyze_conversation_lengths(self) -> dict[str, int]:
        """Analyze distribution of conversation lengths."""
        lengths = [
            conv.metrics.total_messages if conv.metrics else 0
            for conv in self.conversations
        ]

        length_ranges = {
            "very_short_1_5": len([length for length in lengths if 1 <= length <= 5]),
            "short_6_20": len([length for length in lengths if 6 <= length <= 20]),
            "medium_21_100": len([length for length in lengths if 21 <= length <= 100]),
            "long_101_500": len([length for length in lengths if 101 <= length <= 500]),
            "very_long_500_plus": len([length for length in lengths if length > 500]),
        }

        return length_ranges

    def _analyze_threads(self) -> dict[str, Any]:
        """Analyze thread patterns across conversations."""
        all_threads = []
        for conv in self.conversations:
            all_threads.extend(conv.threads)

        if not all_threads:
            return {}

        thread_lengths = [len(thread.messages) for thread in all_threads]
        thread_durations = [
            thread.duration_minutes for thread in all_threads if thread.duration_minutes
        ]

        analysis = {
            "total_threads": len(all_threads),
            "avg_thread_length": statistics.mean(thread_lengths) if thread_lengths else 0,
            "avg_thread_duration_minutes": (
                statistics.mean(thread_durations) if thread_durations else 0
            ),
            "threads_per_conversation": (
                len(all_threads) / len(self.conversations) if self.conversations else 0
            ),
        }

        # Thread topic analysis
        topics = Counter()
        for thread in all_threads:
            if thread.topic:
                topics[thread.topic] += 1

        analysis["popular_thread_topics"] = dict(topics.most_common(10))

        return analysis

    def _identify_peak_periods(self) -> list[dict[str, Any]]:
        """Identify peak messaging periods."""
        # Aggregate all message timestamps
        all_timestamps = []
        for conv in self.conversations:
            for msg in conv.messages:
                if msg.timestamp:
                    all_timestamps.append(msg.timestamp)

        if not all_timestamps:
            return []

        # Group by time periods and find peaks
        hourly_counts = Counter(ts.hour for ts in all_timestamps)
        daily_counts = Counter(ts.strftime("%A") for ts in all_timestamps)
        monthly_counts = Counter(ts.strftime("%Y-%m") for ts in all_timestamps)

        peaks = []

        # Peak hour
        if hourly_counts:
            peak_hour = hourly_counts.most_common(1)[0]
            peaks.append(
                {
                    "type": "hourly",
                    "period": f"{peak_hour[0]}:00",
                    "message_count": peak_hour[1],
                    "description": f"Most active hour: {peak_hour[0]}:00 with {peak_hour[1]} messages",
                }
            )

        # Peak day
        if daily_counts:
            peak_day = daily_counts.most_common(1)[0]
            peaks.append(
                {
                    "type": "daily",
                    "period": peak_day[0],
                    "message_count": peak_day[1],
                    "description": f"Most active day: {peak_day[0]} with {peak_day[1]} messages",
                }
            )

        # Peak month
        if monthly_counts:
            peak_month = monthly_counts.most_common(1)[0]
            peaks.append(
                {
                    "type": "monthly",
                    "period": peak_month[0],
                    "message_count": peak_month[1],
                    "description": f"Most active month: {peak_month[0]} with {peak_month[1]} messages",
                }
            )

        return peaks

    def _analyze_popular_topics(self) -> list[dict[str, Any]]:
        """Analyze popular topics across all conversations."""
        topic_frequency = Counter()

        for conv in self.conversations:
            # Aggregate from conversation keyword frequency
            if conv.keyword_frequency:
                topic_frequency.update(conv.keyword_frequency)

        popular_topics = []
        for topic, frequency in topic_frequency.most_common(20):
            popular_topics.append(
                {
                    "topic": topic,
                    "frequency": frequency,
                    "conversations": len(
                        [
                            c
                            for c in self.conversations
                            if c.keyword_frequency and topic in c.keyword_frequency
                        ]
                    ),
                }
            )

        return popular_topics

    def get_conversation_by_id(self, conversation_id: str) -> Optional[Conversation]:
        """Get a specific conversation by ID."""
        for conv in self.conversations:
            if conv.conversation_id == conversation_id:
                return conv
        return None

    def search_conversations(
        self, query: str, search_content: bool = True, search_participants: bool = True
    ) -> list[Conversation]:
        """Search conversations by content or participants.

        Args:
            query: Search query
            search_content: Whether to search in message content
            search_participants: Whether to search in participant names

        Returns:
            List of matching conversations
        """
        query_lower = query.lower()
        matching_conversations = []

        for conv in self.conversations:
            match_found = False

            # Search in participant names
            if search_participants:
                for participant in conv.participants:
                    if query_lower in participant.name.lower():
                        match_found = True
                        break

            # Search in message content
            if search_content and not match_found:
                for message in conv.messages:
                    if message.content and query_lower in message.content.lower():
                        match_found = True
                        break

            if match_found:
                matching_conversations.append(conv)

        return matching_conversations

    def export_conversation_summary(self, output_path: Path) -> Path:
        """Export conversation analysis summary to JSON.

        Args:
            output_path: Directory to save the summary

        Returns:
            Path to the exported file
        """
        if not self.analysis:
            self.analyze_conversation_patterns()

        summary_file = output_path / "conversation_analysis_summary.json"

        # Convert analysis to dict for JSON serialization
        summary_data = self.analysis.model_dump()

        # Add conversation summaries
        summary_data["conversation_summaries"] = []
        for conv in self.conversations:
            conv_summary = {
                "id": conv.conversation_id,
                "title": conv.title,
                "type": conv.conversation_type.value,
                "participant_count": len(conv.participants),
                "message_count": conv.metrics.total_messages if conv.metrics else 0,
                "thread_count": len(conv.threads),
                "date_range": {
                    "start": (
                        conv.metrics.date_range.get("start").isoformat()
                        if conv.metrics and conv.metrics.date_range.get("start")
                        else None
                    ),
                    "end": (
                        conv.metrics.date_range.get("end").isoformat()
                        if conv.metrics and conv.metrics.date_range.get("end")
                        else None
                    ),
                },
            }
            summary_data["conversation_summaries"].append(conv_summary)

        # Write to file
        import json

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)

        return summary_file
