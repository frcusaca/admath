# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Every Mastery Coin in a student notebook has exactly one answer-key row, and the reverse.

    python tools/check_coins.py

Coin ids look like m<module>.<part>.<n>, e.g. m0.4.10.
- In a student notebook, a coin is *defined* where its id is written in bold:
  **m0.4.10**. Each id must be defined exactly once, and its module number
  must match the notebook's.
- In the matching teacher guide (same leading number, "teacher" in the name),
  each answer-key row is a table row whose first cell is the id:
  | m0.4.10 | ... |
- Every coin defined in the student notebook needs exactly one row; every row
  needs a coin. A student notebook with coins but no teacher guide fails.
"""
import re
import sys
from collections import Counter

from nbutil import fail, load, module_number, student_notebooks, teacher_notebooks, text

COIN = r"m(\d+)\.(\d+)\.(\d+)"
DEFINED = re.compile(r"\*\*(" + COIN + r")\*\*")
KEY_ROW = re.compile(r"^\s*\|\s*(" + COIN + r")\s*\|", re.MULTILINE)
ANY_ID = re.compile(r"\b" + COIN + r"\b")


def markdown(nb):
    return "\n".join(text(c) for c in nb["cells"] if c["cell_type"] == "markdown")


def main():
    problems = []
    guides = {module_number(p): p for p in teacher_notebooks()}
    total = 0
    for student in student_notebooks():
        module = module_number(student)
        md = markdown(load(student))
        defined = Counter(m.group(1) for m in DEFINED.finditer(md))
        mentioned = {m.group(0) for m in ANY_ID.finditer(md)}
        if not defined:
            if mentioned:
                problems.append(f"{student.name}: mentions coin ids {sorted(mentioned)} but defines none in bold")
            print(f"  --   {student.name}: no Mastery Coins")
            continue
        for coin, n in defined.items():
            if n > 1:
                problems.append(f"{student.name}: {coin} is defined {n} times")
            if int(coin[1:].split(".")[0]) != module:
                problems.append(f"{student.name}: {coin} belongs to module {coin[1:].split('.')[0]}, not {module}")
        for coin in sorted(mentioned - set(defined)):
            problems.append(f"{student.name}: {coin} is mentioned but never defined in bold")

        guide = guides.get(module)
        if guide is None:
            problems.append(f"{student.name}: has {len(defined)} coins but there is no teacher guide for module {module}")
            continue
        rows = Counter(m.group(1) for m in KEY_ROW.finditer(markdown(load(guide))))
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
