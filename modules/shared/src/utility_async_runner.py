"""Async runner utilities — safe execution of coroutines from sync contexts."""

import asyncio
import concurrent.futures


def run_async(coro):
    """Run an async coroutine safely from a synchronous caller.

    - No running loop in this thread: use ``asyncio.run()``.
    - A loop is already running in this thread (e.g. an MCP/uvicorn server
      event loop): run the coroutine in a dedicated worker thread with its
      own fresh loop, so the sync caller can block on the result without
      stalling the active loop.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        return asyncio.run(coro)

    # Running loop — offload to a worker thread. The coroutine object has
    # not been scheduled anywhere yet, so asyncio.run() in the new thread
    # is safe.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()
