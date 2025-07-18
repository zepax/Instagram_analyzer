"""Streaming JSON parser utilities for memory-efficient data processing."""

import gc
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import ijson

    HAS_IJSON = True
except ImportError:
    HAS_IJSON = False

from ..logging_config import get_logger

logger = get_logger("utils.streaming_parser")


class StreamingJSONParser:
    """Memory-efficient JSON parser for large Instagram data files."""

    def __init__(self, memory_threshold: int = 50 * 1024 * 1024):
        """Initialize streaming parser.

        Args:
            memory_threshold: File size threshold in bytes for using streaming mode
        """
        self.memory_threshold = memory_threshold
        self.logger = logger
    
    def parse(self, file_path: Union[str, Path], processor_func: Any) -> List[Any]:
        """Parse file and process with given function.
        
        Args:
            file_path: Path to file
            processor_func: Function to process data
            
        Returns:
            List of processed items
        """
        path_obj = Path(file_path) if isinstance(file_path, str) else file_path
        data = self.parse_file(path_obj)
        
        if hasattr(data, '__iter__') and not isinstance(data, (str, dict)):
            # Iterator from streaming
            return [item for item in data if item is not None]
        elif isinstance(data, dict):
            # Single object
            return [data] if data else []
        else:
            return []

    def parse_file(
        self, file_path: Path
    ) -> Any:
        """Parse JSON file, choosing streaming vs. standard based on file size.

        Args:
            file_path: Path to JSON file

        Returns:
            Either parsed JSON dict or iterator of items for large files
        """
        if not file_path.exists():
            return {}

        file_size = file_path.stat().st_size

        if file_size > self.memory_threshold and HAS_IJSON:
            self.logger.info(
                f"Using streaming parser for large file: {file_path} ({file_size} bytes)"
            )
            return self._parse_streaming(file_path)
        else:
            self.logger.debug(
                f"Using standard parser for file: {file_path} ({file_size} bytes)"
            )
            return self._parse_standard(file_path)

    def _parse_standard(self, file_path: Path) -> Dict[str, Any]:
        """Standard JSON parsing for smaller files."""
        try:
            with open(file_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to parse {file_path}: {e}")
            return {}

    def _parse_streaming(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """Streaming JSON parsing for large files."""
        if not HAS_IJSON:
            self.logger.warning("ijson not available, falling back to standard parsing")
            data = self._parse_standard(file_path)
            if isinstance(data, list):
                for item in data:
                    yield item
            elif isinstance(data, dict):
                yield data
            return

        try:
            with open(file_path, "rb") as f:
                # Simple streaming approach - parse as array first
                f.seek(0)
                try:
                    items = ijson.items(f, "item")
                    item_count = 0
                    for item in items:
                        yield item
                        item_count += 1
                        if item_count % 100 == 0:
                            gc.collect()
                    return
                except Exception:
                    # If that fails, try parsing as single object
                    f.seek(0)
                    try:
                        obj = next(ijson.items(f, ""))
                        yield obj
                        return
                    except Exception:
                        pass

        except Exception as e:
            self.logger.error(f"Streaming parsing failed for {file_path}: {e}")
            
        # Fall back to standard parsing
        data = self._parse_standard(file_path)
        if isinstance(data, list):
            for item in data:
                yield item
        elif isinstance(data, dict):
            yield data

    def parse_posts_streaming(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """Parse posts with streaming optimization."""
        data = self.parse_file(file_path)

        if isinstance(data, dict):
            # Handle different post data structures
            posts_data = data
            if "posts" in data:
                posts_data = data["posts"]
            elif "data" in data:
                posts_data = data["data"]
            elif "items" in data:
                posts_data = data["items"]

            if isinstance(posts_data, list):
                yield from posts_data
        else:
            # Iterator from streaming parser
            yield from data

    def parse_stories_streaming(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """Parse stories with streaming optimization."""
        data = self.parse_file(file_path)

        if isinstance(data, dict):
            # Handle different story data structures
            stories_data = data
            if "stories" in data:
                stories_data = data["stories"]
            elif "data" in data:
                stories_data = data["data"]
            elif "items" in data:
                stories_data = data["items"]

            if isinstance(stories_data, list):
                yield from stories_data
        else:
            # Iterator from streaming parser
            yield from data

    def parse_reels_streaming(self, file_path: Path) -> Iterator[Dict[str, Any]]:
        """Parse reels with streaming optimization."""
        data = self.parse_file(file_path)

        if isinstance(data, dict):
            # Handle different reel data structures
            reels_data = data
            if "reels" in data:
                reels_data = data["reels"]
            elif "data" in data:
                reels_data = data["data"]
            elif "items" in data:
                reels_data = data["items"]

            if isinstance(reels_data, list):
                yield from reels_data
        else:
            # Iterator from streaming parser
            yield from data


class BatchProcessor:
    """Process data in batches to optimize memory usage."""

    def __init__(self, batch_size: int = 1000, gc_frequency: int = 10):
        """Initialize batch processor.

        Args:
            batch_size: Number of items to process in each batch
            gc_frequency: How often to run garbage collection (every N batches)
        """
        self.batch_size = batch_size
        self.gc_frequency = gc_frequency
        self.batch_count = 0
        self.logger = logger
    
    def process_posts(self, data: Any) -> List[Any]:
        """Process posts data."""
        from ..parsers.json_parser import JSONParser
        parser = JSONParser()
        if isinstance(data, list):
            return parser.parse_posts(data)
        elif isinstance(data, dict):
            return parser.parse_posts([data])
        return []
    
    def process_stories(self, data: Any) -> List[Any]:
        """Process stories data."""
        from ..parsers.json_parser import JSONParser
        parser = JSONParser()
        if isinstance(data, list):
            return parser.parse_stories(data)
        elif isinstance(data, dict):
            return parser.parse_stories([data])
        return []

    def process_in_batches(self, items: Iterator[Any], processor_func: Any) -> Iterator[Any]:
        """Process items in batches with memory management.

        Args:
            items: Iterator of items to process
            processor_func: Function to process each item

        Yields:
            Processed items
        """
        batch = []

        for item in items:
            batch.append(item)

            if len(batch) >= self.batch_size:
                # Process batch
                yield from self._process_batch(batch, processor_func)

                # Clear batch and manage memory
                batch.clear()
                self.batch_count += 1

                if self.batch_count % self.gc_frequency == 0:
                    gc.collect()
                    self.logger.debug(
                        f"Processed {self.batch_count} batches, garbage collected"
                    )

        # Process remaining items
        if batch:
            yield from self._process_batch(batch, processor_func)

    def _process_batch(self, batch: List[Any], processor_func: Any) -> List[Any]:
        """Process a single batch of items."""
        processed = []
        for item in batch:
            try:
                result = processor_func(item)
                if result is not None:
                    processed.append(result)
            except Exception as e:
                self.logger.debug(f"Failed to process item: {e}")
                continue
        return processed


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes."""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except Exception:
        return 0.0


def should_use_streaming(file_path: Path, memory_threshold: int) -> bool:
    """Determine if streaming should be used based on file size."""
    try:
        file_size = file_path.stat().st_size
        return file_size > memory_threshold
    except OSError:
        return False
