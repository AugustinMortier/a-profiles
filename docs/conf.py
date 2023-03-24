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
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "A-Profiles"
copyright = "2021, Augustin Mortier"
author = "Augustin Mortier"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "recommonmark",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx"
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "xarray": ("http://xarray.pydata.org/en/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference/", None),
}

html_css_files = [
    "css/custom.css",
]

html_js_files = [
    "js/custom.js",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# options for "pydata_sphinx_theme"
html_theme_options = {
    "pygment_light_style": "tango",
    "pygment_dark_style": "native",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/AugustinMortier/A-Profiles",
            "icon": "fab fa-github-square",
            "type": "fontawesome"
        },{
            "name": "V-Profiles",
            "url": "https://vprofiles.met.no",
            "icon": "_static/images/vprofiles-bold.ico",
            "type": "local"
        }
    ],
    "logo": {
      "image_light": "_static/images/A-Profiles.png",
      "image_dark": "_static/images/A-Profiles-white.png",
    }
}

html_sidebars = {
    "**": ["search-field.html", "sidebar-nav-bs.html"]
}

# Some options
add_module_names = True
