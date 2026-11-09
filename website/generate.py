"""Turn the notebooks in notebooks/ into Sphinx sources for the site.

Only notebooks directly inside notebooks/ become pages; everything else in the
repo (playground/, utils/, ...) is ignored. images/ is copied alongside because
the notebooks reference it as ../images/.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from markdown_it import MarkdownIt

NOTEBOOKS = "notebooks"
ASSETS = ["images"]
SITE_TITLE = "Annotated JAX"
TAGLINE = "Deep learning examples using the JAX ecosystem of libraries."
REPO_URL = "https://github.com/shawonashraf/annotated-jax"
# Generated pages have no file in the repo, so drop the right sidebar
# (its "Edit on GitHub" link would 404).
GENERATED_PAGE = "---\nhtml_theme.sidebar_secondary.remove: true\n---\n\n"
# Marks a folder as generator output, so write_sources only ever deletes its own output.
SENTINEL = ".generated-by-website"
_MD = MarkdownIt("commonmark")


class SiteError(Exception):
    pass


def pretty_name(name: str) -> str:
    """`01_basic_matrix` -> `Basic Matrix`: drop the ordering prefix, split, capitalise."""
    name = re.sub(r"^\d+[-_\s]+", "", name)
    words = [w for w in re.split(r"[-_\s]+", name) if w]
    return " ".join(w[0].upper() + w[1:] for w in words)


def find_posts(repo: Path) -> list[Path]:
    """Notebooks directly inside notebooks/, sorted by file name."""
    posts = [p.relative_to(repo) for p in sorted((repo / NOTEBOOKS).glob("*.ipynb"))]
    if not posts:
        raise SiteError(f"no notebooks found in {NOTEBOOKS}/")
    for p in posts:
        if p.stem == "index":
            raise SiteError(f"{p.as_posix()}: 'index' is reserved; rename it")
    return posts


def _text(cell: dict) -> str:
    src = cell["source"]
    return src if isinstance(src, str) else "".join(src)


def _headings(text: str) -> list:
    return [t for t in _MD.parse(text) if t.type == "heading_open"]


def _demote(text: str) -> str:
    """Push every heading one level down so the injected title stays the only H1."""
    lines = text.split("\n")
    for t in reversed(_headings(text)):
        start, end = t.map
        if t.markup.startswith("#"):
            if t.tag != "h6":
                lines[start] = re.sub(r"^(\s*)#", r"\1##", lines[start], count=1)
        elif t.markup == "=":
            lines[end - 1] = lines[end - 1].replace("=", "-")
        else:  # setext H2 -> ATX H3
            lines[start:end] = ["### " + " ".join(l.strip() for l in lines[start : end - 1])]
    return "\n".join(lines)


def _copy_post(repo: Path, out: Path, post: Path) -> None:
    nb = json.loads((repo / post).read_text())
    md_cells = [c for c in nb["cells"] if c["cell_type"] == "markdown"]
    if any(t.tag == "h1" for c in md_cells for t in _headings(_text(c))):
        for c in md_cells:
            c["source"] = _demote(_text(c))
    title = {"cell_type": "markdown", "metadata": {}, "source": [f"# {pretty_name(post.stem)}"]}
    if nb.get("nbformat", 4) > 4 or nb.get("nbformat_minor", 0) >= 5:
        title["id"] = "site-title"
    nb["cells"].insert(0, title)
    dest = out / post
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(nb, indent=1))


def write_sources(repo: Path, out: Path) -> None:
    repo, out = repo.resolve(), out.resolve()
    if repo == out or repo.is_relative_to(out):
        raise SiteError(f"output {out} would contain the repo; refusing to delete it")
    if out.exists() and any(out.iterdir()) and not (out / SENTINEL).exists():
        raise SiteError(f"output {out} is not a generated folder; refusing to delete it")
    posts = find_posts(repo)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    (out / SENTINEL).touch()
    for post in posts:
        _copy_post(repo, out, post)
    for asset in ASSETS:
        if (repo / asset).is_dir():
            shutil.copytree(repo / asset, out / asset)
    (out / "index.md").write_text(
        GENERATED_PAGE
        + f"# {SITE_TITLE}\n\n"
        f"{TAGLINE} Each page is a notebook from [the repository]({REPO_URL}), "
        "rendered with its saved outputs. Setup instructions are in the "
        f"[README]({REPO_URL}#readme).\n\n"
        "```{toctree}\n:maxdepth: 1\n:titlesonly:\n\n"
        + "\n".join(p.with_suffix("").as_posix() for p in posts)
        + "\n```\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args(argv)
    try:
        write_sources(args.repo, args.out)
    except SiteError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
