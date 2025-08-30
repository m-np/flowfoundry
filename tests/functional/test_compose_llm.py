from typing import Any
from flowfoundry.functional.composer.llmcompose import compose_llm
from flowfoundry.utils import register_llm_provider, LLMProvider


# Register a dummy provider so we don't need external services
@register_llm_provider("dummy")
class DummyProvider(LLMProvider):
    def __init__(self, model: str, **_: Any):
        self.model = model

    def generate(
        self, *, system: str, user: str, max_tokens: int = 512, **_: Any
    ) -> str:
        # deterministic and short for test
        return f"[{self.model}] sys={system[:12]} user={user[:12]} tok={max_tokens}"


def test_compose_llm_with_dummy_provider():
    hits = [
        {
            "text": "The people's budget is set to $1,000.",
            "metadata": {"source": "budget.pdf", "page": 3},
        },
        {"text": "Other useful info.", "metadata": {"source": "budget.pdf", "page": 4}},
    ]
    out = compose_llm(
        "What is people's budget?",
        hits,
        provider="dummy",
        model="test-model",
        max_tokens=64,
    )
    assert out.startswith("[test-model]")


def test_compose_llm_no_context_graceful():
    out = compose_llm("Any info?", [], provider="dummy", model="test-model")
    assert "couldn't find relevant context" in out
