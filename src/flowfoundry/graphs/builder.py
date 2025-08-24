from __future__ import annotations
from langgraph.graph import StateGraph
from ..config import WorkflowSpec
from ..registry import registries
from ..exceptions import FFConfigError


def compile_workflow(spec: WorkflowSpec):
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
