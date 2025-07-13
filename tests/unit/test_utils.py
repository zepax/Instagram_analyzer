"""Test cases for utility functions."""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime

from instagram_analyzer.utils import (
    validate_path, get_file_size, safe_json_load,
    parse_instagram_date, format_date_range,
    anonymize_data, detect_sensitive_info
)


class TestFileUtils:
    """Test cases for file utilities."""
    
    def test_validate_path_valid(self):
        """Test path validation with valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            assert validate_path(Path(temp_dir)) is True
    
    def test_validate_path_invalid(self):
        """Test path validation with invalid path."""
        assert validate_path(Path("/nonexistent/path")) is False
    
    def test_get_file_size(self):
        """Test file size calculation."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content")
            temp_path = Path(temp_file.name)
        
        try:
            size = get_file_size(temp_path)
            assert size > 0
        finally:
            temp_path.unlink()
    
    def test_safe_json_load_valid(self):
        """Test JSON loading with valid file."""
        test_data = {"test": "data", "number": 123}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(test_data, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            loaded_data = safe_json_load(temp_path)
            assert loaded_data == test_data
        finally:
            temp_path.unlink()
    
    def test_safe_json_load_invalid(self):
        """Test JSON loading with invalid file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_file.write("invalid json content")
            temp_path = Path(temp_file.name)
        
        try:
            loaded_data = safe_json_load(temp_path)
            assert loaded_data is None
        finally:
            temp_path.unlink()


class TestDateUtils:
    """Test cases for date utilities."""
    
    def test_parse_instagram_date_unix_timestamp(self):
        """Test parsing Unix timestamp."""
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        date = parse_instagram_date(timestamp)
        
        assert date is not None
        assert date.year == 2021
        assert date.month == 1
        assert date.day == 1
    
    def test_parse_instagram_date_milliseconds(self):
        """Test parsing timestamp in milliseconds."""
        timestamp = 1609459200000  # 2021-01-01 00:00:00 UTC in milliseconds
        date = parse_instagram_date(timestamp)
        
        assert date is not None
        assert date.year == 2021
    
    def test_parse_instagram_date_iso_string(self):
        """Test parsing ISO format string."""
        iso_string = "2021-01-01T00:00:00Z"
        date = parse_instagram_date(iso_string)
        
        assert date is not None
        assert date.year == 2021
        assert date.month == 1
        assert date.day == 1
    
    def test_parse_instagram_date_invalid(self):
        """Test parsing invalid date."""
        date = parse_instagram_date("invalid date")
        assert date is None
    
    def test_format_date_range(self):
        """Test date range formatting."""
        start = datetime(2021, 1, 1)
        end = datetime(2021, 12, 31)
        
        formatted = format_date_range(start, end)
        assert "January 01" in formatted
        assert "December 31, 2021" in formatted


class TestPrivacyUtils:
    """Test cases for privacy utilities."""
    
    def test_anonymize_data(self):
        """Test data anonymization."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "posts": [{"caption": "test post"}]
        }

        anonymized = anonymize_data(data)

        assert anonymized["username"] != "testuser"
        assert anonymized["email"] != "test@example.com"
        assert anonymized["posts"][0]["caption"] == "test post"  # Not in anonymize list

    def test_anonymize_data_explicit_none(self):
        """Anonymization when ``fields_to_anonymize`` is ``None``."""
        data = {"username": "user1"}

        anonymized = anonymize_data(data, None)

        assert anonymized["username"] != "user1"

    def test_anonymize_data_custom_fields(self):
        """Anonymization with a custom field set."""
        data = {"username": "user1", "email": "e@x.com"}

        anonymized = anonymize_data(data, {"username"})

        assert anonymized["username"] != "user1"
        # Email should remain unchanged
        assert anonymized["email"] == "e@x.com"
    
    def test_detect_sensitive_info_email(self):
        """Test email detection in text."""
        text = "Contact me at user@example.com for more info"
        sensitive = detect_sensitive_info(text)
        
        assert "email" in sensitive
    
    def test_detect_sensitive_info_phone(self):
        """Test phone number detection in text."""
        text = "Call me at 123-456-7890"
        sensitive = detect_sensitive_info(text)
        
        assert "phone" in sensitive
    
    def test_detect_sensitive_info_url(self):
        """Test URL detection in text."""
        text = "Visit my website at https://example.com"
        sensitive = detect_sensitive_info(text)
        
        assert "url" in sensitive
    
    def test_detect_sensitive_info_clean(self):
        """Test clean text with no sensitive info."""
        text = "This is just a normal caption without sensitive data"
        sensitive = detect_sensitive_info(text)
        
        assert len(sensitive) == 0