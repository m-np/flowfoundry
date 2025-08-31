# external_plugins/pdf_loader_openai.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Union

from flowfoundry.utils import register_strategy, FFIngestionError

# Optional deps
try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None
try:
    from openai import OpenAI  # only if you want to use OpenAI
except Exception:
    OpenAI = None


@register_strategy("ingestion", "pdf_loader_openai")
def pdf_loader_openai(
    path: Union[str, Path],
    *,
    model: str = "gpt-4o-mini",
    api_key: str | None = None,
    use_openai: bool = False,
    skip_empty_pages: bool = True,
) -> List[Dict]:
    """
    Returns: [{"source": str, "page": int, "text": str}, ...]
    """
    root = Path(path)
    if not root.exists():
        raise FFIngestionError(f"❌ Path not found: {root}")

    pdfs = (
        [root]
        if (root.is_file() and root.suffix.lower() == ".pdf")
        else list(root.rglob("*.pdf"))
    )
    if not pdfs:
        raise FFIngestionError(f"❌ No PDFs under {root}")

    pages: List[Dict] = []
    for pdf in pdfs:
        # basic baseline with PyPDF; replace/augment with OpenAI as you like
        if PdfReader is None and not use_openai:
            raise FFIngestionError(
                "pypdf not installed; install pypdf or set use_openai=True"
            )

        extracted: List[Dict] = []
        if PdfReader is not None:
            reader = PdfReader(str(pdf))
            for i, page in enumerate(reader.pages, start=1):
                text = (page.extract_text() or "").strip()
                if text or not skip_empty_pages:
                    extracted.append(
                        {"source": str(pdf.resolve()), "page": i, "text": text}
                    )

        # If use_openai=True, you can enhance empty/low-text pages here with your logic.
        # (left as a placeholder)

        pages.extend(extracted)

    return pages


# Optional: export into flowfoundry.functional for ergonomic imports
FF_EXPORTS = [
    ("ingestion", "pdf_loader_openai", "pdf_loader_openai"),
    # You can also add a convenience alias if you want:
    # ("ingestion", "pdf_loader_openai", "pdf_loader"),
]
