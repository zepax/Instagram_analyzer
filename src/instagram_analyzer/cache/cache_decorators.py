"""Cache decorators for easy integration.

This module provides decorators for caching function results with
intelligent key generation and configurable cache behavior.
"""

import functools
import hashlib
import inspect
import json
import pickle
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..logging_config import get_logger
from .cache_config import CacheConfig
from .cache_manager import CacheManager

logger = get_logger("cache_decorators")

# Global cache manager instance
_default_cache_manager: Optional[CacheManager] = None


def get_default_cache_manager() -> CacheManager:
    """Get or create the default cache manager."""
    global _default_cache_manager
    if _default_cache_manager is None:
        _default_cache_manager = CacheManager()
    return _default_cache_manager


def set_default_cache_manager(cache_manager: CacheManager) -> None:
    """Set the default cache manager."""
    global _default_cache_manager
    _default_cache_manager = cache_manager


def cached(
    ttl: Optional[int] = None,
    cache_manager: Optional[CacheManager] = None,
    key_prefix: Optional[str] = None,
    include_args: bool = True,
    include_kwargs: bool = True,
    exclude_args: Optional[List[str]] = None,
    memory_only: bool = False,
    disk_only: bool = False,
    force_compression: bool = False,
    cache_none: bool = False,
    cache_exceptions: bool = False,
) -> Callable:
    """General-purpose caching decorator.

    Args:
        ttl: Time to live in seconds
        cache_manager: Cache manager to use (default if None)
        key_prefix: Prefix for cache keys
        include_args: Include positional arguments in cache key
        include_kwargs: Include keyword arguments in cache key
        exclude_args: Argument names to exclude from cache key
        memory_only: Store only in memory cache
        disk_only: Store only in disk cache
        force_compression: Force compression for disk storage
        cache_none: Whether to cache None results
        cache_exceptions: Whether to cache exception results

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        cache_mgr = cache_manager or get_default_cache_manager()
        exclude_set = set(exclude_args or [])

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_function_cache_key(
                func,
                args,
                kwargs,
                key_prefix,
                include_args,
                include_kwargs,
                exclude_set,
            )

            # Try to get cached result
            try:
                cached_result = cache_mgr.get(cache_key)
                if cached_result is not None:
                    # Handle cached exceptions
                    if isinstance(cached_result, dict) and cached_result.get(
                        "__cached_exception__"
                    ):
                        exception_data = cached_result["exception_data"]
                        exception_class = exception_data["class"]
                        exception_args = exception_data["args"]
                        raise exception_class(*exception_args)

                    logger.debug(f"Cache hit for function {func.__name__}")
                    return cached_result

            except Exception as e:
                logger.error(f"Error retrieving cached result for {func.__name__}: {e}")

            # Execute function
            try:
                result = func(*args, **kwargs)

                # Cache the result if appropriate
                should_cache = (
                    result is not None or cache_none
                ) and result is not ...  # Don't cache Ellipsis

                if should_cache:
                    try:
                        cache_mgr.set(
                            cache_key,
                            result,
                            ttl=ttl,
                            memory_only=memory_only,
                            disk_only=disk_only,
                            force_compression=force_compression,
                        )
                        logger.debug(f"Cached result for function {func.__name__}")
                    except Exception as e:
                        logger.error(f"Error caching result for {func.__name__}: {e}")

                return result

            except Exception as e:
                # Cache exceptions if requested
                if cache_exceptions:
                    try:
                        exception_data = {
                            "__cached_exception__": True,
                            "exception_data": {
                                "class": type(e),
                                "args": e.args,
                                "str": str(e),
                            },
                        }
                        cache_mgr.set(
                            cache_key,
                            exception_data,
                            ttl=ttl,
                            memory_only=memory_only,
                            disk_only=disk_only,
                        )
                        logger.debug(f"Cached exception for function {func.__name__}")
                    except Exception as cache_error:
                        logger.error(
                            f"Error caching exception for {func.__name__}: {cache_error}"
                        )

                raise

        # Add cache management methods to the wrapper
        wrapper.cache_clear = lambda: _clear_function_cache(func, cache_mgr, key_prefix)
        wrapper.cache_info = lambda: _get_function_cache_info(func, cache_mgr, key_prefix)
        wrapper.cache_invalidate = lambda *args, **kwargs: _invalidate_function_cache(
            func,
            cache_mgr,
            args,
            kwargs,
            key_prefix,
            include_args,
            include_kwargs,
            exclude_set,
        )

        return wrapper

    return decorator


def cached_analysis(
    ttl: int = 3600, include_data_hash: bool = True, **kwargs
) -> Callable:
    """Specialized caching decorator for analysis functions.

    Args:
        ttl: Time to live (default 1 hour for analysis)
        include_data_hash: Include hash of data in cache key
        **kwargs: Additional arguments for @cached decorator

    Returns:
        Decorated function
    """
    return cached(
        ttl=ttl,
        key_prefix="analysis",
        disk_only=True,  # Analysis results are usually large
        force_compression=True,
        cache_none=False,
        **kwargs,
    )


def cached_parsing(ttl: int = 7200, **kwargs) -> Callable:
    """Specialized caching decorator for parsing functions.

    Args:
        ttl: Time to live (default 2 hours for parsing)
        **kwargs: Additional arguments for @cached decorator

    Returns:
        Decorated function
    """
    return cached(
        ttl=ttl,
        key_prefix="parsing",
        memory_only=False,  # Use both memory and disk
        cache_none=False,
        **kwargs,
    )


def cached_property(ttl: Optional[int] = None, **kwargs) -> Callable:
    """Caching decorator for class properties.

    Args:
        ttl: Time to live in seconds
        **kwargs: Additional arguments for @cached decorator

    Returns:
        Decorated property
    """

    def decorator(func: Callable) -> property:
        cached_func = cached(ttl=ttl, key_prefix=f"property_{func.__name__}", **kwargs)(
            func
        )

        return property(cached_func)

    return decorator


def cache_invalidate(
    pattern: Optional[str] = None, cache_manager: Optional[CacheManager] = None
) -> int:
    """Invalidate cache entries matching a pattern.

    Args:
        pattern: Pattern to match (None for all)
        cache_manager: Cache manager to use

    Returns:
        Number of entries invalidated
    """
    cache_mgr = cache_manager or get_default_cache_manager()

    if pattern is None:
        cache_mgr.clear()
        return -1  # All entries cleared
    else:
        return cache_mgr.invalidate_pattern(pattern)


def cache_clear(cache_manager: Optional[CacheManager] = None) -> None:
    """Clear all cache entries.

    Args:
        cache_manager: Cache manager to use
    """
    cache_mgr = cache_manager or get_default_cache_manager()
    cache_mgr.clear()


def cache_stats(cache_manager: Optional[CacheManager] = None) -> Dict[str, Any]:
    """Get cache statistics.

    Args:
        cache_manager: Cache manager to use

    Returns:
        Cache statistics dictionary
    """
    cache_mgr = cache_manager or get_default_cache_manager()
    return cache_mgr.get_stats()


def _generate_function_cache_key(
    func: Callable,
    args: tuple,
    kwargs: Dict[str, Any],
    key_prefix: Optional[str],
    include_args: bool,
    include_kwargs: bool,
    exclude_args: set,
) -> str:
    """Generate cache key for function call."""
    key_parts = []

    # Add prefix if provided
    if key_prefix:
        key_parts.append(key_prefix)

    # Add function name and module
    key_parts.append(f"{func.__module__}.{func.__qualname__}")

    # Add arguments if requested
    if include_args and args:
        # Get function signature to map args to parameter names
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Filter out excluded arguments
            filtered_args = {
                k: v for k, v in bound_args.arguments.items() if k not in exclude_args
            }

            # Create hashable representation
            hashable_args = _make_hashable(filtered_args)
            key_parts.append(str(hash(hashable_args)))

        except (TypeError, ValueError):
            # Fallback: hash args and kwargs separately
            if include_args:
                hashable_args = _make_hashable(args)
                key_parts.append(f"args_{hash(hashable_args)}")

            if include_kwargs:
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k not in exclude_args
                }
                hashable_kwargs = _make_hashable(filtered_kwargs)
                key_parts.append(f"kwargs_{hash(hashable_kwargs)}")

    # Join parts and hash if too long
    cache_key = ":".join(key_parts)

    # Hash long keys
    if len(cache_key) > 200:
        hash_obj = hashlib.sha256(cache_key.encode())
        cache_key = f"hashed:{hash_obj.hexdigest()}"

    return cache_key


def _make_hashable(obj: Any) -> Any:
    """Convert object to hashable form for cache key generation."""
    if isinstance(obj, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return tuple(_make_hashable(item) for item in obj)
    elif isinstance(obj, set):
        return tuple(sorted(_make_hashable(item) for item in obj))
    elif hasattr(obj, "__dict__"):
        # For objects with __dict__, use their attribute hash
        try:
            return tuple(sorted((k, _make_hashable(v)) for k, v in obj.__dict__.items()))
        except (TypeError, AttributeError):
            return str(obj)
    else:
        try:
            hash(obj)  # Test if already hashable
            return obj
        except TypeError:
            # Fallback to string representation
            return str(obj)


def _clear_function_cache(
    func: Callable, cache_manager: CacheManager, key_prefix: Optional[str]
) -> int:
    """Clear cache entries for a specific function."""
    pattern = f"{key_prefix or ''}*{func.__module__}.{func.__qualname__}*"
    return cache_manager.invalidate_pattern(pattern)


def _get_function_cache_info(
    func: Callable, cache_manager: CacheManager, key_prefix: Optional[str]
) -> Dict[str, Any]:
    """Get cache information for a specific function."""
    pattern = f"{key_prefix or ''}*{func.__module__}.{func.__qualname__}*"
    all_keys = cache_manager.keys()
    matching_keys = [
        key for key in all_keys if cache_manager._key_matches_pattern(key, pattern)
    ]

    return {
        "function": f"{func.__module__}.{func.__qualname__}",
        "cached_entries": len(matching_keys),
        "cache_keys": matching_keys[:10],  # Show first 10 keys
    }


def _invalidate_function_cache(
    func: Callable,
    cache_manager: CacheManager,
    args: tuple,
    kwargs: Dict[str, Any],
    key_prefix: Optional[str],
    include_args: bool,
    include_kwargs: bool,
    exclude_args: set,
) -> bool:
    """Invalidate cache entry for specific function call."""
    cache_key = _generate_function_cache_key(
        func, args, kwargs, key_prefix, include_args, include_kwargs, exclude_args
    )
    return cache_manager.delete(cache_key)


# Context manager for temporary cache configuration
class CacheContext:
    """Context manager for temporary cache configuration."""

    def __init__(self, config: CacheConfig):
        """Initialize cache context.

        Args:
            config: Temporary cache configuration
        """
        self.config = config
        self._original_cache_manager = None
        self._temp_cache_manager = None

    def __enter__(self) -> CacheManager:
        """Enter context with temporary cache configuration."""
        global _default_cache_manager

        # Save original cache manager
        self._original_cache_manager = _default_cache_manager

        # Create temporary cache manager
        self._temp_cache_manager = CacheManager(self.config)
        _default_cache_manager = self._temp_cache_manager

        return self._temp_cache_manager

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and restore original cache configuration."""
        global _default_cache_manager

        # Restore original cache manager
        _default_cache_manager = self._original_cache_manager
