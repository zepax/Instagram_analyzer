"""In-memory cache implementation with LRU eviction.

This module provides a high-performance, thread-safe in-memory cache
with configurable eviction policies and advanced features.
"""

import gc
import sys
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Optional, Set, TypeVar

from ..logging_config import get_logger
from .cache_config import CacheConfig

logger = get_logger("memory_cache")

T = TypeVar("T")


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""

    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    ttl: Optional[int]
    size_bytes: int

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self) -> None:
        """Update access time and count."""
        self.last_accessed = time.time()
        self.access_count += 1


class MemoryCache(Generic[T]):
    """Thread-safe in-memory cache with configurable eviction policies.

    Features:
    - Multiple eviction policies (LRU, LFU, FIFO)
    - TTL-based expiration
    - Memory usage tracking
    - Thread-safe operations
    - Cache statistics
    - Weak reference support for large objects
    """

    def __init__(self, config: CacheConfig):
        """Initialize memory cache.

        Args:
            config: Cache configuration object
        """
        self.config = config
        self._data: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._current_size = 0
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0,
            "expirations": 0,
            "size_bytes": 0,
            "entry_count": 0,
        }

        # Weak references for memory management
        self._weak_refs: dict[str, weakref.ref] = {}

        # Start cleanup thread if enabled
        if config.cleanup_interval > 0:
            self._cleanup_thread = threading.Thread(
                target=self._periodic_cleanup, daemon=True
            )
            self._cleanup_thread.start()
        else:
            self._cleanup_thread = None

    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        with self._lock:
            if key not in self._data:
                self._stats["misses"] += 1
                return default

            entry = self._data[key]

            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self._stats["misses"] += 1
                self._stats["expirations"] += 1
                return default

            # Update access info
            entry.touch()

            # Move to end for LRU (most recently used)
            if self.config.eviction_policy == "lru":
                self._data.move_to_end(key)

            self._stats["hits"] += 1
            return entry.value

    def set(
        self, key: str, value: T, ttl: Optional[int] = None, use_weak_ref: bool = False
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (overrides default)
            use_weak_ref: Whether to use weak reference for large objects

        Returns:
            True if value was cached successfully
        """
        if len(key) > self.config.max_key_length:
            logger.warning(
                f"Cache key too long: {len(key)} > {self.config.max_key_length}"
            )
            return False

        # Calculate object size
        size_bytes = self._get_object_size(value)

        # Check if single object exceeds memory limit
        if size_bytes > self.config.memory_limit:
            logger.warning(
                f"Object too large for cache: {size_bytes} > {self.config.memory_limit}"
            )
            return False

        with self._lock:
            current_time = time.time()

            # Use provided TTL or default
            effective_ttl = ttl if ttl is not None else self.config.default_ttl
            if effective_ttl > self.config.max_ttl:
                effective_ttl = self.config.max_ttl

            # Remove existing entry if present
            if key in self._data:
                self._remove_entry(key)

            # Make space if needed
            self._evict_if_needed(size_bytes)

            # Store value (possibly as weak reference)
            stored_value = value
            if use_weak_ref and hasattr(value, "__weakref__"):
                weak_ref = weakref.ref(value, lambda ref: self._cleanup_weak_ref(key))
                self._weak_refs[key] = weak_ref
                stored_value = weak_ref

            # Create cache entry
            entry = CacheEntry(
                value=stored_value,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                ttl=effective_ttl,
                size_bytes=size_bytes,
            )

            # Add to cache
            self._data[key] = entry
            self._current_size += size_bytes
            self._stats["sets"] += 1
            self._update_stats()

            return True

    def delete(self, key: str) -> bool:
        """Delete entry from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted
        """
        with self._lock:
            if key in self._data:
                self._remove_entry(key)
                self._stats["deletes"] += 1
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._data.clear()
            self._weak_refs.clear()
            self._current_size = 0
            self._update_stats()
            logger.info("Memory cache cleared")

    def exists(self, key: str) -> bool:
        """Check if key exists in cache (without updating access stats).

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            if key not in self._data:
                return False

            entry = self._data[key]
            if entry.is_expired():
                self._remove_entry(key)
                return False

            return True

    def keys(self) -> set[str]:
        """Get all non-expired cache keys.

        Returns:
            Set of cache keys
        """
        with self._lock:
            # Remove expired entries first
            self._cleanup_expired()
            return set(self._data.keys())

    def size(self) -> int:
        """Get current cache size in bytes.

        Returns:
            Current cache size in bytes
        """
        return self._current_size

    def entry_count(self) -> int:
        """Get number of entries in cache.

        Returns:
            Number of cache entries
        """
        return len(self._data)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            hit_rate = 0.0
            total_requests = self._stats["hits"] + self._stats["misses"]
            if total_requests > 0:
                hit_rate = self._stats["hits"] / total_requests

            return {
                **self._stats,
                "hit_rate": hit_rate,
                "memory_usage_pct": (self._current_size / self.config.memory_limit) * 100,
                "avg_entry_size": self._current_size / max(1, len(self._data)),
            }

    def _get_object_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return sys.getsizeof(obj)
        except (TypeError, RecursionError):
            # Fallback for complex objects
            return 1024  # Conservative estimate

    def _evict_if_needed(self, new_size: int) -> None:
        """Evict entries if needed to make space."""
        while (
            self._current_size + new_size > self.config.memory_limit
            and len(self._data) > 0
        ):
            if self.config.eviction_policy == "lru":
                # Remove least recently used (first item)
                key = next(iter(self._data))
            elif self.config.eviction_policy == "lfu":
                # Remove least frequently used
                key = min(self._data.keys(), key=lambda k: self._data[k].access_count)
            else:  # FIFO
                # Remove oldest entry
                key = min(self._data.keys(), key=lambda k: self._data[k].created_at)

            self._remove_entry(key)
            self._stats["evictions"] += 1

    def _remove_entry(self, key: str) -> None:
        """Remove entry and update size tracking."""
        if key in self._data:
            entry = self._data.pop(key)
            self._current_size -= entry.size_bytes

            # Clean up weak reference if exists
            if key in self._weak_refs:
                del self._weak_refs[key]

            self._update_stats()

    def _cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        removed_count = 0
        expired_keys = []

        for key, entry in self._data.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            self._remove_entry(key)
            removed_count += 1

        if removed_count > 0:
            self._stats["expirations"] += removed_count
            logger.debug(f"Cleaned up {removed_count} expired cache entries")

        return removed_count

    def _cleanup_weak_ref(self, key: str) -> None:
        """Callback for when weak reference is garbage collected."""
        with self._lock:
            if key in self._data:
                self._remove_entry(key)
                logger.debug(f"Cleaned up weak reference for key: {key}")

    def _periodic_cleanup(self) -> None:
        """Periodic cleanup thread function."""
        while True:
            try:
                time.sleep(self.config.cleanup_interval)

                with self._lock:
                    # Clean up expired entries
                    expired_count = self._cleanup_expired()

                    # Force garbage collection periodically
                    if expired_count > 10:
                        gc.collect()

            except Exception as e:
                logger.error(f"Error in cache cleanup thread: {e}")

    def _update_stats(self) -> None:
        """Update internal statistics."""
        self._stats["size_bytes"] = self._current_size
        self._stats["entry_count"] = len(self._data)

    def __len__(self) -> int:
        """Return number of cache entries."""
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache."""
        return self.exists(key)

    def __getitem__(self, key: str) -> T:
        """Get item using dictionary syntax."""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result

    def __setitem__(self, key: str, value: T) -> None:
        """Set item using dictionary syntax."""
        self.set(key, value)

    def __delitem__(self, key: str) -> None:
        """Delete item using dictionary syntax."""
        if not self.delete(key):
            raise KeyError(key)
