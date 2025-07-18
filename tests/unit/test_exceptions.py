"""Unit tests for exception system."""

from unittest.mock import MagicMock

import pytest

from instagram_analyzer.exceptions import (
    AnalysisConfigError,
    AnalysisError,
    ConfigurationError,
    CorruptedDataError,
    DataError,
    DataNotFoundError,
    DataValidationError,
    DiskSpaceError,
    EncryptionError,
    ExportError,
    ExportFormatError,
    ExportPermissionError,
    InstagramAnalyzerError,
    InsufficientDataError,
    InvalidConfigError,
    InvalidDataFormatError,
    JSONParsingError,
    MemoryError,
    MetricCalculationError,
    MissingConfigError,
    NetworkError,
    ParsingError,
    PrivacyError,
    ResourceError,
    SecurityError,
    TemplateError,
    UnsupportedFormatError,
    handle_analysis_exception,
    handle_parsing_exception,
)


class TestBaseException:
    """Test base InstagramAnalyzerError class."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        error = InstagramAnalyzerError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code == "InstagramAnalyzerError"
        assert error.context == {}

    def test_exception_with_error_code(self):
        """Test exception with custom error code."""
        error = InstagramAnalyzerError("Test message", error_code="TEST_001")

        assert error.error_code == "TEST_001"

    def test_exception_with_context(self):
        """Test exception with context information."""
        context = {"file_path": "/test/path", "line_number": 42}
        error = InstagramAnalyzerError("Test message", context=context)

        assert error.context == context
        assert "file_path=/test/path" in str(error)
        assert "line_number=42" in str(error)

    def test_exception_to_dict(self):
        """Test exception serialization to dictionary."""
        context = {"test_key": "test_value"}
        error = InstagramAnalyzerError(
            "Test message", error_code="TEST_001", context=context
        )

        result = error.to_dict()

        assert result["error_type"] == "InstagramAnalyzerError"
        assert result["error_code"] == "TEST_001"
        assert result["message"] == "Test message"
        assert result["context"] == context

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from base exception."""
        error = DataError("Data error")

        assert isinstance(error, InstagramAnalyzerError)
        assert isinstance(error, Exception)


class TestDataExceptions:
    """Test data-related exceptions."""

    def test_data_not_found_error(self):
        """Test DataNotFoundError."""
        error = DataNotFoundError("/nonexistent/path")

        assert "Data not found at path: /nonexistent/path" in str(error)
        assert error.error_code == "DATA_NOT_FOUND"
        assert error.context["path"] == "/nonexistent/path"

    def test_data_not_found_error_with_custom_message(self):
        """Test DataNotFoundError with custom message."""
        error = DataNotFoundError("/test/path", "Custom error message")

        assert "Custom error message" in str(error)
        assert error.context["path"] == "/test/path"

    def test_invalid_data_format_error(self):
        """Test InvalidDataFormatError."""
        error = InvalidDataFormatError("/test/file.txt", "JSON")

        assert "Invalid data format in /test/file.txt, expected JSON" in str(error)
        assert error.error_code == "INVALID_DATA_FORMAT"
        assert error.context["file_path"] == "/test/file.txt"
        assert error.context["expected_format"] == "JSON"

    def test_data_validation_error(self):
        """Test DataValidationError."""
        error = DataValidationError(
            "username", "invalid@user", "Contains invalid characters"
        )

        assert "Validation failed for field 'username'" in str(error)
        assert error.context["field"] == "username"
        assert error.context["value"] == "invalid@user"
        assert error.context["reason"] == "Contains invalid characters"

    def test_corrupted_data_error(self):
        """Test CorruptedDataError."""
        error = CorruptedDataError("Data corruption detected")

        assert isinstance(error, DataError)
        assert str(error) == "Data corruption detected"


