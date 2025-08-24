from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.chunking import hybrid as _hybrid

Hybrid = make_block_class(
    "Hybrid",
    _hybrid,
    doc="Hybrid(size, overlap) → chunks. Delegates to functional.chunking.hybrid.",
)
