"""Tests for app/common/executor.py"""

import asyncio
import time

import pytest

from app.common.executor import ProcessPoolExecutor, ThreadPoolExecutor


def slow_function(seconds: float) -> str:
    time.sleep(seconds)
    return "completed"


def add_numbers(a: int, b: int) -> int:
    return a + b


def raise_error():
    raise ValueError("Test error")


class TestThreadPoolExecutor:
    def test_init(self):
        executor = ThreadPoolExecutor(max_workers=2)
        assert executor.max_workers == 2
        assert executor._executor is None  # Lazy init

    def test_lazy_executor_initialization(self):
        executor = ThreadPoolExecutor(max_workers=1)
        assert executor._executor is None

        # Access triggers creation
        _ = executor.executor
        assert executor._executor is not None

    @pytest.mark.asyncio
    async def test_run_simple_function(self):
        executor = ThreadPoolExecutor(max_workers=2)

        result, timed_out = await executor.run(add_numbers, 3, 4)

        assert result == 7
        assert timed_out is False
        executor.shutdown(wait=True)

    @pytest.mark.asyncio
    async def test_run_with_timeout(self):
        executor = ThreadPoolExecutor(max_workers=1)

        # Function that takes 2 seconds, but timeout is 0.1
        result, timed_out = await executor.run(slow_function, 2, timeout=0.1)

        assert result is None
        assert timed_out is True
        executor.shutdown(wait=False)

    @pytest.mark.asyncio
    async def test_throttling_limits_concurrent_calls(self):
        executor = ThreadPoolExecutor(max_workers=2)
        start = time.monotonic()

        # Run 4 tasks with 2 workers - should take ~2x the time of 2 tasks
        tasks = [executor.run(slow_function, 0.1) for _ in range(4)]
        results = await asyncio.gather(*tasks)

        elapsed = time.monotonic() - start

        # All should complete successfully
        assert all(r == ("completed", False) for r in results)
        # Should take at least 0.2s (2 batches of 2)
        assert elapsed >= 0.15
        executor.shutdown(wait=True)

    def test_shutdown(self):
        executor = ThreadPoolExecutor(max_workers=1)
        _ = executor.executor  # Initialize

        executor.shutdown(wait=True)
        # Should not raise


def can_use_process_pool():
    """Check if ProcessPoolExecutor can be used in current environment."""
    from concurrent.futures import ProcessPoolExecutor as PPE

    try:
        executor = PPE(max_workers=1)
        executor.shutdown(wait=False)
        return True
    except PermissionError:
        return False


class TestProcessPoolExecutor:
    def test_init(self):
        executor = ProcessPoolExecutor(max_workers=2)
        assert executor.max_workers == 2
        assert executor._executor is None

    @pytest.mark.skipif(
        not can_use_process_pool(),
        reason="ProcessPoolExecutor not available (sandbox/permissions)",
    )
    @pytest.mark.asyncio
    async def test_run_simple_function(self):
        executor = ProcessPoolExecutor(max_workers=1)

        result, timed_out = await executor.run(add_numbers, 5, 10)

        assert result == 15
        assert timed_out is False
        executor.shutdown(wait=True)

    @pytest.mark.skipif(
        not can_use_process_pool(),
        reason="ProcessPoolExecutor not available (sandbox/permissions)",
    )
    @pytest.mark.asyncio
    async def test_run_with_timeout(self):
        executor = ProcessPoolExecutor(max_workers=1)

        result, timed_out = await executor.run(slow_function, 2, timeout=0.1)

        assert result is None
        assert timed_out is True
        executor.shutdown(wait=False)

