# src/flowfoundry/cli.py
from __future__ import annotations

import json
import inspect
from pathlib import Path
from typing import Any, Callable, Dict

import typer

from flowfoundry.utils.functional_registry import strategies
from flowfoundry.utils.functional_autodiscover import import_all_functional

app = typer.Typer(help="FlowFoundry CLI — auto-discovered functional commands.")


# -------- bootstrap registry --------
_imported = import_all_functional()  # import all flowfoundry.functional.* modules
try:
    strategies.load_entrypoints()  # optional: third-party plugins via entry points
except Exception:
    # Safe to ignore if no external entry points are installed
    pass


# -------- helpers --------
def _coerce_kwargs(fn: Callable[..., Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort coercion: matches incoming keys to function params.
    Typer already parsed strings; JSON gives us proper types for most fields.
    """
    sig = inspect.signature(fn)
    out: Dict[str, Any] = {}
    for name, param in sig.parameters.items():
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


# -------- generic 'call' command (works for ANY registered function) --------
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
    """
    Invoke any registered functional callable by family/name:
    flowfoundry call chunking fixed --kwargs '{"data":"...","chunk_size":800}'
    """
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
        # Not JSON-serializable; just print repr
        typer.echo(repr(result))


# -------- auto-generate subcommands for each family/name --------
def _register_family_commands() -> None:
    """
    For every family and registered name, attach a subcommand:
    e.g., `flowfoundry chunking fixed --kwargs ...`
    """
    for family in sorted(strategies.list_families()):
        sub = typer.Typer(help=f"{family} functions")
        app.add_typer(sub, name=family)

        for name in sorted(strategies.list_names(family)):
            fn = strategies.get(family, name)

            def _make_cmd(_fn: Callable[..., Any], _name: str):
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

                _cmd.__name__ = f"{family}_{_name}_cmd"
                _cmd.__doc__ = f"{family}:{_name}  ({_fn.__module__}.{_fn.__name__})"
                return _cmd

            sub.command(name)(_make_cmd(fn, name))


_register_family_commands()


# -------- discovery/info utilities --------
@app.command("list")
def list_all():
    """List all families and names registered."""
    for fam in sorted(strategies.list_families()):
        names = ", ".join(sorted(strategies.list_names(fam)))
        typer.echo(f"{fam}: {names}")


@app.command("info")
def info():
    """Show basic discovery details."""
    typer.echo(f"Imported functional modules: {_imported}")
    typer.echo(f"Families: {sorted(strategies.list_families())}")


if __name__ == "__main__":
    app()
