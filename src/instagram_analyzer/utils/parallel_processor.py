"""Parallel processing utilities for Instagram data analysis.

This module provides parallel processing capabilities for CPU-intensive tasks
such as JSON parsing, data analysis, and file processing.
"""

import asyncio
import concurrent.futures
import os
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from ..logging_config import get_logger

logger = get_logger("parallel_processor")
console = Console()


class ParallelProcessor:
    """Handles parallel processing of Instagram data files and operations."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker threads/processes.
                        If None, uses CPU count.
        """
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.logger = logger

        # Progress tracking
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="green"),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            TextColumn("•"),
            TimeRemainingColumn(),
            console=console,
        )

    def process_files_parallel(
        self,
        files: list[Path],
        processor_func: Callable[[Path], Any],
        description: str = "Processing files",
        show_progress: bool = True,
    ) -> list[Any]:
        """Process multiple files in parallel with optional progress display.

        Args:
            files: List of file paths to process
            processor_func: Function to process each file
            description: Description for progress bar
            show_progress: Whether to show progress bar

        Returns:
            List of results from processing each file
        """
        if not files:
            return []

        results = []

        if show_progress:
            with self.progress:
                task = self.progress.add_task(description, total=len(files))

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.max_workers
                ) as executor:
                    # Submit all tasks
                    future_to_file = {
                        executor.submit(processor_func, file_path): file_path
                        for file_path in files
                    }

                    # Collect results as they complete
                    for future in concurrent.futures.as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            result = future.result()
                            results.append(result)
                            self.logger.debug(f"Processed {file_path}")
                        except Exception as e:
                            self.logger.error(f"Error processing {file_path}: {e}")
                            results.append(None)
                        finally:
                            self.progress.update(task, advance=1)
        else:
            # Process without progress bar
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            ) as executor:
                future_to_file = {
                    executor.submit(processor_func, file_path): file_path
                    for file_path in files
                }

                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
                        results.append(None)

        return results

    def process_data_parallel(
        self,
        data_items: list[Any],
        processor_func: Callable[[Any], Any],
        description: str = "Processing data",
        show_progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> list[Any]:
        """Process data items in parallel with optional progress display.

        Args:
            data_items: List of data items to process
            processor_func: Function to process each item
            description: Description for progress bar
            show_progress: Whether to show progress bar
            chunk_size: Size of chunks for batch processing

        Returns:
            List of results from processing each item
        """
        if not data_items:
            return []

        # Determine chunk size if not provided
        if chunk_size is None:
            chunk_size = max(1, len(data_items) // (self.max_workers * 4))

        results = []

        if show_progress:
            with self.progress:
                task = self.progress.add_task(description, total=len(data_items))

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.max_workers
                ) as executor:
                    # Submit tasks in chunks
                    futures = []
                    for i in range(0, len(data_items), chunk_size):
                        chunk = data_items[i : i + chunk_size]
                        future = executor.submit(
                            self._process_chunk, chunk, processor_func
                        )
                        futures.append(future)

                    # Collect results
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            chunk_results = future.result()
                            results.extend(chunk_results)
                            self.progress.update(task, advance=len(chunk_results))
                        except Exception as e:
                            self.logger.error(f"Error processing chunk: {e}")
        else:
            # Process without progress bar
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            ) as executor:
                futures = []
                for i in range(0, len(data_items), chunk_size):
                    chunk = data_items[i : i + chunk_size]
                    future = executor.submit(self._process_chunk, chunk, processor_func)
                    futures.append(future)

                for future in concurrent.futures.as_completed(futures):
                    try:
                        chunk_results = future.result()
                        results.extend(chunk_results)
                    except Exception as e:
                        self.logger.error(f"Error processing chunk: {e}")

        return results

    def _process_chunk(
        self, chunk: list[Any], processor_func: Callable[[Any], Any]
    ) -> list[Any]:
        """Process a chunk of data items sequentially.

        Args:
            chunk: List of data items to process
            processor_func: Function to process each item

        Returns:
            List of results from processing the chunk
        """
        results = []
        for item in chunk:
            try:
                result = processor_func(item)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing item: {e}")
                results.append(None)
        return results

    async def process_files_async(
        self,
        files: list[Path],
        processor_func: Callable[[Path], Any],
        description: str = "Processing files",
        show_progress: bool = True,
    ) -> list[Any]:
        """Process multiple files asynchronously.

        Args:
            files: List of file paths to process
            processor_func: Function to process each file
            description: Description for progress bar
            show_progress: Whether to show progress bar

        Returns:
            List of results from processing each file
        """
        if not files:
            return []

        loop = asyncio.get_event_loop()

        # Convert sync function to async
        async def async_processor(file_path: Path) -> Any:
            return await loop.run_in_executor(None, processor_func, file_path)

        results = []

        if show_progress:
            with self.progress:
                task = self.progress.add_task(description, total=len(files))

                # Process files asynchronously
                semaphore = asyncio.Semaphore(self.max_workers)

                async def process_with_semaphore(file_path: Path) -> Any:
                    async with semaphore:
                        try:
                            result = await async_processor(file_path)
                            self.logger.debug(f"Processed {file_path}")
                            return result
                        except Exception as e:
                            self.logger.error(f"Error processing {file_path}: {e}")
                            return None
                        finally:
                            self.progress.update(task, advance=1)

                # Execute all tasks
                tasks = [process_with_semaphore(file_path) for file_path in files]
                results = await asyncio.gather(*tasks)
        else:
            # Process without progress bar
            semaphore = asyncio.Semaphore(self.max_workers)

            async def process_with_semaphore(file_path: Path) -> Any:
                async with semaphore:
                    try:
                        result = await async_processor(file_path)
                        return result
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
                        return None

            tasks = [process_with_semaphore(file_path) for file_path in files]
            results = await asyncio.gather(*tasks)

        return results


