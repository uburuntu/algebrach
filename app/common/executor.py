from __future__ import annotations

import asyncio

from concurrent.futures.process import (
    BrokenProcessPool,
    ProcessPoolExecutor as _ProcessPoolExecutor,
)
from concurrent.futures.thread import (
    BrokenThreadPool,
    ThreadPoolExecutor as _ThreadPoolExecutor,
)
from typing import TYPE_CHECKING, Any

from throttler import ThrottlerSimultaneous

if TYPE_CHECKING:
    from collections.abc import Callable


class _BaseExecutor:
    ExecutorClass = None
    ExecutorExceptionClass = None

    def __init__(self, max_workers: int):
        self.max_workers = max_workers
        self.throttler = ThrottlerSimultaneous(count=max_workers)

        self._executor = None  # Lazy initialization

    @property
    def executor(self):
        if self._executor:
            return self._executor
        self._executor = self.ExecutorClass(max_workers=self.max_workers)
        return self._executor

    async def run(
        self, func: Callable, *args, timeout: float | None = 180
    ) -> tuple[Any, bool]:
        async with self.throttler:
            for attempt in range(2):
                try:
                    future = asyncio.get_running_loop().run_in_executor(
                        self.executor, func, *args
                    )
                    try:
                        result = await asyncio.wait_for(future, timeout=timeout)
                    except TimeoutError:
                        return None, True
                    return result, False
                except self.ExecutorExceptionClass:
                    self.shutdown(wait=False)
                    if attempt == 1:
                        raise

        raise RuntimeError("Executor retry loop exited unexpectedly")

    def shutdown(self, wait: bool):
        if self._executor is None:
            return None

        executor, self._executor = self._executor, None
        return executor.shutdown(wait=wait, cancel_futures=True)


class ThreadPoolExecutor(_BaseExecutor):
    ExecutorClass = _ThreadPoolExecutor
    ExecutorExceptionClass = BrokenThreadPool


class ProcessPoolExecutor(_BaseExecutor):
    ExecutorClass = _ProcessPoolExecutor
    ExecutorExceptionClass = BrokenProcessPool
