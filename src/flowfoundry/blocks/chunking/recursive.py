from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.chunking import recursive as _recursive

Recursive = make_block_class(
    "Recursive",
    _recursive,
    doc="Recursive(size, overlap) → chunks. Delegates to functional.chunking.recursive.",
)
