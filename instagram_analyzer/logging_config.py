"""Logging configuration for Instagram Analyzer.

This module provides comprehensive logging configuration with structured logging,
multiple output formats, and performance monitoring capabilities.
"""

import json
import logging
import logging.config
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

from rich.console import Console
from rich.logging import RichHandler


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def __init__(self, include_extra: bool = True) -> None:
        """Initialize the formatter.

        Args:
            include_extra: Whether to include extra fields in log records
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in {
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                }
            }
            if extra_fields:
                log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)


class PerformanceFilter(logging.Filter):
    """Filter to add performance metrics to log records."""

    def __init__(self) -> None:
        """Initialize the performance filter."""
        super().__init__()
        self.start_time = time.time()

    def filter(self, record: logging.LogRecord) -> bool:
        """Add performance metrics to log record.

        Args:
            record: Log record to filter

        Returns:
            True to allow the record to pass through
        """
        record.elapsed_time = time.time() - self.start_time
        return True


class LoggerManager:
    """Centralized logger management for Instagram Analyzer."""

    _instance: Optional["LoggerManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "LoggerManager":
        """Ensure singleton pattern for logger manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger manager."""
        if not self._initialized:
            self.console = Console()
            self.loggers: Dict[str, logging.Logger] = {}
            self.log_dir: Optional[Path] = None
            self._setup_root_logger()
            LoggerManager._initialized = True

    def _setup_root_logger(self) -> None:
        """Setup the root logger with default configuration."""
        root_logger = logging.getLogger("instagram_analyzer")
        root_logger.setLevel(logging.INFO)

        # Prevent duplicate handlers
        if not root_logger.handlers:
            # Console handler with Rich formatting
            console_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_level=True,
                show_path=False,
                rich_tracebacks=True,
            )
            console_handler.setLevel(logging.INFO)

            # Simple format for console output
            console_format = "%(message)s"
            console_handler.setFormatter(logging.Formatter(console_format))

            root_logger.addHandler(console_handler)

    def setup_logging(
        self,
        level: Union[str, int] = logging.INFO,
        log_dir: Optional[Path] = None,
        enable_file_logging: bool = True,
        enable_structured_logging: bool = True,
        enable_performance_logging: bool = False,
    ) -> None:
        """Setup comprehensive logging configuration.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            enable_file_logging: Whether to enable file logging
            enable_structured_logging: Whether to use structured JSON logging
            enable_performance_logging: Whether to add performance metrics
        """
        self.log_dir = log_dir or Path.cwd() / "logs"

        if enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)

        # Get root logger
        root_logger = logging.getLogger("instagram_analyzer")
        root_logger.setLevel(level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler with Rich formatting
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_level=True,
            show_path=False,
            rich_tracebacks=True,
        )
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger.addHandler(console_handler)

        if enable_file_logging:
            # File handler for general logs
            log_file = self.log_dir / "instagram_analyzer.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)

            if enable_structured_logging:
                file_handler.setFormatter(StructuredFormatter())
            else:
                file_handler.setFormatter(
                    logging.Formatter(
                        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                    )
                )

            # Add performance filter if enabled
            if enable_performance_logging:
                file_handler.addFilter(PerformanceFilter())

            root_logger.addHandler(file_handler)

            # Error log file
            error_file = self.log_dir / "errors.log"
            error_handler = logging.FileHandler(error_file, encoding="utf-8")
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(StructuredFormatter())
            root_logger.addHandler(error_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name.

        Args:
            name: Name of the logger

        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(f"instagram_analyzer.{name}")
            self.loggers[name] = logger
        return self.loggers[name]

    def set_level(
        self, level: Union[str, int], logger_name: Optional[str] = None
    ) -> None:
        """Set logging level for a specific logger or all loggers.

        Args:
            level: New logging level
            logger_name: Specific logger name, or None for root logger
        """
        if logger_name:
            if logger_name in self.loggers:
                self.loggers[logger_name].setLevel(level)
        else:
            logging.getLogger("instagram_analyzer").setLevel(level)
            for logger in self.loggers.values():
                logger.setLevel(level)

    def create_operation_logger(
        self, operation_name: str, context: Optional[Dict[str, Any]] = None
    ) -> "OperationLogger":
        """Create an operation logger for tracking specific operations.

        Args:
            operation_name: Name of the operation
            context: Additional context for the operation

        Returns:
            OperationLogger instance
        """
        return OperationLogger(operation_name, context or {})


class OperationLogger:
    """Logger for tracking specific operations with timing and context."""

    def __init__(self, operation_name: str, context: Dict[str, Any]) -> None:
        """Initialize the operation logger.

        Args:
            operation_name: Name of the operation
            context: Context information for the operation
        """
        self.operation_name = operation_name
        self.context = context
        self.logger = logging.getLogger(
            f"instagram_analyzer.operations.{operation_name}"
        )
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def start(self, message: Optional[str] = None) -> None:
        """Start the operation logging.

        Args:
            message: Optional start message
        """
        self.start_time = time.time()
        msg = message or f"Starting operation: {self.operation_name}"
        self.logger.info(
            msg,
            extra={
                "operation": self.operation_name,
                "operation_status": "started",
                "start_time": self.start_time,
                **self.context,
            },
        )

    def progress(
        self, message: str, progress_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log operation progress.

        Args:
            message: Progress message
            progress_data: Additional progress data
        """
        elapsed = time.time() - (self.start_time or time.time())
        self.logger.info(
            message,
            extra={
                "operation": self.operation_name,
                "operation_status": "in_progress",
                "elapsed_time": elapsed,
                **(progress_data or {}),
                **self.context,
            },
        )

    def complete(
        self,
        message: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Complete the operation logging.

        Args:
            message: Optional completion message
            result_data: Data about the operation result
        """
        self.end_time = time.time()
        duration = self.end_time - (self.start_time or self.end_time)

        msg = message or f"Completed operation: {self.operation_name}"
        self.logger.info(
            msg,
            extra={
                "operation": self.operation_name,
                "operation_status": "completed",
                "duration": duration,
                "end_time": self.end_time,
                **(result_data or {}),
                **self.context,
            },
        )

    def error(
        self,
        message: str,
        error: Optional[Exception] = None,
        error_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log operation error.

        Args:
            message: Error message
            error: Exception that occurred
            error_data: Additional error context
        """
        self.end_time = time.time()
        duration = self.end_time - (self.start_time or self.end_time)

        self.logger.error(
            message,
            exc_info=error,
            extra={
                "operation": self.operation_name,
                "operation_status": "failed",
                "duration": duration,
                "error_type": type(error).__name__ if error else "Unknown",
                **(error_data or {}),
                **self.context,
            },
        )

    def __enter__(self) -> "OperationLogger":
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context manager."""
        if exc_type is not None:
            self.error(f"Operation failed: {exc_val}", exc_val)
        else:
            self.complete()


# Global logger manager instance
logger_manager = LoggerManager()


# Convenience functions
def setup_logging(**kwargs) -> None:
    """Setup logging with given configuration."""
    logger_manager.setup_logging(**kwargs)


def get_logger(name: str) -> logging.Logger:
    """Get logger for the given module/component name."""
    return logger_manager.get_logger(name)


def create_operation_logger(
    operation_name: str, context: Optional[Dict[str, Any]] = None
) -> OperationLogger:
    """Create an operation logger."""
    return logger_manager.create_operation_logger(operation_name, context)


def set_level(level: Union[str, int], logger_name: Optional[str] = None) -> None:
    """Set logging level."""
    logger_manager.set_level(level, logger_name)
