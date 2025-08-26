from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, TypeVar, ParamSpec, cast
from importlib.metadata import entry_points
from ..contracts import STRATEGY_CONTRACT_VERSION

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class StrategyRegistries:
    # Heterogeneous registry: strategies can have different signatures
    families: Dict[str, Dict[str, Callable[..., object]]] = field(
        default_factory=lambda: {}
    )

    def register(self, family: str, name: str, fn: Callable[..., object]) -> None:
        self.families.setdefault(family, {})[name] = fn

    def get(self, family: str, name: str) -> Callable[..., object]:
        try:
            return self.families[family][name]
        except KeyError as e:
            avail = list(self.families.get(family, {}).keys())
            raise KeyError(
                f"Strategy '{family}:{name}' not found. Available: {avail}"
            ) from e

    def load_entrypoints(self) -> None:
        eps = entry_points()
        for family in ("ingestion", "chunking", "indexing", "rerank"):
            for ep in eps.select(group=f"flowfoundry.strategies.{family}"):
                self.register(family, ep.name, ep.load())


strategies = StrategyRegistries()


def register_strategy(
    family: str, name: str
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that registers a strategy and preserves the callable's type."""

    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        # Store as a generic callable in the heterogeneous registry
        strategies.register(family, name, cast(Callable[..., object], fn))
        return fn

    return deco


def strategy_contract_version() -> str:
    return STRATEGY_CONTRACT_VERSION
