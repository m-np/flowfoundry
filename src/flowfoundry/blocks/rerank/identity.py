from __future__ import annotations
from flowfoundry.blocks.core import make_block_class
from flowfoundry.functional.rerank import identity as _id

Identity = make_block_class(
    "Identity",
    _id,
    doc="Identity() → hits (no-op). Delegates to functional.rerank.identity.",
)
