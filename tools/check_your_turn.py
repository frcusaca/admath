# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Every "Your turn" has a place to work, and every %%your_turn cell is safe.

    python tools/check_your_turn.py

In each student notebook:
- A markdown cell that holds a "Your turn" exercise ("**Your turn.**" or a
  "## Your turn: ..." heading) is followed by a code cell: the kid's workspace.
- A code cell that starts with "%%your_turn <name>" has a name of the form
  <module>.<part>.<n> (quotes allowed), whose module matches the notebook, and
  no two cells in a notebook share a name.
- "Run all" skips an unchanged %%your_turn cell. So a later cell must not use
  a name that only such a cell makes; it would fail with NameError.
"""
import ast
import re
from collections import Counter

from nbutil import fail, load, module_number, student_notebooks, text

YOUR_TURN_TEXT = re.compile(r"\*\*Your turn[.!:]?\*\*|^#+ Your turn\b", re.MULTILINE)
MAGIC_LINE = re.compile(r"^%%your_turn\b(.*)$")
NAME = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def python_only(code):
    """The cell without IPython's % and ! lines, so that ast can read it."""
    lines = []
    for line in code.splitlines():
        if line.lstrip().startswith(("%", "!")):
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def names_made(code):
    """Names a cell assigns, defines or imports at the top level of its code."""
    made = set()
    try:
        tree = ast.parse(python_only(code))
    except SyntaxError:
        return made
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            made.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            made.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                made.add((alias.asname or alias.name).split(".")[0])
    return made


def names_used(code):
    try:
        tree = ast.parse(python_only(code))
    except SyntaxError:
        return set()
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def check(path):
    problems = []
    module = module_number(path)
    cells = load(path)["cells"]
    names = Counter()
    made_by_others = set()      # names that some cell made, in a run where %%your_turn cells are skipped
    only_guarded = {}           # name -> the exercise whose skipped cell is the only one making it
    for i, cell in enumerate(cells):
        source = text(cell)
        if cell["cell_type"] == "markdown":
            if YOUR_TURN_TEXT.search(source):
                after = cells[i + 1] if i + 1 < len(cells) else None
                if after is None or after["cell_type"] != "code":
                    first = source.strip().splitlines()[0][:60]
                    problems.append(f"{path.name}: the \"Your turn\" in the cell starting {first!r} needs its own code cell right after it")
            continue
        lines = source.splitlines()
        magic = MAGIC_LINE.match(lines[0]) if lines else None
        if magic:
            name = magic.group(1).strip().strip("\"'")
            shape = NAME.match(name)
            if not shape:
                problems.append(f"{path.name}: %%your_turn needs a name like {module}.2.1, not {name!r}")
            elif int(shape.group(1)) != module:
                problems.append(f"{path.name}: %%your_turn {name} belongs in Module {shape.group(1)}, not Module {module}")
            names[name] += 1
            body = "\n".join(lines[1:])
            for made in names_made(body) - made_by_others:
                only_guarded[made] = name
            continue
        made = names_made(source)
        for used in sorted((names_used(source) - made) & set(only_guarded)):
            problems.append(
                f"{path.name}: `{used}` is made only in %%your_turn {only_guarded[used]}, which \"Run all\" skips, "
                "but a later cell uses it"
            )
        made_by_others |= made
        for name in made:
            only_guarded.pop(name, None)
    for name, count in names.items():
        if count > 1:
            problems.append(f"{path.name}: %%your_turn {name} is used {count} times; each exercise needs its own name")
    return problems, sum(names.values())


def main():
    problems = []
    guarded = 0
    notebooks = student_notebooks()
    for path in notebooks:
        found, count = check(path)
        problems += found
        guarded += count
    if problems:
        fail(problems)
    print(f"your turn: every exercise has a workspace; {guarded} %%your_turn cells in {len(notebooks)} notebooks are safe")


if __name__ == "__main__":
    main()
