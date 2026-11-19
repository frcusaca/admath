# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""The %guess_first and %%your_turn magics, in a real IPython shell."""
import pytest

IPython = pytest.importorskip("IPython")
from IPython.core.interactiveshell import InteractiveShell

from vecdraw import _predict


@pytest.fixture
def shell(monkeypatch):
    monkeypatch.delenv(_predict.ALWAYS_RUN, raising=False)
    _predict._guessed.clear()
    _predict._originals.clear()
    _predict._waited.clear()
    sh = InteractiveShell.instance()
    sh.run_line_magic("load_ext", "vecdraw._predict")
    sh.user_ns["x"] = 3
    return sh


def test_guess_first_asks_once_then_answers(shell, capsys):
    assert shell.run_line_magic("guess_first", "x + 1") is None
    assert "guess" in capsys.readouterr().out
    assert shell.run_line_magic("guess_first", "x + 1") == 4
    assert shell.run_line_magic("guess_first", "x + 1") == 4


def test_guess_first_asks_again_for_a_new_expression(shell, capsys):
    shell.run_line_magic("guess_first", "x + 1")
    assert shell.run_line_magic("guess_first", "x + 2") is None


def test_your_turn_waits_for_a_change(shell, capsys):
    shell.run_cell_magic("your_turn", "0.0.1", "y = 7\n")
    assert "y" not in shell.user_ns
    assert "Your turn" in capsys.readouterr().out
    shell.run_cell_magic("your_turn", "0.0.1", "y = 7\n")          # still unchanged
    assert "y" not in shell.user_ns
    shell.run_cell_magic("your_turn", "0.0.1", "y = 4\n")          # changed: it runs
    assert shell.user_ns["y"] == 4


def test_the_second_unchanged_run_tells_how_to_run_anyway(shell, capsys):
    shell.run_cell_magic("your_turn", "0.0.9", "k = 1\n")
    assert "anyway" not in capsys.readouterr().out
    shell.run_cell_magic("your_turn", "0.0.9", "k = 1\n")
    assert "anyway" in capsys.readouterr().out
    shell.run_cell_magic("your_turn", "0.0.9", "k = 1;\n")         # the tip works: add a ;
    assert shell.user_ns["k"] == 1


def test_notes_and_spacing_are_not_a_change(shell):
    shell.run_cell_magic("your_turn", "0.0.2", "z = [1, 2]   # change me\n")
    shell.run_cell_magic("your_turn", "0.0.2", "\n\nz = [1,2]       # I changed this note\n\n")
    assert "z" not in shell.user_ns


def test_a_hash_inside_a_string_is_code(shell):
    shell.run_cell_magic("your_turn", "0.0.3", 'color = "#ff0000"\n')
    shell.run_cell_magic("your_turn", "0.0.3", 'color = "#00ff00"\n')
    assert shell.user_ns["color"] == "#00ff00"


def test_names_keep_exercises_apart_and_quotes_are_optional(shell):
    shell.run_cell_magic("your_turn", '"0.0.4"', "a4 = 1\n")
    shell.run_cell_magic("your_turn", "0.0.5", "a5 = 1\n")
    shell.run_cell_magic("your_turn", "0.0.4", "a4 = 2\n")
    assert shell.user_ns["a4"] == 2
    assert "a5" not in shell.user_ns


def test_a_name_is_required(shell):
    with pytest.raises(ValueError):
        shell.run_cell_magic("your_turn", "", "q = 1\n")


def test_half_typed_code_still_counts_as_a_change(shell):
    shell.run_cell_magic("your_turn", "0.0.6", "w = (1, 2)\n")
    assert _predict.fingerprint("w = (1, 2\n") != _predict.fingerprint("w = (1, 2)\n")


def test_builds_always_run(shell, monkeypatch):
    monkeypatch.setenv(_predict.ALWAYS_RUN, "1")
    assert shell.run_line_magic("guess_first", "x * 2") == 6
    shell.run_cell_magic("your_turn", "0.0.7", "b7 = 1\n")
    assert shell.user_ns["b7"] == 1


def test_a_broken_exercise_stops_a_build(shell, monkeypatch):
    monkeypatch.setenv(_predict.ALWAYS_RUN, "1")
    with pytest.raises(ZeroDivisionError):
        shell.run_cell_magic("your_turn", "0.0.8", "1 / 0\n")


def test_loading_adds_no_names_for_the_kids(shell):
    before = set(shell.user_ns)
    shell.run_line_magic("reload_ext", "vecdraw._predict")
    shell.run_cell("from vecdraw import *")
    added = set(shell.user_ns) - before
    assert not {"_predict", "predict", "_guessed", "_originals", "guess_first", "your_turn"} & added
