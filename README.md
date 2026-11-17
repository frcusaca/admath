<!-- Copyright © 2026-present CAehi.us -->
# Linear Algebra Circle

A linear algebra course for advanced 5th graders, taught math-circle style
alongside an intro machine-learning class. Kids work in Jupyter notebooks
(in Google Colab or locally) and draw with a small, readable library.

**The one rule: predict, then run.** The notebooks are committed without
outputs, so every result is a surprise worth predicting.

## What is here

| Folder | What it is |
| --- | --- |
| `notebooks/` | The lessons (`00_…` to `04_…`) and the teacher guides (`*_teacher_guide.ipynb`). The source of truth. |
| `python/` | `vecdraw`, the drawing library the notebooks import, plus `explore_angles()`. |
| `explorer/` | The Angle Explorer, in TypeScript: a standalone page and a library. |
| `tools/` | Checks and build helpers (run through `make`). |
| `course.toml` | The one course-wide setting: where Colab installs `vecdraw` from. |

## Quick start

```bash
make setup     # .venv, node_modules, Quarto and TinyTeX in .tools/ (nothing system-wide)
make check     # every check and test, both sites rendered
make preview   # the student site in a browser
```

`make` with no target lists everything.

## Requirements

**To run the notebooks** (Python 3.10 or newer):

```bash
pip install -r requirements.txt
```

| Library | Why | Declared in |
| --- | --- | --- |
| numpy ≥ 1.24 | vectors | `requirements.txt`, `python/pyproject.toml` |
| matplotlib ≥ 3.7 | drawing | `requirements.txt`, `python/pyproject.toml` |
| IPython ≥ 8 | shows the Angle Explorer in a notebook | `requirements.txt`, `python/pyproject.toml` (extra `notebook`) |
| vecdraw | the course's drawing library, in `python/` | `requirements.txt` (`-e ./python`) |

In Google Colab nothing needs installing by hand: the first cell of each
notebook installs `vecdraw`, and Colab already has the rest.

**To build and test the course**:

| Need | Version | Declared in |
| --- | --- | --- |
| Python test and notebook tools (pytest, nbclient, nbformat, ipykernel, jupyter-core, PyYAML) | see file | `requirements-dev.txt` (includes `requirements.txt`) |
| Node.js | ≥ 22.12, 26 LTS recommended | `package.json` `engines`, `.nvmrc` |
| TypeScript, Vite, Vitest, Playwright, fonts | exact versions | `explorer/package.json` |
| KaTeX, markdown-it (LaTeX check) | exact versions | `package.json` |
| Quarto | 1.11.9 | `tools/install_quarto.sh` |
| TinyTeX (PDFs) | v2026.11 | `tools/install_tinytex.sh` |
| uv, Google Chrome, make, curl, git | any recent | install yourself |

`make setup` installs everything in the first five rows into the repository
(`.venv/`, `node_modules/`, `.tools/`). The built explorer has no runtime
dependencies: all npm packages are build and test tools.

## Outputs

- `_site/`: the student website, with a PDF of each notebook.
- `_site-teacher/`: the teacher guides. Never publish this with the student site.
- `dist/colab/`: the student notebooks, zipped for Colab.
- `explorer/dist/standalone/angle-explorer.html`: the explorer as one file that works offline.

Maintainers: start with [`maintainer.readme.md`](maintainer.readme.md).

## Copyright

Copyright © 2026-present CAehi.us. Every file carries this notice
(`make check-copyright`); the bundled fonts are credited in
[`explorer/THIRD_PARTY_NOTICES.md`](explorer/THIRD_PARTY_NOTICES.md).
