# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Every file carries the copyright notice and names its license.

    python tools/copyright.py           report problems (exit 1)
    python tools/copyright.py --fix     add or correct notices, sync license copies

Two licenses (see LICENSE.md):
  CC-BY-NC-SA-4.0              course content: notebooks/ and the site pages (*.qmd)
  LicenseRef-Prosperity-3.0.0  everything else: code, tools, configuration, docs

Each file gets two comment lines near the top, in its own comment syntax:
    Copyright © 2026-present CAehi.us
    SPDX-License-Identifier: <license>
  # ...            Python, shell, Makefile, YAML, TOML, requirements, .gitignore
  // ...           TypeScript, JavaScript, tsconfig (JSON with comments)
  /* ... */       CSS
  <!-- ... -->    HTML (after the doctype), Markdown
  YAML comment    .qmd front matter
Notebooks get "copyright" and "license" in their metadata and a small last
cell, so the notice shows in Jupyter, Colab, on the site and in the PDFs.
package.json cannot hold comments: it gets "author" and "license" fields.

Also kept in sync (--fix writes them):
- the "Source Code:" line of the Prosperity license = the repository URL in course.toml;
- python/LICENSE.md = LICENSES/LicenseRef-Prosperity-3.0.0.md (shipped in the wheel).

Exempt: LICENSES/ (license texts are never edited), package-lock.json, .nvmrc.
Generated files (the explorer bundle) get their notice from the build and are
only checked here.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from nbutil import course_config, fail, load, save, set_text, text  # noqa: E402

HOLDER = "CAehi.us"
NOTICE = f"Copyright © 2026-present {HOLDER}"
CONTENT = "CC-BY-NC-SA-4.0"
CODE = "LicenseRef-Prosperity-3.0.0"
CONTENT_URL = "https://creativecommons.org/licenses/by-nc-sa/4.0/"
FOOTER_CELL = f"<small>{NOTICE}. Licensed under [CC BY-NC-SA 4.0]({CONTENT_URL}).</small>"

PROSPERITY = ROOT / "LICENSES" / f"{CODE}.md"
PYTHON_LICENSE = ROOT / "python" / "LICENSE.md"

EXEMPT_NAMES = {"package-lock.json", ".nvmrc"}
EXEMPT_DIRS = ("LICENSES/",)
GENERATED = {"python/src/vecdraw/static/angle-explorer.iife.js", "python/LICENSE.md"}

HASH = {".py", ".sh", ".yml", ".yaml", ".toml", ".txt", ".gitignore"}
SLASH = {".ts", ".mjs", ".js", ".cjs"}
SPDX_LINE = re.compile(r"SPDX-License-Identifier:\s*(\S+)")


def repo_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    return sorted({f for f in out if (ROOT / f).is_file()})


def license_for(rel):
    """Course content is CC BY-NC-SA 4.0; everything else is Prosperity 3.0.0."""
    if rel.startswith("notebooks/") or rel.endswith(".qmd"):
        return CONTENT
    return CODE


def kind(rel):
    p = Path(rel)
    name = p.name
    if name in EXEMPT_NAMES or rel.startswith(EXEMPT_DIRS):
        return "exempt"
    if rel in GENERATED:
        return "generated"
    if name in ("Makefile", ".gitignore"):
        return "hash"
    if name == "package.json":
        return "package"
    if name.startswith("tsconfig") and p.suffix == ".json":
        return "slash"
    if p.suffix in HASH:
        return "hash"
    if p.suffix in SLASH:
        return "slash"
    return {".css": "css", ".html": "html", ".md": "md", ".qmd": "qmd", ".ipynb": "notebook"}.get(p.suffix, "unknown")


def comment_lines(k, license_id):
    lines = [NOTICE, f"SPDX-License-Identifier: {license_id}"]
    if k in ("hash", "qmd"):
        return [f"# {x}\n" for x in lines]
    if k == "slash":
        return [f"// {x}\n" for x in lines]
    if k == "css":
        return [f"/* {x} */\n" for x in lines]
    if k in ("html", "md"):
        return [f"<!-- {x} -->\n" for x in lines]
    raise ValueError(k)


