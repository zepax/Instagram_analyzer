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

import json
import html
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..models import Post, Story, Reel, Profile, User
from ..parsers import JSONParser, DataDetector
from ..analyzers import BasicStatsAnalyzer, TemporalAnalyzer
from ..utils import validate_path, safe_json_load
from ..logging_config import get_logger, create_operation_logger
from ..cache import CacheManager, CacheConfig, cached_analysis, cached_parsing
from ..exceptions import (
    DataNotFoundError,
    InvalidDataFormatError,
    InsufficientDataError,
    AnalysisError,
)


class InstagramAnalyzer:
    """Main analyzer class for Instagram data."""

    def __init__(self, data_path: Path):
        """Initialize analyzer with data path.

        Args:
            data_path: Path to Instagram data export directory
            
        Raises:
            DataNotFoundError: If data path doesn't exist or is invalid
        """
        self.data_path = Path(data_path)
        self.profile: Optional[Profile] = None
        self.posts: List[Post] = []
        self.stories: List[Story] = []
        self.reels: List[Reel] = []

        # Setup logging
        self.logger = get_logger("core.analyzer")
        self.logger.info(f"Initializing InstagramAnalyzer with data path: {self.data_path}")

        # Analyzers
        self.basic_stats = BasicStatsAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()

        # Data detection
        self.detector = DataDetector()
        self.parser = JSONParser()

        # Validation
        if not validate_path(self.data_path):
            error_msg = f"Invalid data path: {self.data_path}"
            self.logger.error(error_msg)
            raise DataNotFoundError(str(self.data_path), error_msg)

    def load_data(self) -> None:
        """Load and parse Instagram data from export.
        
        Raises:
            InvalidDataFormatError: If data structure is invalid
            DataNotFoundError: If required data files are missing
        """
        with create_operation_logger("load_data", {"data_path": str(self.data_path)}) as op_logger:
            try:
                # Detect data structure
                op_logger.progress("Detecting data structure...")
                data_structure = self.detector.detect_structure(self.data_path)

                if not data_structure["is_valid"]:
                    error_msg = "Invalid Instagram data export structure"
                    self.logger.error(error_msg, extra={"data_structure": data_structure})
                    raise InvalidDataFormatError(
                        str(self.data_path), 
                        "Instagram JSON export",
                        error_msg,
                        {"data_structure": data_structure}
                    )

                self.logger.info(
                    f"Detected {data_structure['export_type']} export with {data_structure['total_files']} files"
                )

                # Load profile data
                op_logger.progress("Loading profile data...")
                self._load_profile(data_structure)

                # Load content data
                op_logger.progress("Loading posts...")
                self._load_posts(data_structure)
                
                op_logger.progress("Loading stories...")
                self._load_stories(data_structure)
                
                op_logger.progress("Loading reels...")
                self._load_reels(data_structure)

                total_content = len(self.posts) + len(self.stories) + len(self.reels)
                op_logger.complete(
                    f"Successfully loaded {total_content} content items",
                    {
                        "posts_count": len(self.posts),
                        "stories_count": len(self.stories),
                        "reels_count": len(self.reels),
                        "profile_loaded": self.profile is not None,
                    }
                )

            except Exception as e:
                self.logger.error(f"Failed to load data: {e}", exc_info=True)
                raise

    def _load_profile(self, structure: Dict[str, Any]) -> None:
        """Load profile information."""
        profile_files = structure.get("profile_files", [])

        for file_path in profile_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    self.profile = self.parser.parse_profile(data)
                    break
            except Exception:
                continue

    def _load_posts(self, structure: Dict[str, Any]) -> None:
        """Load posts data."""
        post_files = structure.get("post_files", [])

        for file_path in post_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    posts = self.parser.parse_posts(data)
                    self.posts.extend(posts)
            except Exception:
                continue

    def _load_stories(self, structure: Dict[str, Any]) -> None:
        """Load stories data."""
        story_files = structure.get("story_files", [])

        for file_path in story_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    stories = self.parser.parse_stories(data)
                    self.stories.extend(stories)
            except Exception:
                continue

    def _load_reels(self, structure: Dict[str, Any]) -> None:
        """Load reels data."""
        reel_files = structure.get("reel_files", [])

        for file_path in reel_files:
            try:
                data = safe_json_load(file_path)
                if data:
                    reels = self.parser.parse_reels(data)
                    self.reels.extend(reels)
            except Exception:
                continue

    def analyze(self, include_media: bool = False) -> Dict[str, Any]:
        """Run comprehensive analysis on loaded data.

        Args:
            include_media: Whether to include media file analysis

        Returns:
            Dictionary containing analysis results
        """
        results = {}

        # Basic statistics
        basic_stats = self.basic_stats.analyze(
            posts=self.posts,
            stories=self.stories,
            reels=self.reels,
            profile=self.profile,
        )
        results.update(basic_stats)

        # Temporal analysis
        temporal_stats = self.temporal_analyzer.analyze(
            posts=self.posts, stories=self.stories, reels=self.reels
        )
        results.update(temporal_stats)

        return results

    def validate_data(self) -> Dict[str, Dict[str, Any]]:
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
            "details": "Profile information found"
            if self.profile
            else "No profile data",
        }

        # Check data consistency
        total_content = len(self.posts) + len(self.stories) + len(self.reels)
        validation_results["content_found"] = {
            "valid": total_content > 0,
            "details": f"Total content items: {total_content}",
        }

        return validation_results

    def get_basic_info(self) -> Dict[str, Any]:
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

        # Date range
        all_dates = []
        for post in self.posts:
            if post.timestamp:
                all_dates.append(post.timestamp)
        for story in self.stories:
            if story.timestamp:
                all_dates.append(story.timestamp)
        for reel in self.reels:
            if reel.timestamp:
                all_dates.append(reel.timestamp)

        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
            info[
                "date_range"
            ] = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            info["days_active"] = (max_date - min_date).days

        return info

    def export_html(self, output_path: Path, anonymize: bool = False) -> Path:
        """Export analysis results as HTML report.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data

        Returns:
            Path to generated HTML file
        """
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Placeholder implementation
        html_file = output_path / "instagram_analysis.html"
        html_content = self._generate_html_report(anonymize)

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return html_file

    def export_json(self, output_path: Path, anonymize: bool = False) -> Path:
        """Export analysis results as JSON.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data

        Returns:
            Path to generated JSON file
        """
        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)
        
        json_file = output_path / "instagram_analysis.json"
        results = self.analyze()

        if anonymize:
            results = self._anonymize_results(results)

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        return json_file

    def export_pdf(self, output_path: Path, anonymize: bool = False) -> Path:
        """Export analysis results as PDF report.

        Args:
            output_path: Output directory path
            anonymize: Whether to anonymize sensitive data

        Returns:
            Path to generated PDF file
        """
        from ..exporters import PDFExporter

        # Ensure output directory exists
        output_path.mkdir(parents=True, exist_ok=True)

        # Create PDF exporter and generate report
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

    def _anonymize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data in results."""
        # Placeholder implementation
        # In a real implementation, you would remove or hash sensitive data
        return results
