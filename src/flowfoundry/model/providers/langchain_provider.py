# src/flowfoundry/model/providers/langchain_provider.py
from __future__ import annotations
import os
from typing import Any
from ...utils.llm_contracts import LLMProvider
from ...utils.llm_registry import register_llm_provider
from ...utils.exceptions import FFConfigError, FFDependencyError, FFExecutionError


@register_llm_provider("langchain")
class LangChainProvider(LLMProvider):
    """
    backend: 'openai' (ChatOpenAI) or 'ollama' (ChatOllama from langchain-ollama)
    """

    def __init__(self, model: str, backend: str = "openai", **kwargs: Any):
        self._backend = (backend or "openai").lower()
        self._model = model

        if self._backend == "openai":
            try:
                from langchain_openai import ChatOpenAI  # pip install langchain-openai
            except Exception as e:
                raise FFDependencyError("pip install langchain-openai") from e
            if not os.getenv("OPENAI_API_KEY"):
                raise FFConfigError("Missing OPENAI_API_KEY for LangChain(OpenAI).")
            # You can pass additional OpenAI args via kwargs if needed
            self._impl = ChatOpenAI(model=model, temperature=0.2)

        elif self._backend == "ollama":
            try:
                from langchain_ollama import ChatOllama  # pip install langchain-ollama
            except Exception as e:
                raise FFDependencyError("pip install langchain-ollama") from e
            base_url = kwargs.get("host") or os.getenv(
                "OLLAMA_HOST", "http://localhost:11434"
            )
            # model_kwargs can pass Ollama options if desired
            self._impl = ChatOllama(model=model, temperature=0.2, base_url=base_url)

        else:
            raise FFConfigError(f"Unsupported langchain backend: {backend}")

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **_: Any
    ) -> str:
        try:
            # For ChatOpenAI and ChatOllama, invoking with list of tuples works:
            msg = self._impl.invoke([("system", system), ("human", user)])
            content = getattr(msg, "content", str(msg))
            return content.strip()
        except Exception as e:
            # Improve the 404 error guidance for Ollama
            if "404" in str(e) and self._backend == "ollama":
                raise FFExecutionError(
                    "LangChain(Ollama) failed with 404. "
                    "Make sure the model exists on your Ollama server "
                    "(e.g., `ollama pull <model_name>`) and the base_url is correct."
                ) from e
            raise FFExecutionError(f"LangChain generation failed: {e}") from e
