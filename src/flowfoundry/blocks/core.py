from __future__ import annotations
from typing import Any, Callable, Dict, Type


class StrategyBlock:
    """Configurable wrapper around a functional strategy."""

    def __init__(self, fn: Callable[..., Any], **config: Any) -> None:
        self._fn = fn
        self._config: Dict[str, Any] = dict(config)

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        merged = {**self._config, **kwargs}
        return self._fn(*args, **merged)

    def __repr__(self) -> str:
        cname = self.__class__.__name__
        return f"{cname}({self._config})"


def make_block_class(
    name: str, fn: Callable[..., Any], doc: str | None = None
) -> Type[StrategyBlock]:
    class _Block(StrategyBlock):
        def __init__(self, **config: Any) -> None:
            super().__init__(fn, **config)

    _Block.__name__ = name
    _Block.__qualname__ = name
    _Block.__doc__ = doc or f"{name}: wrapper for `{getattr(fn, '__name__', fn)}`"
    return _Block
