#!/usr/bin/env python3
# examples/python/07_rag_with_custom_ingestion.py
"""
RAG pipeline that can use a CUSTOM decorator-registered ingestion function
(from plain .py files) or fall back to the built-in loader.

Usage:
  python examples/python/07_rag_with_custom_ingestion.py \
    --plugins external_plugins/pdf_loader_openai.py \
    --data-path docs/samples \
    --use-openai false \
    --question "What is people's budget?" \
    --provider openai --lm gpt-4o-mini --k 8 --top-k 5 --verbose

Notes:
- Pass one or more plugin files/dirs via --plugins (or set FLOWFOUNDRY_PLUGINS).
- If a plugin registers `ingestion.pdf_loader_openai`, it will be used; otherwise
  the script falls back to the built-in `ingestion.pdf_loader`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from flowfoundry.utils.plugin_loader import load_plugins
from flowfoundry.utils.functional_registry import strategies


# ----------------------------- CLI -------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="FlowFoundry RAG with custom ingestion")
    # Plugins
    p.add_argument(
        "--plugins",
        "-p",
        nargs="*",
        default=[],
        help="Paths to plugin .py files or directories to import before running.",
    )
    # Data / storage
    p.add_argument("--data-path", default="docs/samples", help="PDF file or directory.")
    p.add_argument("--chroma-path", default=".ff_chroma", help="Chroma DB path.")
    p.add_argument("--collection", default="docs", help="Chroma collection name.")
    # Ingestion (custom only)
    p.add_argument(
        "--use-openai",
        default="false",
        choices=["true", "false"],
        help="Only used if custom loader supports it.",
    )
    p.add_argument(
        "--model", default="gpt-4o-mini", help="Model for custom loader (if used)."
    )
    # Chunking
    p.add_argument("--chunk-size", type=int, default=500, help="Chunk size.")
    p.add_argument("--chunk-overlap", type=int, default=50, help="Chunk overlap.")
    # Retrieval / Rerank
    p.add_argument(
        "--question",
        default="Summarize the budget context.",
        help="Query for retrieval + answering.",
    )
    p.add_argument("--k", type=int, default=8, help="Top-K to retrieve.")
    p.add_argument("--top-k", type=int, default=5, help="Top-K after BM25 preselect.")
    p.add_argument(
        "--show-hits", action="store_true", help="Print retrieved hits preview."
    )
    # LLM compose
    p.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "ollama", "huggingface", "langchain"],
        help="LLM provider.",
    )
    p.add_argument("--lm", default="gpt-4o-mini", help="LLM model name (per provider).")
    p.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Host for providers that need it (e.g., Ollama).",
    )
    p.add_argument("--max-tokens", type=int, default=400, help="Answer max tokens.")
    # Verbosity
    p.add_argument("--verbose", action="store_true", help="Print plugin/registry info.")
    return p.parse_args()


def _bool(s: str) -> bool:
    return s.strip().lower() in {"1", "true", "yes", "y"}


# ---------------------- Ingestion resolution ----------------------------------
def resolve_ingestion(
    use_openai_flag: bool, model: str
) -> Tuple[Callable[..., Any], Dict[str, Any], str]:
    """
    Prefer a custom strategy registered as `ingestion.pdf_loader_openai`.
    If not found, fall back to built-in `ingestion.pdf_loader`.

    Returns: (callable, kwargs, label)
    """
    # Try registered custom function first
    try:
        fn = strategies.get("ingestion", "pdf_loader_openai")
        return (
            fn,
            {"use_openai": use_openai_flag, "model": model},
            "ingestion.pdf_loader_openai",
        )
    except KeyError:
        pass

    # Fallback to built-in loader (takes only `path`)
    try:
        from flowfoundry import pdf_loader as builtin_loader

        return builtin_loader, {}, "ingestion.pdf_loader"
    except Exception as e:
        raise RuntimeError("No ingestion loader available (custom or built-in).") from e


# ----------------------- Chunk mapping helper ---------------------------------
def map_pages_to_chunks(
    pages: List[Dict[str, Any]],
    *,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Dict[str, Any]]:
    """
    Convert page dicts: {"source": str, "page": int, "text": str}
    into FlowFoundry chunk dicts compatible with indexing, preserving metadata.
    """
    from flowfoundry.functional import chunk_recursive  # import after plugins loaded

    chunks: List[Dict[str, Any]] = []
    for p in pages:
        text = (p.get("text") or "").strip()
        if not text:
            continue
        doc_id = f"{Path(p['source']).stem}_p{p['page']}"
        for ch in chunk_recursive(
            text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, doc_id=doc_id
        ):
            meta = dict(ch.get("meta", {}))
            meta.update({"source": p["source"], "page": p["page"]})
            ch["meta"] = meta
            chunks.append(ch)
    return chunks


# ----------------------------- Main ------------------------------------------
def main() -> None:
    args = parse_args()
    use_openai = _bool(args.use_openai)

    # 1) Import plugin files/dirs FIRST so decorators run (and optional FF_EXPORTS bind)
    all_plugins: List[str] = list(args.plugins)
    env_paths = os.getenv("FLOWFOUNDRY_PLUGINS", "")
    if env_paths:
        all_plugins.extend([p for p in env_paths.split(os.pathsep) if p.strip()])

    if all_plugins:
        summary = load_plugins(all_plugins, export_to_functional=True)
        if args.verbose:
            print(
                "Plugin load summary:",
                json.dumps(summary, indent=2, ensure_ascii=False),
            )

    # Optional: show ingestion strategies now present
    if args.verbose:
        ing = (
            sorted(strategies.list_names("ingestion"))
            if "ingestion" in strategies.families
            else []
        )
        print("Ingestion strategies:", ing)

    # 2) Resolve which ingestion function to use
    loader, extra_kwargs, label = resolve_ingestion(use_openai, args.model)
    if args.verbose:
        print("Using loader:", label)

    # 3) Ingest pages
    pages = loader(args.data_path, **extra_kwargs)
    print(f"[load] pages = {len(pages)}")

    # 4) Chunk pages
    chunks = map_pages_to_chunks(
        pages, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap
    )
    print(f"[chunk] chunks = {len(chunks)}")

    # 5) Index
    from flowfoundry.functional import (
        index_chroma_upsert,
        index_chroma_query,
        preselect_bm25,
        compose_llm,
    )

    index_chroma_upsert(chunks, path=args.chroma_path, collection=args.collection)
    print(
        f"[index] upserted {len(chunks)} chunks → {args.chroma_path}:{args.collection}"
    )

    # 6) Retrieve + rerank
    hits = index_chroma_query(
        args.question, path=args.chroma_path, collection=args.collection, k=args.k
    )
    hits = preselect_bm25(args.question, hits, top_k=args.top_k)
    print(f"[retrieve] hits = {len(hits)} for query: {args.question}")

    if args.verbose:
        for i, h in enumerate(hits[:10], 1):
            snippet = (h.get("text", "") or "").replace("\n", " ")[:120]
            print(f"  {i:02d}. {snippet}...")

    # 7) Compose final answer
    compose_kwargs: Dict[str, Any] = dict(
        question=args.question,
        hits=hits,
        provider=args.provider,
        model=args.lm,
        max_tokens=args.max_tokens,
        reuse_provider=True,
    )
    if args.provider == "ollama":
        compose_kwargs["host"] = args.host

    answer = compose_llm(**compose_kwargs)
    print("\n=== Final Answer ===")
    print(answer)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ Error:", e)
        sys.exit(1)
