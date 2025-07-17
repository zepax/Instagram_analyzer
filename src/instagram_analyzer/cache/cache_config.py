"""Cache configuration management.

This module provides configuration classes and utilities for managing
cache behavior, limits, and storage options.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Union


@dataclass
class CacheConfig:
    """Configuration for the caching system.

    This class defines all configurable aspects of the caching system
    including memory limits, storage paths, and behavior settings.

    Attributes:
        memory_limit: Maximum memory usage for in-memory cache (bytes)
        disk_cache_dir: Directory for disk-based cache storage
        disk_limit: Maximum disk usage for cache (bytes)
        default_ttl: Default time-to-live for cached items (seconds)
        compression_enabled: Whether to compress large cached objects
        compression_threshold: Minimum size to trigger compression (bytes)
        max_key_length: Maximum length for cache keys
        stats_enabled: Whether to collect cache statistics
        cleanup_interval: How often to run cache cleanup (seconds)
        memory_cache_enabled: Whether to use memory caching
        disk_cache_enabled: Whether to use disk caching
        prefetch_enabled: Whether to enable intelligent prefetching
        cache_version: Version string for cache invalidation
    """

    # Memory cache settings
    memory_limit: int = 256 * 1024 * 1024  # 256MB default
    memory_cache_enabled: bool = True

    # Disk cache settings
    disk_cache_dir: Optional[Path] = None
    disk_limit: int = 2 * 1024 * 1024 * 1024  # 2GB default
    disk_cache_enabled: bool = True

    # TTL settings
    default_ttl: int = 3600  # 1 hour default
    max_ttl: int = 24 * 3600  # 24 hours max

    # Compression settings
    compression_enabled: bool = True
    compression_threshold: int = 1024  # 1KB threshold
    compression_level: int = 6  # Balance of speed vs size

    # Cache behavior
    max_key_length: int = 250
    stats_enabled: bool = True
    cleanup_interval: int = 300  # 5 minutes
    prefetch_enabled: bool = True

    # Cache versioning
    cache_version: str = "1.0"

    # Advanced settings
    concurrent_cleanup: bool = True
    cache_warming_enabled: bool = False
    eviction_policy: str = "lru"  # lru, lfu, fifo

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Set default disk cache directory if not provided
        if self.disk_cache_dir is None:
            self.disk_cache_dir = Path.home() / ".instagram_analyzer" / "cache"

        # Ensure disk cache directory is a Path object
        if isinstance(self.disk_cache_dir, str):
            self.disk_cache_dir = Path(self.disk_cache_dir)

        # Validate configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate configuration settings."""
        if self.memory_limit < 0:
            raise ValueError("Memory limit cannot be negative")

        if self.disk_limit < 0:
            raise ValueError("Disk limit cannot be negative")

        if self.default_ttl < 0:
            raise ValueError("Default TTL cannot be negative")

        if self.max_ttl < self.default_ttl:
            raise ValueError("Max TTL cannot be less than default TTL")

        if self.compression_level < 1 or self.compression_level > 9:
            raise ValueError("Compression level must be between 1 and 9")

        if self.eviction_policy not in ("lru", "lfu", "fifo"):
            raise ValueError("Eviction policy must be 'lru', 'lfu', or 'fifo'")

    def ensure_cache_directory(self) -> None:
        """Ensure cache directory exists."""
        if self.disk_cache_enabled and self.disk_cache_dir:
            self.disk_cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_size_mb(self, size_bytes: int) -> float:
        """Convert bytes to megabytes for display."""
        return size_bytes / (1024 * 1024)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "memory_limit": self.memory_limit,
            "memory_limit_mb": self.get_cache_size_mb(self.memory_limit),
            "disk_cache_dir": str(self.disk_cache_dir),
            "disk_limit": self.disk_limit,
            "disk_limit_mb": self.get_cache_size_mb(self.disk_limit),
            "default_ttl": self.default_ttl,
            "max_ttl": self.max_ttl,
            "compression_enabled": self.compression_enabled,
            "compression_threshold": self.compression_threshold,
            "compression_level": self.compression_level,
            "max_key_length": self.max_key_length,
            "stats_enabled": self.stats_enabled,
            "cleanup_interval": self.cleanup_interval,
            "memory_cache_enabled": self.memory_cache_enabled,
            "disk_cache_enabled": self.disk_cache_enabled,
            "prefetch_enabled": self.prefetch_enabled,
            "cache_version": self.cache_version,
            "concurrent_cleanup": self.concurrent_cleanup,
            "cache_warming_enabled": self.cache_warming_enabled,
            "eviction_policy": self.eviction_policy,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheConfig":
        """Create configuration from dictionary."""
        # Convert string path back to Path object
        if "disk_cache_dir" in data and isinstance(data["disk_cache_dir"], str):
            data["disk_cache_dir"] = Path(data["disk_cache_dir"])

        # Remove display-only fields
        data.pop("memory_limit_mb", None)
        data.pop("disk_limit_mb", None)

        return cls(**data)

    @classmethod
    def from_env(cls) -> "CacheConfig":
        """Create configuration from environment variables."""
        config_dict = {}

        # Memory settings
        if memory_limit := os.getenv("INSTAGRAM_CACHE_MEMORY_LIMIT"):
            config_dict["memory_limit"] = int(memory_limit)

        if memory_enabled := os.getenv("INSTAGRAM_CACHE_MEMORY_ENABLED"):
            config_dict["memory_cache_enabled"] = memory_enabled.lower() == "true"

        # Disk settings
        if disk_dir := os.getenv("INSTAGRAM_CACHE_DISK_DIR"):
            config_dict["disk_cache_dir"] = Path(disk_dir)

        if disk_limit := os.getenv("INSTAGRAM_CACHE_DISK_LIMIT"):
            config_dict["disk_limit"] = int(disk_limit)

        if disk_enabled := os.getenv("INSTAGRAM_CACHE_DISK_ENABLED"):
            config_dict["disk_cache_enabled"] = disk_enabled.lower() == "true"

        # TTL settings
        if default_ttl := os.getenv("INSTAGRAM_CACHE_DEFAULT_TTL"):
            config_dict["default_ttl"] = int(default_ttl)

        if max_ttl := os.getenv("INSTAGRAM_CACHE_MAX_TTL"):
            config_dict["max_ttl"] = int(max_ttl)

        # Compression settings
        if compression := os.getenv("INSTAGRAM_CACHE_COMPRESSION"):
            config_dict["compression_enabled"] = compression.lower() == "true"

        if compression_level := os.getenv("INSTAGRAM_CACHE_COMPRESSION_LEVEL"):
            config_dict["compression_level"] = int(compression_level)

        # Cache version
        if version := os.getenv("INSTAGRAM_CACHE_VERSION"):
            config_dict["cache_version"] = version

        return cls(**config_dict)


