"""
Test module for continuous integration validation.

This module contains basic tests to ensure the project structure and
core functionality work correctly in CI/CD environments.
"""

import importlib
import subprocess
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version is compatible."""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, got {sys.version_info}"


def test_project_structure():
    """Test that essential project files exist."""
    project_root = Path(__file__).parent.parent

    essential_files = [
        "pyproject.toml",
        "README.md",
        "src/instagram_analyzer/__init__.py",
        "src/instagram_analyzer/models/__init__.py",
        "src/instagram_analyzer/analyzers/__init__.py",
        "src/instagram_analyzer/extractors/__init__.py",
    ]

    for file_path in essential_files:
        assert (project_root / file_path).exists(), f"Missing essential file: {file_path}"


def test_package_imports():
    """Test that core package modules can be imported."""
    import sys

    sys.path.insert(0, "src")

    try:
        import instagram_analyzer
        from instagram_analyzer.analyzers import basic_stats
        from instagram_analyzer.extractors import conversation_extractor
        from instagram_analyzer.models import base

        # Test version is accessible
        assert hasattr(instagram_analyzer, "__version__")
        assert isinstance(instagram_analyzer.__version__, str)

    except ImportError as e:
        pytest.fail(f"Failed to import core modules: {e}")


def test_poetry_dependencies():
    """Test that Poetry configuration is valid."""
    try:
        result = subprocess.run(
            ["poetry", "check"], capture_output=True, text=True, timeout=30
        )
        assert result.returncode == 0, f"Poetry check failed: {result.stderr}"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Poetry might not be available in all CI environments
        # This is not a critical failure
        pass


def test_basic_functionality():
    """Test basic analyzer functionality."""
    import sys

    sys.path.insert(0, "src")

    from datetime import datetime, timezone

    from instagram_analyzer.analyzers.basic_stats import BasicStatsAnalyzer
    from instagram_analyzer.models.media import Media
    from instagram_analyzer.models.post import Post

    # Create a simple test media object with timezone-aware datetime
    test_media = Media(
        uri="test.jpg",
        media_type="image",
        creation_timestamp=datetime.now(timezone.utc),
    )

    # Create a simple test post
    test_post = Post(
        id="test_123",
        media_type="image",
        timestamp=datetime.now(timezone.utc),
        caption="Test post",
        media_files=[],
        media=[test_media],  # Add required media field
    )

    # Create analyzer and test basic functionality
    analyzer = BasicStatsAnalyzer()
    assert analyzer is not None

    # Test data processing doesn't crash - provide all required arguments
    stats = analyzer.analyze([test_post], [], [])  # posts, stories, reels
    assert isinstance(stats, dict)
    assert "total_posts" in stats


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
