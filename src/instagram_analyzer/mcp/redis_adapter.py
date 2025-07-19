"""
MCP Redis Integration

Distributed caching and session management using mcp-server-redis
for persistent progress tracking, analysis caching, and real-time notifications.
"""

import asyncio
import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from .client import get_mcp_client

logger = logging.getLogger(__name__)


class MCPRedisError(Exception):
    """Exception raised for MCP Redis operations."""

    pass


class MCPRedis:
    """
    Redis integration using MCP server for distributed caching and sessions.

    Provides:
    - Session management for multiple users
    - Persistent progress tracking
    - Analysis result caching
    - Job queue management
    - Real-time notifications
    """

    def __init__(self):
        self.fallback_storage: Dict[str, Any] = {}
        self.fallback_sessions: Dict[str, Dict[str, Any]] = {}
        self.fallback_progress: Dict[str, Dict[str, Any]] = {}

    async def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new user session.

        Returns session ID for tracking user state across requests.
        """
        try:
            client = await get_mcp_client()
            session_id = str(uuid.uuid4())

            session_data = {
                "session_id": session_id,
                "user_id": user_id or "anonymous",
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "active_jobs": [],
                "analysis_history": [],
                "preferences": {},
            }

            if client.is_connected("redis"):
                # Use MCP Redis server
                await self._redis_set_session(session_id, session_data)
            else:
                # Fallback to in-memory storage
                self.fallback_sessions[session_id] = session_data

            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise MCPRedisError(f"Session creation failed: {e}")

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID."""
        try:
            client = await get_mcp_client()

            if client.is_connected("redis"):
                return await self._redis_get_session(session_id)
            else:
                return self.fallback_sessions.get(session_id)

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                return False

            session_data.update(updates)
            session_data["last_activity"] = datetime.utcnow().isoformat()

            client = await get_mcp_client()

            if client.is_connected("redis"):
                await self._redis_set_session(session_id, session_data)
            else:
                self.fallback_sessions[session_id] = session_data

            return True

        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    async def set_progress(self, job_id: str, progress_data: Dict[str, Any]) -> bool:
        """Set progress data for a job."""
        try:
            client = await get_mcp_client()

            progress_data["updated_at"] = datetime.utcnow().isoformat()
            progress_data["job_id"] = job_id

            if client.is_connected("redis"):
                await self._redis_set_progress(job_id, progress_data)
            else:
                self.fallback_progress[job_id] = progress_data

            logger.debug(
                f"Updated progress for job {job_id}: {progress_data.get('progress', 0)}%"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to set progress for job {job_id}: {e}")
            return False

    async def get_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get progress data for a job."""
        try:
            client = await get_mcp_client()

            if client.is_connected("redis"):
                return await self._redis_get_progress(job_id)
            else:
                return self.fallback_progress.get(job_id)

        except Exception as e:
            logger.error(f"Failed to get progress for job {job_id}: {e}")
            return None

    async def cache_analysis(
        self, cache_key: str, analysis_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """Cache analysis results with TTL."""
        try:
            client = await get_mcp_client()

            cache_data = {
                "data": analysis_data,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl,
                "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
            }

            if client.is_connected("redis"):
                await self._redis_set_cache(cache_key, cache_data, ttl)
            else:
                # Fallback with manual TTL check
                self.fallback_storage[cache_key] = cache_data

            logger.info(f"Cached analysis data with key {cache_key} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Failed to cache analysis {cache_key}: {e}")
            return False

    async def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis results."""
        try:
            client = await get_mcp_client()

            if client.is_connected("redis"):
                return await self._redis_get_cache(cache_key)
            else:
                # Fallback with TTL check
                cached_data = self.fallback_storage.get(cache_key)
                if cached_data:
                    expires_at = datetime.fromisoformat(cached_data["expires_at"])
                    if datetime.utcnow() < expires_at:
                        return cached_data["data"]
                    else:
                        # Expired, remove from cache
                        del self.fallback_storage[cache_key]

                return None

        except Exception as e:
            logger.error(f"Failed to get cached analysis {cache_key}: {e}")
            return None

    async def generate_cache_key(
        self, file_hash: str, analysis_type: str = "full"
    ) -> str:
        """Generate a cache key based on file hash and analysis type."""
        key_data = f"{file_hash}:{analysis_type}"
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()  # nosec

    async def add_job_to_queue(self, job_data: Dict[str, Any], priority: int = 0) -> str:
        """Add a job to the processing queue."""
        try:
            client = await get_mcp_client()
            job_id = str(uuid.uuid4())

            queue_item = {
                "job_id": job_id,
                "job_data": job_data,
                "priority": priority,
                "created_at": datetime.utcnow().isoformat(),
                "status": "queued",
            }

            if client.is_connected("redis"):
                await self._redis_enqueue_job(job_id, queue_item, priority)
            else:
                # Fallback: immediate processing
                logger.info(f"Fallback: Processing job {job_id} immediately")

            logger.info(f"Added job {job_id} to queue with priority {priority}")
            return job_id

        except Exception as e:
            logger.error(f"Failed to add job to queue: {e}")
            raise MCPRedisError(f"Job queuing failed: {e}")

    async def publish_notification(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish real-time notification to subscribers."""
        try:
            client = await get_mcp_client()

            notification = {
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "channel": channel,
            }

            if client.is_connected("redis"):
                await self._redis_publish(channel, notification)
                logger.debug(f"Published notification to {channel}")
                return True
            else:
                # Fallback: log notification
                logger.info(f"Notification [{channel}]: {message}")
                return True

        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")
            return False

    async def subscribe_to_notifications(self, channels: List[str]) -> Optional[Any]:
        """Subscribe to notification channels."""
        try:
            client = await get_mcp_client()

            if client.is_connected("redis"):
                return await self._redis_subscribe(channels)
            else:
                logger.info(f"Fallback: Cannot subscribe to {channels} without Redis")
                return None

        except Exception as e:
            logger.error(f"Failed to subscribe to notifications: {e}")
            return None

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired sessions, cache, and progress data."""
        try:
            cleanup_stats = {
                "sessions_cleaned": 0,
                "cache_cleaned": 0,
                "progress_cleaned": 0,
            }

            client = await get_mcp_client()

            if client.is_connected("redis"):
                # Redis handles TTL automatically
                logger.info("Redis handles automatic cleanup")
            else:
                # Manual cleanup for fallback storage
                now = datetime.utcnow()

                # Clean expired cache entries
                expired_cache = []
                for key, data in self.fallback_storage.items():
                    if "expires_at" in data:
                        expires_at = datetime.fromisoformat(data["expires_at"])
                        if now > expires_at:
                            expired_cache.append(key)

                for key in expired_cache:
                    del self.fallback_storage[key]
                    cleanup_stats["cache_cleaned"] += 1

                # Clean old sessions (inactive for 24 hours)
                expired_sessions = []
                cutoff_time = now - timedelta(hours=24)

                for session_id, session_data in self.fallback_sessions.items():
                    last_activity = datetime.fromisoformat(session_data["last_activity"])
                    if last_activity < cutoff_time:
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    del self.fallback_sessions[session_id]
                    cleanup_stats["sessions_cleaned"] += 1

                # Clean old progress data (older than 1 hour)
                expired_progress = []
                progress_cutoff = now - timedelta(hours=1)

                for job_id, progress_data in self.fallback_progress.items():
                    updated_at = datetime.fromisoformat(progress_data["updated_at"])
                    if updated_at < progress_cutoff:
                        expired_progress.append(job_id)

                for job_id in expired_progress:
                    del self.fallback_progress[job_id]
                    cleanup_stats["progress_cleaned"] += 1

            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"error": str(e)}

    # Mock Redis operations (in real implementation, these would use actual MCP calls)

    async def _redis_set_session(
        self, session_id: str, session_data: Dict[str, Any]
    ) -> None:
        """Mock Redis session storage."""
        # In real implementation: await mcp_redis.call("set", f"session:{session_id}", json.dumps(session_data), "EX", 86400)
        self.fallback_sessions[session_id] = session_data

    async def _redis_get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Mock Redis session retrieval."""
        # In real implementation: data = await mcp_redis.call("get", f"session:{session_id}")
        return self.fallback_sessions.get(session_id)

    async def _redis_set_progress(
        self, job_id: str, progress_data: Dict[str, Any]
    ) -> None:
        """Mock Redis progress storage."""
        # In real implementation: await mcp_redis.call("set", f"progress:{job_id}", json.dumps(progress_data), "EX", 3600)
        self.fallback_progress[job_id] = progress_data

    async def _redis_get_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Mock Redis progress retrieval."""
        # In real implementation: data = await mcp_redis.call("get", f"progress:{job_id}")
        return self.fallback_progress.get(job_id)

    async def _redis_set_cache(
        self, cache_key: str, cache_data: Dict[str, Any], ttl: int
    ) -> None:
        """Mock Redis cache storage."""
        # In real implementation: await mcp_redis.call("set", f"cache:{cache_key}", json.dumps(cache_data), "EX", ttl)
        self.fallback_storage[cache_key] = cache_data

    async def _redis_get_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Mock Redis cache retrieval."""
        # In real implementation: data = await mcp_redis.call("get", f"cache:{cache_key}")
        cached_data = self.fallback_storage.get(cache_key)
        if cached_data:
            return cached_data.get("data")
        return None

    async def _redis_enqueue_job(
        self, job_id: str, queue_item: Dict[str, Any], priority: int
    ) -> None:
        """Mock Redis job queuing."""
        # In real implementation: await mcp_redis.call("zadd", "job_queue", priority, json.dumps(queue_item))
        logger.info(f"Mock: Enqueued job {job_id} with priority {priority}")

    async def _redis_publish(self, channel: str, notification: Dict[str, Any]) -> None:
        """Mock Redis publish."""
        # In real implementation: await mcp_redis.call("publish", channel, json.dumps(notification))
        logger.debug(f"Mock: Published to {channel}: {notification}")

    async def _redis_subscribe(self, channels: List[str]) -> None:
        """Mock Redis subscribe."""
        # In real implementation: return await mcp_redis.subscribe(channels)
        logger.info(f"Mock: Subscribed to channels {channels}")


# Global Redis instance
_mcp_redis: Optional[MCPRedis] = None


def get_mcp_redis() -> MCPRedis:
    """Get or create the global MCP Redis instance."""
    global _mcp_redis

    if _mcp_redis is None:
        _mcp_redis = MCPRedis()

    return _mcp_redis
