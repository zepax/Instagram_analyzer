"""Memory profiling utilities for tracking memory usage."""

import gc
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

from ..logging_config import get_logger

logger = get_logger("utils.memory_profiler")


@dataclass
class MemorySnapshot:
    """Snapshot of memory usage at a point in time."""

    timestamp: float
    rss_mb: float  # Resident Set Size in MB
    vms_mb: float  # Virtual Memory Size in MB
    percent: float  # Memory usage percentage
    available_mb: float  # Available memory in MB
    gc_objects: int  # Number of garbage collected objects
    operation: str  # What operation was being performed


class MemoryProfiler:
    """Monitor and profile memory usage during operations."""

    def __init__(self, enable_profiling: bool = True):
        """Initialize memory profiler.

        Args:
            enable_profiling: Whether to enable memory profiling
        """
        self.enable_profiling = enable_profiling
        self.snapshots: list[MemorySnapshot] = []
        self.process = psutil.Process()
        self.logger = logger
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

    def take_snapshot(self, operation: str = "unknown") -> MemorySnapshot:
        """Take a snapshot of current memory usage.

        Args:
            operation: Description of current operation

        Returns:
            MemorySnapshot with current memory information
        """
        if not self.enable_profiling:
            return MemorySnapshot(
                timestamp=time.time(),
                rss_mb=0,
                vms_mb=0,
                percent=0,
                available_mb=0,
                gc_objects=0,
                operation=operation,
            )

        try:
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            virtual_memory = psutil.virtual_memory()
            gc_objects = len(gc.get_objects())

            snapshot = MemorySnapshot(
                timestamp=time.time(),
                rss_mb=memory_info.rss / 1024 / 1024,  # Convert to MB
                vms_mb=memory_info.vms / 1024 / 1024,  # Convert to MB
                percent=memory_percent,
                available_mb=virtual_memory.available / 1024 / 1024,
                gc_objects=gc_objects,
                operation=operation,
            )

            self.snapshots.append(snapshot)
            return snapshot

        except Exception as e:
            self.logger.error(f"Failed to take memory snapshot: {e}")
            return MemorySnapshot(
                timestamp=time.time(),
                rss_mb=0,
                vms_mb=0,
                percent=0,
                available_mb=0,
                gc_objects=0,
                operation=operation,
            )

    def start_monitoring(self, interval: float = 1.0):
        """Start continuous memory monitoring.

        Args:
            interval: Monitoring interval in seconds
        """
        if not self.enable_profiling or self._monitoring_thread is not None:
            return

        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitor_memory, args=(interval,), daemon=True
        )
        self._monitoring_thread.start()
        self.logger.debug("Started memory monitoring")

    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        if self._monitoring_thread is None:
            return

        self._stop_monitoring.set()
        self._monitoring_thread.join(timeout=5.0)
        self._monitoring_thread = None
        self.logger.debug("Stopped memory monitoring")

    def _monitor_memory(self, interval: float):
        """Internal method for continuous monitoring."""
        while not self._stop_monitoring.wait(interval):
            self.take_snapshot("monitoring")

    def get_memory_stats(self) -> dict[str, Any]:
        """Get comprehensive memory usage statistics.

        Returns:
            Dictionary with memory statistics
        """
        if not self.snapshots:
            return {
                "total_snapshots": 0,
                "peak_rss_mb": 0,
                "peak_vms_mb": 0,
                "peak_percent": 0,
                "avg_rss_mb": 0,
                "avg_percent": 0,
                "memory_growth_mb": 0,
                "gc_objects_growth": 0,
            }

        rss_values = [s.rss_mb for s in self.snapshots]
        vms_values = [s.vms_mb for s in self.snapshots]
        percent_values = [s.percent for s in self.snapshots]
        gc_values = [s.gc_objects for s in self.snapshots]

        return {
            "total_snapshots": len(self.snapshots),
            "peak_rss_mb": max(rss_values),
            "peak_vms_mb": max(vms_values),
            "peak_percent": max(percent_values),
            "avg_rss_mb": sum(rss_values) / len(rss_values),
            "avg_percent": sum(percent_values) / len(percent_values),
            "memory_growth_mb": (
                rss_values[-1] - rss_values[0] if len(rss_values) > 1 else 0
            ),
            "gc_objects_growth": (
                gc_values[-1] - gc_values[0] if len(gc_values) > 1 else 0
            ),
            "min_available_mb": min(s.available_mb for s in self.snapshots),
            "operations": list({s.operation for s in self.snapshots}),
        }

    def get_memory_timeline(self) -> list[dict[str, Any]]:
        """Get memory usage timeline.

        Returns:
            List of memory usage points over time
        """
        timeline = []
        for snapshot in self.snapshots:
            timeline.append(
                {
                    "timestamp": snapshot.timestamp,
                    "rss_mb": snapshot.rss_mb,
                    "vms_mb": snapshot.vms_mb,
                    "percent": snapshot.percent,
                    "available_mb": snapshot.available_mb,
                    "gc_objects": snapshot.gc_objects,
                    "operation": snapshot.operation,
                }
            )
        return timeline

    def save_profile(self, output_path: Path):
        """Save memory profile to file.

        Args:
            output_path: Path to save the profile
        """
        try:
            profile_data = {
                "stats": self.get_memory_stats(),
                "timeline": self.get_memory_timeline(),
                "system_info": {
                    "total_memory_mb": psutil.virtual_memory().total / 1024 / 1024,
                    "cpu_count": psutil.cpu_count(),
                    "platform": psutil.WINDOWS if hasattr(psutil, "WINDOWS") else "unix",
                },
            }

            import json

            with open(output_path, "w") as f:
                json.dump(profile_data, f, indent=2)

            self.logger.info(f"Memory profile saved to {output_path}")

        except Exception as e:
            self.logger.error(f"Failed to save memory profile: {e}")

    def clear_snapshots(self):
        """Clear all memory snapshots."""
        self.snapshots.clear()
        self.logger.debug("Cleared memory snapshots")

    def log_current_usage(self, operation: str = "current"):
        """Log current memory usage.

        Args:
            operation: Description of current operation
        """
        if not self.enable_profiling:
            return

        snapshot = self.take_snapshot(operation)
        self.logger.info(
            f"Memory usage [{operation}]: "
            f"RSS: {snapshot.rss_mb:.1f}MB, "
            f"VMS: {snapshot.vms_mb:.1f}MB, "
            f"Percent: {snapshot.percent:.1f}%, "
            f"Available: {snapshot.available_mb:.1f}MB, "
            f"GC Objects: {snapshot.gc_objects:,}"
        )

    def check_memory_threshold(self, threshold_percent: float = 80.0) -> bool:
        """Check if memory usage exceeds threshold.

        Args:
            threshold_percent: Memory usage threshold percentage

        Returns:
            True if memory usage exceeds threshold
        """
        if not self.enable_profiling:
            return False

        snapshot = self.take_snapshot("threshold_check")
        if snapshot.percent > threshold_percent:
            self.logger.warning(
                f"Memory usage ({snapshot.percent:.1f}%) exceeds threshold ({threshold_percent}%)"
            )
            return True
        return False

    def force_garbage_collection(self):
        """Force garbage collection and log results."""
        if not self.enable_profiling:
            return

        before = self.take_snapshot("before_gc")
        gc.collect()
        after = self.take_snapshot("after_gc")

        freed_mb = before.rss_mb - after.rss_mb
        freed_objects = before.gc_objects - after.gc_objects

        self.logger.info(
            f"Garbage collection freed {freed_mb:.1f}MB memory "
            f"and {freed_objects:,} objects"
        )


