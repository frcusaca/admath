# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
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
    (tmp_path / "course.toml").write_text(
        '[repository]\nurl = "https://github.com/CHANGE-ME/example"\nref = "main"\n'
    )
    return tmp_path


def write(course, name, nb):
    (course / "notebooks" / name).write_text(json.dumps(nb, indent=1))


def run(course, script, *args):
    return subprocess.run(
        [sys.executable, str(course / "tools" / script), *args],
        cwd=course, capture_output=True, text=True,
    )


STUDENT = notebook(("markdown", "#### Mastery Coins 3.1\n\n- **M 3.1.1**\n\n  one\n- **M 3.1.2**\n\n  two"))


def key(*rows):
    return notebook(("markdown", "| Coin | Answer |\n| --- | --- |\n" + "\n".join(f"| {r} | x |" for r in rows)))


class TestCoins:
    def test_passes_when_every_coin_has_one_row(self, course):
        write(course, "03_lesson.ipynb", STUDENT)
        write(course, "03_teacher_guide.ipynb", key("M 3.1.1", "M 3.1.2"))
        assert run(course, "check_coins.py").returncode == 0

    @pytest.mark.parametrize(
        "rows, message",
        [
            (("M 3.1.1",), "no answer-key row for M 3.1.2"),
            (("M 3.1.1", "M 3.1.2", "M 3.1.3"), "M 3.1.3, which"),
            (("M 3.1.1", "M 3.1.2", "M 3.1.2"), "M 3.1.2 has 2 answer-key rows"),
            (("m3.1.1", "M 3.1.1", "M 3.1.2"), "old coin id m3.1.1"),
        ],
    )
    def test_fails_on_mismatch(self, course, rows, message):
        write(course, "03_lesson.ipynb", STUDENT)
        write(course, "03_teacher_guide.ipynb", key(*rows))
        result = run(course, "check_coins.py")
        assert result.returncode == 1
        assert message in result.stderr

    def test_fails_on_duplicate_or_wrong_module_in_student(self, course):
        write(course, "03_lesson.ipynb", notebook(("markdown", "- **M 3.1.1**\n\n  a\n- **M 3.1.1**\n\n  b\n- **M 2.1.1**\n\n  c")))
        write(course, "03_teacher_guide.ipynb", key("M 3.1.1", "M 2.1.1"))
        result = run(course, "check_coins.py")
        assert "defined 2 times" in result.stderr
        assert "belongs to module 2" in result.stderr

    def test_fails_on_old_id_or_problem_on_the_label_line(self, course):
        write(course, "03_lesson.ipynb", notebook(("markdown", "- **M 3.1.1** on the same line\n- **m3.1.2** old")))
        write(course, "03_teacher_guide.ipynb", key("M 3.1.1"))
        result = run(course, "check_coins.py")
        assert "M 3.1.1 must be a list item holding only the bold id" in result.stderr
        assert "old coin id m3.1.2" in result.stderr

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
    @staticmethod
    def chapter(title):
        return notebook(
            ("markdown", f"# {title}\n\nIntro."),
            ("markdown", "**Setup.** old"),
            ("code", "%%writefile vecdraw.py\nx = 1"),
            ("code", "import vecdraw"),
            ("markdown", "<small>Copyright</small>"),
        )

    def test_check_reports_drift_and_sync_fixes_it(self, course):
        write(course, "01_x.ipynb", self.chapter("Notebook 1: X"))
        assert run(course, "sync_setup.py", "--check").returncode == 1
        assert run(course, "sync_setup.py").returncode == 0
        assert run(course, "sync_setup.py", "--check").returncode == 0
        nb = json.loads((course / "notebooks" / "01_x.ipynb").read_text())
        ids = [c["id"] for c in nb["cells"]]
        assert ids[1] == "nav-top" and ids[-2] == "nav-bottom"
        setup = "".join(nb["cells"][3]["source"])
        assert "CHANGE-ME" in setup and "#subdirectory=python" in setup
        assert "".join(nb["cells"][4]["source"]) == "import vecdraw"

    def test_navigation_links_neighbours_in_new_tabs(self, course):
        for n in range(3):
            write(course, f"0{n}_x.ipynb", self.chapter(f"Notebook {n}: Title <{n}>"))
        assert run(course, "sync_setup.py").returncode == 0
        strips = {}
        for n in range(3):
            nb = json.loads((course / "notebooks" / f"0{n}_x.ipynb").read_text())
            top, bottom = ("".join(c["source"]) for c in nb["cells"] if c["id"] in ("nav-top", "nav-bottom"))
            assert top == bottom
            strips[n] = top
        assert "&lt;&lt;" not in strips[0] and "01_x.ipynb" in strips[0]
        assert "00_x.ipynb" in strips[1] and "02_x.ipynb" in strips[1]
        assert "&gt;&gt;" not in strips[2]
        assert strips[1].count('target="_blank" rel="noopener"') == 2
        assert "Title &lt;0&gt;" in strips[1]          # titles are escaped
        # running again changes nothing (no duplicate strips)
        assert run(course, "sync_setup.py").stdout.count("updated") == 0
        nb = json.loads((course / "notebooks" / "01_x.ipynb").read_text())
        assert [c["id"] for c in nb["cells"]].count("nav-top") == 1


