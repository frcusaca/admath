"""Committed notebooks carry no outputs: the kids predict before they run.

    python tools/check_clean.py          report notebooks with outputs (exit 1)
    python tools/check_clean.py --fix    remove outputs and execution counts in place

Also removes per-cell execution metadata (timings, collapsed/scrolled state),
which Jupyter and Colab add and which would otherwise show up in diffs.
"""
import sys

from nbutil import all_notebooks, fail, load, save

NOISY_METADATA = ("execution", "collapsed", "scrolled", "ExecuteTime")


def dirt(nb):
    found = []
    for i, cell in enumerate(nb["cells"]):
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
        problems.append("run `make strip` to remove outputs")
        fail(problems)
    if not fix:
        print(f"clean: {len(all_notebooks())} notebooks have no outputs")


if __name__ == "__main__":
    main()
