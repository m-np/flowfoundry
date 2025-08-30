# src/flowfoundry/model/providers/huggingface_provider.py
from __future__ import annotations

from typing import Any, List, TypedDict, cast

from ...utils import FFDependencyError, FFExecutionError
from ...utils import LLMProvider, register_llm_provider


# Shape HuggingFace's typical pipeline output for text-generation
class _HFGenItem(TypedDict, total=False):
    generated_text: str


_HFGenOutput = List[_HFGenItem]


@register_llm_provider("huggingface")
class HFProvider(LLMProvider):
    def __init__(self, model: str, device: str | None = None, **_: Any):
        try:
            # Lazy import so the base package installs without HF extras
            from transformers import pipeline
        except Exception as e:  # pragma: no cover - import-time failure path
            raise FFDependencyError(
                "Install transformers: pip install transformers accelerate sentencepiece"
            ) from e

        # Hugging Face accepts device as int, str alias, or -1 for CPU.
        # Keep your original behavior but normalize None -> -1 (CPU).
        hf_device: int | str | None = device if device is not None else -1

        self._pipeline = pipeline(
            "text-generation",
            model=model,
            device=hf_device,
        )

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **_: Any
    ) -> str:
        try:
            prompt = f"<<SYS>>{system}<<SYS>>\n\n{user}"

            # Help mypy: annotate the pipeline output shape
            raw_out: Any = self._pipeline(
                prompt,
                max_new_tokens=max_tokens,
                do_sample=False,
                temperature=0.2,
            )
            out: _HFGenOutput = cast(_HFGenOutput, raw_out)

            if isinstance(out, list) and out:
                # Cast to str so mypy knows we return a string
                text = cast(str, out[0].get("generated_text", ""))
            else:
                # Some pipelines may return a direct string/other shape; fall back
                text = str(raw_out)

            # Trim echoed prompt if the model returns it
            return (
                text[len(prompt) :].strip() if text.startswith(prompt) else text.strip()
            )

        except Exception as e:  # pragma: no cover - wrap & rethrow as framework error
            raise FFExecutionError(f"HuggingFace generation failed: {e}") from e
