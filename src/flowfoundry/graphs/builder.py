from __future__ import annotations
from typing import Any, Dict, TypedDict

from langgraph.graph import StateGraph

from ..config import WorkflowSpec
from ..registry import registries, register_entrypoints
from ..exceptions import FFConfigError


# A permissive state schema used across examples/workflows.
# total=False => every key is optional, so it works for different flows.
class WorkflowState(TypedDict, total=False):
    query: str
    retrieved: list[Dict[str, object]]
    chunks: list[Dict[str, object]]
    prompt: str
    answer: str
    document: str
    doc_id: str
    index_name: str


def _ensure_builtins_loaded() -> None:
    # Importing functional registers strategies via decorators
    from .. import functional  # noqa: F401

    # Import nodes to register @register_node classes
    from ..nodes import io_pdf, prompt, llm_chat, strategy_nodes  # noqa: F401


def compile_workflow(spec: WorkflowSpec):
    # Ensure plugins + built-ins are registered
    register_entrypoints()
    _ensure_builtins_loaded()

    # Use a TypedDict as the state schema (what mypy/langgraph expect)
    g = StateGraph(WorkflowState)

    node_objs: Dict[str, Any] = {}

    for n in spec.nodes:
        NodeCls = registries.nodes.get(n.type)
        if NodeCls is None:
            raise FFConfigError(f"Unknown node type: {n.type}")
        node_objs[n.id] = NodeCls(**n.params)
        g.add_node(n.id, node_objs[n.id])

    for e in spec.edges:
        if e.source not in node_objs or e.target not in node_objs:
            raise FFConfigError(f"Invalid edge {e.source}->{e.target}")
        g.add_edge(e.source, e.target)

    if spec.start not in node_objs:
        raise FFConfigError(f"Invalid entry point: {spec.start}")

    g.set_entry_point(spec.start)
    return g.compile()
