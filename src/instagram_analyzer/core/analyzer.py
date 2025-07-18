"""Core Instagram data analyzer.

This module contains the main InstagramAnalyzer class that orchestrates the entire
analysis pipeline for Instagram data exports. It provides a high-level interface
for loading, parsing, analyzing, and exporting Instagram data.

The analyzer supports:
- Full and partial Instagram data exports
- Multiple content types (posts, stories, reels, conversations)
- Various analysis types (basic stats, temporal patterns, engagement metrics)
- Multiple export formats (JSON, HTML, PDF)
- Data validation and error recovery
- Privacy-preserving anonymization

Example:
    Basic usage:

    >>> analyzer = InstagramAnalyzer("/path/to/instagram/export")
    >>> analyzer.load_data()
    >>> results = analyzer.analyze()
    >>> analyzer.export_html("/path/to/output")

    Advanced usage with options:

    >>> analyzer = InstagramAnalyzer("/path/to/export")
    >>> analyzer.load_data()
    >>> validation = analyzer.validate_data()
    >>> if validation["data_loaded"]["valid"]:
    ...     results = analyzer.analyze(include_media=True)
    ...     analyzer.export_json("/output", anonymize=True)

Classes:
    InstagramAnalyzer: Main analyzer class for Instagram data processing

Dependencies:
    - parsers: For data parsing and validation
    - analyzers: For statistical analysis and pattern detection
    - exporters: For report generation
    - models: For data structure definitions
"""

import gc
import html
import json
import weakref
from collections.abc import Generator, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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

from ..analyzers import BasicStatsAnalyzer, TemporalAnalyzer
from ..cache import CacheConfig, CacheManager, cached_analysis, cached_parsing
from ..exceptions import (
    AnalysisError,
    DataNotFoundError,
    InsufficientDataError,
    InvalidDataFormatError,
)
from ..logging_config import create_operation_logger, get_logger
from ..ml import EngagementPredictor, FeatureEngineer, SentimentAnalyzer
from ..models import Media, Post, Profile, Reel, Story, StoryInteraction, User
from ..parsers import DataDetector, JSONParser
from ..parsers.engagement_parser import EngagementParser
from ..parsers.parallel_json_parser import ParallelJSONParser
from ..utils import safe_json_load, validate_path
from ..utils.memory_profiler import force_gc_if_needed, log_memory_usage, memory_profile


