from .config import WorkflowSpec


def workflow_jsonschema() -> dict:
    return WorkflowSpec.model_json_schema()
