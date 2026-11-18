<!-- Copyright © 2026-present CAehi.us -->
<!-- SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0 -->
# admath

Math learning tools for early mathematics learners.

This repository holds **Linear Algebra Circle**, a linear algebra course for
advanced 5th graders, taught math-circle style alongside an intro
machine-learning class. Kids work in Jupyter notebooks
(in Google Colab or locally) and draw with a small, readable library.

**The one rule: predict, then run.** The notebooks are committed without
outputs, so every result is a surprise worth predicting.

---

## 🚧 BIG TO-DO: accessibility and Section 508 compliance 🚧

> **Not done. Not audited. Do not claim this course is accessible or 508
> compliant until the work below is finished and checked.**

**Why it matters.** Section 508 of the U.S. Rehabilitation Act covers
technology bought or used by federal agencies, and many schools and districts
require the same of what they adopt. Its 2017 standards point to WCAG 2.0,
levels A and AA. Public schools are also covered by ADA Title II, whose 2024
web rule points to WCAG 2.1 AA. **Research first: check the current rules and
deadlines, and which ones apply to the places that will use this course.**

**The goal: cover more and more people, one group at a time.** Make a written
plan that lists who could be shut out today and, for each group, what to fix,
in priority order. Then work through it, with checks in `make check` so fixes
stay fixed. A starting list:

| Who | What is likely in the way now | Where |
| --- | --- | --- |
| Colour-blind kids | Some pictures carry meaning by colour; the colour-mixing lessons (Notebook 01 Deep 2, Notebook 02 Deep 4) are plain RGB by decision | notebooks, `vecdraw`, explorer |
| Blind kids, screen-reader users | Plots are images with no text alternative; math needs to be readable aloud; the PDFs are not tagged | `vecdraw`, site, PDFs |
| Low-vision kids | Contrast and zoom not checked everywhere; small text in plots | site, plots, explorer |
| Keyboard-only and switch users | The explorer has keyboard support, but nothing else is tested | explorer, site |
| Touch-screen users (iPads, Chromebooks) | Hover hints cannot be hovered (the site turns them into footnotes, but notebooks can't) | notebooks |
| Kids who read slowly, or in a second language | Long paragraphs; no audio | lessons |
| Kids with motion sensitivity | The explorer follows "reduced motion"; nothing else is checked | explorer, site |

**Suggested first step for colour: a "color-blindness" setting.** Many
examples could read one setting and, when it is on, show colour differences
with **patterns** (hatching, dashes, marker shapes) or **brightness contrast**
as well as hue. For example:

- `vecdraw`: a setting such as `vecdraw.settings["color-blindness"] = True`
  (one place, read by every drawing function) that switches to dashed or
  hatched arrows and stronger light/dark differences;
- the Angle Explorer: a matching `mountAngleExplorer(el, { colorBlindness: true })`
  option and an on-page toggle, drawing positive and negative with different
  patterns, not only blue and orange;
- the site: the same toggle, remembered per browser.

Other steps for the plan: run an automatic checker (such as axe-core in the
Playwright tests) on the site and the explorer; give every plot a text
description; produce tagged, accessible PDFs; test with a real screen reader;
and, when the course is offered to schools, write an Accessibility
Conformance Report (a VPAT) that says honestly what is and is not supported.

---

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
AI coding agents: read [`AGENTS.md`](AGENTS.md). Security reports and known
issues: [`SECURITY.md`](SECURITY.md).

## Copyright and licenses

Copyright © 2026-present CAehi.us. See [`LICENSE.md`](LICENSE.md).

- **Lessons** (`notebooks/`, the site pages): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
  Share and adapt for noncommercial purposes, with credit, under the same license.
- **Software** (`vecdraw`, the Angle Explorer, tools): [Prosperity Public License 3.0.0](https://prosperitylicense.com/versions/3.0.0).
  Free for noncommercial use, including by schools; a 30-day trial for commercial use.

Every file names its license (`make check-copyright`). The bundled fonts are
credited in [`explorer/THIRD_PARTY_NOTICES.md`](explorer/THIRD_PARTY_NOTICES.md).
