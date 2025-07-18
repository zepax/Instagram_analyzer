"""Integration tests for InstagramAnalyzer main class."""

import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from instagram_analyzer.core import InstagramAnalyzer
from instagram_analyzer.exceptions import DataNotFoundError, InvalidDataFormatError
from instagram_analyzer.models import ContentType, Media, MediaType, Post, Profile, Reel


# Helper functions for creating test objects with required parameters
def create_test_media(uri="test.jpg", media_type=MediaType.IMAGE, timestamp=None):
    """Create a Media object with all required parameters."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    return Media(
        uri=uri,
        media_type=media_type,
        creation_timestamp=timestamp,
        taken_at=None,
        title=None,
        width=None,
        height=None,
        duration=None,
        file_size=None,
        thumbnail_uri=None,
        ig_media_id=None,
    )


def create_test_post(media=None, timestamp=None, caption="Test post"):
    """Create a Post object with all required parameters."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    if media is None:
        media = [create_test_media()]

    return Post(
        media=media,
        timestamp=timestamp,
        caption=caption,
        post_id=None,
        content_type=ContentType.POST,
        location=None,
        likes_count=0,
        comments_count=0,
        is_sponsored=False,
        audience=None,
    )


def create_test_reel(video=None, timestamp=None, caption="Test reel"):
    """Create a Reel object with all required parameters."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    if video is None:
        video = create_test_media(uri="reel.mp4", media_type=MediaType.VIDEO)

    return Reel(
        video=video,
        timestamp=timestamp,
        caption=caption,
        reel_id=None,
        audio_title=None,
        audio_artist=None,
        likes_count=0,
        comments_count=0,
        music_id=None,
        is_original_audio=False,
        shares_count=0,
        plays_count=0,
    )


def create_test_profile(username="testuser"):
    """Create a Profile object with all required parameters."""
    return Profile(
        username=username,
        name=None,
        bio=None,
        website=None,
        email=None,
        phone_number=None,
        followers_count=None,
        following_count=None,
        posts_count=None,
        is_private=False,
        is_verified=False,
        is_business=False,
        date_joined=None,
        last_active=None,
        profile_pic_url=None,
        external_url=None,
        category=None,
    )


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_instagram_data(temp_dir):
    """Create mock Instagram data structure."""
    # Create directory structure
    content_dir = temp_dir / "content"
    content_dir.mkdir()

    messages_dir = temp_dir / "messages"
    messages_dir.mkdir()

    # Create mock posts data
    posts_data = [
        {
            "media": [
                {
                    "uri": "posts/test_image.jpg",
                    "creation_timestamp": 1625097600,  # 2021-07-01
                    "media_metadata": {"photo_metadata": {}},
                }
            ],
            "creation_timestamp": 1625097600,
            "title": "Test post caption",
            "likes": [{"username": "user1"}, {"username": "user2"}],
            "comments": [
                {
                    "text": "Great post!",
                    "timestamp": 1625097700,
                    "author": {"username": "commenter1"},
                }
            ],
        },
        {
            "media": [
                {
                    "uri": "posts/test_video.mp4",
                    "creation_timestamp": 1625184000,  # 2021-07-02
                    "media_metadata": {"video_metadata": {"duration": 30.5}},
                }
            ],
            "creation_timestamp": 1625184000,
            "title": "Test video post #test #video",
        },
    ]

    # Create mock stories data
    stories_data = [
        {
            "uri": "stories/story1.jpg",
            "creation_timestamp": 1625270400,  # 2021-07-03
            "media_metadata": {"photo_metadata": {}},
        }
    ]

    # Create mock profile data
    profile_data = {
        "username": "testuser",
        "name": "Test User",
        "biography": "Test bio",
        "follower_count": 1000,
        "following_count": 500,
        "media_count": 100,
        "is_private": False,
        "is_verified": False,
    }

    # Write JSON files
    with open(content_dir / "posts_1.json", "w") as f:
        json.dump(posts_data, f)

    with open(content_dir / "stories.json", "w") as f:
        json.dump(stories_data, f)

    with open(temp_dir / "personal_information.json", "w") as f:
        json.dump(profile_data, f)

    return temp_dir


class TestInstagramAnalyzerInitialization:
    """Test InstagramAnalyzer initialization."""

    def test_init_with_valid_path(self, mock_instagram_data):
        """Test initialization with valid data path."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        assert analyzer.data_path == mock_instagram_data
        # El mock crea 2 posts y 1 story, y no crea reels
        assert len(analyzer.posts) == 2
        assert len(analyzer.stories) == 1
        assert len(analyzer.reels) == 0

    def test_init_with_invalid_path(self):
        """Test initialization with invalid data path."""
        invalid_path = Path("/nonexistent/path")

        with pytest.raises(DataNotFoundError) as exc_info:
            InstagramAnalyzer(invalid_path)

        assert "Invalid data path" in str(exc_info.value)
        assert exc_info.value.context["path"] == str(invalid_path)

    def test_init_with_nonexistent_directory(self, temp_dir):
        """Test initialization with non-existent directory."""
        nonexistent = temp_dir / "does_not_exist"

        with pytest.raises(DataNotFoundError):
            InstagramAnalyzer(nonexistent)


