# Copyright © 2026-present CAehi.us
"""requirements.txt documents exactly what the vecdraw package declares."""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def names_and_specs(lines):
    out = {}
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        m = re.match(r"([A-Za-z0-9_.-]+)\s*(.*)", line)
        out[m.group(1).lower()] = m.group(2).replace(" ", "")
    return out


def test_requirements_txt_matches_pyproject():
    project = tomllib.loads((ROOT / "python/pyproject.toml").read_text())["project"]
    declared = names_and_specs(project["dependencies"] + project["optional-dependencies"]["notebook"])
    listed = names_and_specs((ROOT / "requirements.txt").read_text().splitlines())
    assert listed == declared


def test_requirements_txt_installs_vecdraw_and_dev_builds_on_it():
    assert "-e ./python" in (ROOT / "requirements.txt").read_text().splitlines()
    assert "-r requirements.txt" in (ROOT / "requirements-dev.txt").read_text().splitlines()
