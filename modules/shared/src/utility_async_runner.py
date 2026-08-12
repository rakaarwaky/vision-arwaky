"""Async runner utilities — safe execution of coroutines from sync contexts."""

import asyncio


def run_async(coro):
    """Run an async coroutine safely, handling existing event loops."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop — safe to use asyncio.run()
        return asyncio.run(coro)
    # Already have a running loop — use Runner()
    with asyncio.Runner() as runner:
        return runner.run(coro)
