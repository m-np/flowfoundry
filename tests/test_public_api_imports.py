from flowfoundry import (
    __version__,
    register_strategy,
    chunk_fixed,
)


def test_public_api_minimal():
    assert isinstance(__version__, str)
    assert callable(register_strategy)
    assert callable(chunk_fixed)