class BatchProcessor:
    """Handles batch processing of data with memory management."""

    def __init__(self, batch_size: int = 1000, memory_threshold: int = 100 * 1024 * 1024):
        """Initialize batch processor.

        Args:
            batch_size: Number of items to process in each batch
            memory_threshold: Memory threshold for triggering garbage collection
        """
        self.batch_size = batch_size
        self.memory_threshold = memory_threshold
        self.logger = logger

    def process_in_batches(
        self,
        data_items: list[Any],
        processor_func: Callable[[list[Any]], list[Any]],
        description: str = "Processing batches",
        show_progress: bool = True,
    ) -> list[Any]:
        """Process data in batches with memory management.

        Args:
            data_items: List of data items to process
            processor_func: Function to process each batch
            description: Description for progress bar
            show_progress: Whether to show progress bar

        Returns:
            List of all results from processing batches
        """
        if not data_items:
            return []

        results = []
        num_batches = (len(data_items) + self.batch_size - 1) // self.batch_size

        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(complete_style="green", finished_style="green"),
                MofNCompleteColumn(),
                TaskProgressColumn(),
                TextColumn("•"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(description, total=num_batches)

                for i in range(0, len(data_items), self.batch_size):
                    batch = data_items[i : i + self.batch_size]

                    try:
                        batch_results = processor_func(batch)
                        results.extend(batch_results)
                        self.logger.debug(
                            f"Processed batch {i//self.batch_size + 1}/{num_batches}"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error processing batch {i//self.batch_size + 1}: {e}"
                        )
                    finally:
                        progress.update(task, advance=1)

                        # Memory management
                        if i > 0 and i % (self.batch_size * 10) == 0:
                            import gc

                            gc.collect()
        else:
            # Process without progress bar
            for i in range(0, len(data_items), self.batch_size):
                batch = data_items[i : i + self.batch_size]

                try:
                    batch_results = processor_func(batch)
                    results.extend(batch_results)
                except Exception as e:
                    self.logger.error(
                        f"Error processing batch {i//self.batch_size + 1}: {e}"
                    )

        return results


def create_parallel_processor(max_workers: Optional[int] = None) -> ParallelProcessor:
    """Create a parallel processor instance.

    Args:
        max_workers: Maximum number of worker threads

    Returns:
        Configured ParallelProcessor instance
    """
    return ParallelProcessor(max_workers=max_workers)


def create_batch_processor(
    batch_size: int = 1000, memory_threshold: int = 100 * 1024 * 1024
) -> BatchProcessor:
    """Create a batch processor instance.

    Args:
        batch_size: Number of items per batch
        memory_threshold: Memory threshold for GC

    Returns:
        Configured BatchProcessor instance
    """
    return BatchProcessor(batch_size=batch_size, memory_threshold=memory_threshold)
