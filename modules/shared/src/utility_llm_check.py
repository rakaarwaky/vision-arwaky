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


def list_models(
    base_url: str,
    api_key: str = "",
    timeout: int = 5,
) -> list[dict]:
    """GET /models from an OpenAI-compatible endpoint and return the model list.

    Returns an empty list on any error.
    """
    try:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        resp = requests.get(
            f"{base_url.rstrip('/')}/models",
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        models = data.get("data", [])
        return models if isinstance(models, list) else []
    except (OSError, requests.RequestException, ValueError, KeyError):
        return []
