"""Disk-based cache implementation with compression.

This module provides persistent disk caching with compression, atomic writes,
and efficient cleanup for large datasets.
"""

import hashlib
import pickle
import shutil
import sqlite3
import tempfile
import threading
import time
import zlib
from pathlib import Path
from typing import Any, Dict, Optional, Set

from ..logging_config import get_logger
from ..utils.retry_utils import safe_file_operation
from .cache_config import CacheConfig

logger = get_logger("disk_cache")


class DiskCache:
    """Persistent disk cache with compression and atomic operations.

    Features:
    - SQLite metadata database for fast lookups
    - Compressed storage for large objects
    - Atomic write operations
    - TTL-based expiration
    - Efficient cleanup and garbage collection
    - Directory size management
    """

    def __init__(self, config: CacheConfig):
        """Initialize disk cache.

        Args:
            config: Cache configuration object
        """
        self.config = config
        # Ensure cache_dir is not None
        self.cache_dir = (
            config.disk_cache_dir if config.disk_cache_dir else Path("./cache")
        )
        self.data_dir = self.cache_dir / "data"
        self.db_path = self.cache_dir / "cache.db"

        # Thread safety
        self._lock = threading.RLock()
        self._db_lock = threading.Lock()

        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "size_bytes": 0,
            "entry_count": 0,
            "compression_ratio": 0.0,
        }

        # Initialize cache
        self._initialize_cache()

        # Start cleanup thread
        if config.cleanup_interval > 0:
            self._cleanup_thread = threading.Thread(
                target=self._periodic_cleanup, daemon=True
            )
            self._cleanup_thread.start()

    def _initialize_cache(self) -> None:
        """Initialize cache directory and database."""
        try:
            # Create directories
            self.config.ensure_cache_directory()
            self.data_dir.mkdir(exist_ok=True)

            # Initialize SQLite database
            self._init_database()

            # Load current stats
            self._update_stats()

            logger.info("Disk cache initialized at %s", self.cache_dir)

        except Exception as e:
            logger.error("Failed to initialize disk cache: %s", e)
            raise

    def _init_database(self) -> None:
        """Initialize SQLite database for metadata."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        filename TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        last_accessed REAL NOT NULL,
                        access_count INTEGER DEFAULT 1,
                        ttl INTEGER,
                        size_bytes INTEGER NOT NULL,
                        compressed BOOLEAN DEFAULT FALSE,
                        compression_ratio REAL DEFAULT 1.0
                    )
                """
                )

                # Create indexes for performance
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_created_at
                    ON cache_entries(created_at)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_last_accessed
                    ON cache_entries(last_accessed)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_ttl_created
                    ON cache_entries(ttl, created_at)
                """
                )

                conn.commit()
            finally:
                conn.close()

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from disk cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        with self._lock:
            # Check if key exists and is not expired
            entry_info = self._get_entry_info(key)
            if not entry_info:
                self._stats["misses"] += 1
                return default

            # Check expiration
            if self._is_expired(entry_info):
                self._remove_entry(key, entry_info["filename"])
                self._stats["misses"] += 1
                return default

            # Load data from disk
            try:
                data = self._load_data(entry_info["filename"], entry_info["compressed"])

                # Update access info
                self._update_access_info(key)

                self._stats["hits"] += 1
                return data

            except Exception as e:
                logger.error("Failed to load cached data for key %s: %s", key, e)
                # Remove corrupted entry
                self._remove_entry(key, entry_info["filename"])
                self._stats["misses"] += 1
                return default

    def store(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        force_compression: bool = False,
    ) -> bool:
        """Set value in disk cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            force_compression: Force compression regardless of size

        Returns:
            True if value was cached successfully
        """
        if len(key) > self.config.max_key_length:
            logger.warning(
                "Cache key too long: %d > %d", len(key), self.config.max_key_length
            )
            return False

        with self._lock:
            try:
                # Generate filename
                filename = self._generate_filename(key)
                file_path = self.data_dir / filename

                # Serialize and optionally compress data
                serialized_data = pickle.dumps(value)
                original_size = len(serialized_data)

                should_compress = force_compression or (
                    self.config.compression_enabled
                    and original_size >= self.config.compression_threshold
                )

                if should_compress:
                    compressed_data = zlib.compress(
                        serialized_data, level=self.config.compression_level
                    )
                    final_data = compressed_data
                    compressed = True
                    compression_ratio = len(compressed_data) / original_size
                else:
                    final_data = serialized_data
                    compressed = False
                    compression_ratio = 1.0

                # Check disk space
                if not self._check_disk_space(len(final_data)):
                    self._evict_entries(len(final_data))

                # Write data atomically
                if not self._write_data_atomic(file_path, final_data):
                    return False

                # Update database
                current_time = time.time()
                effective_ttl = ttl if ttl is not None else self.config.default_ttl

                # Remove existing entry if present
                existing_info = self._get_entry_info(key)
                if existing_info:
                    self._remove_entry(key, existing_info["filename"])

                # Insert new entry
                with self._db_lock:
                    conn = sqlite3.connect(str(self.db_path))
                    try:
                        conn.execute(
                            """
                            INSERT INTO cache_entries
                            (key, filename, created_at, last_accessed, ttl,
                             size_bytes, compressed, compression_ratio)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                key,
                                filename,
                                current_time,
                                current_time,
                                effective_ttl,
                                len(final_data),
                                compressed,
                                compression_ratio,
                            ),
                        )
                        conn.commit()
                    finally:
                        conn.close()

                self._stats["sets"] += 1
                self._update_stats()

                return True

            except Exception as e:
                logger.error("Failed to cache data for key %s: %s", key, e)
                return False

    # Alias for backward compatibility
    set = store

    def delete(self, key: str) -> bool:
        """Delete entry from disk cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted
        """
        with self._lock:
            entry_info = self._get_entry_info(key)
            if entry_info:
                self._remove_entry(key, entry_info["filename"])
                self._stats["deletes"] += 1
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from disk cache."""
        with self._lock:
            try:
                # Remove all data files
                if self.data_dir.exists():
                    shutil.rmtree(self.data_dir)
                    self.data_dir.mkdir()

                # Clear database
                with self._db_lock:
                    conn = sqlite3.connect(str(self.db_path))
                    try:
                        conn.execute("DELETE FROM cache_entries")
                        conn.commit()
                    finally:
                        conn.close()

                # Reset stats
                self._stats.update(
                    {
                        "size_bytes": 0,
                        "entry_count": 0,
                    }
                )

                logger.info("Disk cache cleared")

            except Exception as e:
                logger.error("Failed to clear disk cache: %s", e)

    def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists and is not expired
        """
        entry_info = self._get_entry_info(key)
        if not entry_info:
            return False

        if self._is_expired(entry_info):
            self._remove_entry(key, entry_info["filename"])
            return False

        return True

    def get_keys(self) -> Set[str]:
        """Get all non-expired cache keys.

        Returns:
            Set of cache keys
        """
        with self._lock:
            # Clean up expired entries first
            self._cleanup_expired()

            with self._db_lock:
                conn = sqlite3.connect(str(self.db_path))
                try:
                    cursor = conn.execute("SELECT key FROM cache_entries")
                    return {row[0] for row in cursor.fetchall()}
                finally:
                    conn.close()

    # Alias for backward compatibility
    keys = property(get_keys)

    def size(self) -> int:
        """Get current cache size in bytes.

        Returns:
            Current cache size in bytes
        """
        return self._stats["size_bytes"]

    def entry_count(self) -> int:
        """Get number of entries in cache.

        Returns:
            Number of cache entries
        """
        return self._stats["entry_count"]

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            hit_rate = 0.0
            total_requests = self._stats["hits"] + self._stats["misses"]
            if total_requests > 0:
                hit_rate = float(self._stats["hits"]) / float(total_requests)

            disk_limit = float(self.config.disk_limit) if self.config.disk_limit else 1.0

            return {
                **self._stats,
                "hit_rate": hit_rate,
                "disk_usage_pct": (float(self._stats["size_bytes"]) / disk_limit) * 100,
                "avg_entry_size": (
                    float(self._stats["size_bytes"])
                    / float(max(1, self._stats["entry_count"]))
                ),
                "cache_dir": str(self.cache_dir),
            }

    def _get_entry_info(self, key: str) -> Optional[dict[str, Any]]:
        """Get entry information from database."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                cursor = conn.execute(
                    """
                    SELECT filename, created_at, last_accessed, access_count,
                           ttl, size_bytes, compressed, compression_ratio
                    FROM cache_entries WHERE key = ?
                """,
                    (key,),
                )

                row = cursor.fetchone()
                if row:
                    return {
                        "filename": row[0],
                        "created_at": row[1],
                        "last_accessed": row[2],
                        "access_count": row[3],
                        "ttl": row[4],
                        "size_bytes": row[5],
                        "compressed": bool(row[6]),
                        "compression_ratio": row[7],
                    }
                return None
            finally:
                conn.close()

    def _is_expired(self, entry_info: dict[str, Any]) -> bool:
        """Check if entry has expired."""
        if entry_info["ttl"] is None:
            return False
        return time.time() - entry_info["created_at"] > entry_info["ttl"]

    def _generate_filename(self, key: str) -> str:
        """Generate filename for cache key."""
        hash_obj = hashlib.sha256(key.encode())
        return f"{self.config.cache_version}_{hash_obj.hexdigest()[:16]}.cache"

    @safe_file_operation("data loading")
    def _load_data(self, filename: str, compressed: bool) -> Any:
        """Load data from cache file."""
        file_path = self.data_dir / filename

        with open(file_path, "rb") as f:
            data = f.read()

        if compressed:
            data = zlib.decompress(data)

        return pickle.loads(data)

    @safe_file_operation("atomic write")
    def _write_data_atomic(self, file_path: Path, data: bytes) -> bool:
        """Write data atomically using temporary file."""
        tmp_path = None
        try:
            # Write to temporary file first
            with tempfile.NamedTemporaryFile(
                dir=file_path.parent, delete=False, prefix=".tmp_"
            ) as tmp_file:
                tmp_file.write(data)
                tmp_path = Path(tmp_file.name)

            # Atomic move
            tmp_path.replace(file_path)
            return True

        except Exception as e:
            logger.error("Failed to write cache file %s: %s", file_path, e)
            # Clean up temporary file if it exists
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            return False

    def _update_access_info(self, key: str) -> None:
        """Update access information for cache entry."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                conn.execute(
                    """
                    UPDATE cache_entries
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE key = ?
                """,
                    (time.time(), key),
                )
                conn.commit()
            finally:
                conn.close()

    def _remove_entry(self, key: str, filename: str) -> None:
        """Remove entry from cache and database."""
        try:
            # Remove file
            file_path = self.data_dir / filename
            if file_path.exists():
                file_path.unlink()

            # Remove from database
            with self._db_lock:
                conn = sqlite3.connect(str(self.db_path))
                try:
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                    conn.commit()
                finally:
                    conn.close()

        except Exception as e:
            logger.error("Failed to remove cache entry %s: %s", key, e)

    def _check_disk_space(self, required_bytes: int) -> bool:
        """Check if there's enough disk space."""
        current_size = self._calculate_current_size()
        return current_size + required_bytes <= self.config.disk_limit

    def _evict_entries(self, required_bytes: int) -> None:
        """Evict entries to make space."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Get entries sorted by access pattern
                if self.config.eviction_policy == "lru":
                    cursor = conn.execute(
                        """
                        SELECT key, filename, size_bytes
                        FROM cache_entries
                        ORDER BY last_accessed ASC
                    """
                    )
                elif self.config.eviction_policy == "lfu":
                    cursor = conn.execute(
                        """
                        SELECT key, filename, size_bytes
                        FROM cache_entries
                        ORDER BY access_count ASC, last_accessed ASC
                    """
                    )
                else:  # FIFO
                    cursor = conn.execute(
                        """
                        SELECT key, filename, size_bytes
                        FROM cache_entries
                        ORDER BY created_at ASC
                    """
                    )

                freed_bytes = 0
                for row in cursor.fetchall():
                    key, filename, size_bytes = row
                    self._remove_entry(key, filename)
                    freed_bytes += size_bytes

                    if freed_bytes >= required_bytes:
                        break

            finally:
                conn.close()

    def _cleanup_expired(self) -> int:
        """Remove expired entries."""
        removed_count = 0
        current_time = time.time()

        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Find expired entries
                cursor = conn.execute(
                    """
                    SELECT key, filename
                    FROM cache_entries
                    WHERE ttl IS NOT NULL AND (created_at + ttl) < ?
                """,
                    (current_time,),
                )

                expired_entries = cursor.fetchall()

                for key, filename in expired_entries:
                    self._remove_entry(key, filename)
                    removed_count += 1

            finally:
                conn.close()

        if removed_count > 0:
            logger.debug("Cleaned up %d expired disk cache entries", removed_count)

        return removed_count

    def _calculate_current_size(self) -> int:
        """Calculate current cache size from database."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                cursor = conn.execute("SELECT SUM(size_bytes) FROM cache_entries")
                result = cursor.fetchone()[0]
                return int(result) if result is not None else 0
            finally:
                conn.close()

    def _update_stats(self) -> None:
        """Update cache statistics."""
        with self._db_lock:
            conn = sqlite3.connect(str(self.db_path))
            try:
                # Get size and count
                cursor = conn.execute(
                    """
                    SELECT COUNT(*), SUM(size_bytes), AVG(compression_ratio)
                    FROM cache_entries
                """
                )
                row = cursor.fetchone()

                self._stats["entry_count"] = int(row[0]) if row[0] is not None else 0
                self._stats["size_bytes"] = int(row[1]) if row[1] is not None else 0
                self._stats["compression_ratio"] = (
                    float(row[2]) if row[2] is not None else 1.0
                )

            finally:
                conn.close()

    def _periodic_cleanup(self) -> None:
        """Periodic cleanup thread function."""
        while True:
            try:
                time.sleep(self.config.cleanup_interval)

                with self._lock:
                    # Clean up expired entries
                    self._cleanup_expired()

                    # Update stats
                    self._update_stats()

            except Exception as e:
                logger.error("Error in disk cache cleanup thread: %s", e)
