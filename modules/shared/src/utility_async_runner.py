"""Async runner utilities — safe execution of coroutines from sync contexts."""

import asyncio
from concurrent.futures import ThreadPoolExecutor


def run_async(coro):
    """Run an async coroutine safely from a synchronous caller.

    - No running loop in this thread: use ``asyncio.run()``.
    - A loop is already running in this thread (async context): run the
      coroutine on a fresh loop in a worker thread instead of nesting on
      the active loop, which would raise ``RuntimeError``.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        return asyncio.run(coro)

    # Already inside a running loop — execute on a fresh loop in a worker
    # thread so we neither nest on the active loop nor deadlock it.
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()
