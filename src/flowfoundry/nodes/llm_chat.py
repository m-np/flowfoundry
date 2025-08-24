from __future__ import annotations
from typing import Dict, Any
from ..registry import register_node

# Optional providers
_HAVE_LC_OPENAI = False
_HAVE_OAI_SDK = False

try:
    from langchain_openai import ChatOpenAI as _LCChatOpenAI

    _HAVE_LC_OPENAI = True
except Exception:
    _LCChatOpenAI = None

try:
    from openai import OpenAI as _OpenAIClient

    _HAVE_OAI_SDK = True
except Exception:
    _OpenAIClient = None


@register_node("llm.chat")
class LLMChatNode:
    """
    provider:
      - "echo"  : no network; echoes the prompt head (always available)
      - "openai": use LangChain ChatOpenAI if installed, else raw OpenAI SDK if installed; else echo with a warning
      - "auto"  : same as "openai" (kept for convenience)

    model: OpenAI model name when provider uses OpenAI.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        provider: str = "auto",
        temperature: float | None = None,
    ):
        self.model = model
        self.provider = provider.lower()
        self.temperature = temperature

    def _answer_echo(self, prompt: str) -> str:
        head = prompt[:300].strip().replace("\n", " ")
        return f"[ECHO:{self.model}] {head}"

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = state.get("prompt")
        if not prompt:
            raise ValueError("prompt missing in state")

        provider = self.provider
        if provider == "auto":
            provider = "openai"

        # Offline echo path
        if provider == "echo":
            state["answer"] = self._answer_echo(prompt)
            return state

        # OpenAI via LangChain integration
        if provider == "openai" and _HAVE_LC_OPENAI:
            try:
                llm = _LCChatOpenAI(model=self.model, temperature=self.temperature)
                rsp = llm.invoke(prompt)
                state["answer"] = getattr(rsp, "content", str(rsp))
                return state
            except Exception as e:
                # Fallthrough to SDK if LC path fails at runtime
                print(
                    f"[llm.chat] LangChain OpenAI path failed: {e}. Trying raw SDK..."
                )  # noqa: T201

        # OpenAI via raw SDK (no langchain-openai needed)
        if provider == "openai" and _HAVE_OAI_SDK:
            try:
                client = _OpenAIClient()
                # OpenAI Python SDK v1.x
                kwargs: Dict[str, Any] = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                }
                if self.temperature is not None:
                    kwargs["temperature"] = self.temperature
                resp = client.chat.completions.create(**kwargs)
                state["answer"] = resp.choices[0].message.content or ""
                return state
            except Exception as e:
                print(f"[llm.chat] OpenAI SDK path failed: {e}. Falling back to echo.")  # noqa: T201

        # Final fallback
        if provider == "openai":
            print(
                "[llm.chat] OpenAI provider requested, but neither 'langchain-openai' nor 'openai' are installed. "
                "Install one of them:\n"
                "  pip install langchain-openai\n"
                "  # or\n"
                "  pip install openai\n"
                "Falling back to echo."
            )  # noqa: T201
            state["answer"] = self._answer_echo(prompt)
            return state

        # Unknown provider; echo to keep flows running
        print(f"[llm.chat] Unknown provider '{self.provider}'. Using echo.")  # noqa: T201
        state["answer"] = self._answer_echo(prompt)
        return state
