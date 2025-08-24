from __future__ import annotations
import typer
import json
from pathlib import Path
from .config import load_workflow_yaml, WorkflowSpec
from .graphs.builder import compile_workflow
from .registry import register_entrypoints, registries
from .schema import workflow_jsonschema
from .strategies.registry import strategies

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def list():
    """List registered components and strategies."""
    register_entrypoints()
    typer.echo("Nodes:\n" + "\n".join(sorted(registries.nodes)))
    typer.echo("\nStrategies:")
    for family in sorted(strategies.families.keys()):
        names = ", ".join(sorted(strategies.families[family].keys()))
        typer.echo(f"  {family}: {names}")


@app.command()
def run(path: Path, state: str = "{}"):
    """Run a workflow from YAML (state as JSON string)."""
    spec: WorkflowSpec = load_workflow_yaml(str(path))
    graph = compile_workflow(spec)
    result = graph.invoke(json.loads(state))
    typer.echo(json.dumps(result, indent=2))


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000):
    """Start the local FastAPI service."""
    import uvicorn

    uvicorn.run("flowfoundry.api:app", host=host, port=port, reload=False)


@app.command()
def schema(
    out: Path = typer.Argument(..., help="Output path for the workflow JSON Schema"),
):
    """Write workflow JSON Schema to a file (positional OUT path)."""
    s = workflow_jsonschema()
    text = json.dumps(s, indent=2)
    out.write_text(text)
    typer.echo(f"Wrote schema to {out}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
