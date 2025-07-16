"""Custom exceptions for Instagram Analyzer.

This module defines a comprehensive hierarchy of exceptions for better error
handling and debugging throughout the application.
"""

from typing import Any, Dict, Optional


class InstagramAnalyzerError(Exception):
    """Base exception for all Instagram Analyzer errors.

    This is the base class for all custom exceptions in the application.
    It provides common functionality like error codes and additional context.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for programmatic handling
            context: Additional context information for debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (context: {context_str})"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
        }


# Data-related exceptions
class DataError(InstagramAnalyzerError):
    """Base class for data-related errors."""

    pass


class DataNotFoundError(DataError):
    """Raised when required data is not found."""

    def __init__(
        self,
        path: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with data path information."""
        msg = message or f"Data not found at path: {path}"
        super().__init__(
            msg, error_code="DATA_NOT_FOUND", context={**(context or {}), "path": path}
        )


class InvalidDataFormatError(DataError):
    """Raised when data format is invalid or corrupted."""

    def __init__(
        self,
        file_path: str,
        expected_format: str,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with format information."""
        msg = (
            message or f"Invalid data format in {file_path}, expected {expected_format}"
        )
        super().__init__(
            msg,
            error_code="INVALID_DATA_FORMAT",
            context={
                **(context or {}),
                "file_path": file_path,
                "expected_format": expected_format,
            },
        )


class DataValidationError(DataError):
    """Raised when data validation fails."""

    def __init__(
        self,
        field: str,
        value: Any,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with validation details."""
        msg = f"Validation failed for field '{field}': {reason}"
        super().__init__(
            msg,
            error_code="DATA_VALIDATION_ERROR",
            context={
                **(context or {}),
                "field": field,
                "value": str(value),
                "reason": reason,
            },
        )


class CorruptedDataError(DataError):
    """Raised when data is corrupted or cannot be parsed."""

    pass


# Parsing-related exceptions
class ParsingError(InstagramAnalyzerError):
    """Base class for parsing-related errors."""

    pass


class JSONParsingError(ParsingError):
    """Raised when JSON parsing fails."""

    def __init__(
        self,
        file_path: str,
        line_number: Optional[int] = None,
        message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with parsing details."""
        msg = message or f"Failed to parse JSON file: {file_path}"
        if line_number:
            msg += f" at line {line_number}"

        super().__init__(
            msg,
            error_code="JSON_PARSING_ERROR",
            context={
                **(context or {}),
                "file_path": file_path,
                "line_number": line_number,
            },
        )


class UnsupportedFormatError(ParsingError):
    """Raised when encountering unsupported file formats."""

    def __init__(
        self,
        format_type: str,
        supported_formats: list,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with format information."""
        msg = f"Unsupported format '{format_type}'. Supported formats: {supported_formats}"
        super().__init__(
            msg,
            error_code="UNSUPPORTED_FORMAT",
            context={
                **(context or {}),
                "format_type": format_type,
                "supported_formats": supported_formats,
            },
        )


# Analysis-related exceptions
class AnalysisError(InstagramAnalyzerError):
    """Base class for analysis-related errors."""

    pass


class InsufficientDataError(AnalysisError):
    """Raised when there's insufficient data for analysis."""

    def __init__(
        self,
        required_items: int,
        available_items: int,
        data_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with data quantity information."""
        msg = f"Insufficient {data_type} for analysis: need {required_items}, have {available_items}"
        super().__init__(
            msg,
            error_code="INSUFFICIENT_DATA",
            context={
                **(context or {}),
                "required_items": required_items,
                "available_items": available_items,
                "data_type": data_type,
            },
        )


class AnalysisConfigError(AnalysisError):
    """Raised when analysis configuration is invalid."""

    pass


class MetricCalculationError(AnalysisError):
    """Raised when metric calculation fails."""

    def __init__(
        self,
        metric_name: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with metric information."""
        msg = f"Failed to calculate metric '{metric_name}': {reason}"
        super().__init__(
            msg,
            error_code="METRIC_CALCULATION_ERROR",
            context={**(context or {}), "metric_name": metric_name, "reason": reason},
        )


# Export-related exceptions
class ExportError(InstagramAnalyzerError):
    """Base class for export-related errors."""

    pass


class ExportFormatError(ExportError):
    """Raised when export format is invalid or unsupported."""

    pass


class ExportPermissionError(ExportError):
    """Raised when there are permission issues during export."""

    def __init__(
        self,
        file_path: str,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with permission details."""
        msg = f"Permission denied for {operation} operation on {file_path}"
        super().__init__(
            msg,
            error_code="EXPORT_PERMISSION_ERROR",
            context={
                **(context or {}),
                "file_path": file_path,
                "operation": operation,
            },
        )


class TemplateError(ExportError):
    """Raised when template processing fails."""

    pass


# Configuration-related exceptions
class ConfigurationError(InstagramAnalyzerError):
    """Base class for configuration-related errors."""

    pass


class InvalidConfigError(ConfigurationError):
    """Raised when configuration is invalid."""

    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(
        self,
        config_key: str,
        config_file: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with configuration details."""
        msg = f"Missing required configuration: {config_key}"
        if config_file:
            msg += f" in {config_file}"

        super().__init__(
            msg,
            error_code="MISSING_CONFIG",
            context={
                **(context or {}),
                "config_key": config_key,
                "config_file": config_file,
            },
        )


# Resource-related exceptions
class ResourceError(InstagramAnalyzerError):
    """Base class for resource-related errors."""

    pass


class MemoryError(ResourceError):
    """Raised when memory resources are exhausted."""

    pass


class DiskSpaceError(ResourceError):
    """Raised when disk space is insufficient."""

    def __init__(
        self,
        required_space: int,
        available_space: int,
        path: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize with disk space information."""
        msg = f"Insufficient disk space at {path}: need {required_space}MB, have {available_space}MB"
        super().__init__(
            msg,
            error_code="DISK_SPACE_ERROR",
            context={
                **(context or {}),
                "required_space": required_space,
                "available_space": available_space,
                "path": path,
            },
        )


class NetworkError(ResourceError):
    """Raised when network operations fail."""

    pass


# Security and Privacy exceptions
class SecurityError(InstagramAnalyzerError):
    """Base class for security-related errors."""

    pass


class PrivacyError(SecurityError):
    """Raised when privacy constraints are violated."""

    pass


class EncryptionError(SecurityError):
    """Raised when encryption/decryption operations fail."""

    pass


# Utility functions for exception handling
def handle_parsing_exception(func):
    """Decorator to handle common parsing exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, TypeError) as e:
            raise ParsingError(f"Parsing failed in {func.__name__}: {str(e)}")
        except FileNotFoundError as e:
            raise DataNotFoundError(str(e), context={"function": func.__name__})
        except PermissionError as e:
            raise ExportPermissionError(
                str(e), "read", context={"function": func.__name__}
            )

    return wrapper


def handle_analysis_exception(func):
    """Decorator to handle common analysis exceptions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ZeroDivisionError, ArithmeticError) as e:
            raise MetricCalculationError(
                func.__name__, str(e), context={"function": func.__name__}
            )
        except (IndexError, KeyError) as e:
            raise InsufficientDataError(
                0, 0, "items", context={"function": func.__name__, "error": str(e)}
            )

    return wrapper
