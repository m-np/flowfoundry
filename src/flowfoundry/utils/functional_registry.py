# src/flowfoundry/utils/functional_registry.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, TypeVar, ParamSpec, cast, List
from importlib.metadata import entry_points

# Pull the contract version (and custom errors if you later want to use them)
from .functional_contracts import STRATEGY_CONTRACT_VERSION

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class StrategyRegistries:
    """
    Heterogeneous registry: strategies may have different call signatures.

    Example structure:
        families = {
            "ingestion": {"name": callable, ...},
            "chunking":  {"name": callable, ...},
            "indexing":  {"name": callable, ...},
            "rerank":    {"name": callable, ...},
        }
    """

    families: Dict[str, Dict[str, Callable[..., object]]] = field(default_factory=dict)

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
            # If you prefer custom error type:
            # raise FFRegistryError(f"{self.__class__.__name__}: '{family}:{name}' not found. Available: {avail}") from e

    def has(self, family: str, name: str) -> bool:
        return name in self.families.get(family, {})

    def list_families(self) -> List[str]:
        return list(self.families.keys())

    def list_names(self, family: str) -> List[str]:
        return list(self.families.get(family, {}).keys())

    def load_entrypoints(self) -> None:
        """
        Discover and register strategies exposed via Python entry points.

        Expected entry point groups:
          - flowfoundry.strategies.ingestion
          - flowfoundry.strategies.chunking
          - flowfoundry.strategies.indexing
          - flowfoundry.strategies.rerank
        """
        eps = entry_points()
        for family in ("ingestion", "chunking", "indexing", "rerank"):
            for ep in eps.select(group=f"flowfoundry.strategies.{family}"):
                self.register(family, ep.name, ep.load())


# Global registry instance (backward compatible)
strategies = StrategyRegistries()


def register_strategy(
    family: str, name: str
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that registers a strategy and preserves the callable's type.

    Usage:
        @register_strategy("chunking", "fixed")
        def fixed(...): ...
    """

    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        strategies.register(family, name, cast(Callable[..., object], fn))
        return fn

    return deco


def strategy_contract_version() -> str:
    return STRATEGY_CONTRACT_VERSION


__all__ = [
    "StrategyRegistries",
    "strategies",
    "register_strategy",
    "strategy_contract_version",
]
