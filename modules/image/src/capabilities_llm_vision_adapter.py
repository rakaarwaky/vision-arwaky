"""Infrastructure adapter for VLM inference via OpenAI-compatible APIs.

Configuration via config.yaml in the project root (backend: "external").
"""

import base64
import json
import logging
import os
from pathlib import Path

import requests
import yaml

from modules.shared.src.contract_llm_vision_protocol import LLMVisionProtocol
from modules.shared.src.taxonomy_vision_constant import (
    DEFAULT_MODELS_TIMEOUT_S,
    DEFAULT_VLM_MAX_TOKENS,
    DEFAULT_VLM_TEMPERATURE,
    DEFAULT_VLM_TIMEOUT_S,
)
from modules.shared.src.taxonomy_vision_vo import (
    AnalysisPrompt,
    BackendType,
    FilePath,
    ModelName,
    VisionAnalysis,
)

logger = logging.getLogger("mcp_server.infrastructure.llm")

DEFAULT_URL = "http://127.0.0.1:1234/v1"
DEFAULT_API_KEY = ""


class LLMVisionAdapter(LLMVisionProtocol):
    """Adapter for vision-capable VLM via OpenAI-compatible API."""

    _taxonomy_marker = VisionAnalysis

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ):
        # 1. Load config.yaml — check ~/.config/vision-arwaky/ first, then project root
        project_root = Path(__file__).parent.parent.parent
        user_config = Path.home() / ".config" / "vision-arwaky" / "config.yaml"
        config_path = project_root / "config.yaml"
        self._config: dict[str, object] = {}

        if user_config.exists():
            config_path = user_config

        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from {config_path}")
            except (OSError, ValueError, yaml.YAMLError) as e:
                logger.warning(f"Failed to read config: {e}. Falling back to defaults.")

        self._backend = str(self._config.get("backend", "external"))

        # 2. Configure external HTTP endpoint settings
        url = (
            base_url
            or os.getenv("LLAMA_API_URL")
            or self._get_nested_config("external", "url")
            or DEFAULT_URL
        )
        self.base_url = url.rstrip("/")
        self.api_key = (
            api_key
            or os.getenv("LLAMA_API_KEY")
            or self._get_nested_config("external", "api_key")
            or DEFAULT_API_KEY
        )
        self._model = (
            model
            or os.getenv("LLAMA_MODEL")
            or self._get_nested_config("external", "model")
            or ""
        )

    @property
    def config(self) -> dict:
        """Expose self._config dictionary dynamically."""
        return self._config

    @property
    def backend(self) -> BackendType:
        return BackendType(value=self._backend)

    def _get_nested_config(self, section: str, key: str) -> str:
        sec = self._config.get(section)
        if isinstance(sec, dict):
            return str(sec.get(key, ""))
        return ""

    @property
    def model(self) -> ModelName:
        if self._model:
            return ModelName(value=self._model)
        try:
            session = requests.Session()
            session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            resp = session.get(
                f"{self.base_url}/models", timeout=DEFAULT_MODELS_TIMEOUT_S
            )
            session.close()
            resp.raise_for_status()
            data = resp.json()
            models = data.get("data", [])
            if models:
                self._model = str(models[0]["id"])
                logger.info(f"Auto-selected model: {self._model}")
                return ModelName(value=self._model)
        except (requests.RequestException, KeyError, ValueError) as e:
            logger.warning(f"Failed to list models: {e}")

        return ModelName(value="local-model")

    @staticmethod
    def _encode_image(path: str) -> str:
        with open(path, "rb") as f:
            data = f.read()
        ext = path.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def _analyze_via_http(
        self,
        image_path: str,
        prompt: str,
        timeout: int = DEFAULT_VLM_TIMEOUT_S,
    ) -> str:
        """Send image + prompt via HTTP to an OpenAI-compatible server."""
        model = self.model.value
        image_url = self._encode_image(image_path)

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "temperature": DEFAULT_VLM_TEMPERATURE,
            "max_tokens": DEFAULT_VLM_MAX_TOKENS,
        }

        try:
            session = requests.Session()
            session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
            resp = session.post(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload),
                timeout=timeout,
            )
            session.close()
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content")
            reasoning = message.get("reasoning_content")
            if not content and reasoning:
                content = reasoning
            if not content:
                logger.warning(
                    f"Empty response from LLM. Full data: {json.dumps(data)[:500]}"
                )
            return str(content or "")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to LLM at {self.base_url}: {e}")
            raise RuntimeError(
                f"LLM server not reachable at {self.base_url}. "
                "Ensure the server is running and a vision model is loaded."
            ) from e
        except requests.exceptions.Timeout as e:
            logger.error(f"LLM request timed out after {timeout}s: {e}")
            raise RuntimeError(f"LLM request timed out after {timeout}s") from e
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise RuntimeError(f"LLM request failed: {e}") from e

    def analyze_image(
        self,
        image_path: FilePath,
        prompt: AnalysisPrompt,
        timeout: int = DEFAULT_VLM_TIMEOUT_S,
    ) -> str:
        """Send image + prompt to the VLM and return the text response."""
        path_str = image_path.value
        prompt_str = prompt.value if prompt and prompt.value is not None else ""
        return self._analyze_via_http(path_str, prompt_str, timeout)
