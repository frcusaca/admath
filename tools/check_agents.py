# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""AGENTS.md mentions every part of the project an agent needs to find.

    python tools/check_agents.py

Fails when AGENTS.md does not mention, in backticks:
- a top-level file or folder that git tracks,
- a script in tools/,
- a target in the Makefile.
It cannot tell whether the descriptions are still true; that is up to whoever
changes the code (AGENTS.md, "Keep this file up to date").
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "AGENTS.md"


def mentioned(text):
    """Everything written in backticks, plus each path-like piece inside them."""
    spans = set(re.findall(r"`([^`\n]+)`", text))
    pieces = set()
    for span in spans:
        pieces.update(re.split(r"[\s,]+", span))
    return {x.strip().rstrip("/") for x in spans | pieces if x.strip()}


def top_level():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return sorted({f.split("/")[0] for f in files})


def tool_scripts():
    return sorted(p.name for p in (ROOT / "tools").iterdir() if p.suffix in {".py", ".mjs", ".sh"})


def make_targets():
    text = (ROOT / "Makefile").read_text(encoding="utf-8")
    return sorted(set(re.findall(r"(?m)^([a-z][a-z0-9-]*):", text)))


def main():
    names = mentioned(AGENTS.read_text(encoding="utf-8"))
    missing = []
    missing += [f"top-level `{x}`" for x in top_level() if x not in names]
    missing += [f"tools script `{x}`" for x in tool_scripts() if x not in names]
    missing += [f"make target `{x}`" for x in make_targets() if x not in names and f"make {x}" not in names]
    if missing:
        for m in missing:
            print(f"FAIL: AGENTS.md does not mention {m}", file=sys.stderr)
        print("Update AGENTS.md (see its last section).", file=sys.stderr)
        sys.exit(1)
    print(f"agents: AGENTS.md covers {len(top_level())} top-level entries, {len(tool_scripts())} tools, {len(make_targets())} make targets")


if __name__ == "__main__":
    main()
