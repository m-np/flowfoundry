from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.chunking import fixed as _fixed

Fixed = make_block_class(
    "Fixed",
    _fixed,
    doc="Fixed(size, overlap) → chunks. Delegates to functional.chunking.fixed.",
)
