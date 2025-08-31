# src/flowfoundry/cli.py
from __future__ import annotations

import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import typer

from flowfoundry.utils.functional_autodiscover import import_all_functional
from flowfoundry.utils.functional_registry import strategies
from flowfoundry.utils.plugin_loader import load_plugins

app = typer.Typer(help="FlowFoundry CLI — auto-discovered functional commands.")

# -------- bootstrap registry ---------------------------------------------------
_imported = import_all_functional()  # import all flowfoundry.functional.* modules
try:
    strategies.load_entrypoints()  # optional: third-party plugins via entry points
except Exception:
    # Safe to ignore if no external entry points are installed
    pass


# -------- helpers --------------------------------------------------------------
def _coerce_kwargs(fn: Callable[..., Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort coercion: matches incoming keys to function params.
    Typer already parsed strings; JSON gives us proper types for most fields.
    """
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
    """
    Read FLOWFOUNDRY_PLUGINS from env (pathsep-separated).
    Example:
      export FLOWFOUNDRY_PLUGINS=\"ext/pdf_loader_openai.py{sep}/opt/plugins\"
    """.format(sep=os.pathsep)
    val = os.getenv("FLOWFOUNDRY_PLUGINS", "").strip()
    if not val:
        return []
    parts = [p.strip() for p in val.split(os.pathsep)]
    return [p for p in parts if p]


def _parse_kv(items: List[str]) -> Dict[str, Any]:
    """Parse --var KEY=VALUE pairs."""
    out: Dict[str, Any] = {}
    for s in items:
        if "=" not in s:
            raise typer.BadParameter(f"--var must be KEY=VALUE (got: {s!r})")
        k, v = s.split("=", 1)
        out[k.strip()] = v
    return out


def _load_vars_json(txt: Optional[str]) -> Dict[str, Any]:
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        if not isinstance(obj, dict):
            raise ValueError("must be a JSON object")
        return obj
    except Exception as e:
        raise typer.BadParameter(f"--vars-json invalid: {e}") from e


def _load_vars_file(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {}
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("file must contain a JSON object")
        return obj
    except Exception as e:
        raise typer.BadParameter(f"--vars-file invalid: {e}") from e


def _env_vars_overrides() -> Dict[str, Any]:
    """
    Accept FLOWFOUNDRY_VARS or FLOWFOUNDRY_VARS_JSON env with a JSON object string.
    Precedence is handled later together with CLI overrides.
    """
    txt = os.getenv("FLOWFOUNDRY_VARS", "") or os.getenv("FLOWFOUNDRY_VARS_JSON", "")
    return _load_vars_json(txt) if txt else {}


# -------- generic 'call' command (works for ANY registered function) ----------
@app.command("call")
def call(
    family: str = typer.Argument(
        ..., help="Family: e.g., chunking | indexing | rerank | ingestion | compose"
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


# -------- auto-generate subcommands for each family/name -----------------------
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


# -------- plan (YAML) runner command ------------------------------------------
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
        False,
        "--plugins-verbose/--no-plugins-verbose",
        help="Print plugin load summaries.",
    ),
    var: List[str] = typer.Option(
        [],
        "--var",
        "-V",
        help='Override a plan variable as KEY=VALUE (repeatable). Example: -V question="Summarize the PDFs"',
    ),
    vars_json: Optional[str] = typer.Option(
        None,
        "--vars-json",
        help='Override plan variables with a JSON object string, e.g. \'{"question":"..."}\'',
    ),
    vars_file: Optional[str] = typer.Option(
        None, "--vars-file", help="Path to a JSON file with variable overrides"
    ),
    vars_verbose: bool = typer.Option(
        False,
        "--vars-verbose/--no-vars-verbose",
        help="Print the final vars after overrides.",
    ),
):
    """
    Execute a FlowFoundry plan (YAML). Example:
      flowfoundry run examples/yaml/rag_with_custom_ingestion.yaml \
        -p examples/external_plugins/pdf_loader_openai.py \
        -V question="Summarize the PDFs"
    """
    # --- 1) Load plugins from env + CLI before loading/merging plan ---
    env_paths = _env_plugin_paths()
    all_plugin_paths = [*env_paths, *plugins]
    if all_plugin_paths:
        summary = load_plugins(all_plugin_paths, export_to_functional=True)
        if plugins_verbose:
            typer.echo(
                json.dumps({"plugins_cli": summary}, indent=2, ensure_ascii=False)
            )

    # --- 2) Load plan dict (raw), then resolve plan-embedded plugins relative to the YAML file ---
    from flowfoundry.plans.runner import (
        load_plan_file as _load_plan_file,
        run_plan as _run_plan,
    )

    plan = _load_plan_file(file)

    # plan-embedded plugin paths (resolve relative to YAML location)
    base = Path(file).resolve().parent
    plan_plugins = plan.get("plugins", [])
    if isinstance(plan_plugins, list) and plan_plugins:
        abs_paths: List[str] = []
        for raw in plan_plugins:
            p = Path(raw)
            if not p.is_absolute():
                p = (base / raw).resolve()
            abs_paths.append(str(p))
        plan_plugin_summary = load_plugins(abs_paths, export_to_functional=True)
        if plugins_verbose:
            typer.echo(
                json.dumps(
                    {"plugins_plan": plan_plugin_summary}, indent=2, ensure_ascii=False
                )
            )

    # --- 3) Merge variable overrides (precedence: YAML < env < --vars-file < --vars-json < --var) ---
    overrides: Dict[str, Any] = {}
    overrides.update(_env_vars_overrides())
    overrides.update(_load_vars_file(vars_file))
    overrides.update(_load_vars_json(vars_json))
    overrides.update(_parse_kv(var))

    if overrides:
        plan.setdefault("vars", {})
        plan["vars"].update(overrides)
        if vars_verbose:
            typer.echo(
                json.dumps({"vars_final": plan["vars"]}, indent=2, ensure_ascii=False)
            )

    # --- 4) Execute the plan ---
    result = _run_plan(plan)

    # --- 5) Print outputs ---
    if print_steps:
        typer.echo(json.dumps(result["steps"], indent=2, ensure_ascii=False))
    if print_outputs or (not print_steps and not print_outputs):
        typer.echo(json.dumps(result["outputs"], indent=2, ensure_ascii=False))


# -------- discovery/info utilities --------------------------------------------
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


def main():
    app()


if __name__ == "__main__":
    main()
