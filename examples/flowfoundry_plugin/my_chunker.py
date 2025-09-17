from flowfoundry.utils.functional_registry import register_strategy


@register_strategy("chunking", "toy_chunks")
def toy_chunks(data: str, *, size: int = 3):
    parts = [data[i : i + size] for i in range(0, len(data), size)]
    out, off = [], 0
    for k, p in enumerate(parts):
        out.append(
            {
                "doc": "doc",
                "text": p,
                "start": off,
                "end": off + len(p),
                "chunk_index": k,
            }
        )
        off += len(p)
    return out