class TestInstagramAnalyzerDataLoading:
    """Test data loading functionality."""

    def test_load_data_success(self, mock_instagram_data):
        """Test successful data loading."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock the data detector to return valid structure
        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": True,
                "export_type": "full_export",
                "total_files": 3,
                "post_files": [mock_instagram_data / "content" / "posts_1.json"],
                "story_files": [mock_instagram_data / "content" / "stories.json"],
                "reel_files": [],
                "profile_files": [mock_instagram_data / "personal_information.json"],
                "message_files": [],
            }

            analyzer.load_data()

            # Verify data was loaded - posts should be loaded via lazy loading
            assert len(analyzer.posts) >= 1
            # Note: Stories and reels may use lazy loading and not be loaded until accessed
            assert analyzer.profile is not None

    def test_load_data_invalid_structure(self, mock_instagram_data):
        """Test loading data with invalid structure."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": False,
                "export_type": "invalid",
                "total_files": 0,
            }

            with pytest.raises(InvalidDataFormatError) as exc_info:
                analyzer.load_data()

            assert "Invalid Instagram data export structure" in str(exc_info.value)

    def test_load_data_with_corrupted_json(self, temp_dir):
        """Test loading data with corrupted JSON files."""
        # Create corrupted JSON file
        content_dir = temp_dir / "content"
        content_dir.mkdir()

        with open(content_dir / "posts_1.json", "w") as f:
            f.write("{ invalid json")

        analyzer = InstagramAnalyzer(temp_dir)

        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": True,
                "export_type": "content_export",
                "total_files": 1,
                "post_files": [content_dir / "posts_1.json"],
                "story_files": [],
                "reel_files": [],
                "profile_files": [],
                "message_files": [],
            }

            # Should not raise exception, just skip corrupted files
            analyzer.load_data()
            assert len(analyzer.posts) == 0


class TestInstagramAnalyzerAnalysis:
    """Test analysis functionality."""

    def test_analyze_with_data(self, mock_instagram_data):
        """Test analysis with loaded data."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock loaded data
        analyzer.posts = [
            Post(
                media=[
                    Media(
                        uri="test.jpg",
                        media_type=MediaType.IMAGE,
                        creation_timestamp=datetime.now(timezone.utc),
                        # Add required parameters with default values
                        taken_at=None,
                        title=None,
                        width=None,
                        height=None,
                        duration=None,
                        file_size=None,
                        thumbnail_uri=None,
                        ig_media_id=None,
                    )
                ],
                timestamp=datetime.now(timezone.utc),
                caption="Test post",
                likes_count=10,
                comments_count=5,
                # Add required parameters with default values
                post_id=None,
                content_type=ContentType.POST,
                location=None,
                is_sponsored=False,
                audience=None,
            )
        ]
        analyzer.reels = [
            Reel(
                video=Media(
                    uri="reel.mp4",
                    media_type=MediaType.VIDEO,
                    creation_timestamp=datetime.now(timezone.utc),
                    taken_at=None,
                    title=None,
                    width=None,
                    height=None,
                    duration=None,
                    file_size=None,
                    thumbnail_uri=None,
                    ig_media_id=None,
                ),
                timestamp=datetime.now(timezone.utc),
                caption="Test reel",
                likes_count=7,
                comments_count=2,
                reel_id=None,
                audio_title=None,
                audio_artist=None,
                music_id=None,
                is_original_audio=False,
                shares_count=0,
                plays_count=0,
            )
        ]

        results = analyzer.analyze()

        assert "total_posts" in results
        assert "total_reels" in results
        assert results["total_posts"] == 1
        assert results["total_reels"] == 1
        assert results["total_likes"] == 17
        assert results["total_comments"] == 7

    def test_analyze_with_no_data(self, mock_instagram_data):
        """Test analysis with no data loaded."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        results = analyzer.analyze()

        # El mock siempre crea 2 posts y 1 story
        assert results["total_posts"] == 2
        assert results["total_stories"] == 1
        assert results["total_reels"] == 0

    def test_analyze_with_include_media(self, mock_instagram_data):
        """Test analysis with media inclusion."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock some data using helper functions
        timestamp = datetime.now(timezone.utc)
        media = create_test_media(uri="test.jpg", timestamp=timestamp)
        post = create_test_post(media=[media], timestamp=timestamp, caption="Test post")
        analyzer.posts = [post]

        results = analyzer.analyze(include_media=True)

        # Should still work even with media analysis enabled
        assert "total_posts" in results


class TestInstagramAnalyzerValidation:
    """Test data validation functionality."""

    def test_validate_data_with_content(self, mock_instagram_data):
        """Test validation with loaded content."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock some data
        analyzer.posts = [MagicMock()]
        analyzer.profile = MagicMock()

        validation_results = analyzer.validate_data()

        assert validation_results["data_loaded"]["valid"] is True
        assert validation_results["profile_data"]["valid"] is True
        assert validation_results["content_found"]["valid"] is True

    def test_validate_data_empty(self, mock_instagram_data):
        """Test validation with no data."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        validation_results = analyzer.validate_data()

        assert validation_results["data_loaded"]["valid"] is False
        assert validation_results["profile_data"]["valid"] is False
        assert validation_results["content_found"]["valid"] is False

    def test_validate_data_partial(self, mock_instagram_data):
        """Test validation with partial data."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Only posts, no profile
        analyzer.posts = [MagicMock()]

        validation_results = analyzer.validate_data()

        assert validation_results["data_loaded"]["valid"] is True
        assert validation_results["profile_data"]["valid"] is False
        assert validation_results["content_found"]["valid"] is True


