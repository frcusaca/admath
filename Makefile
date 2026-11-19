# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
# admath: one entry point for everything. `make` lists the targets.
#
# Tools live inside the repo: .venv/ (Python), node_modules/, .tools/quarto,
# .tools/TinyTeX. `make setup` creates them; nothing is installed system-wide.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
MAKEFLAGS += --no-print-directory

ROOT    := $(abspath .)
PY      := $(ROOT)/.venv/bin/python
NPM     := npm
QUARTO  := $(or $(wildcard $(ROOT)/.tools/quarto/bin/quarto),$(shell command -v quarto 2>/dev/null),quarto)
TEXBIN  := $(firstword $(wildcard $(ROOT)/.tools/TinyTeX/bin/*))

# Quarto must execute notebooks with this repo's Python and find TinyTeX first.
export QUARTO_PYTHON := $(PY)
export PATH := $(if $(TEXBIN),$(TEXBIN):)$(PATH)
export MPLBACKEND := Agg

NOTEBOOKS := $(wildcard notebooks/[0-9]*_*.ipynb)
IIFE      := explorer/dist/lib/angle-explorer.iife.js
STATIC    := python/src/vecdraw/static/angle-explorer.iife.js
# the kernel's harmless "running over TCP" warning (it binds to 127.0.0.1 only)
QUIET     := { grep -v --line-buffered "Kernel is running over TCP" || true; }

.PHONY: help setup setup-python setup-node setup-quarto \
        explorer test test-python test-tools test-explorer test-e2e test-site \
        notebooks check-static check-clean check-setup check-coins check-your-turn check-latex check-copyright check-agents check-gitignore check-security audit copyright \
        stage site teacher pdf preview preview-teacher colab sync-setup strip check clean distclean

help: ## Show this list
	@grep -hE '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/^([a-zA-Z0-9_-]+):.*## (.*)$$/  make \1|\2/' | awk -F'|' '{printf "%-24s %s\n", $$1, $$2}'

# ---- setup ---------------------------------------------------------------

setup: setup-python setup-node setup-quarto explorer ## Create .venv, node_modules and .tools, then build the explorer

setup-python: ## Python venv with the package (editable), Jupyter tools and a kernel
	@command -v uv >/dev/null || { echo "Install uv first: https://docs.astral.sh/uv/"; exit 1; }
	uv venv --allow-existing .venv
	uv pip install --python $(PY) -r requirements-dev.txt
	$(PY) -m ipykernel install --sys-prefix --name python3 --display-name "Python 3 (admath .venv)" >/dev/null

setup-node: ## npm workspaces (explorer + node tools); Chrome must be installed for the browser tests
	$(NPM) ci

setup-quarto: ## Quarto 1.11.9 and TinyTeX into .tools/
	./tools/install_quarto.sh
	./tools/install_tinytex.sh

# ---- build ---------------------------------------------------------------

explorer: ## Typecheck and build the explorer (standalone HTML, ES module, IIFE copied into python/)
	$(NPM) run build -w explorer

# ---- tests ---------------------------------------------------------------

test: test-python test-tools test-explorer test-e2e ## All unit and browser tests

test-python: ## pytest for the vecdraw package
	$(PY) -m pytest -q python

test-tools: ## pytest for the check scripts (each check must fail when it should)
	$(PY) -m pytest -q tools/tests

test-explorer: ## Vitest unit tests for the explorer's math and state
	$(NPM) run test -w explorer

test-e2e: explorer ## Playwright: parity with the original page, behaviour, the Python embed
	$(NPM) run test:e2e -w explorer

test-site: ## Playwright smoke tests of the rendered sites (needs `make site teacher`)
	$(NPM) run test:site -w explorer

# ---- notebook checks -------------------------------------------------------

notebooks: ## Execute every notebook end to end; teacher guides must pass "Check the key"
	cd tools && $(PY) run_notebooks.py 2>&1 | $(QUIET)

check-static: explorer ## The explorer copy committed in python/ matches a fresh build
	@git show :$(STATIC) 2>/dev/null | cmp -s - $(IIFE) || { \
	  echo "FAIL: $(STATIC) in git differs from a fresh build. Stage or commit the rebuilt file."; exit 1; }
	@echo "static: $(STATIC) is up to date"

check-clean: ## Notebooks have no outputs and nothing Quarto would misread
	cd tools && $(PY) check_clean.py

check-setup: ## Every setup cell and navigation strip matches course.toml
	cd tools && $(PY) sync_setup.py --check

check-coins: ## Every Mastery Coin has exactly one answer-key row, and the reverse
	cd tools && $(PY) check_coins.py

check-your-turn: ## Every "Your turn" has a workspace cell; every %%your_turn cell is named and safe
	cd tools && $(PY) check_your_turn.py

check-copyright: ## Every file carries the copyright notice and its license
	$(PY) tools/copyright.py

check-gitignore: ## .gitignore ignores junk (caches, venvs, builds) and never hides source
	$(PY) tools/check_gitignore.py

check-agents: ## AGENTS.md mentions every top-level entry, tool script and make target
	$(PY) tools/check_agents.py

check-security: ## Every dependency advisory (npm audit, pip-audit) is tracked in SECURITY.md
	$(PY) tools/check_security.py

audit: check-security ## Same as check-security

check-latex: ## Every $...$ and $$...$$ parses with KaTeX; no dot or cross for multiplication
	node tools/check_latex.mjs $(NOTEBOOKS)

# ---- render ----------------------------------------------------------------
# Quarto never executes notebooks/ in place (it would write outputs into them).
# `stage` copies the project to .build/site/ with executed notebooks; the
# render targets run Quarto there and move the result to the repo root.

STAGE := .build/site

stage: ## Copy the project to .build/site/ and execute every notebook there
	cd tools && $(PY) stage_site.py 2>&1 | $(QUIET)

site: stage ## Render the student website and its PDFs into _site/
	cd $(STAGE) && $(QUARTO) render 2>&1 | $(QUIET)
	rm -rf _site && mv $(STAGE)/_site _site
	@echo "student site: _site/index.html"

teacher: stage ## Render the teacher guides into _site-teacher/ (never part of _site/)
	cd $(STAGE) && $(QUARTO) render --profile teacher 2>&1 | $(QUIET)
	rm -rf _site-teacher && mv $(STAGE)/_site-teacher _site-teacher
	@echo "teacher site: _site-teacher/index.html"

pdf: stage ## Render only the PDFs (into _site/)
	cd $(STAGE) && $(QUARTO) render --to pdf 2>&1 | $(QUIET)
	mkdir -p _site && cp -R $(STAGE)/_site/. _site/

preview: stage ## Preview the student site (from the staged copy; re-run after editing a notebook)
	cd $(STAGE) && $(QUARTO) preview

preview-teacher: stage ## Preview the teacher site (from the staged copy)
	cd $(STAGE) && $(QUARTO) preview --profile teacher

colab: ## Bundle the student notebooks for Colab into dist/colab/
	cd tools && $(PY) bundle_colab.py

# ---- maintenance -------------------------------------------------------------

sync-setup: ## Copy course.toml into every setup cell, the chapter navigation and the Prosperity license
	cd tools && $(PY) sync_setup.py
	$(PY) tools/copyright.py --fix

copyright: ## Add or correct copyright and license lines; sync license copies
	$(PY) tools/copyright.py --fix

strip: ## Remove outputs (and fix Quarto-unsafe rules) in every notebook
	cd tools && $(PY) check_clean.py --fix

# ---- everything ----------------------------------------------------------------

check: ## Everything that can fail: static checks, all tests, every notebook, both sites
	@$(MAKE) check-copyright check-agents check-gitignore check-security check-clean check-setup check-coins check-your-turn check-latex
	@$(MAKE) check-static
	@$(MAKE) test-python test-tools test-explorer test-e2e
	@$(MAKE) site teacher
	@$(MAKE) test-site
	@$(MAKE) check-clean
	@echo "make check: everything passed"

clean: ## Remove build output (keeps .venv, node_modules, .tools)
	rm -rf _site _site-teacher .build .quarto dist explorer/dist explorer/test-results explorer/playwright-report
	find . -name '*.quarto_ipynb' -not -path './node_modules/*' -delete
	find . -name __pycache__ -not -path './.venv/*' -not -path './node_modules/*' -prune -exec rm -rf {} +

distclean: clean ## Also remove .venv, node_modules and .tools
	rm -rf .venv node_modules .tools
