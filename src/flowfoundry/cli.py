from __future__ import annotations

import json
import inspect
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import typer

from flowfoundry.utils.functional_registry import strategies
from flowfoundry.utils.functional_autodiscover import import_all_functional
from flowfoundry.utils.plugin_loader import load_plugins

# Plan/YAML runner (optional import)
run_yaml_file: Optional[Callable[[str], Dict[str, Any]]] = None
_plan_runner_available = False
try:
    from flowfoundry.plans.runner import run_plan_file as _run_yaml_file

    run_yaml_file = _run_yaml_file
    _plan_runner_available = True
except Exception:
    pass

app = typer.Typer(help="FlowFoundry CLI — auto-discovered functional commands.")

# bootstrap registry
_imported = import_all_functional()
try:
    strategies.load_entrypoints()
except Exception:
    pass


def _coerce_kwargs(fn: Callable[..., Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    sig = inspect.signature(fn)
    out: Dict[str, Any] = {}
    for name in sig.parameters:
        if name in raw:
            out[name] = raw[name]
    return out


def _load_kwargs(kwargs: str | None, kwargs_file: str | None) -> Dict[str, Any]:
    if kwargs_file:
        data = json.loads(Path(kwargs_file).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise typer.BadParameter("--kwargs-file must contain a JSON object")
        return data
    if kwargs:
        data = json.loads(kwargs)
        if not isinstance(data, dict):
            raise typer.BadParameter("--kwargs must be a JSON object string")
        return data
    return {}


def _env_plugin_paths() -> List[str]:
    val = os.getenv("FLOWFOUNDRY_PLUGINS", "").strip()
    if not val:
        return []
    return [p for p in (s.strip() for s in val.split(os.pathsep)) if p]


@app.command("call")
def call(
    family: str = typer.Argument(
        ..., help="Family: e.g., chunking | indexing | rerank | ingestion"
    ),
    name: str = typer.Argument(
        ..., help="Strategy/function name registered under the family"
    ),
    kwargs: str | None = typer.Option(
        None, "--kwargs", help="JSON object string of parameters"
    ),
    kwargs_file: str | None = typer.Option(
        None, "--kwargs-file", help="Path to JSON file with parameters"
    ),
    pretty: bool = typer.Option(
        True, "--pretty/--no-pretty", help="Pretty-print JSON results"
    ),
):
    try:
        fn = strategies.get(family, name)
    except KeyError as e:
        raise typer.BadParameter(str(e))
    raw = _load_kwargs(kwargs, kwargs_file)
    args = _coerce_kwargs(fn, raw)
    result = fn(**args)
    try:
        s = json.dumps(result, ensure_ascii=False, indent=2 if pretty else None)
        typer.echo(s)
    except TypeError:
        typer.echo(repr(result))


def _register_family_commands() -> None:
    for family in sorted(strategies.list_families()):
        sub = typer.Typer(help=f"{family} functions")
        app.add_typer(sub, name=family)
        for name in sorted(strategies.list_names(family)):
            fn = strategies.get(family, name)

            def _make_cmd(_fn: Callable[..., Any], _name: str, _family: str):
                def _cmd(
                    kwargs: str | None = typer.Option(
                        None, "--kwargs", help="JSON object string for parameters"
                    ),
                    kwargs_file: str | None = typer.Option(
                        None, "--kwargs-file", help="Path to JSON file with parameters"
                    ),
                    pretty: bool = typer.Option(
                        True, "--pretty/--no-pretty", help="Pretty-print JSON results"
                    ),
                ):
                    raw = _load_kwargs(kwargs, kwargs_file)
                    args = _coerce_kwargs(_fn, raw)
                    res = _fn(**args)
                    try:
                        s = json.dumps(
                            res, ensure_ascii=False, indent=2 if pretty else None
                        )
                        typer.echo(s)
                    except TypeError:
                        typer.echo(repr(res))

                _cmd.__name__ = f"{_family}_{_name}_cmd"
                _cmd.__doc__ = f"{_family}:{_name}  ({_fn.__module__}.{_fn.__name__})"
                return _cmd

            sub.command(name)(_make_cmd(fn, name, family))


_register_family_commands()


@app.command("run")
def run_plan(
    file: str = typer.Argument(..., help="Path to plan YAML"),
    print_steps: bool = typer.Option(False, help="Print all step outputs as JSON"),
    print_outputs: bool = typer.Option(False, help="Print outputs as JSON (default)"),
    plugins: List[str] = typer.Option(
        [],
        "--plugins",
        "-p",
        help=f"Plugin files/dirs to import before running (also reads FLOWFOUNDRY_PLUGINS via {os.pathsep}-sep).",
    ),
    plugins_verbose: bool = typer.Option(
        False, "--plugins-verbose/--no-plugins-verbose"
    ),
):
    env_paths = _env_plugin_paths()
    all_plugin_paths = [*env_paths, *plugins]
    if all_plugin_paths:
        summary = load_plugins(all_plugin_paths, export_to_functional=True)
        if plugins_verbose:
            typer.echo(json.dumps({"plugins": summary}, indent=2, ensure_ascii=False))

    if not _plan_runner_available or run_yaml_file is None:
        raise typer.BadParameter(
            "Plan runner unavailable. Ensure PyYAML is installed and flowfoundry.plans.runner exists."
        )

    assert run_yaml_file is not None
    result = run_yaml_file(file)

    if print_steps:
        typer.echo(json.dumps(result["steps"], indent=2, ensure_ascii=False))
    if print_outputs or (not print_steps and not print_outputs):
        typer.echo(json.dumps(result["outputs"], indent=2, ensure_ascii=False))


@app.command("list")
def list_all():
    for fam in sorted(strategies.list_families()):
        names = ", ".join(sorted(strategies.list_names(fam)))
        typer.echo(f"{fam}: {names}")


@app.command("info")
def info():
    typer.echo(f"Imported functional modules: {_imported}")
    typer.echo(f"Families: {sorted(strategies.list_families())}")


def main():
    app()


if __name__ == "__main__":
    main()