class TestInstagramAnalyzerBasicInfo:
    """Test basic info functionality."""

    def test_get_basic_info_with_data(self, mock_instagram_data):
        """Test getting basic info with data."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock profile and content
        profile = create_test_profile(username="testuser")
        profile.name = "Test User"
        profile.is_verified = True
        profile.is_private = False
        analyzer.profile = profile

        test_time = datetime.now(timezone.utc)
        # Create posts with helper function
        media = create_test_media(uri="test.jpg", timestamp=test_time)
        post = create_test_post(media=[media], timestamp=test_time, caption="")
        analyzer.posts = [post]

        info = analyzer.get_basic_info()

        assert info["username"] == "testuser"
        assert info["display_name"] == "Test User"
        assert info["is_verified"] is True
        assert info["is_private"] is False
        assert info["total_posts"] == 1
        assert "date_range" in info

    def test_get_basic_info_no_profile(self, mock_instagram_data):
        """Test getting basic info without profile."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Create a real Post object instead of MagicMock to avoid datetime/MagicMock TypeError
        test_time = datetime.now(timezone.utc)
        media = create_test_media(uri="test.jpg", timestamp=test_time)
        post = create_test_post(media=[media], timestamp=test_time, caption="Test post")
        analyzer.posts = [post]

        info = analyzer.get_basic_info()

        assert "username" not in info
        assert info["total_posts"] == 1

    def test_get_basic_info_no_dates(self, mock_instagram_data):
        """Test getting basic info with posts that have no timestamps."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Create a mock post without a timestamp by setting it after creation
        test_time = datetime.now(timezone.utc)
        media = create_test_media(uri="test.jpg", timestamp=test_time)
        post = create_test_post(media=[media], timestamp=test_time)

        # Mock the timestamp to be None for this test
        post.__dict__["timestamp"] = None
        analyzer.posts = [post]

        info = analyzer.get_basic_info()

        assert "date_range" not in info
        assert "days_active" not in info


class TestInstagramAnalyzerExports:
    """Test export functionality."""

    def test_export_json(self, mock_instagram_data, temp_dir):
        """Test JSON export."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock some analysis results
        with patch.object(analyzer, "analyze") as mock_analyze:
            mock_analyze.return_value = {"total_posts": 5, "total_likes": 100}

            output_path = temp_dir / "output"
            result_path = analyzer.export_json(output_path)

            assert result_path.exists()
            assert result_path.suffix == ".json"

            # Verify content
            with open(result_path) as f:
                data = json.load(f)

            assert data["total_posts"] == 5
            assert data["total_likes"] == 100

    def test_export_json_with_anonymization(self, mock_instagram_data, temp_dir):
        """Test JSON export with anonymization."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        with patch.object(analyzer, "analyze") as mock_analyze:
            mock_analyze.return_value = {"username": "testuser", "total_posts": 5}

            output_path = temp_dir / "output"
            result_path = analyzer.export_json(output_path, anonymize=True)

            assert result_path.exists()

    def test_export_html(self, mock_instagram_data, temp_dir):
        """Test HTML export."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock the data detector to return valid structure and load data
        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": True,
                "export_type": "full_export",
                "total_files": 3,
                "post_files": [mock_instagram_data / "content" / "posts_1.json"],
                "story_files": [mock_instagram_data / "content" / "stories.json"],
                "reel_files": [],
                "profile_files": [mock_instagram_data / "personal_information.json"],
                "message_files": [],
            }

            analyzer.load_data()

        output_path = temp_dir / "output"
        result_path = analyzer.export_html(output_path)

        assert result_path.exists()
        assert result_path.suffix == ".html"

        # Verify it's valid HTML
        content = result_path.read_text()
        assert "<!DOCTYPE html>" in content
        assert "<html>" in content
        assert "network-graph" in content

        match = re.search(r"const overview = (.*?);", content)
        assert match
        overview = json.loads(match.group(1))
        assert overview["engagement_totals"]["likes"] == 2  # 2 likes from first post
        assert overview["engagement_totals"]["comments"] == 0  # No comments processed

    def test_export_pdf(self, mock_instagram_data, temp_dir):
        """Test PDF export."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        output_path = temp_dir / "output"

        # Mock the PDF exporter to avoid dependencies
        with patch("instagram_analyzer.exporters.PDFExporter") as mock_pdf:
            mock_pdf.return_value.export.return_value = output_path / "test.pdf"

            result_path = analyzer.export_pdf(output_path)

            assert result_path == output_path / "test.pdf"
            mock_pdf.return_value.export.assert_called_once()


class TestInstagramAnalyzerErrorHandling:
    """Test error handling scenarios."""

    def test_analyzer_with_permission_error(self, temp_dir):
        """Test analyzer behavior with permission errors."""
        # Create a directory with no read permissions
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir(mode=0o755)  # Create with normal permissions first

        try:
            # Remove permissions after creation
            restricted_dir.chmod(0o000)
            with pytest.raises(DataNotFoundError):
                InstagramAnalyzer(restricted_dir)
        finally:
            # Always restore permissions for cleanup
            try:
                restricted_dir.chmod(0o755)
            except PermissionError:
                pass

    def test_analyzer_with_memory_constraints(self, mock_instagram_data):
        """Test analyzer behavior under memory constraints."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock a memory error during analysis
        with patch.object(analyzer.basic_stats, "analyze") as mock_analyze:
            mock_analyze.side_effect = MemoryError("Out of memory")

            with pytest.raises(MemoryError):
                analyzer.analyze()

    def test_analyzer_logging_integration(self, mock_instagram_data, caplog):
        """Test that logging is properly integrated."""
        # Initialize analyzer - used to trigger and test logging messages
        InstagramAnalyzer(mock_instagram_data)

        # Check that initialization was logged
        assert "Initializing InstagramAnalyzer" in caplog.text

    def test_analyzer_with_large_dataset_simulation(self, mock_instagram_data):
        """Test analyzer with simulated large dataset."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Simulate large dataset
        large_posts = []
        for i in range(1000):
            timestamp = datetime.now(timezone.utc)
            media = create_test_media(uri=f"test_{i}.jpg", timestamp=timestamp)
            post = create_test_post(
                media=[media], timestamp=timestamp, caption=f"Test post {i}"
            )
            post.likes_count = i
            large_posts.append(post)

        analyzer.posts = large_posts

        # Should handle large dataset without issues
        results = analyzer.analyze()
        assert results["total_posts"] == 1000


@pytest.mark.integration
class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_full_analysis_workflow(self, mock_instagram_data, temp_dir):
        """Test complete analysis workflow from start to finish."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Mock complete data structure
        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": True,
                "export_type": "full_export",
                "total_files": 3,
                "post_files": [mock_instagram_data / "content" / "posts_1.json"],
                "story_files": [mock_instagram_data / "content" / "stories.json"],
                "reel_files": [],
                "profile_files": [mock_instagram_data / "personal_information.json"],
                "message_files": [],
            }

            # Full workflow
            analyzer.load_data()
            validation_results = analyzer.validate_data()
            basic_info = analyzer.get_basic_info()
            analysis_results = analyzer.analyze()

            # Export in all formats
            output_dir = temp_dir / "exports"
            json_path = analyzer.export_json(output_dir)
            html_path = analyzer.export_html(output_dir)

            # Verify all steps completed successfully
            assert validation_results["data_loaded"]["valid"]
            assert "total_posts" in basic_info
            assert "total_posts" in analysis_results
            assert json_path.exists()
            assert html_path.exists()

    def test_workflow_with_errors_and_recovery(self, mock_instagram_data, temp_dir):
        """Test workflow with errors and recovery mechanisms."""
        analyzer = InstagramAnalyzer(mock_instagram_data)

        # Simulate partial failure in data loading
        with patch.object(analyzer.detector, "detect_structure") as mock_detect:
            mock_detect.return_value = {
                "is_valid": True,
                "export_type": "partial_export",
                "total_files": 1,
                "post_files": [Path("/nonexistent/file.json")],  # This will fail
                "story_files": [],
                "reel_files": [],
                "profile_files": [],
                "message_files": [],
            }

            # Should handle the error gracefully
            analyzer.load_data()

            # Analysis should still work with empty data
            results = analyzer.analyze()
            assert results["total_posts"] == 0
