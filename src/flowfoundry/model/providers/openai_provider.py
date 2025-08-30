from __future__ import annotations
import os
from typing import Any
from ...utils import FFConfigError, FFDependencyError, FFExecutionError
from ...utils import LLMProvider, register_llm_provider


@register_llm_provider("openai")
class OpenAIProvider(LLMProvider):
    def __init__(self, model: str, api_key: str | None = None, **_: Any):
        try:
            from openai import OpenAI
        except Exception as e:
            raise FFDependencyError(
                "Install OpenAI SDK: pip install openai>=1.0"
            ) from e
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise FFConfigError("Missing OPENAI_API_KEY for OpenAI provider.")
        self._client = OpenAI(api_key=key)
        self._model = model

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **_: Any
    ) -> str:
        try:
            resp = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                max_tokens=max_tokens,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            raise FFExecutionError(f"OpenAI generation failed: {e}") from e
