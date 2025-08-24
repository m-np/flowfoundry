from __future__ import annotations
from langgraph.graph import StateGraph
from ..config import WorkflowSpec
from ..registry import registries, register_entrypoints
from ..exceptions import FFConfigError


def _ensure_builtins_loaded() -> None:
    # Importing functional registers strategies via decorators
    from .. import functional  # noqa: F401

    # Import nodes to register @register_node classes
    from ..nodes import io_pdf, prompt, llm_chat, strategy_nodes  # noqa: F401


def compile_workflow(spec: WorkflowSpec):
    # Make sure entry points and built-ins are loaded
    register_entrypoints()
    _ensure_builtins_loaded()

    g = StateGraph(dict)
    node_objs = {}

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
