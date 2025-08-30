# src/flowfoundry/utils/llm_registry.py
from __future__ import annotations
from typing import Dict, Type, Any, Tuple
from threading import Lock
from .llm_contracts import LLMProvider
from .exceptions import FFRegistryError

_REG: Dict[str, Type[LLMProvider]] = {}


def register_llm_provider(name: str):
    def deco(cls: Type[LLMProvider]):
        _REG[name.lower()] = cls
        return cls

    return deco


def get_llm_provider(name: str) -> Type[LLMProvider]:
    prov = name.lower()
    if prov not in _REG:
        raise FFRegistryError(f"LLM provider not found: {name}")
    return _REG[prov]


# ---------- NEW: instance caching ----------
_INSTANCES: Dict[Tuple[str, Tuple[Tuple[str, Any], ...]], LLMProvider] = {}
_LOCK = Lock()


def _freeze_kwargs(kwargs: Dict[str, Any]) -> Tuple[Tuple[str, Any], ...]:
    """
    Make kwargs hashable & deterministic: sort by key, and freeze nested dicts/lists/sets.
    """

    def freeze(v: Any) -> Any:
        if isinstance(v, dict):
            return tuple(sorted((k, freeze(v[k])) for k in v))
        if isinstance(v, (list, tuple)):
            return tuple(freeze(x) for x in v)
        if isinstance(v, set):
            return tuple(sorted(freeze(x) for x in v))
        return v

    return tuple(sorted((k, freeze(v)) for k, v in kwargs.items()))


def get_llm_cached(provider: str, **ctor_kwargs: Any) -> LLMProvider:
    """
    Return a cached LLMProvider instance for (provider, ctor_kwargs).
    If absent, create, cache, and return it.
    """
    ProviderCls = get_llm_provider(provider)
    key = (provider.lower(), _freeze_kwargs(ctor_kwargs))
    with _LOCK:
        inst = _INSTANCES.get(key)
        if inst is None:
            inst = ProviderCls(**ctor_kwargs)
            _INSTANCES[key] = inst
        return inst


def clear_llm_cache():
    with _LOCK:
        _INSTANCES.clear()
