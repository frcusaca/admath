<!-- Copyright © 2026-present CAehi.us -->
<!-- SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0 -->
# AGENTS.md

Instructions and a map for AI coding agents (and people) working in this
repository. Read it before changing anything; **keep it up to date** (see the
last section).

**admath** holds *Linear Algebra Circle*, a linear algebra course for advanced
5th graders taught math-circle style next to an intro ML class. Kids work in
Jupyter notebooks, mostly in Google Colab, and draw with a small library,
`vecdraw`, that ships an interactive "Angle Explorer". The notebooks also
render to a website and PDFs with Quarto.

## Rules that never bend

1. **Don't change the lessons by accident.** Math content, lesson wording and
   Mastery Coin ids (`m<module>.<part>.<n>`) only change when the task says so.
2. **Notation:** inner product `$\langle a, b \rangle$`, length `$\lVert a \rVert$`.
   Vectors are rows; a matrix is a stack of row vectors. In Roblox-style 3D, y is up.
3. **Committed notebooks carry no outputs.** Kids predict before they run.
   `make strip` removes outputs; never let Quarto execute `notebooks/` in place.
4. **`python/src/vecdraw/__init__.py` is read by 10-year-olds.** No decorators,
   comprehensions, lambdas or type tricks in the drawing functions; plain loops,
   plain names, a comment per idea. Don't add `__all__`.
5. **In the explorer, blue and orange mean only the sign of the inner product.**
6. **Ask the user first** before pushing, creating or changing remotes, publishing
   anything (site, package), changing licenses, or rewriting pushed history.
7. **Every file carries the copyright notice and its license line** (`make copyright`).
8. **Small commits, one concern each.** Run `make check` before committing.

## Commands

`make` lists every target. The ones you need most:

| Command | What it does |
| --- | --- |
| `make setup` | Create `.venv/`, `node_modules/`, `.tools/` (Quarto, TinyTeX) and build the explorer. Idempotent. |
| `make check` | **Everything that can fail.** Run before every commit (~80 s, needs Chrome). |
| `make test` | Unit and browser tests only: `test-python`, `test-tools`, `test-explorer`, `test-e2e`. |
| `make explorer` | Typecheck and build the explorer; copies the IIFE into `python/`. |
| `make notebooks` | Execute every notebook (nothing written back). |
| `make stage` / `make site` / `make teacher` / `make pdf` | Stage executed copies in `.build/site/`, render `_site/`, `_site-teacher/`, PDFs. |
| `make preview` / `make preview-teacher` | Quarto preview of the staged copy. |
| `make colab` | Zip the student notebooks into `dist/colab/`. |
| `make sync-setup` | Write `course.toml` into every setup cell and the Prosperity license. |
| `make strip` | Remove notebook outputs (and fix `---` rules Quarto misreads). |
| `make copyright` | Add or correct copyright and license lines in every file. |
| `make test-site` | Smoke-test the rendered sites (after `make site teacher`). |
| `make clean` / `make distclean` | Remove build output / also `.venv`, `node_modules`, `.tools`. |
| `make help` | List the targets. |

`make check` runs, in order: `check-copyright`, `check-agents`, `check-gitignore`,
`check-security`, `check-clean`, `check-setup`, `check-coins`, `check-latex`,
`check-static`, `test-python`, `test-tools`, `test-explorer`, `test-e2e`,
`site`, `teacher`, `test-site`, then `check-clean` again. Other targets:
`setup-python`, `setup-node`, `setup-quarto`, `audit` (= `check-security`).

Use the repo's tools, not system ones: `.venv/bin/python`, `npm -w explorer`,
`.tools/quarto/bin/quarto`. The Makefile sets `QUARTO_PYTHON` and puts TinyTeX first on `PATH`.

## Map

### Top level