@contextmanager
def memory_profile(operation: str = "operation", enable_profiling: bool = True):
    """Context manager for memory profiling.

    Args:
        operation: Description of the operation being profiled
        enable_profiling: Whether to enable profiling

    Yields:
        MemoryProfiler instance
    """
    profiler = MemoryProfiler(enable_profiling)

    try:
        profiler.take_snapshot(f"start_{operation}")
        yield profiler
    finally:
        profiler.take_snapshot(f"end_{operation}")
        profiler.stop_monitoring()

        if enable_profiling:
            stats = profiler.get_memory_stats()
            logger.info(
                f"Memory profile [{operation}]: "
                f"Peak RSS: {stats['peak_rss_mb']:.1f}MB, "
                f"Growth: {stats['memory_growth_mb']:.1f}MB, "
                f"Avg Usage: {stats['avg_percent']:.1f}%"
            )


# Global profiler instance
_global_profiler: Optional[MemoryProfiler] = None


def get_memory_profiler(enable_profiling: bool = True) -> MemoryProfiler:
    """Get the global memory profiler instance.

    Args:
        enable_profiling: Whether to enable profiling

    Returns:
        Global MemoryProfiler instance
    """
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = MemoryProfiler(enable_profiling)
    return _global_profiler


def log_memory_usage(operation: str = "current"):
    """Log current memory usage using global profiler.

    Args:
        operation: Description of current operation
    """
    profiler = get_memory_profiler()
    profiler.log_current_usage(operation)


def check_memory_threshold(threshold_percent: float = 80.0) -> bool:
    """Check memory threshold using global profiler.

    Args:
        threshold_percent: Memory usage threshold percentage

    Returns:
        True if memory usage exceeds threshold
    """
    profiler = get_memory_profiler()
    return profiler.check_memory_threshold(threshold_percent)


def force_gc_if_needed(threshold_percent: float = 70.0):
    """Force garbage collection if memory usage exceeds threshold.

    Args:
        threshold_percent: Memory usage threshold for triggering GC
    """
    profiler = get_memory_profiler()
    if profiler.check_memory_threshold(threshold_percent):
        profiler.force_garbage_collection()
