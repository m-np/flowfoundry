from __future__ import annotations
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict, Any
from time import perf_counter
import uuid
from .config import WorkflowSpec
from .graphs.builder import compile_workflow
from .registry import register_entrypoints, registries
from .schema import workflow_jsonschema
from .exceptions import FFError
from fastapi.responses import JSONResponse
from .strategies.registry import strategies as _strategies

app = FastAPI(title="FlowFoundry")


class RunRequest(BaseModel):
    spec: WorkflowSpec
    state: Dict[str, Any] = {}


@app.on_event("startup")
async def _startup():
    register_entrypoints()


@app.exception_handler(FFError)
async def ff_error_handler(_: Request, exc: FFError):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
                "code": "FF_ERROR",
            }
        },
    )


@app.get("/components")
async def components():
    return {
        "nodes": sorted(list(registries.nodes.keys())),
        "memories": sorted(list(registries.memories.keys())),
        "workflows": sorted(list(registries.workflows.keys())),
        "models": sorted(list(registries.models.keys())),
        "strategies": {
            family: sorted(names.keys())
            for family, names in _strategies.families.items()
        },
    }


@app.get("/schema")
async def schema():
    return workflow_jsonschema()


@app.post("/run")
async def run(req: RunRequest):
    trace_id = str(uuid.uuid4())
    t0 = perf_counter()
    graph = compile_workflow(req.spec)
    out = graph.invoke(req.state)
    duration_ms = int((perf_counter() - t0) * 1000)
    return {"state": out, "trace_id": trace_id, "duration_ms": duration_ms}
