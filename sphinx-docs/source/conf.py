import os
import sys
import subprocess

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

if os.getenv("READTHEDOCS", False) and not os.path.exists("riscemu.rst"):
    subprocess.check_call(["../../generate-docs.sh", "generate"])

# -- Project information -----------------------------------------------------

project = "RiscEmu"
copyright = "2022, Anton Lydike"
author = "Anton Lydike"

# The full version, including alpha/beta/rc tags
release = "2.0.0a2"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinx.ext.autodoc", "recommonmark"]

# autodoc options
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
# Markdown support

from recommonmark.parser import CommonMarkParser

# The suffix of source filenames.
source_suffix = [".rst", ".md"]

source_parsers = {
    ".md": CommonMarkParser,
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"

pygments_style = "sphinx"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

sys.path.insert(0, os.path.abspath("../../"))

if os.getenv("READTHEDOCS", False):
    import sphinx_rtd_theme

    extensions.append("sphinx_rtd_theme")

    html_theme = "sphinx_rtd_theme"
