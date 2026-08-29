"""LLM endpoint health check utility."""
from __future__ import annotations

import requests


def check_llm_endpoint(
    base_url: str,
    api_key: str = "",
    timeout: int = 5,
) -> tuple[bool, str]:
    """Verify connectivity to OpenAI-compatible LLM endpoint."""
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        resp = requests.get(
            f"{base_url.rstrip('/')}/models",
            headers=headers,
            timeout=timeout,
        )
        is_ready = 200 <= resp.status_code < 300
        return is_ready, "OK" if is_ready else f"HTTP_{resp.status_code}"
    except (OSError, requests.RequestException):
        return False, "UNREACHABLE"

