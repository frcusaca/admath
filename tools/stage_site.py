# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Stage the Quarto project in .build/site/ with executed notebooks.

    python tools/stage_site.py

Why: when Quarto executes an .ipynb, it writes the outputs (and kernel
metadata) back into that file. The notebooks in notebooks/ must stay
output-free, so Quarto never executes them. Instead this script copies the
project into .build/site/, executes every notebook there with
run_notebooks.py (which fails on any cell error, and checks each teacher
guide's answer key), and `make site` / `make teacher` render that copy.

Two rewrites happen in the copy only: the << / >> links point at the site's
pages instead of Colab, and hover hints (<span title="...">) become footnotes.
"""
import html
import re
import shutil
import subprocess
import sys

from nbutil import ROOT, load, save, set_text, text
from sync_setup import NAV_IDS, chapter_neighbours, nav_html

STAGE = ROOT / ".build" / "site"

# Everything the Quarto project needs, relative to the repo root.
FILES = ["_quarto.yml", "_quarto-student.yml", "_quarto-teacher.yml", "course.toml"]
GLOBS = ["*.qmd"]
TREES = {"tools": ["tests", "__pycache__"]}
RESOURCES = ["explorer/dist/standalone/angle-explorer.html"]


# A hover hint in a notebook (AGENTS.md, Style, "Hover hints"):
#   <span title="the note" style="...">the words</span>
HINT = re.compile(r'<span title="([^"]*)"[^>]*>(.*?)</span>', re.S)


def hints_to_footnotes(source, prefix):
    """Turn hover hints into Quarto footnotes: hover popup on the site, a real footnote in the PDF.

    Returns the new markdown. Footnote ids are prefix-1, prefix-2, ...; the
    definitions go at the end of the cell.
    """
    notes = []

    def swap(m):
        notes.append(html.unescape(m.group(1)))
        return f"{m.group(2)}[^{prefix}-{len(notes)}]"

    body = HINT.sub(swap, source)
    if not notes:
        return source
    return body.rstrip() + "\n\n" + "\n".join(f"[^{prefix}-{i}]: {n}" for i, n in enumerate(notes, 1)) + "\n"


def main():
    missing = [r for r in RESOURCES if not (ROOT / r).exists()]
    if missing:
        sys.exit(f"missing {missing}: run `make explorer` first")
    if STAGE.exists():
        # keep Quarto's cache (.quarto/) between builds; replace everything else
        for child in STAGE.iterdir():
            if child.name != ".quarto":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    STAGE.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(ROOT / name, STAGE / name)
    for pattern in GLOBS:
        for path in ROOT.glob(pattern):
            shutil.copy2(path, STAGE / path.name)
    for tree, skip in TREES.items():
        shutil.copytree(ROOT / tree, STAGE / tree, ignore=shutil.ignore_patterns(*skip))
    for rel in RESOURCES:
        (STAGE / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, STAGE / rel)
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "run_notebooks.py"), "--write", str(STAGE / "notebooks")],
        cwd=ROOT / "tools",
    )
    if result.returncode != 0:
        sys.exit(result.returncode)
    # On the website, << and >> go to the neighbouring pages instead of Colab.
    for path, prev, nxt in chapter_neighbours():
        staged = STAGE / "notebooks" / path.name
        nb = load(staged)
        strip = nav_html(prev, nxt, link=lambda q: q.with_suffix(".html").name)
        for cell in nb["cells"]:
            if cell.get("id") in NAV_IDS:
                set_text(cell, strip)
        save(staged, nb)
    # Hover hints become footnotes (Jupyter and Colab keep the hover version).
    for staged in sorted((STAGE / "notebooks").glob("*.ipynb")):
        nb = load(staged)
        for n, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "markdown":
                set_text(cell, hints_to_footnotes(text(cell), f"hint{n}"))
        save(staged, nb)
    print(f"staged the Quarto project with executed notebooks in {STAGE.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
