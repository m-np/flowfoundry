from __future__ import annotations
import os
from typing import Any
import requests

from ...utils import FFExecutionError
from ...utils import LLMProvider, register_llm_provider


@register_llm_provider("ollama")
class OllamaProvider(LLMProvider):
    def __init__(self, model: str, host: str | None = None, **_: Any):
        self._model = model
        self._host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **_: Any
    ) -> str:
        try:
            r = requests.post(
                f"{self._host}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "options": {"temperature": 0.2, "num_predict": max_tokens},
                    "stream": False,
                },
                timeout=600,
            )
            r.raise_for_status()
            data = r.json()
            return (data.get("message", {}).get("content") or "").strip()
        except Exception as e:
            raise FFExecutionError(f"Ollama generation failed: {e}") from e
