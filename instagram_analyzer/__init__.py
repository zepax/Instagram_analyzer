"""Instagram Analyzer - Advanced Instagram data analysis tool."""

__version__ = "0.2.0"
__author__ = "Instagram Analyzer Team"
__email__ = "team@instagram-analyzer.com"

from .core import InstagramAnalyzer
from .exceptions import (
    InstagramAnalyzerError,
    DataError,
    DataNotFoundError,
    InvalidDataFormatError,
    DataValidationError,
    ParsingError,
    JSONParsingError,
    AnalysisError,
    InsufficientDataError,
    ExportError,
    ConfigurationError,
)

__all__ = [
    "InstagramAnalyzer",
    "InstagramAnalyzerError",
    "DataError",
    "DataNotFoundError",
    "InvalidDataFormatError",
    "DataValidationError",
    "ParsingError",
    "JSONParsingError",
    "AnalysisError",
    "InsufficientDataError",
    "ExportError",
    "ConfigurationError",
]