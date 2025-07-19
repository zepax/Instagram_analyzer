"""Parallel JSON parser for Instagram data files with enhanced performance."""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..logging_config import get_logger
from ..models import Comment, Like, Post, Profile, Reel, Story, StoryInteraction
from ..utils.parallel_processor import BatchProcessor as ParallelBatchProcessor
from ..utils.parallel_processor import ParallelProcessor
from ..utils.streaming_parser import StreamingJSONParser
from .json_parser import JSONParser

logger = get_logger("parallel_json_parser")


class ParallelJSONParser(JSONParser):
    """Enhanced JSON parser with parallel processing capabilities."""

    def __init__(
        self,
        memory_threshold: int = 50 * 1024 * 1024,
        max_workers: Optional[int] = None,
        batch_size: int = 1000,
        enable_parallel: bool = True,
        show_progress: bool = True,
    ):
        """Initialize parallel JSON parser.

        Args:
            memory_threshold: File size threshold for using streaming mode
            max_workers: Maximum number of worker threads
            batch_size: Batch size for processing
            enable_parallel: Whether to enable parallel processing
            show_progress: Whether to show progress bars
        """
        super().__init__(memory_threshold)
        self.enable_parallel = enable_parallel
        self.show_progress = show_progress
        self.batch_size = batch_size

        # Initialize parallel processing components
        self.parallel_processor = ParallelProcessor(max_workers=max_workers)
        self.parallel_batch_processor = ParallelBatchProcessor(batch_size=batch_size)

        self.logger = logger

    def parse_posts_parallel(
        self, data: Union[list[dict[str, Any]], dict[str, Any]]
    ) -> list[Post]:
        """Parse posts data using parallel processing.

        Args:
            data: Raw posts data from JSON

        Returns:
            List of Post model instances
        """
        if not data or not self.enable_parallel:
            return super().parse_posts(data)

        posts: list[Post] = []

        # Handle different data formats
        posts_data = data
        if isinstance(data, dict):
            # Some exports wrap posts in a container
            if "posts" in data:
                posts_data = data["posts"]
            elif "data" in data:
                posts_data = data["data"]
            elif "items" in data:
                posts_data = data["items"]

        if not posts_data:
            return posts

        # Process posts in parallel
        if len(posts_data) > self.batch_size:
            self.logger.info(f"Processing {len(posts_data)} posts in parallel")

            results = self.parallel_processor.process_data_parallel(
                posts_data,
                self._parse_single_post,
                description="Parsing posts",
                show_progress=self.show_progress,
                chunk_size=self.batch_size,
            )

            # Filter out None results
            posts = [post for post in results if post is not None]
        else:
            # Use sequential processing for small datasets
            posts = super().parse_posts(posts_data)

        return posts

    def parse_stories_parallel(self, data: Any) -> list[Story]:
        """Parse stories data using parallel processing.

        Args:
            data: Raw stories data from JSON

        Returns:
            List of Story model instances
        """
        if not data or not self.enable_parallel:
            return super().parse_stories(data)

        stories: list[Story] = []

        # Handle different data formats
        stories_data = data
        if isinstance(data, dict):
            # Some exports wrap stories in a container
            if "ig_stories" in data:
                stories_data = data["ig_stories"]
            elif "stories" in data:
                stories_data = data["stories"]

        if not stories_data:
            return stories

        # Process stories in parallel
        if len(stories_data) > self.batch_size:
            self.logger.info(f"Processing {len(stories_data)} stories in parallel")

            results = self.parallel_processor.process_data_parallel(
                stories_data,
                self._parse_single_story,
                description="Parsing stories",
                show_progress=self.show_progress,
                chunk_size=self.batch_size,
            )

            # Filter out None results
            stories = [story for story in results if story is not None]
        else:
            # Use sequential processing for small datasets
            stories = super().parse_stories(stories_data)

        return stories

    def parse_reels_parallel(
        self, data: Union[list[dict[str, Any]], dict[str, Any]]
    ) -> list[Reel]:
        """Parse reels data using parallel processing.

        Args:
            data: Raw reels data from JSON

        Returns:
            List of Reel model instances
        """
        if not data or not self.enable_parallel:
            return super().parse_reels(data)

        reels: list[Reel] = []

        # Handle different data formats
        reels_data = data
        if isinstance(data, dict):
            # Some exports wrap reels in a container
            if "reels" in data:
                reels_data = data["reels"]

        if not reels_data:
            return reels

        # Process reels in parallel
        if len(reels_data) > self.batch_size:
            self.logger.info(f"Processing {len(reels_data)} reels in parallel")

            results = self.parallel_processor.process_data_parallel(
                reels_data,
                self._parse_single_reel,
                description="Parsing reels",
                show_progress=self.show_progress,
                chunk_size=self.batch_size,
            )

            # Filter out None results
            reels = [reel for reel in results if reel is not None]
        else:
            # Use sequential processing for small datasets
            reels = super().parse_reels(reels_data)

        return reels

    def parse_multiple_files_parallel(
        self,
        file_paths: list[Path],
        description: str = "Processing files",
    ) -> dict[str, Any]:
        """Parse multiple files in parallel.

        Args:
            file_paths: List of file paths to process
            description: Description for progress bar

        Returns:
            Dictionary with results from each file
        """
        if not file_paths:
            return {}

        if not self.enable_parallel:
            # Sequential processing fallback
            results = {}
            for file_path in file_paths:
                try:
                    from ..utils import safe_json_load

                    data = safe_json_load(file_path)
                    results[str(file_path)] = data
                except Exception as e:
                    from instagram_analyzer.exceptions import InstagramAnalyzerError

                    self.logger.error("Error processing %s: %s", file_path, e)
                    raise InstagramAnalyzerError(
                        f"Error processing {file_path}: {e}",
                        context={"file_path": str(file_path)},
                    ) from e
            return results

        # Parallel processing
        self.logger.info(f"Processing {len(file_paths)} files in parallel")

        def process_file(file_path: Path) -> tuple[str, Any]:
            """Process a single file and return key-value pair."""
            try:
                from ..utils import safe_json_load

                data = safe_json_load(file_path)
                return (str(file_path), data)
            except Exception as e:
                from instagram_analyzer.exceptions import InstagramAnalyzerError

                self.logger.error("Error processing %s: %s", file_path, e)
                raise InstagramAnalyzerError(
                    f"Error processing {file_path}: {e}",
                    context={"file_path": str(file_path)},
                ) from e

        results_list = self.parallel_processor.process_files_parallel(
            file_paths,
            lambda path: process_file(path),
            description=description,
            show_progress=self.show_progress,
        )

        # Convert list of tuples to dictionary
        results = {}
        for result in results_list:
            if result is not None:
                key, value = result
                results[key] = value

        return results

    async def parse_multiple_files_async(
        self,
        file_paths: list[Path],
        description: str = "Processing files",
    ) -> dict[str, Any]:
        """Parse multiple files asynchronously.

        Args:
            file_paths: List of file paths to process
            description: Description for progress bar

        Returns:
            Dictionary with results from each file
        """
        if not file_paths:
            return {}

        self.logger.info(f"Processing {len(file_paths)} files asynchronously")

        def process_file(file_path: Path) -> tuple[str, Any]:
            """Process a single file and return key-value pair."""
            try:
                from ..utils import safe_json_load

                data = safe_json_load(file_path)
                return (str(file_path), data)
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                return (str(file_path), None)

        results_list = await self.parallel_processor.process_files_async(
            file_paths,
            lambda path: process_file(path),
            description=description,
            show_progress=self.show_progress,
        )

        # Convert list of tuples to dictionary
        results = {}
        for result in results_list:
            if result is not None:
                key, value = result
                results[key] = value

        return results

    def parse_with_batching(
        self,
        data_items: list[Any],
        parser_func: str,
        description: str = "Processing data",
    ) -> list[Any]:
        """Parse data using batch processing with memory management.

        Args:
            data_items: List of data items to process
            parser_func: Name of the parser function to use
            description: Description for progress bar

        Returns:
            List of parsed results
        """
        if not data_items:
            return []

        # Get the parser function
        parser_method = getattr(self, parser_func)

        def process_batch(batch: list[Any]) -> list[Any]:
            """Process a batch of items."""
            results = []
            for item in batch:
                try:
                    result = parser_method(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing item in batch: {e}")
            return results

        self.logger.info(f"Processing {len(data_items)} items in batches")

        return self.parallel_batch_processor.process_in_batches(
            data_items,
            process_batch,
            description=description,
            show_progress=self.show_progress,
        )

    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics for the parser.

        Returns:
            Dictionary with performance metrics
        """
        return {
            "max_workers": self.parallel_processor.max_workers,
            "batch_size": self.batch_size,
            "enable_parallel": self.enable_parallel,
            "show_progress": self.show_progress,
            "memory_threshold": self.streaming_parser.memory_threshold,
        }

    def _parse_single_post(self, post_data: dict[str, Any]) -> Optional[Post]:
        """Parse a single post from JSON data.

        Args:
            post_data: Single post data dictionary

        Returns:
            Post model instance or None if parsing fails
        """
        try:
            return super()._parse_single_post(post_data)
        except Exception as e:
            self.logger.error(f"Error parsing single post: {e}")
            return None

    def _parse_single_story(self, story_data: dict[str, Any]) -> Optional[Story]:
        """Parse a single story from JSON data.

        Args:
            story_data: Single story data dictionary

        Returns:
            Story model instance or None if parsing fails
        """
        try:
            return super()._parse_single_story(story_data)
        except Exception as e:
            self.logger.error(f"Error parsing single story: {e}")
            return None

    def _parse_single_reel(self, reel_data: dict[str, Any]) -> Optional[Reel]:
        """Parse a single reel from JSON data.

        Args:
            reel_data: Single reel data dictionary

        Returns:
            Reel model instance or None if parsing fails
        """
        try:
            return super()._parse_single_reel(reel_data)
        except Exception as e:
            self.logger.error(f"Error parsing single reel: {e}")
            return None


def create_parallel_parser(
    memory_threshold: int = 50 * 1024 * 1024,
    max_workers: Optional[int] = None,
    batch_size: int = 1000,
    enable_parallel: bool = True,
    show_progress: bool = True,
) -> ParallelJSONParser:
    """Create a parallel JSON parser instance.

    Args:
        memory_threshold: File size threshold for streaming mode
        max_workers: Maximum number of worker threads
        batch_size: Batch size for processing
        enable_parallel: Whether to enable parallel processing
        show_progress: Whether to show progress bars

    Returns:
        Configured ParallelJSONParser instance
    """
    return ParallelJSONParser(
        memory_threshold=memory_threshold,
        max_workers=max_workers,
        batch_size=batch_size,
        enable_parallel=enable_parallel,
        show_progress=show_progress,
    )
