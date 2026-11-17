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

You need `uv`, Node.js 22.12 or newer (26 LTS recommended, see `.nvmrc`),
Google Chrome (for the browser tests), `make`, `curl` and `git`.
`make` with no target lists everything.

## Outputs

- `_site/`: the student website, with a PDF of each notebook.
- `_site-teacher/`: the teacher guides. Never publish this with the student site.
- `dist/colab/`: the student notebooks, zipped for Colab.
- `explorer/dist/standalone/angle-explorer.html`: the explorer as one file that works offline.

Maintainers: start with [`maintainer.readme.md`](maintainer.readme.md).
