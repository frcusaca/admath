# Copyright © 2026-present CAehi.us
"""Every file in the repository carries the copyright notice.

    python tools/copyright.py           report files without it (exit 1)
    python tools/copyright.py --fix     add it where it is missing

The notice goes into each file's own comment syntax, near the top:
  # ...            Python, shell, Makefile, YAML, TOML, requirements, .gitignore
  // ...           TypeScript, JavaScript, tsconfig (JSON with comments)
  /* ... */       CSS
  <!-- ... -->    HTML (after the doctype), Markdown
  YAML comment    .qmd front matter
Notebooks get it in their metadata ("copyright") and as a small last cell,
so it shows in Jupyter, Colab, on the site and in the PDFs.
package.json cannot hold comments, so it names the owner in "author".

Exempt: package-lock.json and .nvmrc (generated or no comment syntax).
Generated files (the explorer bundle) get the notice from the build, and are
only checked here.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from nbutil import fail, load, save, set_text, text  # noqa: E402

HOLDER = "CAehi.us"
NOTICE = f"Copyright © 2026-present {HOLDER}"
FOOTER_CELL = f"<small>{NOTICE}</small>"

EXEMPT = {"package-lock.json", ".nvmrc"}
GENERATED = {"python/src/vecdraw/static/angle-explorer.iife.js"}

HASH = {".py", ".sh", ".yml", ".yaml", ".toml", ".txt", ".gitignore"}
SLASH = {".ts", ".mjs", ".js", ".cjs"}


def repo_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    return sorted({f for f in out if (ROOT / f).is_file()})


def kind(rel):
    p = Path(rel)
    name = p.name
    if name in EXEMPT:
        return "exempt"
    if rel in GENERATED:
        return "generated"
    if name == "Makefile" or name == ".gitignore":
        return "hash"
    if name == "package.json":
        return "package"
    if name.startswith("tsconfig") and p.suffix == ".json":
        return "slash"
    suffix = p.suffix
    if suffix in HASH:
        return "hash"
    if suffix in SLASH:
        return "slash"
    return {".css": "css", ".html": "html", ".md": "md", ".qmd": "qmd", ".ipynb": "notebook"}.get(suffix, "unknown")


def has_notice(rel, k):
    path = ROOT / rel
    if k == "package":
        return json.loads(path.read_text(encoding="utf-8")).get("author") == HOLDER
    if k == "notebook":
        nb = load(path)
        last = nb["cells"][-1] if nb["cells"] else None
        return (
            nb.get("metadata", {}).get("copyright") == NOTICE
            and last is not None
            and last["cell_type"] == "markdown"
            and text(last) == FOOTER_CELL
        )
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:6])
    return NOTICE in head


def add_notice(rel, k):
    path = ROOT / rel
    if k == "package":
        data = json.loads(path.read_text(encoding="utf-8"))
        ordered = {}
        for key, value in data.items():   # put "author" right after "description"
            ordered[key] = value
            if key == "description":
                ordered["author"] = HOLDER
        ordered.setdefault("author", HOLDER)
        path.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    if k == "notebook":
        nb = load(path)
        nb.setdefault("metadata", {})["copyright"] = NOTICE
        cells = nb["cells"]
        if cells and cells[-1]["cell_type"] == "markdown" and "Copyright" in text(cells[-1]):
            set_text(cells[-1], FOOTER_CELL)
        else:
            cells.append({"cell_type": "markdown", "id": "copyright", "metadata": {}, "source": [FOOTER_CELL]})
        save(path, nb)
        return
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    at = 0
    if k == "hash":
        line = f"# {NOTICE}\n"
        if lines and lines[0].startswith("#!"):
            at = 1
    elif k == "slash":
        line = f"// {NOTICE}\n"
    elif k == "css":
        line = f"/* {NOTICE} */\n"
    elif k == "html":
        line = f"<!-- {NOTICE} -->\n"
        if lines and lines[0].lower().startswith("<!doctype"):
            at = 1
    elif k == "md":
        line = f"<!-- {NOTICE} -->\n"
    elif k == "qmd":
        if not lines or lines[0].strip() != "---":
            raise SystemExit(f"{rel}: a .qmd page needs YAML front matter to hold the notice")
        line = f"# {NOTICE}\n"
        at = 1
    else:
        raise SystemExit(f"{rel}: no rule for this kind of file; add one to tools/copyright.py or EXEMPT")
    lines.insert(at, line)
    path.write_text("".join(lines), encoding="utf-8")


def main():
    fix = "--fix" in sys.argv
    problems = []
    checked = 0
    for rel in repo_files():
        k = kind(rel)
        if k == "exempt":
            continue
        if k == "unknown":
            problems.append(f"{rel}: no copyright rule for this kind of file (add one to tools/copyright.py)")
            continue
        checked += 1
        if has_notice(rel, k):
            continue
        if k == "generated":
            problems.append(f"{rel}: generated without the notice; rebuild it (make explorer)")
        elif fix:
            add_notice(rel, k)
            print(f"added notice: {rel}")
        else:
            problems.append(f"{rel}: no copyright notice (run `make copyright`)")
    if problems:
        fail(problems)
    if not fix:
        print(f"copyright: all {checked} files carry '{NOTICE}'")


if __name__ == "__main__":
    main()
