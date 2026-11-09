import json
import re
import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from sphinx.cmd.build import build_main

WEBSITE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEBSITE_DIR))

from generate import write_sources  # noqa: E402

# 1x1 transparent PNG.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


def _write_nb(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cell = {"cell_type": "markdown", "metadata": {}, "source": [text]}
    path.write_text(json.dumps({"cells": [cell], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}))


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("site")
    repo, src, out = root / "repo", root / "src", root / "out"
    _write_nb(repo / "notebooks/01_first_steps.ipynb", "## Section\n\n![pic](../images/pic.png)")
    _write_nb(repo / "notebooks/02_second.ipynb", "# Own Title\n\n# Another H1")
    _write_nb(repo / "playground/scratch.ipynb", "## Debug")
    (repo / "images").mkdir()
    (repo / "images/pic.png").write_bytes(PNG)
    write_sources(repo, src)
    assert build_main(["-q", "-c", str(WEBSITE_DIR), str(src), str(out)]) == 0
    return out


def soup(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(), "html.parser")


def test_post_page(site):
    html = soup(site / "notebooks/01_first_steps.html")
    assert html.title.text.startswith("First Steps")
    sidebar = html.select_one(".bd-sidebar-primary").get_text()
    assert "First Steps" in sidebar and "Second" in sidebar
    assert html.find("a", href=re.compile(r"/edit/main/notebooks/01_first_steps\.ipynb$"))


def test_post_image(site):
    img = soup(site / "notebooks/01_first_steps.html").find("img", alt="pic")
    assert img is not None
    assert (site / "notebooks" / img["src"]).resolve().exists()


def test_playground_not_built(site):
    assert not (site / "playground").exists()
    assert "scratch" not in (site / "index.html").read_text().lower()


def test_root_page_lists_each_post_once(site):
    html = soup(site / "index.html")
    links = [a.get_text(strip=True) for a in html.select("article .toctree-wrapper a")]
    assert links == ["First Steps", "Second"]
    assert not html.find("a", href=re.compile("/edit/"))


def test_ursine_theme_loaded(site):
    hrefs = [l.get("href", "") for l in soup(site / "notebooks/01_first_steps.html").find_all("link", rel="stylesheet")]
    assert any(h.endswith("_static/ursine.css") or "_static/ursine.css?" in h for h in hrefs)
    assert any(h.startswith("https://fonts.googleapis.com/css2?family=Fira+Mono") for h in hrefs)
    assert (site / "_static/ursine.css").exists()