| Path | What it is |
| --- | --- |
| `notebooks/` | **Source of truth for the course.** `NN_<name>.ipynb` student notebooks (`00`–`04`), `NN_teacher_guide.ipynb` teacher guides (only `00` so far). License CC BY-NC-SA 4.0. |
| `python/` | The `vecdraw` package (pip-installable; Colab installs it from git). |
| `explorer/` | The Angle Explorer: strict TypeScript, ES modules, no framework. |
| `tools/` | Checks and build helpers, run through `make`. |
| `docs/` | `docs/PLAN.md`: the original restructuring plan and its deviations (history). |
| `course.toml` | The one course-wide setting: repository URL and ref Colab installs from. |
| `Makefile` | The single entry point. |
| `_quarto.yml` | Shared Quarto settings; **holds no file lists** (profiles append to lists). |
| `_quarto-student.yml` | Default profile `student`: student site → `_site/`, never teacher guides. |
| `_quarto-teacher.yml` | Profile `teacher`: teacher guides → `_site-teacher/`. |
| `index.qmd`, `angle-explorer.qmd`, `teacher.qmd` | Site pages (CC BY-NC-SA 4.0). `index.qmd` builds the notebook table and Colab links from `course.toml`. |
| `package.json`, `package-lock.json` | npm workspace root (`explorer` + KaTeX/markdown-it for the LaTeX check). |
| `requirements.txt` | Python libraries to run the notebooks (kept equal to `python/pyproject.toml` by a test). |
| `requirements-dev.txt` | `requirements.txt` plus test and notebook tools (installed by `make setup`). |
| `.nvmrc` | Recommended Node version (26). |
| `.gitignore` | Curated; tested by `tools/check_gitignore.py`. No end-of-line comments. |
| `README.md` | For anyone opening the repo: what it is, quick start, requirements, licenses. |
| `maintainer.readme.md` | The human maintainer's manual: add, change, build, deploy, troubleshoot. |
| `SECURITY.md` | Security record: every finding (SEC-NNN) and how we monitor. |
| `AGENTS.md` | This file. `CLAUDE.md` only imports it. |
| `LICENSE.md` | Which license covers what. `LICENSES/` holds the texts (never edit by hand). |

Generated and ignored (never commit): `.venv/`, `node_modules/`, `.tools/`,
`.build/`, `_site/`, `_site-teacher/`, `dist/`, `explorer/dist/`, caches.

### `python/` (vecdraw)

| Path | What it is |
| --- | --- |
| `src/vecdraw/__init__.py` | The drawing library kids read (`new_grid`, `draw_vector`, `draw_path`, `draw_point`, `draw_dots`, `draw_skewed_grid`, `draw_digit`, `angle_between`, `show`, `COLORS`). |
| `src/vecdraw/explore.py` | `explore_angles(*vectors, names=None)`: displays an object whose mimebundle has `text/html` (embedded explorer) and `image/png` (matplotlib fallback for PDF). |
| `src/vecdraw/static/angle-explorer.iife.js` | **Generated** by `make explorer`; committed so `pip install git+…` needs no Node. `check-static` compares it with a fresh build. |
| `pyproject.toml`, `LICENSE.md`, `README.md`, `tests/` | Packaging (hatchling), license copy shipped in the wheel (synced), tests. |

### `explorer/` (Angle Explorer)

| Path | What it is |
| --- | --- |
| `src/math.ts` | Pure vector math: inner product, length, normalized value, signed angle, turn direction. |
| `src/format.ts`, `src/state.ts`, `src/hit.ts`, `src/geometry.ts`, `src/numpy.ts` | Formatting and `esc()`, state and every user action, pointer hit tests, SVG coordinates, "Copy as NumPy". All pure and unit-tested (`*.test.ts`). |
| `src/render/` | HTML/SVG string builders for the plot, readout, curve and tables. Escape every caller-supplied string. |
| `src/ui/` | `styles.css` (in the shadow root), `template.ts` (markup), `fonts.ts` (inlined OFL fonts). |
| `src/mount.ts` | `mountAngleExplorer(element, options)`: Shadow DOM, events, Spin animation, focus handling. |
| `src/index.ts`, `src/standalone.ts`, `src/copyright.ts`, `src/env.d.ts` | Library exports, standalone page entry, notice/license constants, Vite types. |
| `reference/angle-explorer.original.html` | The original page: the pixel-parity baseline. |
| `e2e/`, `e2e-site/` | Playwright tests (explorer; rendered site) using the installed Chrome. |
| `scripts/` | `postbuild.mjs` (names outputs, copies the IIFE to `python/`), `serve.mjs` (static server for site tests). |
| `index.html`, `vite.config.ts`, `tsconfig*.json`, `playwright*.config.ts`, `package.json`, `THIRD_PARTY_NOTICES.md` | Build and test configuration; font credits. |

Builds (`explorer/dist/`, ignored): `standalone/angle-explorer.html` (everything
inlined), `lib/angle-explorer.js` (ES module), `lib/angle-explorer.iife.js`, `types/`.

### `tools/`

