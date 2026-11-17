# Restructuring plan (2026-11-16)

Written before the restructure so the final report can say how closely the work
followed it. Deviations are recorded at the bottom as they happen.

## Layout

```
linalg-circle/
  course.toml                 one config: repo URL, git ref (feeds every setup cell)
  Makefile                    single entry point
  package.json                npm workspace root (explorer + node tools)
  _quarto.yml                 website + per-page PDF, student notebooks only
  _quarto-teacher.yml         profile "teacher": teacher guides -> _site-teacher/
  index.qmd, angle-explorer.qmd
  notebooks/                  .ipynb sources of truth, committed without outputs
  python/                     installable package `vecdraw`
    pyproject.toml            hatchling, numpy + matplotlib (+ ipython optional)
    src/vecdraw/__init__.py   the kid-readable drawing code (was vecdraw.py)
    src/vecdraw/explore.py    explore_angles(): notebook -> explorer bridge
    src/vecdraw/static/       built explorer (generated, committed, checked for staleness)
    tests/
  explorer/                   TypeScript library, no framework
    src/math.ts ...           pure vector math + formatting, unit-tested
    src/ui/...                render modules, mount, styles (Shadow DOM)
    reference/                the original single-file page, for parity checks
    e2e/                      Playwright tests against installed Chrome
  tools/                      checks: latex, coins, clean outputs, run notebooks,
                              sync setup cells, colab bundle
  docs/
```

## Tool choices (versions checked 2026-11-16 against npm / nodejs.org / quarto.org)

- Node 26 LTS pinned in `.nvmrc`; engines `>=22.12` (Vite 8 floor; local box has 22.22).
- TypeScript 7.0.2 strict, typecheck only (`tsc --noEmit`); Vite 8.3 builds; Vitest 5.1.
- Builds: `vite-plugin-singlefile` for the standalone HTML; Vite library mode for
  ES module + IIFE (the IIFE is what Python embeds, since notebook frontends run
  classic `<script>` most reliably).
- Fonts (OFL) bundled via @fontsource so "self-contained" really is offline.
- Python: uv-managed `.venv`, hatchling package, pytest, nbclient for execution.
- Quarto 1.11.x; installed to `.tools/` by `make setup` if not on PATH.
  PDF via LuaLaTeX (installed) rather than Quarto's default XeLaTeX.
- KaTeX check kept (rewritten, no HTML side files); site uses `html-math-method: katex`
  so the checked engine is the published engine; PDF build checks real LaTeX.

## Decisions

1. Setup cell: Colab -> `pip install git+<repo>@<ref>#subdirectory=python`;
   elsewhere -> import installed package, else add `../python/src` to `sys.path`.
   URL lives in `course.toml`; `tools/sync_setup.py` stamps it into every notebook;
   `make check` fails if a notebook is out of sync. Placeholder URL fails loudly in Colab.
2. Only the two setup cells change in 01-04 (the markdown line saying "the next cell is
   the library" and the `%%writefile` cell). The import cell stays byte-identical.
3. "Look inside the library": `inspect.getsource` works unchanged on an installed package.
   "Change the library" (Deep 6): edit `COLORS[0]` live instead of editing a file cell.
   Minimal wording change, reported.
4. Explorer mounts into a Shadow DOM so its CSS and ids cannot collide with Jupyter,
   Colab or Quarto, and several explorers can share a page.
5. `explore_angles` displays an object whose mimebundle has `text/html` and `image/png`
   (matplotlib). HTML frontends take the HTML; PDF takes the PNG.
6. "Copy as NumPy" writes ASCII code (the readout uses U+2212 minus; code must not),
   with a visible, selectable text box when the clipboard API is blocked.
7. No lesson gets a new `explore_angles` call; a separate site page demonstrates it.
8. Order of work: baseline -> python pkg -> explorer math -> explorer UI/builds ->
   e2e/parity -> Copy as NumPy -> explore_angles -> notebooks -> checks -> Quarto ->
   Makefile -> docs (README, maintainer.readme.md last).

## Deviations

(filled in as work proceeds)
