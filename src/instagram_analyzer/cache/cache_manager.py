"""Unified cache manager combining memory and disk caching.

This module provides the main CacheManager class that orchestrates
both memory and disk caching with intelligent fallback strategies.
"""

import hashlib
import json
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Union

from ..logging_config import get_logger
from .cache_config import CacheConfig
from .disk_cache import DiskCache
from .memory_cache import MemoryCache

logger = get_logger("cache_manager")


class CacheManager:
    """Unified cache manager with memory and disk backends.

    This class provides a high-level interface for caching with automatic
    fallback between memory and disk storage, intelligent cache warming,
    and comprehensive statistics.

    Features:
    - Two-tier caching (memory + disk)
    - Automatic cache warming
    - Intelligent key generation
    - Cache statistics and monitoring
    - Thread-safe operations
    - Configurable fallback strategies
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """Initialize cache manager.

        Args:
            config: Cache configuration (uses default if None)
        """
        self.config = config or CacheConfig()
        self._lock = threading.RLock()

        # Initialize cache backends
        self.memory_cache: Optional[MemoryCache] = None
        self.disk_cache: Optional[DiskCache] = None

        if self.config.memory_cache_enabled:
            self.memory_cache = MemoryCache(self.config)
            logger.info("Memory cache initialized")

        if self.config.disk_cache_enabled:
            try:
                self.disk_cache = DiskCache(self.config)
                logger.info("Disk cache initialized")
            except Exception as e:
                logger.error(f"Failed to initialize disk cache: {e}")
                self.config.disk_cache_enabled = False

        # Cache warming queue
        self._warming_queue: List[str] = []
        self._warming_thread: Optional[threading.Thread] = None

        if self.config.cache_warming_enabled:
            self._start_warming_thread()

        # Statistics
        self._global_stats = {
            "requests": 0,
            "hits": 0,
            "misses": 0,
            "memory_hits": 0,
            "disk_hits": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0,
        }

        logger.info(f"Cache manager initialized with config: {self.config.to_dict()}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with automatic fallback.

        Tries memory cache first, then disk cache, with automatic
        promotion of disk-cached items to memory.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        with self._lock:
            self._global_stats["requests"] += 1

            try:
                # Try memory cache first
                if self.memory_cache:
                    value = self.memory_cache.get(key)
                    if value is not None:
                        self._global_stats["hits"] += 1
                        self._global_stats["memory_hits"] += 1
                        return value

                # Try disk cache
                if self.disk_cache:
                    value = self.disk_cache.get(key)
                    if value is not None:
                        self._global_stats["hits"] += 1
                        self._global_stats["disk_hits"] += 1

                        # Promote to memory cache if enabled
                        if self.memory_cache and self.config.memory_cache_enabled:
                            self.memory_cache.set(key, value)

                        return value

                # Not found in any cache
                self._global_stats["misses"] += 1
                return default

            except Exception as e:
                logger.error(f"Error getting cached value for key {key}: {e}")
                self._global_stats["errors"] += 1
                return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        memory_only: bool = False,
        disk_only: bool = False,
        force_compression: bool = False,
    ) -> bool:
        """Set value in cache with flexible storage options.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            memory_only: Store only in memory cache
            disk_only: Store only in disk cache
            force_compression: Force compression for disk storage

        Returns:
            True if at least one cache operation succeeded
        """
        with self._lock:
            self._global_stats["sets"] += 1
            success = False

            try:
                # Generate consistent key
                cache_key = self._generate_cache_key(key)

                # Store in memory cache
                if (
                    self.memory_cache
                    and self.config.memory_cache_enabled
                    and not disk_only
                ):
                    if self.memory_cache.set(cache_key, value, ttl):
                        success = True
                    else:
                        logger.warning(f"Failed to store key {key} in memory cache")

                # Store in disk cache
                if self.disk_cache and self.config.disk_cache_enabled and not memory_only:
                    if self.disk_cache.set(cache_key, value, ttl, force_compression):
                        success = True
                    else:
                        logger.warning(f"Failed to store key {key} in disk cache")

                # Add to warming queue if configured
                if success and self.config.cache_warming_enabled:
                    self._add_to_warming_queue(cache_key)

                return success

            except Exception as e:
                logger.error(f"Error setting cached value for key {key}: {e}")
                self._global_stats["errors"] += 1
                return False

    def delete(self, key: str) -> bool:
        """Delete key from all cache layers.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted from at least one cache
        """
        with self._lock:
            self._global_stats["deletes"] += 1
            cache_key = self._generate_cache_key(key)
            success = False

            try:
                # Delete from memory cache
                if self.memory_cache:
                    if self.memory_cache.delete(cache_key):
                        success = True

                # Delete from disk cache
                if self.disk_cache:
                    if self.disk_cache.delete(cache_key):
                        success = True

                return success

            except Exception as e:
                logger.error(f"Error deleting cached key {key}: {e}")
                self._global_stats["errors"] += 1
                return False

    def exists(self, key: str) -> bool:
        """Check if key exists in any cache layer.

        Args:
            key: Cache key to check

        Returns:
            True if key exists in any cache
        """
        cache_key = self._generate_cache_key(key)

        try:
            # Check memory cache first
            if self.memory_cache and self.memory_cache.exists(cache_key):
                return True

            # Check disk cache
            if self.disk_cache and self.disk_cache.exists(cache_key):
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking if key {key} exists: {e}")
            return False

    def clear(self, memory_only: bool = False, disk_only: bool = False) -> None:
        """Clear cache entries.

        Args:
            memory_only: Clear only memory cache
            disk_only: Clear only disk cache
        """
        with self._lock:
            try:
                if not disk_only and self.memory_cache:
                    self.memory_cache.clear()
                    logger.info("Memory cache cleared")

                if not memory_only and self.disk_cache:
                    self.disk_cache.clear()
                    logger.info("Disk cache cleared")

                # Clear warming queue
                self._warming_queue.clear()

            except Exception as e:
                logger.error(f"Error clearing cache: {e}")

    def keys(self, include_memory: bool = True, include_disk: bool = True) -> Set[str]:
        """Get all cache keys from specified layers.

        Args:
            include_memory: Include memory cache keys
            include_disk: Include disk cache keys

        Returns:
            Set of all cache keys
        """
        all_keys = set()

        try:
            if include_memory and self.memory_cache:
                all_keys.update(self.memory_cache.keys())

            if include_disk and self.disk_cache:
                all_keys.update(self.disk_cache.keys())

        except Exception as e:
            logger.error(f"Error getting cache keys: {e}")

        return all_keys

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics.

        Returns:
            Dictionary with cache statistics from all layers
        """
        stats = {
            "global": self._global_stats.copy(),
            "memory": {},
            "disk": {},
            "config": self.config.to_dict(),
        }

        # Calculate global hit rate
        total_requests = self._global_stats["requests"]
        if total_requests > 0:
            stats["global"]["hit_rate"] = self._global_stats["hits"] / total_requests
            stats["global"]["memory_hit_rate"] = (
                self._global_stats["memory_hits"] / total_requests
            )
            stats["global"]["disk_hit_rate"] = (
                self._global_stats["disk_hits"] / total_requests
            )
        else:
            stats["global"]["hit_rate"] = 0.0
            stats["global"]["memory_hit_rate"] = 0.0
            stats["global"]["disk_hit_rate"] = 0.0

        # Get backend-specific stats
        try:
            if self.memory_cache:
                stats["memory"] = self.memory_cache.get_stats()

            if self.disk_cache:
                stats["disk"] = self.disk_cache.get_stats()

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")

        return stats

    def warm_cache(self, keys: List[str], loader_func: Callable[[str], Any]) -> int:
        """Warm cache with pre-loaded data.

        Args:
            keys: List of keys to warm
            loader_func: Function to load data for each key

        Returns:
            Number of keys successfully warmed
        """
        warmed_count = 0

        for key in keys:
            try:
                if not self.exists(key):
                    value = loader_func(key)
                    if self.set(key, value):
                        warmed_count += 1

            except Exception as e:
                logger.error(f"Error warming cache for key {key}: {e}")

        logger.info(f"Cache warming completed: {warmed_count}/{len(keys)} keys loaded")
        return warmed_count

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern.

        Args:
            pattern: Pattern to match (simple wildcard support)

        Returns:
            Number of keys invalidated
        """
        invalidated_count = 0
        all_keys = self.keys()

        for key in all_keys:
            if self._key_matches_pattern(key, pattern):
                if self.delete(key):
                    invalidated_count += 1

        logger.info(f"Invalidated {invalidated_count} keys matching pattern: {pattern}")
        return invalidated_count

    def _generate_cache_key(self, key: str) -> str:
        """Generate consistent cache key with versioning.

        Args:
            key: Original key

        Returns:
            Versioned cache key
        """
        # Include cache version in key for invalidation
        versioned_key = f"{self.config.cache_version}:{key}"

        # Hash long keys to ensure they fit within limits
        if len(versioned_key) > self.config.max_key_length:
            hash_obj = hashlib.sha256(versioned_key.encode())
            return f"{self.config.cache_version}:{hash_obj.hexdigest()}"

        return versioned_key

    def _add_to_warming_queue(self, key: str) -> None:
        """Add key to cache warming queue."""
        if len(self._warming_queue) < 1000:  # Prevent unbounded growth
            self._warming_queue.append(key)

    def _start_warming_thread(self) -> None:
        """Start cache warming thread."""

        def warming_worker():
            while True:
                try:
                    time.sleep(60)  # Check every minute

                    if self._warming_queue:
                        # Process warming queue
                        keys_to_warm = self._warming_queue[:10]  # Process in batches
                        self._warming_queue = self._warming_queue[10:]

                        for key in keys_to_warm:
                            # Simple warming strategy: promote from disk to memory
                            if (
                                self.disk_cache
                                and self.memory_cache
                                and self.disk_cache.exists(key)
                                and not self.memory_cache.exists(key)
                            ):
                                value = self.disk_cache.get(key)
                                if value is not None:
                                    self.memory_cache.set(key, value)

                except Exception as e:
                    logger.error(f"Error in cache warming thread: {e}")

        self._warming_thread = threading.Thread(target=warming_worker, daemon=True)
        self._warming_thread.start()

    def _key_matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches simple wildcard pattern.

        Args:
            key: Cache key
            pattern: Pattern with * wildcards

        Returns:
            True if key matches pattern
        """
        # Simple wildcard matching
        if "*" not in pattern:
            return key == pattern

        # Convert pattern to regex-like matching
        parts = pattern.split("*")
        if not key.startswith(parts[0]):
            return False

        current_pos = len(parts[0])
        for part in parts[1:-1]:
            pos = key.find(part, current_pos)
            if pos == -1:
                return False
            current_pos = pos + len(part)

        if parts[-1] and not key.endswith(parts[-1]):
            return False

        return True

    def __enter__(self) -> "CacheManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        # Cleanup if needed
        pass

    def __len__(self) -> int:
        """Return total number of cached items."""
        total = 0
        if self.memory_cache:
            total += len(self.memory_cache)
        if self.disk_cache:
            total += self.disk_cache.entry_count()
        return total
