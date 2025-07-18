"""Instagram Analyzer - Advanced Instagram data analysis tool."""

__version__ = "0.2.05"
__author__ = "Instagram Analyzer Team"
__email__ = "team@instagram-analyzer.com"

from .core import InstagramAnalyzer
from .exceptions import (
    AnalysisError,
    ConfigurationError,
    DataError,
    DataNotFoundError,
    DataValidationError,
    ExportError,
    InstagramAnalyzerError,
    InsufficientDataError,
    InvalidDataFormatError,
    JSONParsingError,
    ParsingError,
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
