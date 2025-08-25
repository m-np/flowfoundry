from __future__ import annotations
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# ---- Path to project sources (src/flowfoundry) ----
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

# ---- Project info ----
project = "FlowFoundry"
author = "FlowFoundry Contributors"
copyright = f"{date.today().year}, {author}"
release = "1.0.0"

# ---- General config ----
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_autodoc_typehints",
    "sphinxcontrib.mermaid",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = ["_build", "Thumbs.db", ".DS_Store"]

# ---- HTML ----
html_theme = "furo"
html_static_path = ["_static"]
html_title = "FlowFoundry"
html_logo = None
html_favicon = None

# ---- Options ----
autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
todo_include_todos = True
default_role = "code"

# allow GitHub-style fenced code & colon-fenced directives
myst_enable_extensions = ["colon_fence", "deflist", "attrs_block"]

# ---- Intersphinx (popular libs used by strategies) ----
intersphinx_mapping: dict[str, tuple[str, Optional[str]]] = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "langchain": ("https://python.langchain.com/docs", None),
    "fastapi": ("https://fastapi.tiangolo.com/", None),
}
