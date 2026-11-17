# Maintainer guide

How to add, change, build and deploy the course. The kids never see this.
For the reasons behind the layout, see [`docs/PLAN.md`](docs/PLAN.md).

- [1. The map](#1-the-map)
- [2. First-time setup](#2-first-time-setup)
- [3. Everyday commands](#3-everyday-commands)
- [4. Edit a notebook](#4-edit-a-notebook)
- [5. Add a module](#5-add-a-module)
- [6. Change the vecdraw library](#6-change-the-vecdraw-library)
- [7. Change the Angle Explorer](#7-change-the-angle-explorer)
- [8. Publish the repository (Colab installs from it)](#8-publish-the-repository-colab-installs-from-it)
- [9. Deploy the site](#9-deploy-the-site)
- [10. Give notebooks to the kids](#10-give-notebooks-to-the-kids)
- [11. Upgrade the tools](#11-upgrade-the-tools)
- [12. When something breaks](#12-when-something-breaks)

## 1. The map

```
linalg-circle/
├── Makefile                  the only entry point: `make` lists every target
├── course.toml               repository URL + ref; copied into every setup cell
├── notebooks/                SOURCE OF TRUTH. Committed without outputs.
│   ├── 00_vectors_and_inner_product.ipynb     student notebook (module 0)
│   ├── 00_teacher_guide.ipynb                 teacher guide (module 0)
│   └── 01_… 04_…                              older modules (not yet in the Module 0 format)
├── python/                   the vecdraw package (pip-installable)
│   ├── src/vecdraw/__init__.py    the drawing code kids read. Keep it simple.
│   ├── src/vecdraw/explore.py     explore_angles(): notebook → explorer
│   ├── src/vecdraw/static/        GENERATED explorer bundle (committed; do not edit)
│   └── tests/
├── explorer/                 the Angle Explorer (TypeScript, no framework)
│   ├── src/math.ts …              pure math, state, formatting (unit-tested)
│   ├── src/render/, src/ui/       HTML/SVG builders, styles, template
│   ├── src/mount.ts               mountAngleExplorer(element, options)
│   ├── reference/                 the original single-file page (parity baseline)
│   ├── e2e/, e2e-site/            Playwright tests (explorer; rendered site)
│   └── dist/                      build output (git-ignored)
├── tools/                    checks + build helpers (Python stdlib + nbclient; one Node script)
├── _quarto.yml               shared Quarto settings
├── _quarto-student.yml       profile "student" (default) → _site/
├── _quarto-teacher.yml       profile "teacher"           → _site-teacher/
├── index.qmd, angle-explorer.qmd, teacher.qmd             site pages
└── .venv/ node_modules/ .tools/ .build/ _site*/ dist/     all git-ignored, all re-creatable
```

**Rules that never bend**

- Committed notebooks carry **no outputs**. Kids predict before they run.
- Don't change the math content, the lesson wording or any coin id without
  meaning to. `make check` catches broken coins, but not changed wording.
- Notation: inner product `$\langle a, b \rangle$`, length `$\lVert a \rVert$`.
  Vectors are rows; a matrix is a stack of row vectors. In Roblox-style 3D, y is up.
- Blue and orange in the explorer mean **only** the sign of the inner product.

## 2. First-time setup

Prerequisites: `uv` (<https://docs.astral.sh/uv/>), Node.js ≥ 22.12 (26 LTS
recommended: `nvm use` reads `.nvmrc`), Google Chrome, `make`, `curl`, `git`.

```bash
make setup
```

This creates `.venv/` (Python with `vecdraw` installed in editable mode, plus
Jupyter tools and a `python3` kernel), runs `npm ci`, downloads Quarto and
TinyTeX into `.tools/`, and builds the explorer. Nothing is installed
system-wide. Run it again any time; finished steps are skipped.

The first PDF render downloads a few extra LaTeX packages into `.tools/TinyTeX`.

To open the notebooks locally: `.venv/bin/jupyter lab notebooks/` (install with
`uv pip install --python .venv/bin/python jupyterlab` if you want it). Choose
the kernel "Python 3 (linalg-circle .venv)". The setup cell finds `python/src`
by itself.

## 3. Everyday commands

| Command | What it does |
| --- | --- |
| `make check` | **Run before every commit.** Every check, every test, both sites (about 1.5 minutes). |
| `make preview` | Student site in the browser (from a staged copy, see §12). |
| `make strip` | Remove outputs from notebooks (and fix `---` rules Quarto would misread). |
| `make notebooks` | Execute every notebook top to bottom. |
| `make site` / `make teacher` | Render `_site/` / `_site-teacher/`. |
| `make explorer` | Rebuild the explorer (and the copy in `python/`). |
| `make test` | Unit and browser tests only (no notebooks, no Quarto). |
| `make colab` | Zip the student notebooks into `dist/colab/`. |

What `make check` runs, in order:

1. `check-clean`: no outputs or execution counts in any notebook.
2. `check-setup`: every setup cell matches `course.toml`.
3. `check-coins`: every Mastery Coin has exactly one answer-key row, and the reverse.
4. `check-latex`: every `$…$` and `$$…$$` parses with KaTeX (strict).
5. `check-static`: the explorer bundle committed in `python/` matches a fresh build.
6. Tests: pytest (`python/`, `tools/tests`), Vitest (explorer math and state), and
   Playwright (pixel parity with the original page, behaviour, the Python embed).
7. `site` and `teacher`: executes every notebook. Each teacher guide's "Check
   the key" cell must print `All N checks passed.`. Then renders HTML and PDF.
8. `test-site`: the explorer mounts on the site, KaTeX has no errors, PDFs are
   linked, and no teacher guide is in `_site/`.
9. `check-clean` again: proves the build did not touch the sources.

## 4. Edit a notebook

1. Open it in Jupyter or VS Code with the `.venv` kernel. Run cells as much as you like.
2. Before committing: `make strip`, then `make check`.
3. Commit. Don't commit with outputs: `check-clean` will fail.

Things the checks enforce, so you don't have to remember them:

- **Mastery Coins.** A coin is defined in the student notebook by its bold id,
  `- **m0.4.10** question…`. Each id appears in bold exactly once, and the
  module number matches the file's prefix. The teacher guide answers it in a
  table row that starts with the id: `| m0.4.10 | answer |`.
- **Math.** Inside a Markdown table, inline math must not contain `|` (it splits
  the cell): write `\lvert`/`\rVert` instead. A lone `$` (money) is reported.
- **Horizontal rules.** A markdown cell that starts with `---` needs a blank line
  after it. Without one, Quarto reads the cell as YAML. `make strip` adds it.

To use the explorer in a lesson, add a code cell such as:

```python
explore_angles(a, b, c)                    # names a, b, c
explore_angles(a, b, names=["u", "w"])     # your own names (1 to 8 characters)
explore_angles(M)                          # each ROW of the matrix M is a vector
```

It takes 2 to 8 vectors, each with 2 numbers between −8 and 8, and shows a
static picture in PDFs. Today it appears only on the site's `angle-explorer.qmd`
page; no lesson calls it yet.

## 5. Add a module

1. **Student notebook:** `notebooks/05_short_name.ipynb`. The two-digit prefix is
   the module number used by the coin check and the site order.
2. **Setup cells:** copy the three cells right after the title of
   `00_vectors_and_inner_product.ipynb` (the "**Setup.**" markdown, the setup
   code cell, and the import cell that starts `import numpy as np`). Then run
   `make sync-setup`. The code cell is generated, so don't edit it by hand.
3. **Coins:** ids `m5.<part>.<n>` in bold.
4. **Teacher guide:** `notebooks/05_teacher_guide.ipynb` (the name must contain
   `teacher` and share the prefix). Give it an answer-key table with one row per
   coin, and a "## Check the key" heading followed by a code cell that ends with
   `print("All", checked, "checks passed.")`. Copy the pattern from the
   `00` guide.
5. `make strip && make check`. The site's sidebar and front page pick the
   notebook up automatically, and the teacher guide goes only to `_site-teacher/`.

Converting `01`–`04` to the Module 0 format is the same procedure: once a
notebook has bold coin ids, the coin check requires its teacher guide.

## 6. Change the vecdraw library

`python/src/vecdraw/__init__.py` is read by 10-year-olds. Keep it that way:

- No decorators, comprehensions, lambdas, `*args` tricks or clever typing in
  the drawing functions. Plain loops, plain names, a comment per idea.
- Don't add `__all__`: `from vecdraw import *` must keep exporting `np`, `plt`
  and the shared `COLORS` list. Deep 6 asks kids to run `COLORS[0] = "black"`,
  and the tests check that this still works.
- Keep the function names: notebooks use them, and some print their source
  with `inspect.getsource`.

Then:

```bash
make test-python          # quick
make check                # before committing
```

**How the change reaches Colab.** Colab installs from git at the `ref` in
`course.toml`. A change is live for kids once it is pushed to that branch, or
once you move `ref` to a new tag and `make sync-setup`. A Colab session that
already installed vecdraw keeps the old one until *Runtime → Restart session*.
Bump `version` in `python/pyproject.toml` when you tag.

## 7. Change the Angle Explorer

```bash
npm run dev -w explorer          # live dev server for the standalone page
npm run test -w explorer         # unit tests (math, state, rendering)
make test-e2e                    # browser tests (builds first)
make explorer                    # build; also refreshes python/src/vecdraw/static/
```

- **Math** lives in `src/math.ts` as pure functions. `math.test.ts` compares it with
  the original page's formulas on thousands of pairs. If you change a threshold
  on purpose, update the oracle in that test.
- **Look.** `e2e/parity.spec.ts` compares screenshots with
  `reference/angle-explorer.original.html` (light, dark, 1200 px and 390 px wide).
  For an intentional design change, update the reference page in the same
  commit, or relax that test with a note saying why. The parity test is
  skipped (not failed) without internet, because the original page loads Google Fonts.
- **Escaping.** Anything that ends up in `innerHTML` and comes from the caller
  (vector names) goes through `esc()`. `render.test.ts` checks every view.
- **Python's copy.** After `make explorer`, commit
  `python/src/vecdraw/static/angle-explorer.iife.js` with your change.
  `check-static` fails until the committed or staged copy matches a fresh build.
  It is committed so `pip install git+…` works without Node.

Embedding elsewhere:

```js
import { mountAngleExplorer } from "./angle-explorer.js";   // dist/lib/
const h = mountAngleExplorer(document.querySelector("#here"), {
  vectors: [[4, 0], [3, 3]], names: ["a", "b"],
  first: 0, second: 1, snap: true, mode: "norm",   // all optional
  theme: "auto",      // or "light" / "dark"
  header: true,       // title and intro line
});
h.getVectors(); h.toNumpy(); h.destroy();
```

## 8. Publish the repository (Colab installs from it)

Colab runs `pip install "vecdraw @ git+<url>@<ref>#subdirectory=python"`, so the
repository must be on GitHub (or any public git host) and **public**. Until
then, the setup cell stops in Colab with "The course repository URL is not set
yet. Ask your teacher." Locally everything works without a remote.

One-time steps:

```bash
# 1. On GitHub: create an empty PUBLIC repository, e.g. <you>/linalg-circle
#    (no README, no license, no .gitignore: this repo has its own).
# 2. Point this repo at it and push:
git remote add origin git@github.com:<you>/linalg-circle.git
git push -u origin main
# 3. Put the URL in course.toml:  url = "https://github.com/<you>/linalg-circle"
make sync-setup          # writes it into every setup cell
make check
git commit -am "course.toml: set repository URL"
git push
```

Then try it in Colab (see §10). For a term, pin a tag so the library can't
change under the kids: `git tag v0.4.0 && git push --tags`, set
`ref = "v0.4.0"` in `course.toml`, then `make sync-setup`, commit and push.

**Licensing.** No license file has been added; that is your decision. The
explorer bundles two OFL-licensed fonts, credited in
`explorer/THIRD_PARTY_NOTICES.md`.

**This folder sits inside another repository** (`CAeHius`), which sees it as an
untracked folder. Add `math/linalg-circle/` to that repository's `.gitignore`
(or make it a submodule) so it is not committed twice.

## 9. Deploy the site

`make site` produces a self-contained static site in `_site/` (HTML, plus a PDF
per notebook). Any static host works: upload the folder.

GitHub Pages from a `gh-pages` branch, by hand:

```bash
make site
git worktree add --orphan -b gh-pages ../linalg-circle-pages   # first time only
# later times: git worktree add ../linalg-circle-pages gh-pages
rsync -a --delete --exclude .git _site/ ../linalg-circle-pages/
touch ../linalg-circle-pages/.nojekyll
git -C ../linalg-circle-pages add -A
git -C ../linalg-circle-pages commit -m "Publish site"
git -C ../linalg-circle-pages push origin gh-pages
git worktree remove ../linalg-circle-pages
```

Then, in the GitHub repository: *Settings → Pages → Deploy from branch → gh-pages*.

**Never upload `_site-teacher/` to the public host.** Share the teacher guides
privately: the PDFs in `_site-teacher/notebooks/`, or a password-protected host.

## 10. Give notebooks to the kids

- **From GitHub (best):** the site's front page has an "Open in Colab" link per
  notebook once `course.toml` has a real GitHub URL. Each kid gets a fresh copy;
  *File → Save a copy in Drive* keeps their work.
- **As files:** `make colab`, then share `dist/colab/linalg-circle-notebooks.zip`.
  In Colab: *File → Upload notebook*.

**What to try in Colab** after publishing (none of this can be tested from
this machine):

1. Open `00_vectors_and_inner_product.ipynb` from GitHub in Colab. Run the
   setup cell: it should install quietly (about 10–20 s) and finish without
   errors. The note "you may need to restart the kernel" can be ignored on the
   first run.
2. Run the import cell, then the first drawing cell (`new_grid(6)` …): a grid with arrows.
3. Run the "Look inside the library" cell: the source of `angle_between` prints.
4. In a new cell: `explore_angles(np.array([4, 0]), np.array([3, 3]))`. The explorer
   appears. Check that you can drag a tip, Spin works, and the theme follows
   your system's dark/light setting.
5. Press **Copy as NumPy** and paste into a new cell. If the message says to select
   and copy by hand, Colab blocked the clipboard: copying from the box should work.
6. Deep 6: `COLORS[0] = "black"`, then redraw the angle gallery; arrow `a` turns black.
7. Run the setup cell again: it should skip the install and be instant.
8. *Runtime → Restart session*, then run the setup and import cells again. Everything works.

## 11. Upgrade the tools

Every version is pinned in one place:

| Tool | Where |
| --- | --- |
| Node (recommended) | `.nvmrc` (26); minimum in `package.json` `engines` |
| TypeScript, Vite, Vitest, Playwright, fonts | `explorer/package.json` (exact versions) |
| KaTeX, markdown-it | `package.json` |
| Quarto | `tools/install_quarto.sh` (`QUARTO_VERSION`) |
| TinyTeX | `tools/install_tinytex.sh` (`TINYTEX_VERSION`) |
| Python test and notebook tools | `requirements-dev.txt` |
| vecdraw's runtime dependencies | `python/pyproject.toml` (keep the minimums low: Colab decides numpy) |

Check what's current with `npm outdated`, <https://quarto.org/docs/download/>,
and <https://github.com/rstudio/tinytex-releases/releases>. Upgrade one tool at
a time, then run `make check`. A Quarto upgrade is the riskiest: re-check the PDF
and the explorer page by eye.

## 12. When something breaks

**"Why does `make site` copy everything to `.build/site/`?"** When Quarto
executes an `.ipynb`, it writes the outputs back into the file. So Quarto never
executes `notebooks/`: `tools/stage_site.py` executes copies, and Quarto renders
those. Don't add `execute: enabled: true` to `_quarto.yml`. A plain
`quarto render` in the repo root is safe; it just shows no outputs. For the same
reason `make preview` previews the staged copy: after editing a notebook,
stop it and run `make preview` again.

**`check-clean` fails.** Someone committed or saved outputs. `make strip`.

**`check-setup` fails.** `course.toml` changed, or a setup cell was edited by hand.
`make sync-setup`.

**`check-static` fails.** The explorer changed but its copy in `python/` was not
committed. `make explorer`, then `git add python/src/vecdraw/static/`.

**`check-coins` fails.** The message names the coin and the file. Usually a
missing or duplicated answer-key row, or a coin id typo.

**A notebook fails to execute.** `make notebooks` prints the cell and the error.
Notebooks run with `notebooks/` as the working folder, like Jupyter.

**The explorer is blank on the site.** Run `make test-site`. If Quarto has
started rewriting the embedded script again, look for a Quarto HTML
post-processing feature (as `html-table-processing` was) and switch it off in
`_quarto.yml`.

**PDF build fails with a LaTeX error.** The log is in `.build/site/`. Missing
LaTeX packages are fetched automatically by TinyTeX's `tlmgr`, which needs a
network connection the first time.

**"Kernel is running over TCP without encryption."** Harmless: the kernel listens
on 127.0.0.1 only, and `make` hides this line. (IPC sockets would avoid it, but
socket paths are limited to 108 characters and deep checkouts exceed that.)

**Parity test skipped.** No internet, so the original page could not load its
Google Fonts. Run it again online.
