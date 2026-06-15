"""Infrastructure adapter for local LLM/VLM inference.

Supports two modes:
1. Native: In-process GGUF loading using llama-cpp-python.
2. External: OpenAI-compatible APIs (OpenAI-compatible API).

Configuration via config.yaml in the project root.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import requests
from src.shared.llm_vision_port import LLMVisionPort
from src.shared.vision_models_vo import VisionAnalysis

if TYPE_CHECKING:
    from llama_cpp import Llama

logger = logging.getLogger("mcp_server.infrastructure.llm")

DEFAULT_URL = "http://127.0.0.1:1234/v1"
DEFAULT_API_KEY = ""


class LLMVisionAdapter(LLMVisionPort):
    """Adapter for vision-capable local LLM."""

    _taxonomy_marker = VisionAnalysis

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
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
                import yaml
                with open(config_path, "r") as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to read config: {e}. Falling back to defaults.")

        self._backend = str(self._config.get("backend", "external"))
        self._native_llm: Optional["Llama"] = None

        # 2. Configure external HTTP endpoint settings
        url = base_url or os.getenv("LLAMA_API_URL") or self._get_nested_config("external", "url") or DEFAULT_URL
        self.base_url = url.rstrip("/")
        self.api_key = api_key or os.getenv("LLAMA_API_KEY") or self._get_nested_config("external", "api_key") or DEFAULT_API_KEY
        self._model = model or os.getenv("LLAMA_MODEL") or self._get_nested_config("external", "model") or ""
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    @property
    def config(self) -> dict:
        """Expose self._config dictionary dynamically."""
        return self._config

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def model(self) -> str:
        if self._backend == "native":
            native_cfg = self._config.get("native")
            if not isinstance(native_cfg, dict):
                native_cfg = {}
            model_rel_path = str(native_cfg.get("model_path", "models/MiniCPM-V-4_6-Q8_0.gguf"))
            return os.path.basename(model_rel_path)

        if self._model:
            return self._model
        try:
            resp = self.session.get(f"{self.base_url}/models", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            models = data.get("data", [])
            if models:
                self._model = str(models[0]["id"])
                logger.info(f"Auto-selected model: {self._model}")
                return self._model
        except Exception as e:
            logger.warning(f"Failed to list models: {e}")
        return "local-model"

    def _get_nested_config(self, section: str, key: str) -> str:
        sec = self._config.get(section)
        if isinstance(sec, dict):
            return str(sec.get(key, ""))
        return ""

    def _init_native_llm(self):
        """Lazy-load the native Llama model to keep initialization light."""
        if self._native_llm is not None:
            return

        try:
            from llama_cpp import Llama
            from llama_cpp.llama_chat_format import MiniCPMv26ChatHandler
        except ImportError as e:
            raise ImportError(
                "Libraries 'llama-cpp-python' or 'pyyaml' are not installed. "
                "To run natively, please install them inside your active environment:\n"
                "  pip install llama-cpp-python pyyaml\n"
                "Or configure CUDA for GPU acceleration:\n"
                "  CMAKE_ARGS='-GGPU_INTERFACES=ON' pip install llama-cpp-python pyyaml"
            ) from e

        project_root = Path(__file__).parent.parent.parent
        native_cfg = self._config.get("native")
        if not isinstance(native_cfg, dict):
            native_cfg = {}
        
        model_rel_path = str(native_cfg.get("model_path", "models/MiniCPM-V-4_6-Q8_0.gguf"))
        mmproj_rel_path = str(native_cfg.get("mmproj_path", "models/mmproj-MiniCPM-V-4.6-F16.gguf"))
        
        model_path = project_root / model_rel_path
        mmproj_path = project_root / mmproj_rel_path

        if not model_path.exists():
            raise FileNotFoundError(
                f"Native GGUF model file not found at: {model_path}\n"
                "Please place your GGUF model inside the models/ directory."
            )
        if not mmproj_path.exists():
            raise FileNotFoundError(
                f"Multimodal projector (mmproj) not found at: {mmproj_path}\n"
                "MiniCPM-V requires the mmproj GGUF file to process images."
            )

        n_ctx = int(native_cfg.get("n_ctx", 2048))
        n_threads = int(native_cfg.get("n_threads", 4))
        n_gpu_layers = int(native_cfg.get("n_gpu_layers", -1))

        logger.info(f"Initializing native llama-cpp-python VLM. Model: {model_rel_path}, Projector: {mmproj_rel_path}")

        try:
            chat_handler = MiniCPMv26ChatHandler(clip_model_path=str(mmproj_path))
            self._native_llm = Llama(
                model_path=str(model_path),
                chat_handler=chat_handler,
                n_ctx=n_ctx,
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )
            logger.info("Native llama-cpp-python VLM successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize native Llama model: {e}")
            raise RuntimeError(f"Failed to initialize native Llama model: {e}") from e

    @staticmethod
    def _encode_image(path: str) -> str:
        with open(path, "rb") as f:
            data = f.read()
        ext = path.split(".")[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    def analyze_image(self, image_path: str, prompt: str, timeout: int = 120) -> str:
        """Send image + prompt to VLM and return the text response."""
        if self.backend == "native":
            self._init_native_llm()
            llm = self._native_llm
            if llm is None:
                raise RuntimeError("Native VLM was not initialized")

            image_url = self._encode_image(image_path)
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are an assistant who perfectly describes images and helps AI agents understand UI layouts."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]

            logger.info("Running native VLM inference (in-process)...")
            try:
                response = llm.create_chat_completion(
                    messages=messages,
                    temperature=0.4,
                    max_tokens=1024
                )
                content = str(response["choices"][0]["message"]["content"])
                return content
            except Exception as e:
                logger.error(f"Native VLM inference failed: {e}")
                raise RuntimeError(f"Native VLM inference failed: {e}") from e
        else:
            # External HTTP API mode (original)
            model = self.model
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
                "temperature": 0.4,
                "max_tokens": 2048,
            }

            try:
                resp = self.session.post(
                    f"{self.base_url}/chat/completions",
                    data=json.dumps(payload),
                    timeout=timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                choice = data.get("choices", [{}])[0]
                message = choice.get("message", {})
                content = str(message.get("content", ""))
                if not content:
                    logger.warning(f"Empty response from LLM. Full data: {json.dumps(data)[:500]}")
                return content
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to LLM at {self.base_url}: {e}")
                raise RuntimeError(
                    f"Local LLM server not reachable at {self.base_url}. "
                    "Ensure your LLM server is running and a vision model is loaded."
                ) from e
            except requests.exceptions.Timeout as e:
                logger.error(f"LLM request timed out after {timeout}s: {e}")
                raise RuntimeError(f"LLM request timed out after {timeout}s") from e
            except Exception as e:
                logger.error(f"LLM request failed: {e}")
                raise RuntimeError(f"LLM request failed: {e}") from e