class InstagramAnalyzer:
    """Main analyzer class for Instagram data."""

    def __init__(
        self,
        data_path: Path,
        lazy_loading: bool = True,
        enable_parallel: bool = True,
        max_workers: Optional[int] = None,
        show_progress: bool = True,
    ):
        """Initialize analyzer with data path.

        Args:
            data_path: Path to Instagram data export directory
            lazy_loading: If True, use lazy loading for memory efficiency
            enable_parallel: If True, enable parallel processing
            max_workers: Maximum number of worker threads
            show_progress: Whether to show progress bars

        Raises:
            DataNotFoundError: If data path doesn't exist or is invalid
        """
        self.data_path = Path(data_path)
        self._profile: Optional[Profile] = None
        self.lazy_loading = lazy_loading
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers
        self.show_progress = show_progress

        # Data structure storage
        self._data_structure: Optional[dict[str, Any]] = None
        self._engagement_data: Optional[dict[str, Any]] = None

        # For lazy loading mode
        if lazy_loading:
            self._posts_cache: Optional[list[Post]] = None
            self._stories_cache: Optional[list[Story]] = None
            self._reels_cache: Optional[list[Reel]] = None
            self._archived_posts_cache: Optional[list[Post]] = None
            self._recently_deleted_cache: Optional[list[Media]] = None
            self._story_interactions_cache: Optional[list[StoryInteraction]] = None
        else:
            # Legacy mode - keep everything in memory
            self._posts_list: list[Post] = []
            self._stories_list: list[Story] = []
            self._reels_list: list[Reel] = []
            self._archived_posts_list: list[Post] = []
            self._recently_deleted_list: list[Media] = []
            self._story_interactions_list: list[StoryInteraction] = []

        # Setup logging
        self.logger = get_logger("core.analyzer")
        self.logger.info(
            f"Initializing InstagramAnalyzer with data path: {self.data_path}"
        )

        # Setup Rich console and progress
        self.console = Console()
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
            console=self.console,
        )

        # Analyzers
        self.basic_stats = BasicStatsAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()

        # ML Components
        self.sentiment_analyzer = SentimentAnalyzer(
            model_type="textblob", include_emotions=True
        )
        self.engagement_predictor = EngagementPredictor(algorithm="random_forest")
        self.feature_engineer = FeatureEngineer(include_derived=True)

        # Data detection
        self.detector = DataDetector()

        # Initialize parsers (parallel or standard)
        if enable_parallel:
            self.parser = ParallelJSONParser(
                max_workers=max_workers,
                enable_parallel=enable_parallel,
                show_progress=show_progress,
            )
        else:
            self.parser = JSONParser()

        self.engagement_parser = EngagementParser()

        # Validation
        if not validate_path(self.data_path):
            error_msg = f"Invalid data path: {self.data_path}"
            self.logger.error(error_msg)
            raise DataNotFoundError(str(self.data_path), error_msg)

    def load_data_parallel(self, batch_size: int = 1000) -> None:
        """Load and parse Instagram data using parallel processing.

        Args:
            batch_size: Batch size for parallel processing

        Raises:
            InvalidDataFormatError: If data structure is invalid
            DataNotFoundError: If required data files are missing
        """
        if not self.enable_parallel:
            self.logger.warning(
                "Parallel processing is disabled, falling back to standard loading"
            )
            return self.load_data()

        with memory_profile("load_data_parallel") as profiler:
            with create_operation_logger(
                "load_data_parallel",
                {"data_path": str(self.data_path), "batch_size": batch_size},
            ) as op_logger:
                try:
                    # Detect data structure
                    op_logger.progress("Detecting data structure...")
                    profiler.take_snapshot("detect_structure")
                    data_structure = self.detector.detect_structure(self.data_path)

                    if not data_structure["is_valid"]:
                        error_msg = "Invalid Instagram data export structure"
                        self.logger.error(
                            error_msg, extra={"data_structure": data_structure}
                        )
                        raise InvalidDataFormatError(
                            str(self.data_path),
                            "Instagram JSON export",
                            error_msg,
                            {"data_structure": data_structure},
                        )

                    self.logger.info(
                        f"Detected {data_structure['export_type']} export with {data_structure['total_files']} files"
                    )

                    # Store data structure for lazy loading
                    self._data_structure = data_structure

                    # Load profile data (always loaded immediately)
                    op_logger.progress("Loading profile data...")
                    profiler.take_snapshot("load_profile")
                    self._load_profile(data_structure)

                    # Load engagement data
                    op_logger.progress("Loading engagement data...")
                    profiler.take_snapshot("load_engagement")
                    self._load_engagement_data(data_structure)

                    if self.lazy_loading:
                        # In lazy mode, just validate files exist and get counts
                        op_logger.progress("Validating data files...")
                        profiler.take_snapshot("validate_files")
                        self._validate_data_files(data_structure)

                        # Log that data is ready for lazy loading
                        self.logger.info(
                            "Data structure validated, ready for lazy loading with parallel processing"
                        )
                    else:
                        # Load all data immediately using parallel processing
                        op_logger.progress("Loading all data with parallel processing...")
                        profiler.take_snapshot("load_all_parallel")
                        self._load_all_data_parallel(data_structure, batch_size)

                    op_logger.complete(
                        "Data loaded successfully with parallel processing"
                    )

                except Exception as e:
                    self.logger.error(f"Error loading data: {e}")
                    raise

    @property
    def profile(self) -> Optional[Profile]:
        """Get profile with lazy loading support."""
        if self.lazy_loading:
            if self._profile is None:
                self._profile = self._load_profile_lazy()
            return self._profile
        else:
            return self._profile

    @profile.setter
    def profile(self, value: Optional[Profile]) -> None:
        """Set profile (for backward compatibility)."""
        self._profile = value

    @property
    def posts(self) -> list[Post]:
        """Get posts with lazy loading support."""
        if self.lazy_loading:
            if self._posts_cache is None:
                self._posts_cache = self._load_posts_lazy()
            return self._posts_cache
        else:
            return self._posts_list

    @posts.setter
    def posts(self, value: list[Post]) -> None:
        """Set posts (for backward compatibility)."""
        if self.lazy_loading:
            self._posts_cache = value
        else:
            self._posts_list = value

    @property
    def stories(self) -> list[Story]:
        """Get stories with lazy loading support."""
        if self.lazy_loading:
            if self._stories_cache is None:
                self._stories_cache = self._load_stories_lazy()
            return self._stories_cache
        else:
            return self._stories_list

    @stories.setter
    def stories(self, value: list[Story]) -> None:
        """Set stories (for backward compatibility)."""
        if self.lazy_loading:
            self._stories_cache = value
        else:
            self._stories_list = value

    @property
    def reels(self) -> list[Reel]:
        """Get reels with lazy loading support."""
        if self.lazy_loading:
            if self._reels_cache is None:
                self._reels_cache = self._load_reels_lazy()
            return self._reels_cache
        else:
            return self._reels_list

    @reels.setter
    def reels(self, value: list[Reel]) -> None:
        """Set reels (for backward compatibility)."""
        if self.lazy_loading:
            self._reels_cache = value
        else:
            self._reels_list = value

    @property
    def archived_posts(self) -> list[Post]:
        """Get archived posts with lazy loading support."""
        if self.lazy_loading:
            if self._archived_posts_cache is None:
                self._archived_posts_cache = self._load_archived_posts_lazy()
            return self._archived_posts_cache
        else:
            return self._archived_posts_list

    @property
    def recently_deleted(self) -> list[Media]:
        """Get recently deleted media with lazy loading support."""
        if self.lazy_loading:
            if self._recently_deleted_cache is None:
                self._recently_deleted_cache = self._load_recently_deleted_lazy()
            return self._recently_deleted_cache
        else:
            return self._recently_deleted_list

    @property
    def story_interactions(self) -> list[StoryInteraction]:
        """Get story interactions with lazy loading support."""
        if self.lazy_loading:
            if self._story_interactions_cache is None:
                self._story_interactions_cache = self._load_story_interactions_lazy()
            return self._story_interactions_cache
        else:
            return self._story_interactions_list

    def load_data(self) -> None:
        """Load and parse Instagram data from export.

        Raises:
            InvalidDataFormatError: If data structure is invalid
            DataNotFoundError: If required data files are missing
        """
        with memory_profile("load_data") as profiler:
            with create_operation_logger(
                "load_data", {"data_path": str(self.data_path)}
            ) as op_logger:
                try:
                    # Detect data structure
                    op_logger.progress("Detecting data structure...")
                    profiler.take_snapshot("detect_structure")
                    data_structure = self.detector.detect_structure(self.data_path)

                    if not data_structure["is_valid"]:
                        error_msg = "Invalid Instagram data export structure"
                        self.logger.error(
                            error_msg, extra={"data_structure": data_structure}
                        )
                        raise InvalidDataFormatError(
                            str(self.data_path),
                            "Instagram JSON export",
                            error_msg,
                            {"data_structure": data_structure},
                        )

                    self.logger.info(
                        f"Detected {data_structure['export_type']} export with {data_structure['total_files']} files"
                    )

                    # Store data structure for lazy loading
                    self._data_structure = data_structure

                    # Load profile data (always loaded immediately)
                    op_logger.progress("Loading profile data...")
                    profiler.take_snapshot("load_profile")
                    self._load_profile(data_structure)

                    # Load engagement data
                    op_logger.progress("Loading engagement data...")
                    profiler.take_snapshot("load_engagement")
                    self._load_engagement_data(data_structure)

                    if self.lazy_loading:
                        # In lazy mode, just validate files exist and get counts
                        op_logger.progress("Validating data files...")
                        profiler.take_snapshot("validate_files")
                        posts_count = self._count_content_files(
                            data_structure, "post_files"
                        )
                        stories_count = self._count_content_files(
                            data_structure, "story_files"
                        )
                        reels_count = self._count_content_files(
                            data_structure, "reel_files"
                        )
                        archived_count = self._count_content_files(
                            data_structure, "archived_post_files"
                        )
                        deleted_count = self._count_content_files(
                            data_structure, "recently_deleted_files"
                        )
                        interactions_count = self._count_story_interactions(
                            data_structure
                        )

                        total_content = posts_count + stories_count + reels_count
                        op_logger.complete(
                            f"Successfully validated {total_content} content items (lazy loading enabled)",
                            {
                                "posts_count": posts_count,
                                "stories_count": stories_count,
                                "reels_count": reels_count,
                                "archived_count": archived_count,
                                "deleted_count": deleted_count,
                                "interactions_count": interactions_count,
                                "profile_loaded": self.profile is not None,
                                "lazy_loading": True,
                            },
                        )
                    else:
                        # Load content data immediately
                        op_logger.progress("Loading posts...")
                        profiler.take_snapshot("load_posts")
                        self._load_posts(data_structure)

                        op_logger.progress("Loading stories...")
                        profiler.take_snapshot("load_stories")
                        self._load_stories(data_structure)

                        op_logger.progress("Loading reels...")
                        profiler.take_snapshot("load_reels")
                        self._load_reels(data_structure)

                        total_content = (
                            len(self.posts) + len(self.stories) + len(self.reels)
                        )
                        op_logger.complete(
                            f"Successfully loaded {total_content} content items",
                            {
                                "posts_count": len(self.posts),
                                "stories_count": len(self.stories),
                                "reels_count": len(self.reels),
                                "profile_loaded": self.profile is not None,
                                "lazy_loading": False,
                            },
                        )

                    # Check memory usage and force GC if needed
                    force_gc_if_needed(threshold_percent=70.0)

                except Exception as e:
                    self.logger.error(f"Failed to load data: {e}", exc_info=True)
                    raise

    def _load_profile(self, structure: dict[str, Any]) -> None:
        """Load profile information."""
        profile_files = structure.get("profile_files", [])

        for file_path in profile_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    self._profile = self.parser.parse_profile(data)
                    break
            except Exception:
                continue

    def _load_posts(self, structure: dict[str, Any]) -> None:
        """Load posts data."""
        post_files = structure.get("post_files", [])

        for file_path in post_files:
            try:
                # Use streaming parser for memory efficiency
                posts = self.parser.parse_posts_from_file(str(file_path))

                # Enrich posts with engagement data
                if self._engagement_data:
                    posts = self.parser.enrich_posts_with_engagement(
                        posts, self._engagement_data
                    )

                if self.lazy_loading:
                    if self._posts_cache is None:
                        self._posts_cache = []
                    self._posts_cache.extend(posts)
                else:
                    self._posts_list.extend(posts)
            except Exception:
                continue

    def _load_stories(self, structure: dict[str, Any]) -> None:
        """Load stories data."""
        story_files = structure.get("story_files", [])

        for file_path in story_files:
            try:
                # Use streaming parser for memory efficiency
                stories = self.parser.parse_stories_from_file(str(file_path))

                if self.lazy_loading:
                    if self._stories_cache is None:
                        self._stories_cache = []
                    self._stories_cache.extend(stories)
                else:
                    self._stories_list.extend(stories)
            except Exception:
                import traceback

                traceback.print_exc()
                continue

    def _load_reels(self, structure: dict[str, Any]) -> None:
        """Load reels data."""
        reel_files = structure.get("reel_files", [])

        for file_path in reel_files:
            try:
                # Use streaming parser for memory efficiency
                reels = self.parser.parse_reels_from_file(str(file_path))

                # Enrich reels with engagement data
                if self._engagement_data:
                    reels = self._enrich_reels_with_engagement(
                        reels, self._engagement_data
                    )

                if self.lazy_loading:
                    if self._reels_cache is None:
                        self._reels_cache = []
                    self._reels_cache.extend(reels)
                else:
                    self._reels_list.extend(reels)
            except Exception:
                continue

    def _load_engagement_data(self, structure: dict[str, Any]) -> None:
        """Load engagement data from separate files."""
        engagement_files = structure.get("engagement_files", {})

        if not engagement_files:
            self.logger.warning("No engagement files found in data structure")
            self._engagement_data = {}
            return

        try:
            self._engagement_data = self.engagement_parser.parse_engagement_files(
                engagement_files
            )
            self.logger.info(
                f"Loaded engagement data: {len(self._engagement_data.get('liked_posts', {}))} liked posts, "
                f"{len(self._engagement_data.get('post_comments', {}))} post comment threads"
            )
        except Exception as e:
            self.logger.error(f"Failed to load engagement data: {e}", exc_info=True)
            self._engagement_data = {}

    def _load_all_data_parallel(self, structure: dict[str, Any], batch_size: int) -> None:
        """Load all data using parallel processing for improved performance.

        Args:
            structure: Detected data structure
            batch_size: Batch size for parallel processing
        """
        try:
            # Load posts in parallel
            if structure.get("posts"):
                self.logger.info(
                    f"Loading {len(structure['posts'])} post files in parallel..."
                )
                self._posts_list = []
                for file_path in structure["posts"]:
                    try:
                        data = safe_json_load(file_path)
                        if data:
                            posts = self.parser.parse_posts_parallel(data)
                            self._posts_list.extend(posts)
                    except Exception as e:
                        self.logger.error(f"Error loading posts from {file_path}: {e}")
                        continue

                self.logger.info(
                    f"Loaded {len(self._posts_list)} posts using parallel processing"
                )

            # Load stories in parallel
            if structure.get("stories"):
                self.logger.info(
                    f"Loading {len(structure['stories'])} story files in parallel..."
                )
                self._stories_list = []
                for file_path in structure["stories"]:
                    try:
                        data = safe_json_load(file_path)
                        if data:
                            stories = self.parser.parse_stories_parallel(data)
                            self._stories_list.extend(stories)
                    except Exception as e:
                        self.logger.error(f"Error loading stories from {file_path}: {e}")
                        continue

                self.logger.info(
                    f"Loaded {len(self._stories_list)} stories using parallel processing"
                )

            # Load reels in parallel
            if structure.get("reels"):
                self.logger.info(
                    f"Loading {len(structure['reels'])} reel files in parallel..."
                )
                self._reels_list = []
                for file_path in structure["reels"]:
                    try:
                        data = safe_json_load(file_path)
                        if data:
                            reels = self.parser.parse_reels_parallel(data)
                            self._reels_list.extend(reels)
                    except Exception as e:
                        self.logger.error(f"Error loading reels from {file_path}: {e}")
                        continue

                self.logger.info(
                    f"Loaded {len(self._reels_list)} reels using parallel processing"
                )

            # Load archived posts in parallel
            if structure.get("archived_posts"):
                self.logger.info(
                    f"Loading {len(structure['archived_posts'])} archived post files in parallel..."
                )
                self._archived_posts_list = []
                for file_path in structure["archived_posts"]:
                    try:
                        data = safe_json_load(file_path)
                        if data:
                            archived_posts = self.parser.parse_archived_posts(data)
                            self._archived_posts_list.extend(archived_posts)
                    except Exception as e:
                        self.logger.error(
                            f"Error loading archived posts from {file_path}: {e}"
                        )
                        continue

                self.logger.info(
                    f"Loaded {len(self._archived_posts_list)} archived posts using parallel processing"
                )

            # Load recently deleted media in parallel
            if structure.get("recently_deleted"):
                self.logger.info(
                    f"Loading {len(structure['recently_deleted'])} recently deleted files in parallel..."
                )
                self._recently_deleted_list = []
                for file_path in structure["recently_deleted"]:
                    try:
                        data = safe_json_load(file_path)
                        if data:
                            deleted_media = self.parser.parse_recently_deleted(data)
                            self._recently_deleted_list.extend(deleted_media)
                    except Exception as e:
                        self.logger.error(
                            f"Error loading recently deleted from {file_path}: {e}"
                        )
                        continue

                self.logger.info(
                    f"Loaded {len(self._recently_deleted_list)} recently deleted items using parallel processing"
                )

            # Load story interactions in parallel
            if structure.get("story_interaction_files"):
                self.logger.info("Loading story interactions in parallel...")
                self._story_interactions_list = []
                for interaction_type, files in structure[
                    "story_interaction_files"
                ].items():
                    for file_path in files:
                        try:
                            data = safe_json_load(file_path)
                            if data:
                                interactions = self.parser.parse_story_interactions(
                                    data, interaction_type
                                )
                                self._story_interactions_list.extend(interactions)
                        except Exception as e:
                            self.logger.error(
                                f"Error loading story interactions from {file_path}: {e}"
                            )
                            continue

                self.logger.info(
                    f"Loaded {len(self._story_interactions_list)} story interactions using parallel processing"
                )

            # Enrich posts with engagement data if available
            if self._engagement_data and hasattr(self, "_posts_list"):
                self.logger.info("Enriching posts with engagement data...")
                try:
                    self._posts_list = self.parser.enrich_posts_with_engagement(
                        self._posts_list, self._engagement_data
                    )
                    self.logger.info("Successfully enriched posts with engagement data")
                except Exception as e:
                    self.logger.error(f"Error enriching posts with engagement data: {e}")

            # Force garbage collection after loading all data
            force_gc_if_needed()

        except Exception as e:
            self.logger.error(f"Error in parallel data loading: {e}", exc_info=True)
            raise

    def _validate_data_files(self, structure: dict[str, Any]) -> None:
        """Validate that data files exist and are accessible.

        Args:
            structure: Detected data structure

        Raises:
            DataNotFoundError: If critical data files are missing
        """
        missing_files = []

        # Check profile files
        profile_files = structure.get("profile_files", [])
        for file_path in profile_files:
            if not Path(file_path).exists():
                missing_files.append(str(file_path))

        # Check content files
        for content_type in [
            "posts",
            "stories",
            "reels",
            "archived_posts",
            "recently_deleted",
        ]:
            files = structure.get(content_type, [])
            for file_path in files:
                if not Path(file_path).exists():
                    missing_files.append(str(file_path))

        # Check story interaction files
        interaction_files = structure.get("story_interaction_files", {})
        for interaction_type, files in interaction_files.items():
            for file_path in files:
                if not Path(file_path).exists():
                    missing_files.append(str(file_path))

        if missing_files:
            error_msg = f"Missing {len(missing_files)} data files"
            self.logger.error(
                error_msg, extra={"missing_files": missing_files[:10]}
            )  # Log first 10
            raise DataNotFoundError(
                str(self.data_path),
                f"{error_msg}: {', '.join(missing_files[:5])}"
                + ("..." if len(missing_files) > 5 else ""),
            )

        self.logger.info(
            f"All data files validated successfully ({structure.get('total_files', 0)} files)"
        )

    def _count_content_files(self, structure: dict[str, Any], content_type: str) -> int:
        """Count items in content files without loading them."""
        files = structure.get(content_type, [])
        count = 0
        for file_path in files:
            try:
                data = safe_json_load(file_path)
                if not data:
                    continue

                # Handle both list-based and dictionary-based JSON structures
                if isinstance(data, list):
                    count += len(data)
                elif isinstance(data, dict):
                    # Look for common keys that hold the list of items
                    for key in [
                        "posts",
                        "stories",
                        "reels",
                        "archived_posts",
                        "deleted_content",
                        "ig_stories",
                    ]:
                        if key in data and isinstance(data[key], list):
                            count += len(data[key])
                            break  # Assume only one key contains the data
            except Exception:
                continue
        return count

    def _count_story_interactions(self, structure: dict[str, Any]) -> int:
        """Count story interactions in files without loading them."""
        interaction_files = structure.get("story_interaction_files", {})
        count = 0
        for interaction_type, files in interaction_files.items():
            for file_path in files:
                try:
                    data = safe_json_load(file_path)
                    if not data:
                        continue

                    # Interactions can be in various structures
                    if isinstance(data, list):
                        count += len(data)
                    elif isinstance(data, dict):
                        # Look for common keys that hold the list of items
                        for key in ["story_activities", "interactions"]:
                            if key in data and isinstance(data[key], list):
                                count += len(data[key])
                                break
                except Exception:
                    continue
        return count

    def _ensure_data_structure(self) -> None:
        """Ensure data structure is detected and available for lazy loading."""
        if self._data_structure is None:
            try:
                self.logger.info("Auto-detecting data structure for lazy loading...")
                self._data_structure = self.detector.detect_structure(self.data_path)
                if not self._data_structure["is_valid"]:
                    self.logger.warning(
                        f"Invalid data structure detected: {self._data_structure}"
                    )
                    self._data_structure = None
                else:
                    self.logger.info(
                        f"Auto-detected {self._data_structure['export_type']} export with {self._data_structure['total_files']} files"
                    )
            except Exception as e:
                self.logger.error(f"Failed to auto-detect data structure: {e}")
                self._data_structure = None

    def _load_profile_lazy(self) -> Optional[Profile]:
        """Load profile using lazy loading."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return None

        profile_files = self._data_structure.get("profile_files", [])
        if not profile_files:
            return None

        # Try to parse profile from first available file
        for file_path in profile_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    profile = self.parser.parse_profile(data)
                    self.logger.info(f"Lazy loaded profile from: {file_path}")
                    return profile
            except Exception as e:
                self.logger.warning(f"Could not parse profile file {file_path}: {e}")
                continue

        return None

    def _load_posts_lazy(self) -> list[Post]:
        """Load posts using lazy loading with streaming optimization."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        posts = []
        with create_operation_logger(
            "lazy_load_posts", {"data_path": str(self.data_path)}
        ) as op_logger:
            post_files = self._data_structure.get("post_files", [])

            for file_path in post_files:
                try:
                    # Use streaming parser for memory efficiency
                    file_posts = self.parser.parse_posts_from_file(Path(file_path))
                    posts.extend(file_posts)
                except Exception as e:
                    self.logger.warning(f"Could not parse post file {file_path}: {e}")
                    continue

            op_logger.complete(f"Lazy loaded {len(posts)} posts")

        # Enrich posts with engagement data
        if self._engagement_data:
            try:
                posts = self.parser.enrich_posts_with_engagement(
                    posts, self._engagement_data
                )
            except Exception as e:
                self.logger.warning(f"Could not enrich posts with engagement data: {e}")

        return posts

    def _load_stories_lazy(self) -> list[Story]:
        """Load stories using lazy loading with streaming optimization."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        files = self._data_structure.get("story_files", [])

        stories = []
        for file_path in files:
            try:
                # Use streaming parser for memory efficiency
                parsed_stories = self.parser.parse_stories_from_file(str(file_path))
                stories.extend(parsed_stories)
            except Exception as e:
                self.logger.warning(f"Could not parse story file {file_path}: {e}")

        return stories

    def _load_reels_lazy(self) -> list[Reel]:
        """Load reels using lazy loading with streaming optimization."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        files = self._data_structure.get("reel_files", [])

        reels = []
        for file_path in files:
            try:
                # Use streaming parser for memory efficiency
                reels.extend(self.parser.parse_reels_from_file(str(file_path)))
            except Exception as e:
                self.logger.warning(f"Could not parse reel file {file_path}: {e}")

        # Enrich reels with engagement data
        if self._engagement_data:
            reels = self._enrich_reels_with_engagement(reels, self._engagement_data)

        return reels

    def _load_archived_posts_lazy(self) -> list[Post]:
        """Load archived posts using lazy loading."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        archived_posts = []
        files = self._data_structure.get("archived_post_files", [])
        for file_path in files:
            try:
                archived_posts.extend(
                    self.parser.parse_archived_posts_from_file(str(file_path))
                )
            except Exception as e:
                self.logger.warning(
                    f"Could not parse archived post file {file_path}: {e}"
                )
        return archived_posts

    def _load_recently_deleted_lazy(self) -> list[Media]:
        """Load recently deleted media using lazy loading."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        deleted_media = []
        files = self._data_structure.get("recently_deleted_files", [])
        for file_path in files:
            try:
                deleted_media.extend(self.parser.parse_media_from_file(str(file_path)))
            except Exception as e:
                self.logger.warning(
                    f"Could not parse recently deleted file {file_path}: {e}"
                )
        return deleted_media

    def _load_story_interactions_lazy(self) -> list[StoryInteraction]:
        """Load story interactions using lazy loading."""
        if self._data_structure is None:
            self._ensure_data_structure()
            if self._data_structure is None:
                return []

        interactions = []
        files_dict = self._data_structure.get("story_interaction_files", {})
        for interaction_type, files in files_dict.items():
            for file_path in files:
                try:
                    interactions.extend(
                        self.parser.parse_story_interactions_from_file(
                            str(file_path), interaction_type
                        )
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Could not parse story interaction file {file_path}: {e}"
                    )
        return interactions

    def _enrich_reels_with_engagement(
        self, reels: list[Reel], engagement_data: dict[str, Any]
    ) -> list[Reel]:
        """Enrich reels with engagement data from separate files.

        Args:
            reels: List of reels to enrich
            engagement_data: Engagement data from EngagementParser

        Returns:
            List of enriched reels
        """
        if not engagement_data:
            return reels

        reel_comments = engagement_data.get("reel_comments", {})

        enriched_reels = []

        for reel in reels:
            # Create a copy to avoid modifying the original
            enriched_reel = reel

            # First, try to get engagement from raw_data if available
            likes_count = enriched_reel.likes_count
            comments_count = enriched_reel.comments_count

            if reel.raw_data:
                raw_data = reel.raw_data

                # Check if engagement data is already in raw_data
                if "like_count" in raw_data:
                    likes_count = raw_data.get("like_count", 0)
                if "comment_count" in raw_data:
                    comments_count = raw_data.get("comment_count", 0)

            # Try to match engagement data from separate files
            if reel.timestamp:
                # Look for comments with similar timestamps
                for url, comments_list in reel_comments.items():
                    for comment in comments_list:
                        if comment.get("datetime"):
                            time_diff = abs(
                                (reel.timestamp - comment["datetime"]).total_seconds()
                            )
                            if time_diff <= 3600:  # Within 1 hour
                                comments_count += 1

            # If we found engagement data, create a new reel with updated values
            if (
                likes_count != enriched_reel.likes_count
                or comments_count != enriched_reel.comments_count
            ):
                enriched_reel = reel.model_copy(
                    update={
                        "likes_count": likes_count,
                        "comments_count": comments_count,
                    }
                )

            enriched_reels.append(enriched_reel)

        return enriched_reels

    def clear_cache(self) -> None:
        """Clear cached data to free memory."""
        if self.lazy_loading:
            self._posts_cache = None
            self._stories_cache = None
            self._reels_cache = None
            self._archived_posts_cache = None
            self._recently_deleted_cache = None
            self._story_interactions_cache = None
            gc.collect()
            self.logger.info("Memory cache cleared")

    def analyze(
        self, include_media: bool = False, show_progress: bool = True
    ) -> dict[str, Any]:
        """Run comprehensive analysis on loaded data.

        Args:
            include_media: Whether to include media file analysis
            show_progress: Whether to show progress bars

        Returns:
            Dictionary containing analysis results
        """
        results = {}

        if show_progress:
            with self.progress:
                # Create main analysis task
                main_task = self.progress.add_task(
                    "Running comprehensive analysis", total=3
                )

                # Basic statistics
                self.progress.update(
                    main_task, description="Analyzing basic statistics..."
                )
                basic_stats = self.basic_stats.analyze(
                    posts=self.posts,
                    stories=self.stories,
                    reels=self.reels,
                    profile=self.profile,
                    archived_posts=self.archived_posts,
                    recently_deleted=self.recently_deleted,
                    story_interactions=self.story_interactions,
                )
                results.update(basic_stats)
                self.progress.update(main_task, advance=1)

                # Temporal analysis
                self.progress.update(
                    main_task, description="Analyzing temporal patterns..."
                )
                temporal_stats = self.temporal_analyzer.analyze(
                    posts=self.posts, stories=self.stories, reels=self.reels
                )
                results.update(temporal_stats)
                self.progress.update(main_task, advance=1)

                # Media analysis if requested
                if include_media:
                    self.progress.update(
                        main_task, description="Analyzing media content..."
                    )
                    # Add media analysis here if needed
                    pass

                self.progress.update(main_task, advance=1)
                self.progress.update(main_task, description="Analysis complete!")
        else:
            # Run without progress bars
            basic_stats = self.basic_stats.analyze(
                posts=self.posts,
                stories=self.stories,
                reels=self.reels,
                profile=self.profile,
                archived_posts=self.archived_posts,
                recently_deleted=self.recently_deleted,
                story_interactions=self.story_interactions,
            )
            results.update(basic_stats)

            temporal_stats = self.temporal_analyzer.analyze(
                posts=self.posts, stories=self.stories, reels=self.reels
            )
            results.update(temporal_stats)

        return results

    def analyze_with_ml(
        self,
        include_media: bool = False,
        include_sentiment: bool = True,
        include_engagement_prediction: bool = True,
        show_progress: bool = True,
    ) -> dict[str, Any]:
        """Run comprehensive analysis including ML components.

        Args:
            include_media: Whether to include media file analysis
            include_sentiment: Whether to run sentiment analysis
            include_engagement_prediction: Whether to run engagement prediction
            show_progress: Whether to show progress bars

        Returns:
            Dictionary containing analysis results including ML insights
        """
        # Run standard analysis first
        results = self.analyze(include_media=include_media, show_progress=show_progress)

        if show_progress:
            with self.progress:
                # Calculate total ML tasks
                total_tasks = 1  # Feature engineering is always run
                if include_sentiment:
                    total_tasks += 1
                if include_engagement_prediction:
                    total_tasks += 1

                ml_task = self.progress.add_task("Running ML analysis", total=total_tasks)

                try:
                    # Sentiment Analysis
                    if include_sentiment:
                        self.progress.update(
                            ml_task, description="Analyzing sentiment..."
                        )
                        sentiment_results = self._run_sentiment_analysis_with_progress()
                        results.update(sentiment_results)
                        self.progress.update(ml_task, advance=1)

                    # Engagement Prediction
                    if include_engagement_prediction:
                        self.progress.update(
                            ml_task, description="Predicting engagement..."
                        )
                        engagement_results = (
                            self._run_engagement_prediction_with_progress()
                        )
                        results.update(engagement_results)
                        self.progress.update(ml_task, advance=1)

                    # Feature Engineering Results
                    self.progress.update(ml_task, description="Extracting ML features...")
                    feature_results = self._extract_ml_features()
                    results.update(feature_results)
                    self.progress.update(ml_task, advance=1)

                    self.progress.update(ml_task, description="ML analysis complete!")

                except Exception as e:
                    self.logger.warning(f"ML analysis failed: {str(e)}", exc_info=True)
                    results["ml_analysis_error"] = str(e)
        else:
            # Run without progress bars
            try:
                if include_sentiment:
                    self.logger.info("Running sentiment analysis...")
                    sentiment_results = self._run_sentiment_analysis()
                    results.update(sentiment_results)

                if include_engagement_prediction:
                    self.logger.info("Running engagement prediction...")
                    engagement_results = self._run_engagement_prediction()
                    results.update(engagement_results)

                self.logger.info("Extracting ML features...")
                feature_results = self._extract_ml_features()
                results.update(feature_results)

            except Exception as e:
                self.logger.warning(f"ML analysis failed: {str(e)}", exc_info=True)
                results["ml_analysis_error"] = str(e)

        return results

    def _run_sentiment_analysis(self) -> dict[str, Any]:
        """Run sentiment analysis on posts and conversations."""
        sentiment_results = {
            "sentiment_analysis": {
                "posts": [],
                "conversations": [],
                "overall_sentiment": {
                    "avg_polarity": 0.0,
                    "avg_subjectivity": 0.0,
                    "dominant_emotion": None,
                    "sentiment_distribution": {},
                },
            }
        }

        all_sentiments = []

        # Analyze posts
        if self.posts:
            post_texts = []
            for post in self.posts:
                if hasattr(post, "caption") and post.caption:
                    post_texts.append(post.caption)

            if post_texts:
                post_sentiments = self.sentiment_analyzer.predict(post_texts)
                sentiment_results["sentiment_analysis"]["posts"] = post_sentiments
                if isinstance(post_sentiments, list):
                    all_sentiments.extend(post_sentiments)
                else:
                    all_sentiments.append(post_sentiments)

        # Analyze conversations if available
        conversations = getattr(self, "conversations", [])
        if conversations:
            conversation_sentiments = self.sentiment_analyzer.analyze_conversations(
                conversations
            )
            sentiment_results["sentiment_analysis"][
                "conversations"
            ] = conversation_sentiments

        # Calculate overall sentiment metrics
        if all_sentiments:
            avg_polarity = sum(s.get("polarity", 0) for s in all_sentiments) / len(
                all_sentiments
            )
            avg_subjectivity = sum(
                s.get("subjectivity", 0) for s in all_sentiments
            ) / len(all_sentiments)

            emotions = [s.get("emotion") for s in all_sentiments if s.get("emotion")]
            dominant_emotion = (
                max(set(emotions), key=emotions.count) if emotions else None
            )

            # Sentiment distribution
            polarities = [s.get("polarity", 0) for s in all_sentiments]
            positive_count = sum(1 for p in polarities if p > 0.1)
            negative_count = sum(1 for p in polarities if p < -0.1)
            neutral_count = len(polarities) - positive_count - negative_count

            sentiment_results["sentiment_analysis"]["overall_sentiment"] = {
                "avg_polarity": avg_polarity,
                "avg_subjectivity": avg_subjectivity,
                "dominant_emotion": dominant_emotion,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": len(polarities),
                },
            }

        return sentiment_results

    def _run_sentiment_analysis_with_progress(self) -> dict[str, Any]:
        """Run sentiment analysis on posts and conversations with progress tracking."""
        sentiment_results = {
            "sentiment_analysis": {
                "posts": [],
                "conversations": [],
                "overall_sentiment": {
                    "avg_polarity": 0.0,
                    "avg_subjectivity": 0.0,
                    "dominant_emotion": None,
                    "sentiment_distribution": {},
                },
            }
        }

        all_sentiments = []

        # Analyze posts
        if self.posts:
            post_texts = []
            for post in self.posts:
                if hasattr(post, "caption") and post.caption:
                    post_texts.append(post.caption)

            if post_texts:
                # Process posts in batches with progress
                batch_size = 100
                post_sentiments = []

                for i in range(0, len(post_texts), batch_size):
                    batch = post_texts[i : i + batch_size]
                    batch_sentiments = self.sentiment_analyzer.predict(batch)
                    if isinstance(batch_sentiments, list):
                        post_sentiments.extend(batch_sentiments)
                    else:
                        post_sentiments.append(batch_sentiments)

                sentiment_results["sentiment_analysis"]["posts"] = post_sentiments
                all_sentiments.extend(post_sentiments)

        # Analyze conversations if available
        conversations = getattr(self, "conversations", [])
        if conversations:
            conversation_sentiments = self.sentiment_analyzer.analyze_conversations(
                conversations
            )
            sentiment_results["sentiment_analysis"][
                "conversations"
            ] = conversation_sentiments

        # Calculate overall sentiment metrics
        if all_sentiments:
            avg_polarity = sum(s.get("polarity", 0) for s in all_sentiments) / len(
                all_sentiments
            )
            avg_subjectivity = sum(
                s.get("subjectivity", 0) for s in all_sentiments
            ) / len(all_sentiments)

            # Count sentiment distribution
            polarities = [s.get("polarity", 0) for s in all_sentiments]
            positive_count = sum(1 for p in polarities if p > 0.1)
            negative_count = sum(1 for p in polarities if p < -0.1)
            neutral_count = len(polarities) - positive_count - negative_count

            sentiment_results["sentiment_analysis"]["overall_sentiment"] = {
                "avg_polarity": avg_polarity,
                "avg_subjectivity": avg_subjectivity,
                "dominant_emotion": (
                    "positive"
                    if positive_count > negative_count
                    else "negative" if negative_count > positive_count else "neutral"
                ),
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": len(polarities),
                },
            }

        return sentiment_results

    def _run_engagement_prediction(self) -> dict[str, Any]:
        """Run engagement prediction on posts."""
        engagement_results = {
            "engagement_prediction": {
                "predictions": [],
                "feature_importance": {},
                "optimal_timing": {},
                "model_performance": {},
            }
        }

        if not self.posts:
            return engagement_results

        try:
            # Train model on existing posts (if they have engagement data)
            posts_with_engagement = [
                post
                for post in self.posts
                if hasattr(post, "likes_count") or hasattr(post, "comments_count")
            ]

            if len(posts_with_engagement) >= 10:  # Minimum data for training
                self.logger.info(
                    f"Training engagement model on {len(posts_with_engagement)} posts"
                )

                # Train the model
                self.engagement_predictor.fit(posts_with_engagement)

                # Make predictions on all posts
                predictions = self.engagement_predictor.predict(self.posts)
                engagement_results["engagement_prediction"]["predictions"] = predictions

                # Get feature importance
                for metric in ["likes", "comments"]:
                    importance = self.engagement_predictor.get_feature_importance(metric)
                    if importance:
                        engagement_results["engagement_prediction"]["feature_importance"][
                            metric
                        ] = importance

                # Predict optimal timing for a sample post
                if self.posts:
                    sample_features = self.feature_engineer.transform([self.posts[0]])
                    optimal_timing = self.engagement_predictor.predict_optimal_timing(
                        sample_features
                    )
                    engagement_results["engagement_prediction"][
                        "optimal_timing"
                    ] = optimal_timing

                # Evaluate model performance
                if len(posts_with_engagement) > 1:
                    evaluation = self.engagement_predictor.evaluate(posts_with_engagement)
                    engagement_results["engagement_prediction"][
                        "model_performance"
                    ] = evaluation

            else:
                self.logger.warning(
                    f"Insufficient data for engagement prediction (need ≥10, have {len(posts_with_engagement)})"
                )
                engagement_results["engagement_prediction"][
                    "error"
                ] = "Insufficient training data"

        except Exception as e:
            self.logger.error(f"Engagement prediction failed: {str(e)}", exc_info=True)
            engagement_results["engagement_prediction"]["error"] = str(e)

        return engagement_results

    def _run_engagement_prediction_with_progress(self) -> dict[str, Any]:
        """Run engagement prediction on posts with progress tracking."""
        engagement_results = {
            "engagement_prediction": {
                "predictions": [],
                "feature_importance": {},
                "optimal_timing": {},
                "model_performance": {},
            }
        }

        if not self.posts:
            return engagement_results

        try:
            # Train model on existing posts (if they have engagement data)
            posts_with_engagement = [
                post
                for post in self.posts
                if hasattr(post, "likes_count") or hasattr(post, "comments_count")
            ]

            if len(posts_with_engagement) >= 10:  # Minimum data for training
                self.logger.info(
                    f"Training engagement model on {len(posts_with_engagement)} posts"
                )

                # Train the model
                self.engagement_predictor.fit(posts_with_engagement)

                # Make predictions on all posts in batches
                batch_size = 50
                all_predictions = []

                for i in range(0, len(self.posts), batch_size):
                    batch = self.posts[i : i + batch_size]
                    batch_predictions = self.engagement_predictor.predict(batch)
                    all_predictions.extend(batch_predictions)

                engagement_results["engagement_prediction"][
                    "predictions"
                ] = all_predictions

                # Get feature importance
                for metric in ["likes", "comments"]:
                    importance = self.engagement_predictor.get_feature_importance(metric)
                    if importance:
                        engagement_results["engagement_prediction"]["feature_importance"][
                            metric
                        ] = importance

                # Predict optimal timing for a sample post
                if self.posts:
                    sample_features = self.feature_engineer.transform([self.posts[0]])
                    optimal_timing = self.engagement_predictor.predict_optimal_timing(
                        sample_features
                    )
                    engagement_results["engagement_prediction"][
                        "optimal_timing"
                    ] = optimal_timing

                # Evaluate model performance
                if len(posts_with_engagement) > 1:
                    evaluation = self.engagement_predictor.evaluate(posts_with_engagement)
                    engagement_results["engagement_prediction"][
                        "model_performance"
                    ] = evaluation

            else:
                self.logger.warning(
                    f"Insufficient data for engagement prediction (need ≥10, have {len(posts_with_engagement)})"
                )
                engagement_results["engagement_prediction"][
                    "error"
                ] = "Insufficient training data"

        except Exception as e:
            self.logger.error(f"Engagement prediction failed: {str(e)}", exc_info=True)
            engagement_results["engagement_prediction"]["error"] = str(e)

        return engagement_results

    def _extract_ml_features(self) -> dict[str, Any]:  # noqa: C901
        """Extract ML features from all content."""
        feature_results = {
            "ml_features": {
                "posts": {},
                "stories": {},
                "reels": {},
                "feature_summary": {},
            }
        }

        try:
            # Extract features from posts
            if self.posts:
                post_features = self.feature_engineer.transform(self.posts)
                feature_results["ml_features"]["posts"] = post_features

            # Extract features from stories
            if self.stories:
                story_features = self.feature_engineer.transform(self.stories)
                feature_results["ml_features"]["stories"] = story_features

            # Extract features from reels
            if self.reels:
                reel_features = self.feature_engineer.transform(self.reels)
                feature_results["ml_features"]["reels"] = reel_features

            # Create feature summary
            all_data = []
            if self.posts:
                all_data.extend(self.posts)
            if self.stories:
                all_data.extend(self.stories)
            if self.reels:
                all_data.extend(self.reels)

            if all_data:
                summary_features = self.feature_engineer.transform(all_data)

                # Calculate feature statistics
                feature_summary = {}
                for group_name, group_features in summary_features.items():
                    if isinstance(group_features, dict):
                        group_summary = {}
                        for feature_name, feature_values in group_features.items():
                            if isinstance(feature_values, list) and feature_values:
                                if all(
                                    isinstance(v, (int, float))
                                    for v in feature_values
                                    if v is not None
                                ):
                                    numeric_values = [
                                        v for v in feature_values if v is not None
                                    ]
                                    if numeric_values:
                                        group_summary[feature_name] = {
                                            "mean": sum(numeric_values)
                                            / len(numeric_values),
                                            "min": min(numeric_values),
                                            "max": max(numeric_values),
                                            "count": len(numeric_values),
                                        }
                                else:
                                    # For categorical features, count unique values
                                    non_null_values = [
                                        v for v in feature_values if v is not None
                                    ]
                                    if non_null_values:
                                        unique_values = list(set(non_null_values))
                                        group_summary[feature_name] = {
                                            "unique_values": unique_values[
                                                :10
                                            ],  # Limit to 10
                                            "unique_count": len(unique_values),
                                            "total_count": len(non_null_values),
                                        }
                        feature_summary[group_name] = group_summary

                feature_results["ml_features"]["feature_summary"] = feature_summary

        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}", exc_info=True)
            feature_results["ml_features"]["error"] = str(e)

        return feature_results

    def validate_data(self) -> dict[str, dict[str, Any]]:
        """Validate loaded data integrity.

        Returns:
            Dictionary containing validation results
        """
        validation_results = {}

        # Check if data was loaded
        validation_results["data_loaded"] = {
            "valid": bool(self.posts or self.stories or self.reels or self.profile),
            "details": f"Loaded: {len(self.posts)} posts, {len(self.stories)} stories, {len(self.reels)} reels",
        }

        # Check profile data
        validation_results["profile_data"] = {
            "valid": self.profile is not None,
            "details": (
                "Profile information found" if self.profile else "No profile data"
            ),
        }

        # Check data consistency
        total_content = len(self.posts) + len(self.stories) + len(self.reels)
        validation_results["content_found"] = {
            "valid": total_content > 0,
            "details": f"Total content items: {total_content}",
        }

        return validation_results

    def get_basic_info(self) -> dict[str, Any]:
        """Get basic information about the data export.

        Returns:
            Dictionary containing basic information
        """
        info = {}

        if self.profile:
            info["username"] = self.profile.username
            info["display_name"] = self.profile.name or "Unknown"
            info["is_verified"] = self.profile.is_verified
            info["is_private"] = self.profile.is_private

        info["total_posts"] = len(self.posts)
        info["total_stories"] = len(self.stories)
        info["total_reels"] = len(self.reels)
        info["total_archived_posts"] = len(self.archived_posts)
        info["total_recently_deleted"] = len(self.recently_deleted)
        info["total_story_interactions"] = len(self.story_interactions)

        # Date range
        all_dates = []
        for item in self.posts + self.stories + self.reels + self.archived_posts:
            if item.timestamp:
                all_dates.append(item.timestamp)

        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
            info["date_range"] = (
                f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            )
            info["days_active"] = (max_date - min_date).days

        return info

    def export_html(
        self,
        output_path: Path,
        anonymize: bool = False,
        show_progress: bool = True,
        compact: bool = False,
        max_items: int = 100,
    ) -> Path:
        """Export analysis results as HTML report.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data
            show_progress: Whether to show progress bars
            compact: Whether to generate compact report (smaller file size)
            max_items: Maximum number of items per section in compact mode

        Returns:
            Path to generated HTML file
        """
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        from ..exporters import HTMLExporter

        if show_progress:
            with self.progress:
                export_task = self.progress.add_task("Exporting HTML report", total=100)

                self.progress.update(
                    export_task, description="Initializing HTML exporter..."
                )
                exporter = HTMLExporter()
                self.progress.update(export_task, advance=10)

                self.progress.update(export_task, description="Generating HTML report...")
                result = exporter.export(
                    self,
                    output_path,
                    anonymize,
                    show_progress=False,
                    compact=compact,
                    max_items=max_items,
                )
                self.progress.update(export_task, advance=90)

                self.progress.update(export_task, description="HTML export complete!")
                return result
        else:
            exporter = HTMLExporter()
            return exporter.export(
                self, output_path, anonymize, compact=compact, max_items=max_items
            )

    def export_json(
        self, output_path: Path, anonymize: bool = False, show_progress: bool = True
    ) -> Path:
        """Export analysis results as JSON.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data
            show_progress: Whether to show progress bars

        Returns:
            Path to generated JSON file
        """
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        if show_progress:
            with self.progress:
                export_task = self.progress.add_task("Exporting JSON report", total=100)

                self.progress.update(export_task, description="Running analysis...")
                results = self.analyze(show_progress=False)
                self.progress.update(export_task, advance=50)

                if anonymize:
                    self.progress.update(export_task, description="Anonymizing data...")
                    results = self._anonymize_results(results)
                    self.progress.update(export_task, advance=20)

                self.progress.update(export_task, description="Writing JSON file...")
                json_file = output_path / "instagram_analysis.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, default=str)
                self.progress.update(export_task, advance=30)

                self.progress.update(export_task, description="JSON export complete!")
                return json_file
        else:
            json_file = output_path / "instagram_analysis.json"
            results = self.analyze()

            if anonymize:
                results = self._anonymize_results(results)

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, default=str)

            return json_file

    def export_pdf(
        self, output_path: Path, anonymize: bool = False, show_progress: bool = True
    ) -> Path:
        """Export analysis results as PDF report.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data
            show_progress: Whether to show progress bars

        Returns:
            Path to generated PDF file
        """
        from ..exporters import PDFExporter

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        if show_progress:
            with self.progress:
                export_task = self.progress.add_task("Exporting PDF report", total=100)

                self.progress.update(
                    export_task, description="Initializing PDF exporter..."
                )
                exporter = PDFExporter()
                self.progress.update(export_task, advance=10)

                self.progress.update(export_task, description="Generating PDF report...")
                result = exporter.export(self, output_path, anonymize)
                self.progress.update(export_task, advance=90)

                self.progress.update(export_task, description="PDF export complete!")
                return result
        else:
            exporter = PDFExporter()
            return exporter.export(self, output_path, anonymize)

    def _generate_html_report(self, anonymize: bool = False) -> str:
        """Generate HTML report content."""
        # Placeholder HTML template
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Instagram Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #333; }}
                .stats {{ margin: 20px 0; }}
                .stat-item {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Instagram Analysis Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="stats">
                <h2>Basic Statistics</h2>
                <div class="stat-item">Total Posts: {html.escape(str(len(self.posts)))}</div>
                <div class="stat-item">Total Stories: {html.escape(str(len(self.stories)))}</div>
                <div class="stat-item">Total Reels: {html.escape(str(len(self.reels)))}</div>
            </div>
        </body>
        </html>
        """

    def _anonymize_results(self, results: dict[str, Any]) -> dict[str, Any]:
        """Anonymize sensitive data in results."""
        # Placeholder implementation
        # In a real implementation, you would remove or hash sensitive data
        return results
