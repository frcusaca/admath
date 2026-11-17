"""Execute notebooks from top to bottom and fail on the first error.

    python tools/run_notebooks.py                 every notebook
    python tools/run_notebooks.py notebooks/00_*  just these

Nothing is written back: the committed notebooks keep no outputs.
For a teacher guide, the cell under the "Check the key" heading must also
print "All N checks passed.".
"""
import re
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

from nbutil import NOTEBOOKS, all_notebooks, is_teacher, text

CHECK_HEADING = re.compile(r"^#+\s*Check the key", re.MULTILINE)
CHECK_PASSED = re.compile(r"All (\d+) checks passed\.")


def stdout_of(cell):
    return "".join(o.get("text", "") for o in cell.get("outputs", []) if o.get("output_type") == "stream")


def check_the_key(nb, name):
    """The answer key's self-check must exist and pass."""
    cells = nb.cells
    for i, cell in enumerate(cells):
        if cell.cell_type == "markdown" and CHECK_HEADING.search(text(cell)):
            for nxt in cells[i + 1 :]:
                if nxt.cell_type == "code":
                    m = CHECK_PASSED.search(stdout_of(nxt))
                    if not m:
                        return f"{name}: the 'Check the key' cell did not print 'All N checks passed.'"
                    print(f"    answer key: {m.group(0)}")
                    return None
    return f"{name}: no 'Check the key' section found"


def run(path):
    nb = nbformat.read(path, as_version=4)
    # The kernel talks over TCP on 127.0.0.1 only. (IPC would avoid the kernel's
    # "running over TCP" warning, but its socket file lives in the working directory
    # and deep checkouts exceed the 108-character limit on socket paths.)
    client = NotebookClient(
        nb,
        timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(NOTEBOOKS)}},   # run from notebooks/, like Jupyter would
    )
    start = time.time()
    try:
        client.execute()
    except CellExecutionError as err:
        first_lines = "\n".join(str(err).splitlines()[:40])
        return f"{path.name}: a cell raised an error\n{first_lines}"
    print(f"  ok   {path.name}  ({time.time() - start:.1f}s, {len(nb.cells)} cells)")
    if is_teacher(path):
        return check_the_key(nb, path.name)
    return None


def main():
    paths = [Path(p) for p in sys.argv[1:]] or all_notebooks()
    failures = []
    for path in paths:
        problem = run(path)
        if problem:
            print(f"  FAIL {problem}", file=sys.stderr)
            failures.append(path.name)
    if failures:
        print(f"{len(failures)} of {len(paths)} notebooks failed: {', '.join(failures)}", file=sys.stderr)
        sys.exit(1)
    print(f"all {len(paths)} notebooks executed without error")


if __name__ == "__main__":
    main()