class TestParsingExceptions:
    """Test parsing-related exceptions."""

    def test_json_parsing_error(self):
        """Test JSONParsingError."""
        error = JSONParsingError("/test/file.json", line_number=10)

        assert "Failed to parse JSON file: /test/file.json at line 10" in str(error)
        assert error.error_code == "JSON_PARSING_ERROR"
        assert error.context["file_path"] == "/test/file.json"
        assert error.context["line_number"] == 10

    def test_json_parsing_error_no_line(self):
        """Test JSONParsingError without line number."""
        error = JSONParsingError("/test/file.json")

        assert "Failed to parse JSON file: /test/file.json" in str(error)
        assert error.context["line_number"] is None

    def test_unsupported_format_error(self):
        """Test UnsupportedFormatError."""
        supported = ["JSON", "XML", "CSV"]
        error = UnsupportedFormatError("YAML", supported)

        assert "Unsupported format 'YAML'" in str(error)
        assert "Supported formats: ['JSON', 'XML', 'CSV']" in str(error)
        assert error.context["format_type"] == "YAML"
        assert error.context["supported_formats"] == supported


class TestAnalysisExceptions:
    """Test analysis-related exceptions."""

    def test_insufficient_data_error(self):
        """Test InsufficientDataError."""
        error = InsufficientDataError(100, 50, "posts")

        assert "Insufficient posts for analysis: need 100, have 50" in str(error)
        assert error.error_code == "INSUFFICIENT_DATA"
        assert error.context["required_items"] == 100
        assert error.context["available_items"] == 50
        assert error.context["data_type"] == "posts"

    def test_metric_calculation_error(self):
        """Test MetricCalculationError."""
        error = MetricCalculationError("engagement_rate", "Division by zero")

        assert "Failed to calculate metric 'engagement_rate': Division by zero" in str(
            error
        )
        assert error.context["metric_name"] == "engagement_rate"
        assert error.context["reason"] == "Division by zero"

    def test_analysis_config_error(self):
        """Test AnalysisConfigError."""
        error = AnalysisConfigError("Invalid configuration")

        assert isinstance(error, AnalysisError)
        assert str(error) == "Invalid configuration"


class TestExportExceptions:
    """Test export-related exceptions."""

    def test_export_permission_error(self):
        """Test ExportPermissionError."""
        error = ExportPermissionError("/restricted/file.pdf", "write")

        assert "Permission denied for write operation on /restricted/file.pdf" in str(
            error
        )
        assert error.error_code == "EXPORT_PERMISSION_ERROR"
        assert error.context["file_path"] == "/restricted/file.pdf"
        assert error.context["operation"] == "write"

    def test_export_format_error(self):
        """Test ExportFormatError."""
        error = ExportFormatError("Unsupported export format")

        assert isinstance(error, ExportError)
        assert str(error) == "Unsupported export format"

    def test_template_error(self):
        """Test TemplateError."""
        error = TemplateError("Template rendering failed")

        assert isinstance(error, ExportError)
        assert str(error) == "Template rendering failed"


class TestConfigurationExceptions:
    """Test configuration-related exceptions."""

    def test_missing_config_error(self):
        """Test MissingConfigError."""
        error = MissingConfigError("database_url", "config.yaml")

        assert "Missing required configuration: database_url in config.yaml" in str(error)
        assert error.error_code == "MISSING_CONFIG"
        assert error.context["config_key"] == "database_url"
        assert error.context["config_file"] == "config.yaml"

    def test_missing_config_error_no_file(self):
        """Test MissingConfigError without config file."""
        error = MissingConfigError("api_key")

        assert "Missing required configuration: api_key" in str(error)
        assert error.context["config_file"] is None

    def test_invalid_config_error(self):
        """Test InvalidConfigError."""
        error = InvalidConfigError("Invalid configuration format")

        assert isinstance(error, ConfigurationError)
        assert str(error) == "Invalid configuration format"