| Script | What it does | Make target |
| --- | --- | --- |
| `nbutil.py` | Shared helpers: load/save notebooks in Jupyter's format, list student/teacher notebooks. | – |
| `run_notebooks.py` | Execute notebooks; teacher guides must print "All N checks passed."; `--write DIR` saves executed copies. | `notebooks` |
| `stage_site.py` | Copy the Quarto project to `.build/site/` and execute the notebooks there. | `stage` |
| `check_clean.py` | No outputs in notebooks; `---` rules followed by a blank line (`--fix`). | `check-clean`, `strip` |
| `check_coins.py` | Each Mastery Coin has exactly one answer-key row, and the reverse. | `check-coins` |
| `check_latex.mjs` | Every `$…$`/`$$…$$` parses with KaTeX (strict). | `check-latex` |
| `sync_setup.py` | Write the setup cells from `course.toml` (`--check`). | `sync-setup`, `check-setup` |
| `copyright.py` | Copyright + SPDX license line in every file; syncs license copies with `course.toml`. | `copyright`, `check-copyright` |
| `check_gitignore.py` | Junk is ignored, source is not, nothing committed is ignored. | `check-gitignore` |
| `check_security.py` | `npm audit` + `pip-audit` advisories must all be tracked in `SECURITY.md`. | `check-security` |
| `check_agents.py` | This file mentions every top-level entry, tool script and `make` target. | `check-agents` |
| `bundle_colab.py` | Student notebooks → `dist/colab/admath-notebooks.zip`. | `colab` |
| `install_quarto.sh`, `install_tinytex.sh` | Pinned Quarto and TinyTeX into `.tools/`. | `setup-quarto` |
| `tests/` | pytest for the tools: every check must fail when it should. | `test-tools` |

## How the pieces connect

- **`course.toml` → everything that names the repository.** `make sync-setup`
  writes the URL and ref into each student notebook's setup cell and into the
  Prosperity license's "Source Code:" line; `index.qmd` builds Colab links from it.
- **Explorer → Python.** `make explorer` builds `explorer/dist/lib/angle-explorer.iife.js`
  and copies it into `python/src/vecdraw/static/`. `explore_angles` embeds that
  file in notebook outputs. Commit the copy with the explorer change (`check-static`).
- **Notebooks → site.** `tools/stage_site.py` copies the project into `.build/site/`
  and executes the notebooks there; Quarto renders that copy, and `make site`
  moves `_site/` back. The sources are never executed in place.
- **Setup cell in Colab:** `%pip install "vecdraw @ git+<url>@<ref>#subdirectory=python"`.
  Locally it puts `python/src` on `sys.path` instead.

## Where to make common changes

| Task | Where | Then |
| --- | --- | --- |
| Edit a lesson | `notebooks/NN_*.ipynb` | `make strip && make check` |
| Add a module | New `notebooks/NN_name.ipynb` + `NN_teacher_guide.ipynb` (maintainer guide §5) | `make sync-setup && make check` |
| Change drawing functions | `python/src/vecdraw/__init__.py` (rule 4) | `make test-python` |
| Change the explorer | `explorer/src/…`; math in `math.ts` with tests | `make explorer`, commit the `python/…/static` copy |
| Change site layout or footers | `_quarto.yml`, profiles, `*.qmd` | `make site teacher test-site` |
| New dependency | `python/pyproject.toml` **and** `requirements.txt`, or `explorer/package.json` (exact version) | `make check` |
| New file type or folder | Add a rule in `tools/copyright.py`; add paths to `tools/check_gitignore.py` lists | `make check` |
| Security finding | New `SEC-NNN` entry in `SECURITY.md` | `make check-security` |

## Gotchas (learned the hard way)

- **Quarto writes outputs back into an `.ipynb` it executes.** Hence the staging;
  don't add `execute: enabled: true` to `_quarto.yml`.
- **Quarto profiles append to the base config's lists.** Keep file lists in the profiles only.
- **Quarto rewrote `<table>` markup inside the explorer's embedded `<script>`.**
  `html-table-processing: none` in `_quarto.yml` prevents it; `make test-site` catches it.
- **A markdown cell starting with `---` followed by text is read as YAML** by Pandoc. `make strip` adds the blank line.
- **The minifier drops `/*!` banners;** the explorer uses Rolldown's `postBanner`.
- **Imports in `explorer/vite.config.ts` need their file extension** (`./src/copyright.ts`);
  Vite's coming native config loader rejects extensionless ones.
- **`.gitignore` has no end-of-line comments**: a `#` after a pattern becomes part of it.
- **Shell pipelines in the Makefile run with `pipefail`;** don't add a blanket `|| true` (it hid failures once).
- **Kernels use TCP on 127.0.0.1;** IPC fails on paths longer than 108 characters (SECURITY.md SEC-009).
- **The system TeX Live may be unable to load fonts in LuaLaTeX;** PDFs use TinyTeX in `.tools/`.
- **The parity e2e test is skipped offline** (the reference page loads Google Fonts).

## Keep this file up to date

AGENTS.md is part of the code. **In the same commit** as the change:

- Add, move, rename or remove a top-level file or folder, an `explorer/` or
  `python/` module, or a `tools/` script → update the map.
- Add or change a `make` target or what `make check` runs → update "Commands".
- Learn something that cost you time → add it to "Gotchas".
- Change a rule or convention (only when the user asks) → update the rules.
- Find a security problem → add it to `SECURITY.md`, not here.

`make check-agents` (part of `make check`) fails when a top-level entry, a
`tools/` script or a `make` target is not mentioned in this file. It can't check
that descriptions are still true: read the section you touched before committing.
