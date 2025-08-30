import pytest
from typing import Any
from flowfoundry.utils.functional_registry import strategies, register_strategy


def test_register_and_get_strategy_roundtrip():
    @register_strategy("chunking", "unit_fixed")
    def unit_fixed(data: str, chunk_size: int = 4) -> list[dict[str, Any]]:
        return [
            {
                "text": data[i : i + chunk_size],
                "start": i,
                "end": i + chunk_size,
                "doc": "X",
                "chunk_index": i // chunk_size,
            }
            for i in range(0, len(data), chunk_size)
        ]

    fn = strategies.get("chunking", "unit_fixed")
    out = fn("abcdef", chunk_size=2)
    assert isinstance(out, list) and len(out) == 3
    with pytest.raises(KeyError):
        strategies.get("chunking", "does_not_exist")