class TestResourceExceptions:
    """Test resource-related exceptions."""

    def test_disk_space_error(self):
        """Test DiskSpaceError."""
        error = DiskSpaceError(1000, 500, "/tmp")

        assert "Insufficient disk space at /tmp: need 1000MB, have 500MB" in str(error)
        assert error.error_code == "DISK_SPACE_ERROR"
        assert error.context["required_space"] == 1000
        assert error.context["available_space"] == 500
        assert error.context["path"] == "/tmp"

    def test_memory_error(self):
        """Test MemoryError (custom)."""
        error = MemoryError("Out of memory")

        assert isinstance(error, ResourceError)
        assert str(error) == "Out of memory"

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection timeout")

        assert isinstance(error, ResourceError)
        assert str(error) == "Connection timeout"


class TestSecurityExceptions:
    """Test security-related exceptions."""

    def test_privacy_error(self):
        """Test PrivacyError."""
        error = PrivacyError("Privacy violation detected")

        assert isinstance(error, SecurityError)
        assert str(error) == "Privacy violation detected"

    def test_encryption_error(self):
        """Test EncryptionError."""
        error = EncryptionError("Decryption failed")

        assert isinstance(error, SecurityError)
        assert str(error) == "Decryption failed"


class TestExceptionDecorators:
    """Test exception handling decorators."""

    def test_handle_parsing_exception_value_error(self):
        """Test parsing exception decorator with ValueError."""

        @handle_parsing_exception
        def failing_function():
            raise ValueError("Invalid value")

        with pytest.raises(ParsingError) as exc_info:
            failing_function()

        assert "Parsing failed in failing_function: Invalid value" in str(exc_info.value)

    def test_handle_parsing_exception_file_not_found(self):
        """Test parsing exception decorator with FileNotFoundError."""

        @handle_parsing_exception
        def failing_function():
            raise FileNotFoundError("File not found")

        with pytest.raises(DataNotFoundError) as exc_info:
            failing_function()

        assert exc_info.value.context["function"] == "failing_function"

    def test_handle_parsing_exception_permission_error(self):
        """Test parsing exception decorator with PermissionError."""

        @handle_parsing_exception
        def failing_function():
            raise PermissionError("Permission denied")

        with pytest.raises(ExportPermissionError) as exc_info:
            failing_function()

        assert exc_info.value.context["function"] == "failing_function"

    def test_handle_parsing_exception_success(self):
        """Test parsing exception decorator with successful function."""

        @handle_parsing_exception
        def successful_function():
            return "success"

        result = successful_function()
        assert result == "success"

    def test_handle_analysis_exception_zero_division(self):
        """Test analysis exception decorator with ZeroDivisionError."""

        @handle_analysis_exception
        def failing_function():
            return 1 / 0

        with pytest.raises(MetricCalculationError) as exc_info:
            failing_function()

        assert exc_info.value.context["function"] == "failing_function"

    def test_handle_analysis_exception_index_error(self):
        """Test analysis exception decorator with IndexError."""

        @handle_analysis_exception
        def failing_function():
            return [][0]  # Index error

        with pytest.raises(InsufficientDataError) as exc_info:
            failing_function()

        assert exc_info.value.context["function"] == "failing_function"

    def test_handle_analysis_exception_key_error(self):
        """Test analysis exception decorator with KeyError."""

        @handle_analysis_exception
        def failing_function():
            return {}["missing_key"]  # Key error

        with pytest.raises(InsufficientDataError) as exc_info:
            failing_function()

        assert exc_info.value.context["function"] == "failing_function"

    def test_handle_analysis_exception_success(self):
        """Test analysis exception decorator with successful function."""

        @handle_analysis_exception
        def successful_function():
            return {"result": "success"}

        result = successful_function()
        assert result == {"result": "success"}


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_exception_hierarchy(self):
        """Test that all exceptions inherit properly."""
        # Data exceptions
        assert issubclass(DataError, InstagramAnalyzerError)
        assert issubclass(DataNotFoundError, DataError)
        assert issubclass(InvalidDataFormatError, DataError)
        assert issubclass(DataValidationError, DataError)
        assert issubclass(CorruptedDataError, DataError)

        # Parsing exceptions
        assert issubclass(ParsingError, InstagramAnalyzerError)
        assert issubclass(JSONParsingError, ParsingError)
        assert issubclass(UnsupportedFormatError, ParsingError)

        # Analysis exceptions
        assert issubclass(AnalysisError, InstagramAnalyzerError)
        assert issubclass(InsufficientDataError, AnalysisError)
        assert issubclass(AnalysisConfigError, AnalysisError)
        assert issubclass(MetricCalculationError, AnalysisError)

        # Export exceptions
        assert issubclass(ExportError, InstagramAnalyzerError)
        assert issubclass(ExportFormatError, ExportError)
        assert issubclass(ExportPermissionError, ExportError)
        assert issubclass(TemplateError, ExportError)

        # Configuration exceptions
        assert issubclass(ConfigurationError, InstagramAnalyzerError)
        assert issubclass(InvalidConfigError, ConfigurationError)
        assert issubclass(MissingConfigError, ConfigurationError)

        # Resource exceptions
        assert issubclass(ResourceError, InstagramAnalyzerError)
        assert issubclass(MemoryError, ResourceError)
        assert issubclass(DiskSpaceError, ResourceError)
        assert issubclass(NetworkError, ResourceError)

        # Security exceptions
        assert issubclass(SecurityError, InstagramAnalyzerError)
        assert issubclass(PrivacyError, SecurityError)
        assert issubclass(EncryptionError, SecurityError)

    def test_exception_catching(self):
        """Test that exceptions can be caught by their base classes."""
        # Should be caught by base class
        try:
            raise DataNotFoundError("/test/path")
        except DataError:
            pass
        except Exception:
            pytest.fail("Should have been caught by DataError")

        # Should be caught by root base class
        try:
            raise JSONParsingError("/test/file.json")
        except InstagramAnalyzerError:
            pass
        except Exception:
            pytest.fail("Should have been caught by InstagramAnalyzerError")

    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""
        exceptions_to_test = [
            DataNotFoundError("/test"),
            InvalidDataFormatError("/test", "JSON"),
            JSONParsingError("/test.json"),
            InsufficientDataError(10, 5, "items"),
            ExportPermissionError("/test", "write"),
            MissingConfigError("key"),
        ]

        for exception in exceptions_to_test:
            assert isinstance(exception, InstagramAnalyzerError)
            assert hasattr(exception, "error_code")
            assert hasattr(exception, "context")
            assert hasattr(exception, "to_dict")


