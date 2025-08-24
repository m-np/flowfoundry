from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List
import yaml


class NodeSpec(BaseModel):
    id: str
    type: str
    params: Dict[str, Any] = Field(default_factory=dict)


class EdgeSpec(BaseModel):
    source: str
    target: str


class WorkflowSpec(BaseModel):
    schema_version: str = "1.0"
    nodes: List[NodeSpec]
    edges: List[EdgeSpec]
    start: str

    def json_schema(self) -> Dict[str, Any]:
        return self.model_json_schema()


def load_workflow_yaml(path: str) -> WorkflowSpec:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return WorkflowSpec.model_validate(data)
