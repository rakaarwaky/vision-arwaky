"""Async runner utilities — safe execution of coroutines from sync contexts."""

import asyncio


def run_async(coro):
    """Run an async coroutine safely from a synchronous caller.

    - No running loop in this thread: use ``asyncio.run()``.
    - A loop is already running in this thread: this is an async context —
      blocking on the result would stall the active loop. Raise a clear
      error instead; async callers should ``await`` the coroutine directly
      (or use ``asyncio.to_thread`` when a sync operation is unavoidable).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        return asyncio.run(coro)

    raise RuntimeError(
        "run_async() called from within a running event loop; "
        "await the coroutine directly instead of blocking the loop."
    )
