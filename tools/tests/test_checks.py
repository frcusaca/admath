# Copyright © 2026-present CAehi.us
"""Each check must fail when it should. Synthetic notebooks in a temp folder."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent
ROOT = TOOLS.parent


def notebook(*cells):
    out = []
    for kind, source in cells:
        cell = {"cell_type": kind, "id": f"c{len(out)}", "metadata": {}, "source": source}
        if kind == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {"cells": out, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}


@pytest.fixture
def course(tmp_path):
    """A throwaway copy of the tools with its own notebooks/ and course.toml."""
    shutil.copytree(TOOLS, tmp_path / "tools", ignore=shutil.ignore_patterns("tests", "__pycache__"))
    (tmp_path / "notebooks").mkdir()
    shutil.copy(ROOT / "course.toml", tmp_path / "course.toml")
    return tmp_path


def write(course, name, nb):
    (course / "notebooks" / name).write_text(json.dumps(nb, indent=1))


def run(course, script, *args):
    return subprocess.run(
        [sys.executable, str(course / "tools" / script), *args],
        cwd=course, capture_output=True, text=True,
    )


STUDENT = notebook(("markdown", "- **m3.1.1** one\n- **m3.1.2** two"))


def key(*rows):
    return notebook(("markdown", "| Coin | Answer |\n| --- | --- |\n" + "\n".join(f"| {r} | x |" for r in rows)))


class TestCoins:
    def test_passes_when_every_coin_has_one_row(self, course):
        write(course, "03_lesson.ipynb", STUDENT)
        write(course, "03_teacher_guide.ipynb", key("m3.1.1", "m3.1.2"))
        assert run(course, "check_coins.py").returncode == 0

    @pytest.mark.parametrize(
        "rows, message",
        [
            (("m3.1.1",), "no answer-key row for m3.1.2"),
            (("m3.1.1", "m3.1.2", "m3.1.3"), "m3.1.3, which"),
            (("m3.1.1", "m3.1.2", "m3.1.2"), "m3.1.2 has 2 answer-key rows"),
        ],
    )
    def test_fails_on_mismatch(self, course, rows, message):
        write(course, "03_lesson.ipynb", STUDENT)
        write(course, "03_teacher_guide.ipynb", key(*rows))
        result = run(course, "check_coins.py")
        assert result.returncode == 1
        assert message in result.stderr

    def test_fails_on_duplicate_or_wrong_module_in_student(self, course):
        write(course, "03_lesson.ipynb", notebook(("markdown", "**m3.1.1** a\n**m3.1.1** b\n**m2.1.1** c")))
        write(course, "03_teacher_guide.ipynb", key("m3.1.1", "m2.1.1"))
        result = run(course, "check_coins.py")
        assert "defined 2 times" in result.stderr
        assert "belongs to module 2" in result.stderr

    def test_fails_without_a_teacher_guide(self, course):
        write(course, "03_lesson.ipynb", STUDENT)
        assert "no teacher guide" in run(course, "check_coins.py").stderr


class TestClean:
    def test_fails_on_outputs_and_fix_removes_them(self, course):
        nb = notebook(("code", "print(1)"))
        nb["cells"][0]["outputs"] = [{"output_type": "stream", "name": "stdout", "text": "1\n"}]
        nb["cells"][0]["execution_count"] = 1
        write(course, "01_x.ipynb", nb)
        assert run(course, "check_clean.py").returncode == 1
        assert run(course, "check_clean.py", "--fix").returncode == 0
        assert run(course, "check_clean.py").returncode == 0


class TestRunNotebooks:
    def test_fails_on_an_error(self, course):
        write(course, "01_x.ipynb", notebook(("code", "1 / 0")))
        result = run(course, "run_notebooks.py")
        assert result.returncode == 1
        assert "ZeroDivisionError" in result.stderr

    def test_teacher_guide_must_print_the_key_line(self, course):
        write(course, "01_teacher_guide.ipynb", notebook(("markdown", "## Check the key"), ("code", "print('oops')")))
        result = run(course, "run_notebooks.py")
        assert result.returncode == 1
        assert "did not print" in result.stderr

    def test_teacher_guide_passes_with_the_key_line(self, course):
        write(course, "01_teacher_guide.ipynb", notebook(("markdown", "## Check the key"), ("code", "print('All 3 checks passed.')")))
        assert run(course, "run_notebooks.py").returncode == 0


class TestSyncSetup:
    def test_check_reports_drift_and_sync_fixes_it(self, course):
        write(course, "01_x.ipynb", notebook(("markdown", "**Setup.** old"), ("code", "%%writefile vecdraw.py\nx = 1"), ("code", "import vecdraw")))
        assert run(course, "sync_setup.py", "--check").returncode == 1
        assert run(course, "sync_setup.py").returncode == 0
        assert run(course, "sync_setup.py", "--check").returncode == 0
        nb = json.loads((course / "notebooks" / "01_x.ipynb").read_text())
        setup = "".join(nb["cells"][1]["source"])
        assert "CHANGE-ME" in setup and "#subdirectory=python" in setup
        assert "".join(nb["cells"][2]["source"]) == "import vecdraw"


class TestLatex:
    def test_fails_on_bad_math_and_stray_dollar(self, course):
        write(course, "01_x.ipynb", notebook(("markdown", "good $\\langle a, b \\rangle$ and bad $\\frac{1}{$ and $5")))
        result = subprocess.run(
            ["node", str(ROOT / "tools" / "check_latex.mjs"), str(course / "notebooks" / "01_x.ipynb")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "KATEX ERROR" in result.stdout or "STRAY $" in result.stdout


class TestQuartoYamlLookalike:
    def test_rule_followed_by_text_is_reported_and_fixed(self, course):
        write(course, "01_x.ipynb", notebook(("markdown", "---\n## Part 1\ntext"), ("markdown", "---\n\n## Part 2")))
        result = run(course, "check_clean.py")
        assert result.returncode == 1 and "cell 0 starts with '---'" in result.stderr
        assert run(course, "check_clean.py", "--fix").returncode == 0
        nb = json.loads((course / "notebooks" / "01_x.ipynb").read_text())
        assert "".join(nb["cells"][0]["source"]) == "---\n\n## Part 1\ntext"
        assert "".join(nb["cells"][1]["source"]) == "---\n\n## Part 2"


class TestCopyright:
    """tools/copyright.py on a throwaway git repository."""

    @pytest.fixture
    def repo(self, course):
        subprocess.run(["git", "init", "-q"], cwd=course, check=True)
        (course / ".gitignore").write_text("# Copyright © 2026-present CAehi.us\n__pycache__/\n")
        return course

    def test_reports_and_fixes_each_kind_of_file(self, repo):
        files = {
            "a.py": "#!/usr/bin/env python\nprint(1)\n",
            "b.ts": "export const x = 1;\n",
            "c.css": "p { color: red; }\n",
            "d.html": "<!DOCTYPE html>\n<p>hi</p>\n",
            "e.md": "# Title\n",
            "f.qmd": "---\ntitle: x\n---\nBody\n",
            "Makefile": "all:\n\techo hi\n",
            "package.json": '{\n  "name": "x",\n  "description": "y"\n}\n',
        }
        for name, body in files.items():
            (repo / name).write_text(body)
        write(repo, "01_x.ipynb", notebook(("markdown", "# Lesson")))
        result = run(repo, "copyright.py")
        assert result.returncode == 1
        for name in [*files, "notebooks/01_x.ipynb"]:
            assert name in result.stderr, name
        assert run(repo, "copyright.py", "--fix").returncode == 0
        assert run(repo, "copyright.py").returncode == 0

        notice = "Copyright © 2026-present CAehi.us"
        assert (repo / "a.py").read_text().splitlines()[:2] == ["#!/usr/bin/env python", f"# {notice}"]
        assert (repo / "d.html").read_text().splitlines()[:2] == ["<!DOCTYPE html>", f"<!-- {notice} -->"]
        assert (repo / "f.qmd").read_text().splitlines()[:2] == ["---", f"# {notice}"]
        assert json.loads((repo / "package.json").read_text())["author"] == "CAehi.us"
        nb = json.loads((repo / "notebooks" / "01_x.ipynb").read_text())
        assert nb["metadata"]["copyright"] == notice
        assert notice in "".join(nb["cells"][-1]["source"])
        # running --fix again changes nothing
        before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}
        run(repo, "copyright.py", "--fix")
        assert before == {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    def test_unknown_file_kinds_are_not_silently_skipped(self, repo):
        (repo / "data.csv").write_text("a,b\n")
        result = run(repo, "copyright.py")
        assert result.returncode == 1 and "no copyright rule" in result.stderr
