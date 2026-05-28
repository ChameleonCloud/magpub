# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add magpub to the path so autodoc can import it
sys.path.insert(0, os.path.abspath(".."))

# -- Project information
project = "magpub"
copyright = "2026, Chameleon Cloud Team"
author = "Chameleon Cloud Team"
version = "0.1.0"
release = "0.1.0"

# -- General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- autodoc settings
autodoc_member_order = "bysource"
autosummary_generate = True
