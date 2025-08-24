from __future__ import annotations
from typing import Dict, Type
from importlib.metadata import entry_points
from dataclasses import dataclass, field
from .exceptions import FFRegistryError


@dataclass
class _Registries:
    nodes: Dict[str, Type] = field(default_factory=dict)
    memories: Dict[str, Type] = field(default_factory=dict)
    workflows: Dict[str, Type] = field(default_factory=dict)
    models: Dict[str, Type] = field(default_factory=dict)


registries = _Registries()


def register_node(name: str):
    def deco(cls):
        if name in registries.nodes:
            raise FFRegistryError(f"Node '{name}' already registered")
        registries.nodes[name] = cls
        return cls

    return deco


def register_memory(name: str):
    def deco(cls):
        if name in registries.memories:
            raise FFRegistryError(f"Memory '{name}' already registered")
        registries.memories[name] = cls
        return cls

    return deco


def register_workflow(name: str):
    def deco(cls):
        if name in registries.workflows:
            raise FFRegistryError(f"Workflow '{name}' already registered")
        registries.workflows[name] = cls
        return cls

    return deco


def register_model(name: str):
    def deco(cls):
        if name in registries.models:
            raise FFRegistryError(f"Model '{name}' already registered")
        registries.models[name] = cls
        return cls

    return deco


def register_entrypoints() -> None:
    eps = entry_points()
    for group, dest in [
        ("flowfoundry.nodes", registries.nodes),
        ("flowfoundry.memories", registries.memories),
        ("flowfoundry.workflows", registries.workflows),
        ("flowfoundry.models", registries.models),
    ]:
        for ep in eps.select(group=group):
            if ep.name in dest:
                continue
            dest[ep.name] = ep.load()
