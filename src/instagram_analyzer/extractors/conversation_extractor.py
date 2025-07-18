"""Advanced conversation extractor with enhanced features and optimizations."""

import json
import logging
import time
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..analyzers.conversation_analyzer import ConversationAnalyzer
from ..models.conversation import Conversation, ConversationAnalysis, MessageType
from ..parsers.conversation_parser import ConversationParser

logger = logging.getLogger(__name__)


class ConversationExtractor:
    """Enhanced conversation extractor with advanced features and optimizations."""

    def __init__(self, data_root: Path, max_workers: int = 4):
        """Initialize the conversation extractor.

        Args:
            data_root: Root directory of Instagram data export
            max_workers: Maximum number of threads for parallel processing
        """
        self.data_root = Path(data_root)
        self.max_workers = max_workers
        self.parser = ConversationParser(data_root)
        self.analyzer = ConversationAnalyzer(data_root)

        # Performance tracking
        self.extraction_stats = {
            "total_conversations": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "total_messages": 0,
            "processing_time": 0.0,
        }

        # Extraction filters and options
        self.filters: dict[str, Any] = {
            "min_messages": 1,
            "max_messages": None,
            "date_range": None,
            "participants": None,
            "message_types": None,
            "exclude_empty": True,
        }

    def set_filters(self, **kwargs) -> None:
        """Set extraction filters.

        Available filters:
        - min_messages: Minimum number of messages in conversation
        - max_messages: Maximum number of messages in conversation
        - date_range: Tuple of (start_date, end_date)
        - participants: List of participant names to include
        - message_types: List of message types to include
        - exclude_empty: Whether to exclude conversations with no content
        """
        self.filters.update(kwargs)
        logger.info("Updated extraction filters: %s", kwargs)

    def extract_all_conversations(self, parallel: bool = True) -> list[Conversation]:
        """Extract all conversations with parallel processing support.

        Args:
            parallel: Whether to use parallel processing

        Returns:
            List of extracted and processed conversations
        """
        start_time = time.time()

        # Find all conversation files
        inbox_dir = self.data_root / "your_instagram_activity" / "messages" / "inbox"
        conversation_files = self._discover_conversation_files(inbox_dir)

        logger.info("Found %d conversation files", len(conversation_files))

        if parallel and len(conversation_files) > 1:
            conversations = self._extract_conversations_parallel(conversation_files)
        else:
            conversations = self._extract_conversations_sequential(conversation_files)

        # Apply filters
        filtered_conversations = self._apply_filters(conversations)

        # Update stats
        self.extraction_stats.update(
            {
                "total_conversations": len(conversation_files),
                "successful_extractions": len(filtered_conversations),
                "failed_extractions": len(conversation_files) - len(conversations),
                "total_messages": sum(
                    len(conv.messages) for conv in filtered_conversations
                ),
                "processing_time": time.time() - start_time,
            }
        )

        logger.info("Extraction completed: %s", self.extraction_stats)

        return filtered_conversations

    def extract_conversation_subset(
        self,
        conversation_ids: Optional[list[str]] = None,
        limit: Optional[int] = None,
        sample_random: bool = False,
    ) -> list[Conversation]:
        """Extract a subset of conversations.

        Args:
            conversation_ids: Specific conversation IDs to extract
            limit: Maximum number of conversations to extract
            sample_random: Whether to randomly sample conversations

        Returns:
            List of extracted conversations
        """
        inbox_dir = self.data_root / "your_instagram_activity" / "messages" / "inbox"
        conversation_files = self._discover_conversation_files(inbox_dir)

        # Filter by conversation IDs if specified
        if conversation_ids:
            filtered_files = []
            for file_path in conversation_files:
                conv_id = file_path.parent.name
                if conv_id in conversation_ids:
                    filtered_files.append(file_path)
            conversation_files = filtered_files

        # Apply limit and sampling
        if limit and len(conversation_files) > limit:
            if sample_random:
                import random

                conversation_files = random.sample(conversation_files, limit)
            else:
                conversation_files = conversation_files[:limit]

        return self._extract_conversations_sequential(conversation_files)

    def extract_conversations_by_criteria(
        self,
        date_range: Optional[tuple[datetime, datetime]] = None,
        participant_names: Optional[list[str]] = None,
        min_message_count: int = 1,
        message_content_filter: Optional[str] = None,
    ) -> list[Conversation]:
        """Extract conversations matching specific criteria.

        Args:
            date_range: Tuple of (start_date, end_date) to filter by
            participant_names: List of participant names to filter by
            min_message_count: Minimum number of messages required
            message_content_filter: Text content to search for in messages

        Returns:
            List of conversations matching criteria
        """
        # Set temporary filters
        original_filters = self.filters.copy()

        self.filters.update(
            {
                "min_messages": min_message_count,
                "date_range": date_range,
                "participants": participant_names,
            }
        )

        try:
            conversations = self.extract_all_conversations()

            # Additional content filtering
            if message_content_filter:
                conversations = self._filter_by_content(
                    conversations, message_content_filter
                )

            return conversations
        finally:
            # Restore original filters
            self.filters = original_filters

    def extract_and_analyze(
        self,
        export_path: Optional[Path] = None,
        include_advanced_analytics: bool = True,
        anonymize: bool = False,
    ) -> tuple[list[Conversation], ConversationAnalysis]:
        """Extract conversations and perform comprehensive analysis.

        Args:
            export_path: Path to export results (optional)
            include_advanced_analytics: Whether to include advanced analytics
            anonymize: Whether to anonymize sensitive data

        Returns:
            Tuple of (conversations, analysis)
        """
        logger.info("Starting comprehensive conversation extraction and analysis")

        # Extract conversations
        conversations = self.extract_all_conversations()

        if not conversations:
            logger.warning("No conversations extracted")
            return [], ConversationAnalysis(
                total_conversations=0,
                total_messages=0,
                date_range={},
                conversation_types={},
                most_active_conversations=[],
                conversation_sizes={},
                most_frequent_contacts=[],
                group_vs_direct_ratio={},
                unique_contacts=0,
                messaging_by_hour={},
                messaging_by_day={},
                messaging_by_month={},
                peak_messaging_periods=[],
                message_type_distribution={},
                media_sharing_patterns={},
                reaction_usage={},
                popular_topics=[],
                response_time_analysis={},
                conversation_length_distribution={},
                thread_analysis={},
                conversations_with_sensitive_data=0,
                anonymization_recommendations=[],
            )

        # Load into analyzer
        self.analyzer.conversations = conversations

        # Perform analysis
        if include_advanced_analytics:
            analysis = self.analyzer.analyze_conversation_patterns()
        else:
            analysis = self.parser.generate_conversation_analysis(conversations)

        # Apply anonymization if requested
        if anonymize:
            conversations = self._anonymize_conversations(conversations)
            analysis = self._anonymize_analysis(analysis)

        # Export results if path specified
        if export_path:
            export_path = Path(export_path)
            export_path.mkdir(parents=True, exist_ok=True)
            self._export_results(conversations, analysis, export_path, anonymize)

        return conversations, analysis

    def get_extraction_statistics(self) -> dict[str, Any]:
        """Get detailed extraction statistics and performance metrics."""
        stats = self.extraction_stats.copy()

        # Add derived metrics
        if stats["total_conversations"] > 0:
            stats["success_rate"] = (
                stats["successful_extractions"] / stats["total_conversations"]
            ) * 100
            stats["avg_messages_per_conversation"] = (
                stats["total_messages"] / stats["successful_extractions"]
                if stats["successful_extractions"] > 0
                else 0
            )
            stats["processing_rate_conversations_per_second"] = (
                stats["total_conversations"] / stats["processing_time"]
                if stats["processing_time"] > 0
                else 0
            )

        # Add filter information
        stats["active_filters"] = {k: v for k, v in self.filters.items() if v is not None}

        return stats

    def _discover_conversation_files(self, inbox_dir: Path) -> list[Path]:
        """Discover all conversation files in the inbox directory."""
        conversation_files: list[Path] = []

        if not inbox_dir.exists():
            logger.warning("Inbox directory not found: %s", inbox_dir)
            return conversation_files

        for conv_dir in inbox_dir.iterdir():
            if conv_dir.is_dir():
                message_files = list(conv_dir.glob("message_*.json"))
                conversation_files.extend(message_files)

        logger.info("Discovered %d conversation files", len(conversation_files))
        return conversation_files

    def _extract_conversations_parallel(
        self, conversation_files: list[Path]
    ) -> list[Conversation]:
        """Extract conversations using parallel processing."""
        conversations = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all parsing tasks
            future_to_file = {
                executor.submit(self._safe_parse_conversation, file_path): file_path
                for file_path in conversation_files
            }

            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    conversation = future.result()
                    if conversation:
                        conversations.append(conversation)
                except Exception as e:
                    logger.error("Failed to parse %s: %s", file_path, e)

        logger.info(
            "Parallel extraction completed: %d conversations",
            len(conversations),
        )
        return conversations

    def _extract_conversations_sequential(
        self, conversation_files: list[Path]
    ) -> list[Conversation]:
        """Extract conversations sequentially."""
        conversations = []

        for file_path in conversation_files:
            try:
                conversation = self._safe_parse_conversation(file_path)
                if conversation:
                    conversations.append(conversation)
            except Exception as e:
                logger.error("Failed to parse %s: %s", file_path, e)

        logger.info(
            "Sequential extraction completed: %d conversations",
            len(conversations),
        )
        return conversations

    def _safe_parse_conversation(self, file_path: Path) -> Optional[Conversation]:
        """Safely parse a conversation file with error handling."""
        try:
            return self.parser.parse_conversation_file(file_path)
        except Exception as e:
            logger.debug("Error parsing %s: %s", file_path, e)
            return None

    def _apply_filters(self, conversations: list[Conversation]) -> list[Conversation]:
        """Apply extraction filters to conversations."""
        filtered = conversations.copy()

        # Filter by message count
        min_messages = self.filters.get("min_messages")
        if isinstance(min_messages, int) and min_messages > 1:
            filtered = [conv for conv in filtered if len(conv.messages) >= min_messages]

        max_messages = self.filters.get("max_messages")
        if isinstance(max_messages, int):
            filtered = [conv for conv in filtered if len(conv.messages) <= max_messages]

        # Filter by date range
        date_range = self.filters.get("date_range")
        if (
            isinstance(date_range, tuple)
            and len(date_range) == 2
            and all(isinstance(d, datetime) for d in date_range)
        ):
            start_date, end_date = date_range
            filtered = [
                conv
                for conv in filtered
                if self._conversation_in_date_range(conv, start_date, end_date)
            ]

        participants = self.filters.get("participants")
        if isinstance(participants, list):
            participant_names = [name.lower() for name in participants]
            filtered = [
                conv
                for conv in filtered
                if any(
                    (p.name.lower() if hasattr(p, "name") else str(p).lower())
                    in participant_names
                    for p in conv.participants
                )
            ]

        message_types = self.filters.get("message_types")
        if isinstance(message_types, list):
            filtered = [
                conv
                for conv in filtered
                if self._conversation_has_message_types(conv, message_types)
            ]

        return filtered

    def _conversation_in_date_range(
        self, conv: Conversation, start_date: datetime, end_date: datetime
    ) -> bool:
        """Check if conversation falls within date range."""
        if not conv.messages:
            return False

        message_dates = [msg.timestamp for msg in conv.messages if msg.timestamp]
        if not message_dates:
            return False

        conv_start = min(message_dates)
        conv_end = max(message_dates)

        return not (conv_end < start_date or conv_start > end_date)

    def _conversation_has_participants(
        self, conv: Conversation, participant_names: list[str]
    ) -> bool:
        """Check if conversation includes specified participants."""
        conv_participant_names = [p.name.lower() for p in conv.participants]
        return any(name in conv_participant_names for name in participant_names)

    def _conversation_has_message_types(
        self, conv: Conversation, message_types: list[MessageType]
    ) -> bool:
        """Check if conversation contains specified message types."""
        conv_message_types = {msg.message_type for msg in conv.messages}
        return any(msg_type in conv_message_types for msg_type in message_types)

    def _filter_by_content(
        self, conversations: list[Conversation], content_filter: str
    ) -> list[Conversation]:
        """Filter conversations by message content."""
        content_lower = content_filter.lower()
        filtered = []

        for conv in conversations:
            if any(
                msg.content and content_lower in msg.content.lower()
                for msg in conv.messages
            ):
                filtered.append(conv)

        return filtered

    def _anonymize_conversations(
        self, conversations: list[Conversation]
    ) -> list[Conversation]:
        """Apply anonymization to conversation data."""
        # Placeholder for anonymization logic
        return conversations.copy()

    def _anonymize_analysis(self, analysis: ConversationAnalysis) -> ConversationAnalysis:
        """Apply anonymization to analysis results."""
        # Replace participant names with generic identifiers
        if analysis.most_frequent_contacts:
            for i, contact in enumerate(analysis.most_frequent_contacts):
                contact["name"] = f"Contact_{i+1}"

        if analysis.most_active_conversations:
            for i, conv in enumerate(analysis.most_active_conversations):
                conv["title"] = f"Conversation_{i+1}"

        return analysis

    def _export_results(
        self,
        conversations: list[Conversation],
        analysis: ConversationAnalysis,
        export_path: Path,
        anonymized: bool = False,
    ) -> None:
        """Export extraction results to files."""
        # Export conversation summaries
        summaries = []
        for conv in conversations:
            start = conv.metrics.date_range.get("start") if conv.metrics else None
            end = conv.metrics.date_range.get("end") if conv.metrics else None
            summary = {
                "id": conv.conversation_id,
                "title": conv.title,
                "type": conv.conversation_type.value,
                "participants": len(conv.participants),
                "messages": len(conv.messages),
                "threads": len(conv.threads),
                "date_range": (
                    {
                        "start": start.isoformat() if start is not None else None,
                        "end": end.isoformat() if end is not None else None,
                    }
                    if conv.metrics
                    else None
                ),
            }
            summaries.append(summary)

        # Export main results
        results = {
            "extraction_stats": self.get_extraction_statistics(),
            "analysis": analysis.model_dump() if analysis else {},
            "conversation_summaries": summaries,
            "extraction_timestamp": datetime.now().isoformat(),
            "anonymized": anonymized,
        }

        # Write results
        results_file = export_path / "conversation_extraction_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        # Export individual conversation details if requested
        conversations_dir = export_path / "conversations"
        conversations_dir.mkdir(exist_ok=True)

        for conv in conversations[:10]:  # Limit to first 10 for space
            conv_file = conversations_dir / f"{conv.conversation_id}.json"
            with open(conv_file, "w", encoding="utf-8") as f:
                json.dump(
                    conv.model_dump(),
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                )

        logger.info("Results exported to %s", export_path)