def problem(rel, k):
    """None if the file is fine, else what is wrong."""
    path = ROOT / rel
    want = license_for(rel)
    if k == "package":
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("author") != HOLDER or data.get("license") != want:
            return f'needs "author": "{HOLDER}" and "license": "{want}"'
        return None
    if k == "notebook":
        nb = load(path)
        meta = nb.get("metadata", {})
        last = nb["cells"][-1] if nb["cells"] else None
        if meta.get("copyright") != NOTICE or meta.get("license") != want:
            return "notebook metadata needs copyright and license"
        if last is None or last["cell_type"] != "markdown" or text(last) != FOOTER_CELL:
            return "the last cell must be the copyright footer"
        return None
    head = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()[:8]]
    notice_line, license_line = (x.strip() for x in comment_lines(k, want))
    if notice_line not in head:
        return "no copyright notice comment"   # the words inside code do not count
    below = head[head.index(notice_line) + 1] if head.index(notice_line) + 1 < len(head) else ""
    found = SPDX_LINE.search(below)
    if not found:
        return "no SPDX-License-Identifier line under the notice"
    if below != license_line:
        return f"license is {found.group(1)}, should be {want}"
    return None


def fix(rel, k):
    path = ROOT / rel
    want = license_for(rel)
    if k == "package":
        data = json.loads(path.read_text(encoding="utf-8"))
        ordered = {}
        for key, value in data.items():   # "author" and "license" right after "description"
            if key in ("author", "license"):
                continue
            ordered[key] = value
            if key == "description":
                ordered["author"] = HOLDER
                ordered["license"] = want
        ordered.setdefault("author", HOLDER)
        ordered.setdefault("license", want)
        path.write_text(json.dumps(ordered, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    if k == "notebook":
        nb = load(path)
        meta = nb.setdefault("metadata", {})
        meta["copyright"] = NOTICE
        meta["license"] = want
        cells = nb["cells"]
        if cells and cells[-1]["cell_type"] == "markdown" and "Copyright" in text(cells[-1]):
            set_text(cells[-1], FOOTER_CELL)
        else:
            cells.append({"cell_type": "markdown", "id": "copyright", "metadata": {}, "source": [FOOTER_CELL]})
        save(path, nb)
        return

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    new = comment_lines(k, want)
    # 1. a file that already has the notice comment: fix or add the license line below it
    for i, line in enumerate(lines[:8]):
        if line.strip() == new[0].strip():
            if i + 1 < len(lines) and SPDX_LINE.search(lines[i + 1]):
                lines[i + 1] = new[1]
            else:
                lines.insert(i + 1, new[1])
            path.write_text("".join(lines), encoding="utf-8")
            return
    # 2. a file without it: insert both lines at the right place
    at = 0
    if k == "hash" and lines and lines[0].startswith("#!"):
        at = 1
    elif k == "html" and lines and lines[0].lower().startswith("<!doctype"):
        at = 1
    elif k == "qmd":
        if not lines or lines[0].strip() != "---":
            raise SystemExit(f"{rel}: a .qmd page needs YAML front matter to hold the notice")
        at = 1
    elif k not in ("hash", "slash", "css", "html", "md"):
        raise SystemExit(f"{rel}: no rule for this kind of file; add one to tools/copyright.py")
    lines[at:at] = new
    path.write_text("".join(lines), encoding="utf-8")


def prosperity_text():
    """The Prosperity license with the repository URL from course.toml."""
    url = course_config()["repository"]["url"]
    body = PROSPERITY.read_text(encoding="utf-8")
    return re.sub(r"(?m)^Source Code: .*$", f"Source Code: {url}", body, count=1)


def license_copies(fixing):
    """Problems with the license texts that must track course.toml."""
    problems = []
    want = prosperity_text()
    for path in (PROSPERITY, PYTHON_LICENSE):
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == want:
            continue
        if fixing:
            path.write_text(want, encoding="utf-8")
            print(f"synced: {path.relative_to(ROOT)}")
        else:
            problems.append(f"{path.relative_to(ROOT)}: out of date with course.toml (run `make copyright`)")
    return problems


def main():
    fixing = "--fix" in sys.argv
    problems = license_copies(fixing)
    checked = 0
    for rel in repo_files():
        k = kind(rel)
        if k == "exempt":
            continue
        if k == "unknown":
            problems.append(f"{rel}: no copyright rule for this kind of file (add one to tools/copyright.py)")
            continue
        checked += 1
        if k == "generated":
            if rel.endswith(".js"):
                head = (ROOT / rel).read_text(encoding="utf-8")[:300]
                if NOTICE not in head or CODE not in head:
                    problems.append(f"{rel}: built without the notice; rebuild it (make explorer)")
            continue
        wrong = problem(rel, k)
        if wrong is None:
            continue
        if fixing:
            fix(rel, k)
            print(f"fixed: {rel}")
        else:
            problems.append(f"{rel}: {wrong} (run `make copyright`)")
    if problems:
        fail(problems)
    if not fixing:
        print(f"copyright: all {checked} files carry the notice and their license")


if __name__ == "__main__":
    main()
