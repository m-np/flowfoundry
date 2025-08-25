def ping() -> str:
    """Lightweight health check."""
    return "flowfoundry: ok"


def hello(name: str = "world") -> str:
    """Simple greeting helper."""
    return f"hello, {name}!"
