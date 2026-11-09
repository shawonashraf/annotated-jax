import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from generate import (  # noqa: E402
    SiteError,
    find_posts,
    main,
    pretty_name,
    write_sources,
)


def make_nb(path: Path, cells=()) -> dict:
    nb = {
        "cells": list(cells),
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 4,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(nb))
    return nb


def md(*lines: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": ["\n".join(lines)]}


CODE_CELL = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": ["print(1)"],
}


def test_pretty_name():
    assert pretty_name("01_basic_matrix") == "Basic Matrix"
    assert pretty_name("07_autodiff_and_linear_regression") == "Autodiff And Linear Regression"
    assert pretty_name("12_cnn_cifar10") == "Cnn Cifar10"
    assert pretty_name("a--b__c") == "A B C"
    assert pretty_name("My VAE notes") == "My VAE Notes"


def test_find_posts_only_notebooks_folder(tmp_path):
    for p in [
        "notebooks/02_b.ipynb",
        "notebooks/01_a.ipynb",
        "notebooks/sub/nested.ipynb",
        "notebooks/.ipynb_checkpoints/01_a-checkpoint.ipynb",
        "playground/scratch.ipynb",
        "stray.ipynb",
    ]:
        make_nb(tmp_path / p)
    assert find_posts(tmp_path) == [Path("notebooks/01_a.ipynb"), Path("notebooks/02_b.ipynb")]


def test_find_posts_empty(tmp_path):
    make_nb(tmp_path / "playground/x.ipynb")
    with pytest.raises(SiteError, match="no notebooks"):
        find_posts(tmp_path)


def test_index_notebook_rejected(tmp_path):
    make_nb(tmp_path / "notebooks/index.ipynb")
    with pytest.raises(SiteError, match="notebooks/index.ipynb"):
        find_posts(tmp_path)


def test_write_sources_post(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    original = make_nb(repo / "notebooks/01_my_post.ipynb", [CODE_CELL])
    write_sources(repo, out)
    nb = json.loads((out / "notebooks/01_my_post.ipynb").read_text())
    assert nb["cells"][0]["source"] == ["# My Post"]
    assert nb["cells"][1] == CODE_CELL
    assert "id" not in nb["cells"][0]
    assert json.loads((repo / "notebooks/01_my_post.ipynb").read_text()) == original


def test_write_sources_skips_playground(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(repo / "notebooks/01_a.ipynb")
    make_nb(repo / "playground/scratch.ipynb")
    write_sources(repo, out)
    assert not (out / "playground").exists()
    assert sorted(p.relative_to(out).as_posix() for p in out.rglob("*.ipynb")) == ["notebooks/01_a.ipynb"]


def test_write_sources_copies_images(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(repo / "notebooks/01_a.ipynb", [md("![x](../images/x.png)")])
    (repo / "images").mkdir()
    (repo / "images/x.png").write_bytes(b"png")
    write_sources(repo, out)
    assert (out / "images/x.png").read_bytes() == b"png"


def test_write_sources_title_cell_id_for_nbformat_45(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    path = repo / "notebooks/x.ipynb"
    make_nb(path)
    nb = json.loads(path.read_text())
    nb["nbformat_minor"] = 5
    path.write_text(json.dumps(nb))
    write_sources(repo, out)
    assert json.loads((out / "notebooks/x.ipynb").read_text())["cells"][0]["id"] == "site-title"


def test_write_sources_index(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    for p in ["notebooks/02_b.ipynb", "notebooks/01_a.ipynb"]:
        make_nb(repo / p)
    write_sources(repo, out)
    root = (out / "index.md").read_text()
    assert "\n# Annotated JAX\n" in root
    assert root.index("\nnotebooks/01_a\n") < root.index("\nnotebooks/02_b\n")
    assert ":hidden:" not in root


def test_rerun_removes_stale(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(repo / "notebooks/x.ipynb")
    make_nb(repo / "notebooks/y.ipynb")
    write_sources(repo, out)
    (repo / "notebooks/x.ipynb").unlink()
    write_sources(repo, out)
    assert not (out / "notebooks/x.ipynb").exists()
    assert (out / "notebooks/y.ipynb").exists()


def test_empty_notebook(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(repo / "notebooks/empty.ipynb")
    write_sources(repo, out)
    cells = json.loads((out / "notebooks/empty.ipynb").read_text())["cells"]
    assert cells == [{"cell_type": "markdown", "metadata": {}, "source": ["# Empty"]}]


def test_main_reports_error(tmp_path, capsys):
    assert main([str(tmp_path), str(tmp_path / "out")]) == 1
    assert "no notebooks found" in capsys.readouterr().err


def test_write_sources_refuses_to_wipe_repo(tmp_path):
    make_nb(tmp_path / "notebooks/x.ipynb")
    for out in [tmp_path, tmp_path.parent]:
        with pytest.raises(SiteError, match="output"):
            write_sources(tmp_path, out)
    assert (tmp_path / "notebooks/x.ipynb").exists()


def test_write_sources_refuses_non_generated_output(tmp_path):
    repo = tmp_path / "repo"
    make_nb(repo / "notebooks/x.ipynb")
    keep = tmp_path / "keep"
    keep.mkdir()
    (keep / "precious.ipynb").write_text("{}")
    with pytest.raises(SiteError, match="output"):
        write_sources(repo, keep)
    assert (keep / "precious.ipynb").exists()
    with pytest.raises(SiteError, match="output"):
        write_sources(repo, repo / "notebooks")
    assert (repo / "notebooks/x.ipynb").exists()


def test_notebook_h1_headings_demoted_below_title(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(
        repo / "notebooks/x.ipynb",
        [md("# Own Title", "text", "## Sub", "```", "# not a heading", "```"), md("Setext", "===="), CODE_CELL],
    )
    write_sources(repo, out)
    cells = json.loads((out / "notebooks/x.ipynb").read_text())["cells"]
    assert cells[0]["source"] == ["# X"]
    assert "".join(cells[1]["source"]) == "\n".join(
        ["## Own Title", "text", "### Sub", "```", "# not a heading", "```"]
    )
    assert "".join(cells[2]["source"]) == "Setext\n----"
    assert cells[3] == CODE_CELL


def test_headings_kept_when_notebook_has_no_h1(tmp_path):
    repo, out = tmp_path / "repo", tmp_path / "out"
    make_nb(repo / "notebooks/x.ipynb", [md("## Sub", "text")])
    write_sources(repo, out)
    assert "".join(json.loads((out / "notebooks/x.ipynb").read_text())["cells"][1]["source"]) == "## Sub\ntext"
