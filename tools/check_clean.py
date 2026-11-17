# Copyright © 2026-present CAehi.us
"""Committed notebooks carry no outputs: the kids predict before they run.

    python tools/check_clean.py          report problems (exit 1)
    python tools/check_clean.py --fix    fix them in place

Checks, and with --fix repairs:
- outputs and execution counts on code cells;
- per-cell execution metadata (timings, collapsed/scrolled state), which Jupyter
  and Colab add and which would otherwise show up in diffs;
- a markdown cell that starts with a "---" rule directly followed by text. Quarto
  (Pandoc) reads that as the start of a YAML header and the render fails. A blank
  line after the rule fixes it and looks the same in Jupyter and Colab.
"""
import re
import sys

from nbutil import all_notebooks, fail, load, save, set_text, text

NOISY_METADATA = ("execution", "collapsed", "scrolled", "ExecuteTime")
YAML_LOOKALIKE = re.compile(r"\A---[ \t]*\n(?![ \t]*\n)")


def dirt(nb):
    found = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] == "markdown" and YAML_LOOKALIKE.match(text(cell)):
            found.append(f"cell {i} starts with '---' followed by text (Quarto reads it as YAML)")
        if cell["cell_type"] != "code":
            continue
        if cell.get("outputs"):
            found.append(f"cell {i} has outputs")
        if cell.get("execution_count") is not None:
            found.append(f"cell {i} has an execution count")
        for key in NOISY_METADATA:
            if key in cell.get("metadata", {}):
                found.append(f"cell {i} has metadata '{key}'")
    for key in ("widgets",):
        if key in nb.get("metadata", {}):
            found.append(f"notebook metadata '{key}'")
    return found


def clean(nb):
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown" and YAML_LOOKALIKE.match(text(cell)):
            set_text(cell, YAML_LOOKALIKE.sub("---\n\n", text(cell), count=1))
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        for key in NOISY_METADATA:
            cell.get("metadata", {}).pop(key, None)
    nb.get("metadata", {}).pop("widgets", None)


def main():
    fix = "--fix" in sys.argv
    problems = []
    for path in all_notebooks():
        nb = load(path)
        found = dirt(nb)
        if not found:
            continue
        if fix:
            clean(nb)
            save(path, nb)
            print(f"cleaned {path.name}")
        else:
            problems.append(f"{path.name}: {found[0]}" + (f" (and {len(found) - 1} more)" if len(found) > 1 else ""))
    if problems:
        problems.append("run `make strip` to fix these")
        fail(problems)
    if not fix:
        print(f"clean: {len(all_notebooks())} notebooks have no outputs")


if __name__ == "__main__":
    main()
