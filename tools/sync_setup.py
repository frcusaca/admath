# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Write the generated cells of every student notebook from course.toml.

    python tools/sync_setup.py           rewrite the notebooks
    python tools/sync_setup.py --check   only report notebooks that are out of date (exit 1)

The setup is two cells near the top of each student notebook:
  1. a markdown cell starting with "**Setup.**"
  2. the code cell that gets the library (it replaced the old `%%writefile vecdraw.py` cell)
The import cell after them (`import importlib, vecdraw ...`) is never touched.

It also writes the chapter navigation: a "<< previous   next >>" strip as the
second cell (after the title) and again just before the copyright footer.
Cell ids "nav-top" and "nav-bottom" mark them. Links open in a new tab.
In the notebooks they point at "Open in Colab"; stage_site.py rewrites them to
the website's .html pages (the PDF leaves the strip out: it is raw HTML).
"""
import html
import sys
from pathlib import Path

from nbutil import course_config, fail, load, save, set_text, student_notebooks, text

SETUP_MARKDOWN = (
    "**Setup.** The next cell gets the drawing library, `vecdraw`. "
    "The library is short, and you are allowed to read it and change it. "
    "To read all of it, run `import inspect` and then `print(inspect.getsource(vecdraw))`."
)

SETUP_CODE = '''\
# Setup: this cell gets the vecdraw library. You do not need to read it.
REPO_URL = "{url}"   # set in course.toml
REPO_REF = "{ref}"

import importlib.util, sys
from pathlib import Path

if "google.colab" in sys.modules:
    if importlib.util.find_spec("vecdraw") is None:
        if "CHANGE-ME" in REPO_URL:
            raise RuntimeError("The course repository URL is not set yet. Ask your teacher.")
        %pip install --quiet "vecdraw @ git+{{REPO_URL}}@{{REPO_REF}}#subdirectory=python"
else:
    # On a computer with the course folder: use the library in python/src.
    for folder in [Path.cwd(), *Path.cwd().parents]:
        if (folder / "python" / "src" / "vecdraw").is_dir():
            sys.path.insert(0, str(folder / "python" / "src"))
            break
    if importlib.util.find_spec("vecdraw") is None:
        raise RuntimeError("Cannot find vecdraw. Run `make setup` in the course folder, or `pip install -e python`.")'''

OLD_CODE_MARKERS = ("%%writefile vecdraw.py", "# Setup: this cell gets the vecdraw library.")


# Decoration only: the arrows and words carry the meaning. Not blue or orange,
# which mean the sign of an inner product in this course.
NAV_COLORS = {"prev": "#00875f", "next": "#a8327d"}
NAV_IDS = ("nav-top", "nav-bottom")


def chapter_title(path):
    """'# Notebook 1: The Rover's Moves (...)' -> ("Notebook 1", "Notebook 1: The Rover's Moves (...)")."""
    full = text(load(path)["cells"][0]).splitlines()[0].lstrip("# ").strip()
    return full.split(":")[0], full


def colab_link(path, repo):
    url = repo["url"].rstrip("/")
    if url.startswith("https://github.com/") and "CHANGE-ME" not in url:
        return f"https://colab.research.google.com/github/{url.removeprefix('https://github.com/')}/blob/{repo['ref']}/notebooks/{path.name}"
    return path.name


def nav_html(prev, nxt, link):
    """The strip for one notebook. prev/nxt are paths or None; link(path) gives the href."""
    parts = []
    for path, side in ((prev, "prev"), (nxt, "next")):
        if path is None:
            continue
        short, full = chapter_title(path)
        arrow = f'<b style="color:{NAV_COLORS[side]}">{"&lt;&lt;" if side == "prev" else "&gt;&gt;"}</b>'
        label = html.escape(short)
        inner = f"{arrow} {label}" if side == "prev" else f"{label} {arrow}"
        word = "Previous" if side == "prev" else "Next"
        parts.append(
            f'<a href="{html.escape(link(path))}" target="_blank" rel="noopener" '
            f'title="{word}: {html.escape(full)} (opens in a new tab)">{inner}</a>'
        )
    return "<p>" + " &emsp;&emsp; ".join(parts) + "</p>"


def chapter_neighbours():
    """[(path, previous path or None, next path or None)] for the student notebooks, in order."""
    paths = student_notebooks()
    return [(p, paths[i - 1] if i else None, paths[i + 1] if i + 1 < len(paths) else None) for i, p in enumerate(paths)]


def place_nav(nb, strip):
    """Put the strip after the title and before the copyright footer. True if anything changed."""
    cells = nb["cells"]
    before = [(c.get("id"), text(c)) for c in cells]
    cells[:] = [c for c in cells if c.get("id") not in NAV_IDS]
    cells.insert(1, {"cell_type": "markdown", "id": "nav-top", "metadata": {}, "source": []})
    cells.insert(len(cells) - 1, {"cell_type": "markdown", "id": "nav-bottom", "metadata": {}, "source": []})
    set_text(cells[1], strip)
    set_text(cells[-2], strip)
    return before != [(c.get("id"), text(c)) for c in cells]


def find_setup(nb):
    """Indexes of the setup markdown and code cells, or None."""
    for i, cell in enumerate(nb["cells"][:-1]):
        nxt = nb["cells"][i + 1]
        if (
            cell["cell_type"] == "markdown"
            and text(cell).startswith("**Setup.**")
            and nxt["cell_type"] == "code"
            and text(nxt).startswith(OLD_CODE_MARKERS)
        ):
            return i, i + 1
    return None


def main():
    check = "--check" in sys.argv
    repo = course_config()["repository"]
    code = SETUP_CODE.format(url=repo["url"], ref=repo["ref"])
    problems = []
    neighbours = {p: (a, b) for p, a, b in chapter_neighbours()}
    for path in student_notebooks():
        nb = load(path)
        strip = nav_html(*neighbours[path], link=lambda q: colab_link(q, repo))
        if place_nav(nb, strip):
            if check:
                problems.append(f"{path.name}: chapter navigation is out of date (run `make sync-setup`)")
                continue
            save(path, nb)
            print("updated navigation in", path.name)
        found = find_setup(nb)
        if found is None:
            problems.append(f"{path.name}: no setup cells found")
            continue
        md, cc = found
        cells = nb["cells"]
        if text(cells[md]) == SETUP_MARKDOWN and text(cells[cc]) == code:
            continue
        if check:
            problems.append(f"{path.name}: setup cell is out of date (run `make sync-setup`)")
            continue
        set_text(cells[md], SETUP_MARKDOWN)
        set_text(cells[cc], code)
        cells[cc]["outputs"] = []
        cells[cc]["execution_count"] = None
        save(path, nb)
        print("updated", path.name)
    if problems:
        fail(problems)
    if check:
        print(f"setup cells and chapter navigation: {len(student_notebooks())} notebooks in sync with course.toml")


if __name__ == "__main__":
    main()
