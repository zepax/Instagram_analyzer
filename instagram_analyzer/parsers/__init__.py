"""Parsers for different Instagram data file formats."""

from .json_parser import JSONParser
from .data_detector import DataDetector

__all__ = ["JSONParser", "DataDetector"]