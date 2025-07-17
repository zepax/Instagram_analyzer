"""Parsers for different Instagram data file formats."""

from .data_detector import DataDetector
from .json_parser import JSONParser

__all__ = ["JSONParser", "DataDetector"]
