# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from importlib import metadata

project = 'synop'
copyright = '2025, Kolja Wagner'
author = 'Kolja Wagner'
release = metadata.version("synop")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    "sphinx_togglebutton",
    "sphinx_design",
    'sphinx_copybutton',
    'myst_nb'
    ]

templates_path = ['_templates']
exclude_patterns = []

# -- options for copybutton
copybutton_prompt_text = r"/>>>|\.\.\.|\([a-zA-Z]+\)\ \$\ |\$\ /gm"
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']

html_theme_options = {
    "logo": {
        #"image_light": "_static/synop_logo.png",
        #"image_dark":  "_static/synop_logo.png",
        "text": f"synop {release}",
        },
    
    #"navbar_start": None,
    "navigation_with_keys":True    ,
    }
html_sidebars ={
    "setup": [],
}
