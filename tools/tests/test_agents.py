# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""tools/check_agents.py: AGENTS.md must mention every part of the project."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_agents as ca  # noqa: E402


def test_backticked_names_and_their_pieces_count():
    names = ca.mentioned("Run `make site teacher` and read `tools/`, `a.py, b.py`.")
    assert {"make", "site", "teacher", "tools", "a.py", "b.py"} <= names


def test_the_real_agents_md_is_complete():
    names = ca.mentioned(ca.AGENTS.read_text())
    for entry in ca.top_level() + ca.tool_scripts():
        assert entry in names, entry
    for target in ca.make_targets():
        assert target in names, target


def test_a_missing_target_is_caught(monkeypatch):
    monkeypatch.setattr(ca, "make_targets", lambda: ["brand-new-target"])
    monkeypatch.setattr(ca, "top_level", lambda: [])
    monkeypatch.setattr(ca, "tool_scripts", lambda: [])
    try:
        ca.main()
    except SystemExit as stop:
        assert stop.code == 1
    else:
        raise AssertionError("check_agents did not fail")
