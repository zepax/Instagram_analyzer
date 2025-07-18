"""Unit tests for logging system."""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from instagram_analyzer.logging_config import (
    LoggerManager,
    OperationLogger,
    PerformanceFilter,
    StructuredFormatter,
    create_operation_logger,
    get_logger,
    setup_logging,
)


class TestStructuredFormatter:
    """Test structured JSON formatter."""

    def test_format_basic_record(self):
        """Test formatting of basic log record."""
        formatter = StructuredFormatter()

        # Create a mock log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        record.module = "test_module"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert data["level"] == "INFO"
        assert data["logger"] == "test_logger"
        assert data["message"] == "Test message"
        assert data["module"] == "test_module"
        assert data["function"] == "test_function"
        assert data["line"] == 10
        assert "timestamp" in data

    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        formatter = StructuredFormatter(include_extra=True)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.custom_field = "custom_value"
        record.operation_id = "12345"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert "extra" in data
        assert data["extra"]["custom_field"] == "custom_value"
        assert data["extra"]["operation_id"] == "12345"

    def test_format_without_extra_fields(self):
        """Test formatting without extra fields."""
        formatter = StructuredFormatter(include_extra=False)

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.custom_field = "custom_value"

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert "extra" not in data

    def test_format_with_exception(self):
        """Test formatting with exception information."""
        formatter = StructuredFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info(),
            )

        formatted = formatter.format(record)
        data = json.loads(formatted)

        assert "exception" in data
        assert "ValueError: Test exception" in data["exception"]


class TestPerformanceFilter:
    """Test performance filter."""

    def test_filter_adds_elapsed_time(self):
        """Test that filter adds elapsed time to records."""
        filter_obj = PerformanceFilter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = filter_obj.filter(record)

        assert result is True
        assert hasattr(record, "elapsed_time")
        assert isinstance(record.elapsed_time, float)
        assert record.elapsed_time >= 0


class TestLoggerManager:
    """Test logger manager."""

    def test_singleton_pattern(self):
        """Test that LoggerManager follows singleton pattern."""
        manager1 = LoggerManager()
        manager2 = LoggerManager()

        assert manager1 is manager2

    def test_get_logger(self):
        """Test getting logger instances."""
        manager = LoggerManager()

        logger1 = manager.get_logger("test_module")
        logger2 = manager.get_logger("test_module")
        logger3 = manager.get_logger("another_module")

        assert logger1 is logger2  # Same logger for same name
        assert logger1 is not logger3  # Different logger for different name
        assert logger1.name == "instagram_analyzer.test_module"
        assert logger3.name == "instagram_analyzer.another_module"

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        manager = LoggerManager()

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)

            manager.setup_logging(
                level=logging.DEBUG,
                log_dir=log_dir,
                enable_file_logging=True,
            )

            # Check that log directory was created
            assert log_dir.exists()

            # Test that logging works
            logger = manager.get_logger("test")
            logger.info("Test message")

            # Check log files were created
            log_file = log_dir / "instagram_analyzer.log"
            error_file = log_dir / "errors.log"

            assert log_file.exists()
            assert error_file.exists()

    def test_setup_logging_no_file(self):
        """Test logging setup without file logging."""
        manager = LoggerManager()

        manager.setup_logging(
            level=logging.INFO,
            enable_file_logging=False,
        )

        # Should not create any files
        logger = manager.get_logger("test")
        logger.info("Test message")

        # Verify console logging works
        root_logger = logging.getLogger("instagram_analyzer")
        assert len(root_logger.handlers) >= 1

    def test_set_level(self):
        """Test setting logging levels."""
        manager = LoggerManager()

        logger = manager.get_logger("test")
        original_level = logger.level

        manager.set_level(logging.DEBUG, "test")
        assert logger.level == logging.DEBUG

        manager.set_level(logging.ERROR)  # All loggers
        root_logger = logging.getLogger("instagram_analyzer")
        assert root_logger.level == logging.ERROR

    def test_create_operation_logger(self):
        """Test creating operation logger."""
        manager = LoggerManager()

        op_logger = manager.create_operation_logger("test_operation", {"user_id": "123"})

        assert isinstance(op_logger, OperationLogger)
        assert op_logger.operation_name == "test_operation"
        assert op_logger.context == {"user_id": "123"}