class ConversationIterator:
    """Iterator for processing conversations in batches to manage memory usage."""

    def __init__(self, extractor: ConversationExtractor, batch_size: int = 50):
        """Initialize conversation iterator.

        Args:
            extractor: ConversationExtractor instance
            batch_size: Number of conversations to process in each batch
        """
        self.extractor = extractor
        self.batch_size = batch_size
        self.conversation_files: list[Path] = []
        self.current_index = 0

    def __iter__(self) -> Iterator[list[Conversation]]:
        """Iterate over conversation batches."""
        inbox_dir = (
            self.extractor.data_root / "your_instagram_activity" / "messages" / "inbox"
        )
        self.conversation_files = self.extractor._discover_conversation_files(inbox_dir)
        self.current_index = 0
        return self

    def __next__(self) -> list[Conversation]:
        """Get next batch of conversations."""
        if self.current_index >= len(self.conversation_files):
            raise StopIteration

        # Get batch of files
        batch_files = self.conversation_files[
            self.current_index : self.current_index + self.batch_size
        ]
        self.current_index += self.batch_size

        # Extract batch
        conversations = self.extractor._extract_conversations_sequential(batch_files)
        return self.extractor._apply_filters(conversations)


# Utility functions for common extraction tasks


def quick_extract_top_conversations(
    data_root: Path, limit: int = 10
) -> list[Conversation]:
    """Quickly extract the most active conversations.

    Args:
        data_root: Instagram data root directory
        limit: Number of top conversations to extract

    Returns:
        List of most active conversations
    """
    extractor = ConversationExtractor(data_root)
    extractor.set_filters(min_messages=5)  # Only conversations with some activity

    conversations = extractor.extract_all_conversations()

    # Sort by message count and return top N
    conversations.sort(key=lambda c: len(c.messages), reverse=True)
    return conversations[:limit]


def extract_conversations_with_keywords(
    data_root: Path, keywords: list[str]
) -> list[Conversation]:
    """Extract conversations containing specific keywords.

    Args:
        data_root: Instagram data root directory
        keywords: List of keywords to search for

    Returns:
        List of conversations containing any of the keywords
    """
    extractor = ConversationExtractor(data_root)

    all_conversations = extractor.extract_all_conversations()
    matching_conversations = []

    for keyword in keywords:
        matches = extractor._filter_by_content(all_conversations, keyword)
        matching_conversations.extend(matches)

    # Remove duplicates
    seen_ids = set()
    unique_conversations = []
    for conv in matching_conversations:
        if conv.conversation_id not in seen_ids:
            seen_ids.add(conv.conversation_id)
            unique_conversations.append(conv)

    return unique_conversations