class TestHintsToFootnotes:
    def test_hint_becomes_a_numbered_footnote(self):
        sys.path.insert(0, str(TOOLS))
        from stage_site import hints_to_footnotes

        src = 'Two <span title="One &amp; two." style="x">pizza orders</span> and <span title="B">b</span>.'
        out = hints_to_footnotes(src, "hint3")
        assert out.startswith("Two pizza orders[^hint3-1] and b[^hint3-2].")
        assert "[^hint3-1]: One & two.\n[^hint3-2]: B" in out
        assert hints_to_footnotes("no hints here", "hint0") == "no hints here"


class TestLatex:
    def test_fails_on_bad_math_and_stray_dollar(self, course):
        write(course, "01_x.ipynb", notebook(("markdown", "good $\\langle a, b \\rangle$ and bad $\\frac{1}{$ and $5")))
        result = subprocess.run(
            ["node", str(ROOT / "tools" / "check_latex.mjs"), str(course / "notebooks" / "01_x.ipynb")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1
        assert "KATEX ERROR" in result.stdout or "STRAY $" in result.stdout


    def test_fails_on_dot_or_cross_for_multiplication(self, course):
        write(course, "01_x.ipynb", notebook(("markdown", "$2 \\times 3$ is fine in `code · ×` only")))
        result = subprocess.run(
            ["node", str(ROOT / "tools" / "check_latex.mjs"), str(course / "notebooks" / "01_x.ipynb")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 1 and result.stdout.count("PRODUCT SIGN") == 1
        write(course, "01_x.ipynb", notebook(("markdown", "$(3)(4) + 2\\mathbf{a}$ and `a · b`")))
        result = subprocess.run(
            ["node", str(ROOT / "tools" / "check_latex.mjs"), str(course / "notebooks" / "01_x.ipynb")],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout


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
        (course / ".gitignore").write_text(
            "# Copyright © 2026-present CAehi.us\n# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0\n__pycache__/\n"
        )
        shutil.copytree(ROOT / "LICENSES", course / "LICENSES")
        (course / "python").mkdir()
        shutil.copy(ROOT / "python" / "LICENSE.md", course / "python" / "LICENSE.md")
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
        code = "LicenseRef-Prosperity-3.0.0"
        assert (repo / "a.py").read_text().splitlines()[:3] == ["#!/usr/bin/env python", f"# {notice}", f"# SPDX-License-Identifier: {code}"]
        assert (repo / "d.html").read_text().splitlines()[:3] == ["<!DOCTYPE html>", f"<!-- {notice} -->", f"<!-- SPDX-License-Identifier: {code} -->"]
        assert (repo / "f.qmd").read_text().splitlines()[:3] == ["---", f"# {notice}", "# SPDX-License-Identifier: CC-BY-NC-SA-4.0"]
        package = json.loads((repo / "package.json").read_text())
        assert (package["author"], package["license"]) == ("CAehi.us", code)
        nb = json.loads((repo / "notebooks" / "01_x.ipynb").read_text())
        assert nb["metadata"]["copyright"] == notice
        assert notice in "".join(nb["cells"][-1]["source"])
        title = "".join(nb["cells"][0]["source"])
        assert title.startswith("# Lesson\n\n<small>" + notice) and "This whole notebook" in title
        # running --fix again changes nothing
        before = {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}
        run(repo, "copyright.py", "--fix")
        assert before == {p: p.read_bytes() for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts}

    def test_unknown_file_kinds_are_not_silently_skipped(self, repo):
        (repo / "data.csv").write_text("a,b\n")
        result = run(repo, "copyright.py")
        assert result.returncode == 1 and "no copyright rule" in result.stderr

    def test_notice_inside_code_does_not_count(self, repo):
        (repo / "c.ts").write_text('export const C = "Copyright © 2026-present CAehi.us";\n')
        assert run(repo, "copyright.py").returncode == 1
        assert run(repo, "copyright.py", "--fix").returncode == 0
        lines = (repo / "c.ts").read_text().splitlines()
        assert lines[:2] == ["// Copyright © 2026-present CAehi.us", "// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0"]
        assert lines[2].startswith("export const C")

    def test_content_and_code_get_different_licenses(self, repo):
        (repo / "page.qmd").write_text("---\ntitle: x\n---\n")
        (repo / "tool.py").write_text("x = 1\n")
        write(repo, "01_x.ipynb", notebook(("markdown", "# L")))
        run(repo, "copyright.py", "--fix")
        assert "SPDX-License-Identifier: CC-BY-NC-SA-4.0" in (repo / "page.qmd").read_text()
        assert "SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0" in (repo / "tool.py").read_text()
        nb = json.loads((repo / "notebooks" / "01_x.ipynb").read_text())
        assert nb["metadata"]["license"] == "CC-BY-NC-SA-4.0"

    def test_wrong_license_is_reported_and_corrected(self, repo):
        (repo / "tool.py").write_text("# Copyright © 2026-present CAehi.us\n# SPDX-License-Identifier: MIT\nx = 1\n")
        result = run(repo, "copyright.py")
        assert "license is MIT" in result.stderr
        run(repo, "copyright.py", "--fix")
        assert (repo / "tool.py").read_text().splitlines()[1] == "# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0"
