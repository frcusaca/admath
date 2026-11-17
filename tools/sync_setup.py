# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Write the setup cells of every student notebook from course.toml.

    python tools/sync_setup.py           rewrite the notebooks
    python tools/sync_setup.py --check   only report notebooks that are out of date (exit 1)

The setup is two cells near the top of each student notebook:
  1. a markdown cell starting with "**Setup.**"
  2. the code cell that gets the library (it replaced the old `%%writefile vecdraw.py` cell)
The import cell after them (`import importlib, vecdraw ...`) is never touched.
"""
import sys

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
    for path in student_notebooks():
        nb = load(path)
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
        print(f"setup cells: {len(student_notebooks())} notebooks in sync with course.toml")


if __name__ == "__main__":
    main()
