# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Small helpers shared by the notebook tools. Standard library only."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, nb):
    """Write in Jupyter's own format (indent 1, UTF-8), so diffs stay small."""
    Path(path).write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def text(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def set_text(cell, value):
    lines = value.splitlines(keepends=True)
    cell["source"] = lines


def is_teacher(path):
    return "teacher" in Path(path).stem


def module_number(path):
    """'00_vectors....ipynb' -> 0. None if the name does not start with digits and '_'."""
    m = re.match(r"(\d+)_", Path(path).name)
    return int(m.group(1)) if m else None


def student_notebooks():
    return sorted(p for p in NOTEBOOKS.glob("[0-9]*_*.ipynb") if not is_teacher(p))


def teacher_notebooks():
    return sorted(p for p in NOTEBOOKS.glob("[0-9]*_*.ipynb") if is_teacher(p))


def all_notebooks():
    return sorted(NOTEBOOKS.glob("[0-9]*_*.ipynb"))


def course_config():
    import tomllib

    return tomllib.loads((ROOT / "course.toml").read_text(encoding="utf-8"))


def fail(messages):
    for m in messages:
        print("FAIL:", m, file=sys.stderr)
    sys.exit(1)
