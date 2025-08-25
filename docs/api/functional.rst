Functional Strategies
=====================

Single source of truth: all strategy logic lives here.

.. list-table:: Available functions
   :header-rows: 1

   * - Function
     - Purpose
     - Extra deps
   * - :py:func:`flowfoundry.functional.chunking.fixed.fixed`
     - Fixed-size sliding window splitter
     - –
   * - :py:func:`flowfoundry.functional.chunking.recursive.recursive`
     - Recursive splitter (falls back to fixed)
     - langchain-text-splitters (optional)
   * - :py:func:`flowfoundry.functional.chunking.hybrid.hybrid`
     - Hybrid/example splitter
     - –
   * - :py:func:`flowfoundry.functional.indexing.chroma.chroma_upsert`
     - Upsert chunks into Chroma
     - chromadb
   * - :py:func:`flowfoundry.functional.indexing.chroma.chroma_query`
     - Query a Chroma collection
     - chromadb
   * - :py:func:`flowfoundry.functional.indexing.qdrant.qdrant_upsert`
     - Upsert vectors into Qdrant
     - qdrant-client
   * - :py:func:`flowfoundry.functional.indexing.qdrant.qdrant_query`
     - Vector search in Qdrant
     - qdrant-client
   * - :py:func:`flowfoundry.functional.rerank.identity.identity`
     - No-op reranker
     - –
   * - :py:func:`flowfoundry.functional.rerank.bm25.bm25_preselect`
     - BM25 preselect (top_k)
     - rank-bm25 (optional)
   * - :py:func:`flowfoundry.functional.rerank.cross_encoder.cross_encoder`
     - Sentence-transformers cross-encoder reranker
     - sentence-transformers

Usage
-----

.. code-block:: python

   from flowfoundry.functional import (
     chunk_recursive, index_chroma_upsert, index_chroma_query, preselect_bm25
   )

   chunks = chunk_recursive("Some text...", size=200, overlap=20, doc_id="doc1")
   index_chroma_upsert(chunks, path=".ff_chroma", collection="docs")
   hits = index_chroma_query("What is this?", path=".ff_chroma", collection="docs", k=10)
   hits = preselect_bm25("What is this?", hits, top_k=5)

API
---

.. autosummary::
   :toctree: generated
   :nosignatures:

   flowfoundry.functional.chunking.fixed.fixed
   flowfoundry.functional.chunking.recursive.recursive
   flowfoundry.functional.chunking.hybrid.hybrid
   flowfoundry.functional.indexing.chroma.chroma_upsert
   flowfoundry.functional.indexing.chroma.chroma_query
   flowfoundry.functional.indexing.qdrant.qdrant_upsert
   flowfoundry.functional.indexing.qdrant.qdrant_query
   flowfoundry.functional.rerank.identity.identity
   flowfoundry.functional.rerank.bm25.bm25_preselect
   flowfoundry.functional.rerank.cross_encoder.cross_encoder
