project = "Annotated JAX"
author = "Shawon Ashraf"

extensions = ["myst_nb"]
nb_execution_mode = "off"
myst_enable_extensions = ["dollarmath", "amsmath"]
# Saved tracebacks often fail strict lexing; Pygments falls back to relaxed mode.
suppress_warnings = ["myst.header", "misc.highlighting_failure"]
templates_path = ["_templates"]

html_theme = "pydata_sphinx_theme"
html_title = "Annotated JAX"
# Ursine palette and fonts, shared with the blog.
html_static_path = ["_static"]
html_css_files = [
    "https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700"
    "&family=Open+Sans:ital,wght@0,400;0,600;1,400;1,600"
    "&family=Roboto+Slab:wght@200;400&display=swap",
    "ursine.css",
]
html_theme_options = {
    "navbar_center": [],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/shawonashraf/annotated-jax",
            "icon": "fa-brands fa-github",
        },
    ],
    "use_edit_page_button": True,
    "show_toc_level": 2,
}
html_context = {
    "github_user": "shawonashraf",
    "github_repo": "annotated-jax",
    "github_version": "main",
    "doc_path": "",
}
