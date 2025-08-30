from __future__ import annotations
from typing import Protocol, Any


# LLM provider contract
class LLMProvider(Protocol):
    """
    Minimal LLM contract consumed by functional.compose.
    """

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **kwargs: Any
    ) -> str: ...
