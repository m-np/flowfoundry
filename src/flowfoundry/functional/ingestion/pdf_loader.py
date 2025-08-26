from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Union

from ...strategies.registry import register_strategy

from langchain_community.document_loaders import PyPDFLoader

from ...exceptions import FFIngestionError


@register_strategy("ingestion", "pdf_loader")
def pdf_loader(path: Union[str, Path]) -> List[Dict]:
    """
    Extract text from one or many PDF files into structured dictionaries.

    Raises:
        FFIngestionError: If the path is invalid, not a PDF, or no PDFs found.
    """
    path = Path(path)

    if not path.exists():
        raise FFIngestionError(f"❌ Path not found: {path}")

    if path.is_file():
        if path.suffix.lower() != ".pdf":
            raise FFIngestionError(f"❌ File is not a PDF: {path}")
        pdf_files = [path]
    elif path.is_dir():
        pdf_files = list(path.rglob("*.pdf"))
    else:
        raise FFIngestionError(f"❌ Path is neither a file nor directory: {path}")

    if not pdf_files:
        raise FFIngestionError(f"❌ No PDF files found under {path}")

    all_docs: List[Dict] = []
    for pdf in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf))
            pages = loader.load()
            for i, page in enumerate(pages, start=1):
                all_docs.append(
                    {
                        "source": str(pdf.resolve()),
                        "page": i,
                        "text": page.page_content.strip(),
                    }
                )
        except Exception as e:
            raise FFIngestionError(f"❌ Failed to load {pdf}: {e}") from e

    return all_docs