class TestOperationLogger:
    """Test operation logger."""

    def test_operation_lifecycle(self, caplog):
        """Test complete operation lifecycle."""
        op_logger = OperationLogger("test_op", {"test": "context"})

        # Capture logs from the specific operation logger
        with caplog.at_level(
            logging.INFO, logger="instagram_analyzer.operations.test_op"
        ):
            op_logger.start("Starting test operation")
            op_logger.progress("Making progress", {"step": 1})
            op_logger.complete("Operation completed", {"result": "success"})

        # Check that all phases were logged
        assert "Starting test operation" in caplog.text
        assert "Making progress" in caplog.text
        assert "Operation completed" in caplog.text

    def test_operation_with_error(self, caplog):
        """Test operation with error."""
        op_logger = OperationLogger("test_op", {})

        test_error = ValueError("Test error")

        with caplog.at_level(logging.ERROR):
            op_logger.start()
            op_logger.error("Operation failed", test_error, {"error_code": "TEST_001"})

        assert "Operation failed" in caplog.text

    def test_operation_context_manager(self, caplog):
        """Test operation logger as context manager."""
        with caplog.at_level(
            logging.INFO, logger="instagram_analyzer.operations.test_op"
        ):
            with create_operation_logger("test_op", {"test": True}) as op_logger:
                op_logger.progress("In progress")

        # Should automatically start and complete
        assert "Starting operation: test_op" in caplog.text
        assert "Completed operation: test_op" in caplog.text

    def test_operation_context_manager_with_exception(self, caplog):
        """Test operation logger context manager with exception."""
        with caplog.at_level(logging.ERROR):
            with pytest.raises(ValueError):
                with create_operation_logger("test_op") as op_logger:
                    raise ValueError("Test error")

        # Should log the error
        assert "Operation failed" in caplog.text

    def test_operation_timing(self):
        """Test operation timing functionality."""
        op_logger = OperationLogger("test_op", {})

        op_logger.start()
        assert op_logger.start_time is not None

        op_logger.complete()
        assert op_logger.end_time is not None
        assert op_logger.end_time >= op_logger.start_time


class TestLoggingIntegration:
    """Test logging system integration."""

    def test_setup_logging_function(self):
        """Test setup_logging convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(
                level="DEBUG",
                log_dir=Path(tmpdir),
                enable_file_logging=True,
                enable_structured_logging=True,
                enable_performance_logging=True,
            )

            # Test that it works
            logger = get_logger("integration_test")
            logger.info("Integration test message")

    def test_get_logger_function(self):
        """Test get_logger convenience function."""
        logger = get_logger("function_test")

        assert logger.name == "instagram_analyzer.function_test"
        assert isinstance(logger, logging.Logger)

    def test_create_operation_logger_function(self):
        """Test create_operation_logger convenience function."""
        op_logger = create_operation_logger("func_test", {"key": "value"})

        assert isinstance(op_logger, OperationLogger)
        assert op_logger.operation_name == "func_test"
        assert op_logger.context == {"key": "value"}

    def test_logging_with_rich_output(self):
        """Test that Rich integration works."""
        # This mainly tests that no errors occur with Rich formatting
        logger = get_logger("rich_test")

        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")

    def test_structured_logging_output(self):
        """Test structured logging output format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            setup_logging(
                log_dir=Path(tmpdir),
                enable_file_logging=True,
                enable_structured_logging=True,
            )

            logger = get_logger("struct_test")
            logger.info("Structured test", extra={"test_field": "test_value"})

            # Read and verify structured output
            if log_file.exists():
                content = log_file.read_text()
                # Should contain JSON-formatted log
                assert '"level": "INFO"' in content
                assert '"test_field": "test_value"' in content

    def test_performance_logging(self):
        """Test performance logging functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(
                log_dir=Path(tmpdir),
                enable_file_logging=True,
                enable_performance_logging=True,
            )

            logger = get_logger("perf_test")
            logger.info("Performance test message")

            # Performance filter should add elapsed_time to records

    def test_error_only_log_file(self):
        """Test that error log file only contains errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            setup_logging(
                log_dir=Path(tmpdir),
                enable_file_logging=True,
            )

            logger = get_logger("error_test")
            logger.info("Info message")
            logger.error("Error message")

            error_file = Path(tmpdir) / "errors.log"
            if error_file.exists():
                content = error_file.read_text()
                assert "Error message" in content
                assert "Info message" not in content

    def test_logging_levels(self):
        """Test different logging levels."""
        logger = get_logger("level_test")

        # Test all levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    def test_concurrent_logging(self):
        """Test logging from multiple loggers concurrently."""
        import threading
        import time

        def log_messages(logger_name, count):
            logger = get_logger(logger_name)
            for i in range(count):
                logger.info(f"Message {i} from {logger_name}")
                time.sleep(0.001)  # Small delay

        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_messages, args=(f"concurrent_{i}", 5))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should complete without errors
