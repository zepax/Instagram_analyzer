"""Tests for PDF exporter functionality."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from datetime import datetime, timezone

from instagram_analyzer.exporters.pdf_exporter import PDFExporter
from instagram_analyzer import __version__


class TestPDFExporter:
    """Test PDF exporter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.exporter = PDFExporter()

        # Create mock analyzer
        self.mock_analyzer = Mock()
        self.mock_analyzer.profile = Mock()
        self.mock_analyzer.profile.username = "test_user"
        self.mock_analyzer.profile.name = "Test User"

        # Create mock posts
        self.mock_posts = [
            Mock(
                caption="Test post #hashtag",
                likes_count=45,
                comments_count=3,
                timestamp=datetime(2023, 6, 15, tzinfo=timezone.utc),
                media=[],
            ),
            Mock(
                caption="Another post #test",
                likes_count=67,
                comments_count=8,
                timestamp=datetime(2023, 6, 16, tzinfo=timezone.utc),
                media=[],
            ),
        ]

        self.mock_analyzer.posts = self.mock_posts
        self.mock_analyzer.stories = []
        self.mock_analyzer.reels = []
        self.mock_analyzer.analyze.return_value = {"basic_stats": {"total_posts": 2}}

    def test_metadata_generation(self):
        """Test metadata generation."""
        metadata = self.exporter._get_metadata(self.mock_analyzer, anonymize=False)

        assert metadata["username"] == "test_user"
        assert metadata["display_name"] == "Test User"
        assert metadata["total_posts"] == 2
        assert metadata["total_stories"] == 0
        assert metadata["total_reels"] == 0
        assert metadata["analyzer_version"] == __version__

    def test_metadata_generation_anonymized(self):
        """Test anonymized metadata generation."""
        metadata = self.exporter._get_metadata(self.mock_analyzer, anonymize=True)

        assert metadata["username"] == "Anonymous User"
        assert metadata["display_name"] == "Anonymous"
        assert metadata["total_posts"] == 2
        assert metadata["analyzer_version"] == __version__

    def test_metadata_generation_no_profile(self):
        """Metadata indicates missing profile data."""
        self.mock_analyzer.profile = None
        metadata = self.exporter._get_metadata(self.mock_analyzer, anonymize=False)

        assert metadata["username"] == "No profile data available"
        assert metadata["display_name"] == "No profile data available"
        assert metadata["analyzer_version"] == __version__

    def test_overview_stats_calculation(self):
        """Test overview statistics calculation."""
        overview = self.exporter._get_overview_stats(self.mock_analyzer)

        assert overview["total_content"] == 2
        assert overview["total_likes"] == 112  # 45 + 67
        assert overview["total_comments"] == 11  # 3 + 8
        assert overview["avg_likes_per_post"] == 56.0
        assert overview["avg_comments_per_post"] == 5.5

    def test_temporal_analysis(self):
        """Test temporal analysis."""
        temporal = self.exporter._get_temporal_analysis(self.mock_analyzer)

        assert "2023-06" in temporal["monthly_distribution"]
        assert temporal["monthly_distribution"]["2023-06"] == 2
        assert temporal["most_active_month"] == ("2023-06", 2)

    def test_engagement_analysis(self):
        """Test engagement analysis."""
        engagement = self.exporter._get_engagement_analysis(self.mock_analyzer)

        assert len(engagement["top_posts"]) == 2
        assert engagement["top_posts"][0]["total_engagement"] == 75  # 67 + 8
        assert engagement["top_posts"][1]["total_engagement"] == 48  # 45 + 3
        assert engagement["avg_engagement"] == 61.5

    def test_content_analysis(self):
        """Test content analysis."""
        content = self.exporter._get_content_analysis(self.mock_analyzer)

        assert content["total_hashtags"] == 2
        assert content["unique_hashtags"] == 2
        assert "#hashtag" in content["top_hashtags"]
        assert "#test" in content["top_hashtags"]

    def test_date_range_calculation(self):
        """Test date range calculation."""
        date_range = self.exporter._get_date_range(self.mock_analyzer)

        assert date_range == "June 2023 - June 2023"

    def test_engagement_rate_calculation(self):
        """Test engagement rate calculation."""
        rate = self.exporter._calculate_engagement_rate(self.mock_analyzer)

        assert rate == 61.5  # (112 + 11) / 2

    def test_generate_report_data(self):
        """Test complete report data generation."""
        data = self.exporter._generate_report_data(self.mock_analyzer, anonymize=False)

        assert "metadata" in data
        assert "overview" in data
        assert "temporal_analysis" in data
        assert "engagement_analysis" in data
        assert "content_analysis" in data
        assert "generated_at" in data

    def test_generate_report_data_anonymized(self):
        """Test anonymized report data generation."""
        with patch(
            "instagram_analyzer.exporters.pdf_exporter.anonymize_data"
        ) as mock_anonymize:
            mock_anonymize.return_value = {"anonymized": True}

            data = self.exporter._generate_report_data(
                self.mock_analyzer, anonymize=True
            )

            mock_anonymize.assert_called_once()
            assert data == {"anonymized": True}

    def test_custom_styles_setup(self):
        """Test custom styles are properly set up."""
        assert "CustomTitle" in self.exporter.styles
        assert "SectionHeader" in self.exporter.styles
        assert "StatStyle" in self.exporter.styles
        assert "Highlight" in self.exporter.styles

    @patch("instagram_analyzer.exporters.pdf_exporter.SimpleDocTemplate")
    def test_export_pdf_creation(self, mock_doc):
        """Test PDF export creates document."""
        mock_doc_instance = Mock()
        mock_doc.return_value = mock_doc_instance

        output_path = Path("/tmp/test_output")

        with patch.object(self.exporter, "_generate_report_data") as mock_generate:
            mock_generate.return_value = {"test": "data"}

            with patch.object(self.exporter, "_build_pdf_content") as mock_build:
                mock_build.return_value = ["test_content"]

                result = self.exporter.export(
                    self.mock_analyzer, output_path, anonymize=False
                )

                # Verify document was created and built
                mock_doc.assert_called_once()
                mock_doc_instance.build.assert_called_once_with(["test_content"])

                # Verify return path
                assert result == output_path / "instagram_analysis.pdf"