# Predefined configurations for different use cases
class CachePresets:
    """Predefined cache configurations for different scenarios."""

    @staticmethod
    def development() -> CacheConfig:
        """Configuration optimized for development."""
        return CacheConfig(
            memory_limit=64 * 1024 * 1024,  # 64MB
            disk_limit=500 * 1024 * 1024,  # 500MB
            default_ttl=600,  # 10 minutes
            compression_enabled=False,  # Faster for dev
            stats_enabled=True,
            cleanup_interval=60,  # More frequent cleanup
            cache_warming_enabled=False,
        )

    @staticmethod
    def production() -> CacheConfig:
        """Configuration optimized for production."""
        return CacheConfig(
            memory_limit=512 * 1024 * 1024,  # 512MB
            disk_limit=5 * 1024 * 1024 * 1024,  # 5GB
            default_ttl=3600,  # 1 hour
            max_ttl=12 * 3600,  # 12 hours
            compression_enabled=True,
            compression_level=6,
            stats_enabled=True,
            cleanup_interval=300,  # 5 minutes
            cache_warming_enabled=True,
            prefetch_enabled=True,
        )

    @staticmethod
    def memory_constrained() -> CacheConfig:
        """Configuration for memory-constrained environments."""
        return CacheConfig(
            memory_limit=32 * 1024 * 1024,  # 32MB
            disk_limit=1 * 1024 * 1024 * 1024,  # 1GB
            default_ttl=1800,  # 30 minutes
            compression_enabled=True,
            compression_level=9,  # Maximum compression
            compression_threshold=512,  # Lower threshold
            stats_enabled=False,  # Reduce overhead
            cleanup_interval=120,  # More aggressive cleanup
            cache_warming_enabled=False,
        )

    @staticmethod
    def high_performance() -> CacheConfig:
        """Configuration optimized for maximum performance."""
        return CacheConfig(
            memory_limit=1024 * 1024 * 1024,  # 1GB
            disk_limit=10 * 1024 * 1024 * 1024,  # 10GB
            default_ttl=7200,  # 2 hours
            max_ttl=24 * 3600,  # 24 hours
            compression_enabled=False,  # No compression overhead
            stats_enabled=True,
            cleanup_interval=600,  # Less frequent cleanup
            cache_warming_enabled=True,
            prefetch_enabled=True,
            concurrent_cleanup=True,
        )

    @staticmethod
    def minimal() -> CacheConfig:
        """Minimal cache configuration."""
        return CacheConfig(
            memory_limit=16 * 1024 * 1024,  # 16MB
            disk_cache_enabled=False,  # Memory only
            default_ttl=300,  # 5 minutes
            compression_enabled=False,
            stats_enabled=False,
            cleanup_interval=60,
            cache_warming_enabled=False,
            prefetch_enabled=False,
        )
