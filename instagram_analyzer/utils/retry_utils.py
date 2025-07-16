"""Retry utilities for robust I/O operations.

This module provides decorators and utilities for implementing retry logic
with exponential backoff, jitter, and comprehensive error handling.
"""

import functools
import random
import time
from typing import Any, Callable, Optional, Type, Union, Tuple
from pathlib import Path

from ..exceptions import (
    InstagramAnalyzerError,
    DataNotFoundError,
    NetworkError,
    ResourceError,
)
from ..logging_config import get_logger

logger = get_logger("retry_utils")


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (
        IOError,
        OSError,
        TimeoutError,
        ConnectionError,
    ),
) -> Callable:
    """Decorator for retrying operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for first retry
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Tuple of exception types to retry on
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(
                            f"Operation {func.__name__} succeeded after {attempt} retries"
                        )
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Operation {func.__name__} failed after {max_retries} retries",
                            extra={"error": str(e), "function": func.__name__}
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter to prevent thundering herd
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(
                        f"Operation {func.__name__} failed on attempt {attempt + 1}/{max_retries + 1}, "
                        f"retrying in {delay:.2f}s",
                        extra={
                            "error": str(e),
                            "attempt": attempt + 1,
                            "delay": delay,
                            "function": func.__name__
                        }
                    )
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    # Don't retry on unexpected exceptions
                    logger.error(
                        f"Operation {func.__name__} failed with non-retryable error",
                        extra={"error": str(e), "function": func.__name__}
                    )
                    raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def retry_on_file_error(
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
) -> Callable:
    """Specialized retry decorator for file operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay between retries
        
    Returns:
        Decorator function
    """
    return exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(
            FileNotFoundError,
            PermissionError,
            OSError,
            IOError,
        )
    )


def retry_on_network_error(
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable:
    """Specialized retry decorator for network operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay between retries
        
    Returns:
        Decorator function
    """
    return exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(
            ConnectionError,
            TimeoutError,
            NetworkError,
        )
    )


class CircuitBreaker:
    """Circuit breaker pattern implementation for fault tolerance.
    
    Prevents cascading failures by temporarily disabling operations
    that are likely to fail.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
        
    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == "open":
                if (time.time() - self.last_failure_time) > self.recovery_timeout:
                    self.state = "half-open"
                    logger.info(f"Circuit breaker for {func.__name__} entering half-open state")
                else:
                    raise ResourceError(
                        f"Circuit breaker is open for {func.__name__}",
                        context={"state": self.state, "failure_count": self.failure_count}
                    )
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset circuit breaker
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} reset to closed state")
                
                return result
                
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
                    logger.error(
                        f"Circuit breaker opened for {func.__name__} after {self.failure_count} failures",
                        extra={
                            "failure_count": self.failure_count,
                            "state": self.state,
                            "function": func.__name__
                        }
                    )
                
                raise
                
        return wrapper


def safe_file_operation(
    operation_name: str,
    max_retries: int = 3,
    circuit_breaker: bool = False,
) -> Callable:
    """Combined decorator for safe file operations.
    
    Args:
        operation_name: Name of the operation for logging
        max_retries: Maximum retry attempts
        circuit_breaker: Whether to use circuit breaker pattern
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Apply retry logic
        func = retry_on_file_error(max_retries=max_retries)(func)
        
        # Apply circuit breaker if requested
        if circuit_breaker:
            breaker = CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30.0,
                expected_exception=(IOError, OSError, PermissionError)
            )
            func = breaker(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.debug(f"Starting {operation_name} operation: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Completed {operation_name} operation: {func.__name__}")
                return result
                
            except Exception as e:
                logger.error(
                    f"Failed {operation_name} operation: {func.__name__}",
                    extra={"error": str(e), "operation": operation_name}
                )
                raise
                
        return wrapper
    return decorator


# Convenience decorators for common operations
def safe_json_load(func: Callable) -> Callable:
    """Decorator for safe JSON loading operations."""
    return safe_file_operation("JSON loading", max_retries=2)(func)


def safe_file_write(func: Callable) -> Callable:
    """Decorator for safe file writing operations."""
    return safe_file_operation("file writing", max_retries=3, circuit_breaker=True)(func)


def safe_directory_scan(func: Callable) -> Callable:
    """Decorator for safe directory scanning operations."""
    return safe_file_operation("directory scanning", max_retries=2)(func)


# Context manager for retryable operations
class RetryableOperation:
    """Context manager for operations that need retry logic."""
    
    def __init__(
        self,
        operation_name: str,
        max_retries: int = 3,
        base_delay: float = 1.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        """Initialize retryable operation context.
        
        Args:
            operation_name: Name for logging
            max_retries: Maximum retry attempts
            base_delay: Base delay between retries
            exceptions: Exception types to retry on
        """
        self.operation_name = operation_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exceptions = exceptions
        self.attempt = 0
        
    def __enter__(self) -> "RetryableOperation":
        """Enter context."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context with retry logic."""
        if exc_type and issubclass(exc_type, self.exceptions):
            self.attempt += 1
            
            if self.attempt <= self.max_retries:
                delay = self.base_delay * (2 ** (self.attempt - 1))
                logger.warning(
                    f"Operation {self.operation_name} failed on attempt {self.attempt}, "
                    f"retrying in {delay}s",
                    extra={"error": str(exc_val), "attempt": self.attempt}
                )
                time.sleep(delay)
                return True  # Suppress exception and retry
                
        return False  # Don't suppress exception
        
    def should_retry(self) -> bool:
        """Check if operation should be retried."""
        return self.attempt < self.max_retries