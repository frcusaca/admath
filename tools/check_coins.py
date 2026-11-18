# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Every Mastery Coin in a student notebook has exactly one answer-key row, and the reverse.

    python tools/check_coins.py

Coin ids look like M <module>.<part>.<n>, e.g. M 0.4.10 (capital M, a space).
- In a student notebook, a coin is *defined* by a list item holding only its
  bold id, with the problem indented on the lines below:

      - **M 0.4.10**

        Find the number ...

  Each id must be defined exactly once, and its module number must match the
  notebook's. The coins sit under a "#### Mastery Coins <module>.<part>" heading.
- In the matching teacher guide (same leading number, "teacher" in the name),
  each answer-key row is a table row whose first cell is the id:
  | M 0.4.10 | ... |
- The old form (m0.4.10) is reported wherever it appears.
- Every coin defined in the student notebook needs exactly one row; every row
  needs a coin. A student notebook with coins but no teacher guide fails.
"""
import re
import sys
from collections import Counter

from nbutil import fail, load, module_number, student_notebooks, teacher_notebooks, text

COIN = r"M (\d+)\.(\d+)\.(\d+)"
DEFINED = re.compile(r"\*\*(" + COIN + r")\*\*")
# the layout: "- **M 0.4.10**", a blank line, then the problem indented by two spaces
LAID_OUT = re.compile(r"^- \*\*(" + COIN + r")\*\*\n\n  \S", re.MULTILINE)
KEY_ROW = re.compile(r"^\s*\|\s*(" + COIN + r")\s*\|", re.MULTILINE)
ANY_ID = re.compile(r"\b" + COIN + r"\b")
OLD_ID = re.compile(r"\bm\d+\.\d+\.\d+\b")


def module_of(coin):
    return int(coin.split()[1].split(".")[0])


def markdown(nb):
    return "\n".join(text(c) for c in nb["cells"] if c["cell_type"] == "markdown")


def main():
    problems = []
    guides = {module_number(p): p for p in teacher_notebooks()}
    total = 0
    for student in student_notebooks():
        module = module_number(student)
        md = markdown(load(student))
        for old in sorted(set(OLD_ID.findall(md))):
            problems.append(f"{student.name}: old coin id {old}; write it as M {old[1:]}")
        defined = Counter(m.group(1) for m in DEFINED.finditer(md))
        laid_out = {m.group(1) for m in LAID_OUT.finditer(md)}
        for coin in sorted(set(defined) - laid_out):
            problems.append(f"{student.name}: {coin} must be a list item holding only the bold id, with the problem indented below it")
        mentioned = {m.group(0) for m in ANY_ID.finditer(md)}
        if not defined:
            if mentioned:
                problems.append(f"{student.name}: mentions coin ids {sorted(mentioned)} but defines none in bold")
            print(f"  --   {student.name}: no Mastery Coins")
            continue
        for coin, n in defined.items():
            if n > 1:
                problems.append(f"{student.name}: {coin} is defined {n} times")
            if module_of(coin) != module:
                problems.append(f"{student.name}: {coin} belongs to module {module_of(coin)}, not {module}")
        for coin in sorted(mentioned - set(defined)):
            problems.append(f"{student.name}: {coin} is mentioned but never defined in bold")

        guide = guides.get(module)
        if guide is None:
            problems.append(f"{student.name}: has {len(defined)} coins but there is no teacher guide for module {module}")
            continue
        guide_md = markdown(load(guide))
        for old in sorted(set(OLD_ID.findall(guide_md))):
            problems.append(f"{guide.name}: old coin id {old}; write it as M {old[1:]}")
        rows = Counter(m.group(1) for m in KEY_ROW.finditer(guide_md))
        for coin, n in rows.items():
            if n > 1:
                problems.append(f"{guide.name}: {coin} has {n} answer-key rows")
        for coin in sorted(set(defined) - set(rows)):
            problems.append(f"{guide.name}: no answer-key row for {coin} (defined in {student.name})")
        for coin in sorted(set(rows) - set(defined)):
            problems.append(f"{guide.name}: answer-key row for {coin}, which {student.name} does not define")
        total += len(defined)
        print(f"  ok   {student.name}: {len(defined)} coins, {sum(rows.values())} answer-key rows in {guide.name}")

    if problems:
        fail(problems)
    print(f"coins: {total} coins, each with exactly one answer-key row")


if __name__ == "__main__":
    sys.exit(main())