class TestExceptionUsageScenarios:
    """Test realistic exception usage scenarios."""

    def test_data_loading_scenario(self):
        """Test exceptions in data loading scenario."""
        # File not found
        with pytest.raises(DataNotFoundError):
            raise DataNotFoundError("/missing/data.json")

        # Invalid format
        with pytest.raises(InvalidDataFormatError):
            raise InvalidDataFormatError("/data.txt", "JSON", "File is not valid JSON")

        # Corrupted data
        with pytest.raises(CorruptedDataError):
            raise CorruptedDataError("JSON structure is corrupted")

    def test_analysis_scenario(self):
        """Test exceptions in analysis scenario."""
        # Not enough data
        with pytest.raises(InsufficientDataError):
            raise InsufficientDataError(100, 10, "posts")

        # Calculation error
        with pytest.raises(MetricCalculationError):
            raise MetricCalculationError("engagement_rate", "No posts to analyze")

    def test_export_scenario(self):
        """Test exceptions in export scenario."""
        # Permission denied
        with pytest.raises(ExportPermissionError):
            raise ExportPermissionError("/readonly/report.pdf", "write")

        # Unsupported format
        with pytest.raises(ExportFormatError):
            raise ExportFormatError("Format 'XYZ' is not supported")

    def test_error_context_propagation(self):
        """Test that error context is properly propagated."""
        original_context = {"original_file": "test.json", "line": 42}

        try:
            raise DataNotFoundError("/test/path", context=original_context)
        except DataNotFoundError as e:
            assert e.context["original_file"] == "test.json"
            assert e.context["line"] == 42
            assert e.context["path"] == "/test/path"  # Added by exception
