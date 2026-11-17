# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""The .gitignore ignores what it should, and nothing else.

    python tools/check_gitignore.py

Three checks:
1. JUNK: files that Python, Jupyter, Node, Quarto, editors and operating systems
   create must be ignored (so `git add -A` never picks them up).
2. SOURCE: files this project might reasonably add (including folders with
   names like lib/ or build/ inside the source tree) must NOT be ignored.
3. No committed file matches an ignore rule.
Paths in 1 and 2 need not exist: git checks the rules, not the disk.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JUNK = [
    # Python
    "python/src/vecdraw/__pycache__/explore.cpython-314.pyc", "tools/__pycache__/nbutil.cpython-312.pyc",
    "x.pyc", ".venv/bin/python3", "venv/bin/python", "python/.venv/bin/python", ".env",
    "python/build/lib/vecdraw/__init__.py", "python/dist/vecdraw-0.4.0-py3-none-any.whl",
    "python/src/vecdraw.egg-info/PKG-INFO", "build/x", ".eggs/x",
    ".pytest_cache/v/cache/nodeids", "python/.pytest_cache/x", ".coverage", "htmlcov/index.html",
    ".mypy_cache/x", ".ruff_cache/x", ".hypothesis/x", ".tox/x",
    # Jupyter
    "notebooks/.ipynb_checkpoints/00_vectors_and_inner_product-checkpoint.ipynb",
    ".ipynb_checkpoints/x", ".ipython/profile_default/history.sqlite", ".jupyter/x", ".virtual_documents/x",
    # Node and the explorer
    "node_modules/vite/package.json", "explorer/node_modules/x", "explorer/dist/lib/angle-explorer.js",
    "explorer/test-results/x.png", "explorer/playwright-report/index.html",
    # Quarto, LaTeX, the site and the bundles
    "_site/index.html", "_site-teacher/index.html", ".build/site/_quarto.yml", ".quarto/x",
    "index.quarto_ipynb", "notebooks/00_x.quarto_ipynb", "angle-explorer.tex", "angle-explorer.log",
    "notebooks/00_teacher_guide.tex", "_freeze/x", "dist/colab/admath-notebooks.zip",
    # this project's tools
    ".tools/quarto/bin/quarto", ".tools/TinyTeX/bin/x86_64-linux/lualatex", ".remember/now.md",
    # editors and operating systems
    ".vscode/settings.json", ".idea/workspace.xml", "notebooks/x.ipynb.swp", "README.md~",
    ".DS_Store", "notebooks/.DS_Store", "Thumbs.db", "desktop.ini",
]

SOURCE = [
    "notebooks/05_new_module.ipynb", "notebooks/05_teacher_guide.ipynb", "notebooks/images/arrow.png",
    "python/src/vecdraw/__init__.py", "python/src/vecdraw/lib/helpers.py", "python/src/vecdraw/static/angle-explorer.iife.js",
    "python/tests/test_drawing.py", "python/pyproject.toml", "python/LICENSE.md",
    "explorer/src/lib/util.ts", "explorer/src/build/x.ts", "explorer/e2e/new.spec.ts", "explorer/reference/x.html",
    "tools/lib/x.py", "tools/build_site.py", "tools/stage_site.py", "docs/var/notes.md", "docs/parts/x.md",
    "LICENSES/CC-BY-NC-SA-4.0.txt", "requirements.txt", "package-lock.json", ".nvmrc", "course.toml",
    "_quarto.yml", "_quarto-student.yml", "index.qmd", "Makefile", ".gitignore",
]


def git(*args, stdin=None):
    return subprocess.run(["git", *args], cwd=ROOT, input=stdin, capture_output=True, text=True)


def ignored(paths):
    """{path: the rule that ignores it, or None}"""
    out = git("check-ignore", "--no-index", "-v", "-n", "--stdin", stdin="\n".join(paths) + "\n").stdout
    result = {}
    for line in out.splitlines():
        rule, path = line.split("\t", 1)
        result[path] = None if rule == "::" else rule
    return result


def main():
    problems = []
    for path, rule in ignored(JUNK).items():
        if rule is None:
            problems.append(f"not ignored, but should be: {path}")
    for path, rule in ignored(SOURCE).items():
        if rule is not None:
            problems.append(f"ignored, but it is source: {path}  (rule {rule})")
    for path in git("ls-files", "-ci", "--exclude-standard").stdout.split():
        problems.append(f"committed, but matches an ignore rule: {path}")
    if problems:
        for p in problems:
            print("FAIL:", p, file=sys.stderr)
        sys.exit(1)
    print(f"gitignore: {len(JUNK)} junk paths ignored, {len(SOURCE)} source paths kept, no committed file ignored")


if __name__ == "__main__":
    main()
