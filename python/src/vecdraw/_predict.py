# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Two notebook helpers for "predict, then run".

The setup cell loads them with  %load_ext vecdraw._predict

    %guess_first 2 * a
        The first time, it asks for your guess and shows nothing.
        Run the cell again to see the answer.

    %%your_turn 0.5.1
    ...your code...
        The cell runs only after you change it. 0.5.1 is the exercise's
        name: Module 0, Part 0.5, the first "Your turn" in that part.

They remember what they have seen until the notebook restarts. The memory
lives here, in this module, never among your own variables. The module's
name starts with "_" so that `from vecdraw import *` does not copy it.
"""
import hashlib
import io
import os
import tokenize

# The course's build tools set this to "1", so the website and the PDFs show
# every answer instead of the "guess first" messages.
ALWAYS_RUN = "VECDRAW_ALWAYS_RUN"

GUESS_MESSAGE = "Make your guess first: what will this be? Say it out loud, then run this cell again."
YOUR_TURN_MESSAGE = (
    "Your turn! Make a change and answer the question. "
    "This cell runs once you have changed something. (Changing only a # note does not count.)"
)
# Shown from the second unchanged run on, for a kid who already changed the cell
# before the notebook restarted, or who wants to see the example run as it is.
YOUR_TURN_TIP = "To run it anyway, add or delete a ; at the end of a line, and run again."

_guessed = set()      # the expressions that already asked for a guess
_originals = {}       # exercise name -> fingerprint of its code the first time it ran
_waited = set()       # the exercises that already showed their message once


def always_run():
    return os.environ.get(ALWAYS_RUN) == "1"


def fingerprint(code):
    """A short code for what the cell *does*: spaces, blank lines and # notes do not count."""
    pieces = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.ENDMARKER):
                continue
            if token.type in (tokenize.INDENT, tokenize.DEDENT):
                pieces.append(tokenize.tok_name[token.type])     # the depth, not the number of spaces
            else:
                pieces.append(token.string)
    except (tokenize.TokenError, SyntaxError):
        # Half-typed code that Python cannot read yet: compare the lines instead.
        pieces = [line.strip() for line in code.splitlines() if line.strip()]
    return hashlib.sha256("\n".join(pieces).encode()).hexdigest()[:16]


def exercise_name(line):
    name = line.strip().strip("\"'")
    if not name:
        raise ValueError('Give the exercise its name, like this:  %%your_turn 0.5.1')
    return name


def guess_first(line):
    """Line magic. The first run asks for a guess; the next run shows the value."""
    from IPython import get_ipython

    expression = line.strip()
    if not always_run() and expression not in _guessed:
        _guessed.add(expression)
        print(GUESS_MESSAGE)
        return None
    return get_ipython().ev(expression)


def your_turn(line, cell):
    """Cell magic. Runs the cell only after it differs from the first version it saw."""
    from IPython import get_ipython

    name = exercise_name(line)
    now = fingerprint(cell)
    if name not in _originals:
        _originals[name] = now
    if not always_run() and now == _originals[name]:
        print(YOUR_TURN_MESSAGE)
        if name in _waited:
            print(YOUR_TURN_TIP)
        _waited.add(name)
        return
    result = get_ipython().run_cell(cell)
    if always_run() and not result.success:
        # In a build, a broken exercise must stop the build, not just print an error.
        raise result.error_in_exec or result.error_before_exec


def load_ipython_extension(ipython):
    """Called by %load_ext vecdraw._predict."""
    ipython.register_magic_function(guess_first, "line", "guess_first")
    ipython.register_magic_function(your_turn, "cell", "your_turn")
