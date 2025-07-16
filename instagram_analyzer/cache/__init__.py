"""Caching system for Instagram Analyzer.

This package provides a comprehensive caching system with multiple cache backends,
intelligent cache invalidation, and performance optimization for large datasets.

Features:
- Memory and disk-based caching
- TTL-based expiration
- Cache invalidation strategies
- Compressed storage for large objects
- Thread-safe operations
- Cache statistics and monitoring

Example:
    Basic usage:
    
    >>> cache = CacheManager()
    >>> cache.set("key", {"data": "value"}, ttl=3600)
    >>> result = cache.get("key")
    
    Advanced configuration:
    
    >>> config = CacheConfig(
    ...     memory_limit=512*1024*1024,  # 512MB
    ...     disk_cache_dir="/tmp/instagram_cache",
    ...     compression_enabled=True
    ... )
    >>> cache = CacheManager(config)
"""

from .cache_manager import CacheManager
from .memory_cache import MemoryCache
from .disk_cache import DiskCache
from .cache_config import CacheConfig, CachePresets
from .cache_decorators import (
    cached,
    cached_analysis,
    cached_parsing,
    cache_invalidate,
    cache_clear,
)

__all__ = [
    "CacheManager",
    "MemoryCache", 
    "DiskCache",
    "CacheConfig",
    "CachePresets",
    "cached",
    "cached_analysis",
    "cached_parsing",
    "cache_invalidate",
    "cache_clear",
]