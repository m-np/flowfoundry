from __future__ import annotations
from typing import Any, Dict, Mapping, cast
import sys

# External YAML parser (PyYAML)
try:
    import yaml
except Exception:
    print("Please `pip install pyyaml` to use plan YAMLs.", file=sys.stderr)
    raise

# Reuse global functional registry (same object CLI uses)
from ..utils import strategies  # StrategyRegistries


class _Ctx:
    def __init__(self, vars: Dict[str, Any] | None = None):
        self.vars: Dict[str, Any] = vars or {}
        self.steps: Dict[str, Any] = {}

    def get(self, ref: str) -> Any:
        if ref.startswith("vars."):
            base, path = self.vars, ref[len("vars.") :]
        else:
            first, *rest = ref.split(".", 1)
            if first not in self.steps:
                raise KeyError(f"Unknown step '{first}'")
            base = self.steps[first]
            path = rest[0] if rest else ""
        if not path:
            return base

        def _index(obj: Any, token: str) -> Any:
            if "[" in token:
                head, *rest = token.split("[")
                if head:
                    obj = _index(obj, head)
                for r in rest:
                    key = r[:-1]
                    if key.isdigit():
                        obj = obj[int(key)]
                    else:
                        if (key.startswith("'") and key.endswith("'")) or (
                            key.startswith('"') and key.endswith('"')
                        ):
                            key = key[1:-1]
                        obj = obj[key]
                return obj
            if isinstance(obj, Mapping) and token in obj:
                return obj[token]
            if hasattr(obj, token):
                return getattr(obj, token)
            try:
                return obj[token]
            except Exception:
                pass
            raise KeyError(f"Cannot resolve '{token}' in {type(obj).__name__}")

        cur = base
        for tok in path.split("."):
            if tok:
                cur = _index(cur, tok)
        return cur


def _is_ref(val: Any) -> bool:
    return (
        isinstance(val, str)
        and val.strip().startswith("${{")
        and val.strip().endswith("}}")
    )


def _resolve(obj: Any, ctx: _Ctx) -> Any:
    if isinstance(obj, dict):
        return {k: _resolve(v, ctx) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve(v, ctx) for v in obj]
    if _is_ref(obj):
        inner = obj.strip()[3:-2].strip()
        return ctx.get(inner)
    return obj


def run_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a FlowFoundry plan:
      version: 1
      vars: {...}
      steps: [{id, use, with}, ...]
      outputs: {...}
    """
    version = plan.get("version", 1)
    if version != 1:
        raise ValueError(f"Unsupported plan version: {version}")

    ctx = _Ctx(vars=plan.get("vars", {}))
    steps = plan.get("steps", [])
    if not steps or not isinstance(steps, list):
        raise ValueError("Plan must include non-empty 'steps'")

    reg = strategies  # StrategyRegistries (families -> {name: fn})

    for s in steps:
        sid = s.get("id")
        use = s.get("use")
        kwargs = s.get("with", {})

        if not sid or not use:
            raise ValueError(f"Each step needs 'id' and 'use'. Got: {s}")

        kw = _resolve(kwargs, ctx)

        # Resolve callable: allow "family.name" or bare "name"
        fn = None
        if "." in use:
            family, name = use.split(".", 1)
            fn = reg.get(family, name)
        else:
            for fam, fns in reg.families.items():
                if use in fns:
                    fn = fns[use]
                    break
        if fn is None:
            raise AttributeError(f"No function '{use}' in functional registry")

        out = fn(**kw)
        ctx.steps[sid] = out

    outputs = plan.get("outputs", {})
    final = _resolve(outputs, ctx) if outputs else {}
    return {"version": version, "steps": ctx.steps, "outputs": final}


def load_plan_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return cast(Dict[str, Any], yaml.safe_load(f))


def run_plan_file(path: str) -> Dict[str, Any]:
    return run_plan(load_plan_file(path))


# Backwards-compat alias for older CLI/imports that expect "run_yaml_file"
run_yaml_file = run_plan_file
