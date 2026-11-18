<!-- Copyright © 2026-present CAehi.us -->
<!-- SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0 -->
# Security

This file is the project's security record: how to report a problem, what we
consider in scope, and **every finding we know about**, open or closed. It
grows: findings are added, never deleted. A fixed finding stays here with how
it was fixed and what test keeps it fixed.

`make check` runs `tools/check_security.py`, which audits the npm and Python
dependencies and **fails if an advisory is not mentioned here** (by its
`GHSA-…`, `PYSEC-…` or `CVE-…` id). So a new advisory cannot go unnoticed: it
either gets an entry below or the build stays red.

## Reporting a vulnerability

Please don't open a public issue. Use GitHub's private reporting on
<https://github.com/frcusaca/admath>: **Security → Report a vulnerability**.

> Maintainer: private vulnerability reporting must be switched on once in the
> repository's *Settings → Security*. Until then, see SEC-012.

## What is in scope

The course has no server, no accounts and collects no data. What matters:

| Part | Who runs it | What could go wrong |
| --- | --- | --- |
| `vecdraw` (`python/`) | Kids, in Google Colab or Jupyter, installed from this repository by each notebook's setup cell | Code kids run comes from whatever the configured branch holds (SEC-004) |
| The Angle Explorer (`explorer/`) | Kids' browsers: in notebook outputs, on the website, as a standalone page | Script injection through vector names (SEC-002, SEC-003), unwanted network requests (SEC-010) |
| Notebooks and the website | Kids and teachers | Answer keys or personal data published by mistake (SEC-005, SEC-006, SEC-008) |
| Build tools (npm packages, Python test tools, Quarto, TinyTeX) | The maintainer's machine | Vulnerable or tampered tools (SEC-001, SEC-007) |

## How we monitor

- `make check` (and `make check-security` alone) runs `npm audit` and
  `pip-audit` and compares their advisories with this file. Offline, it warns
  and skips; `python tools/check_security.py --strict` fails instead.
- When the check fails, add a finding below (template at the end), then rerun.
- When the check says an id "is in SECURITY.md but no audit reports it now",
  confirm the fix and mark that finding **Fixed**.
- Review the open findings at the start of each term and before tagging a
  release, and add a line to the review log.

Severity is our rating for **this project**, which can be lower than the
advisory's own rating when the vulnerable code never sees untrusted input
(the advisory's rating is noted too). Status is one of **Open** (needs action),
**Monitoring** (waiting on others; nothing to do yet), **Accepted** (known and
deliberately left), **Fixed**, or **Closed** (no longer applies without a fix
on our side, e.g. the advisory was withdrawn).

## Findings

| ID | Finding | Severity | Status | Since |
| --- | --- | --- | --- | --- |
| [SEC-001](#sec-001) | `picomatch` ReDoS in build tools (GHSA-fc5q-39xc-vjpf) | Low | Closed | 2026-11-17 |
| [SEC-002](#sec-002) | Vector names could inject HTML into the explorer | Medium | Fixed | 2026-11-16 |
| [SEC-003](#sec-003) | `explore_angles` output could break out of its `<script>` | Medium | Fixed | 2026-11-16 |
| [SEC-004](#sec-004) | Colab installs `vecdraw` from a moving branch | Medium | Open | 2026-11-16 |
| [SEC-005](#sec-005) | Teacher guides (answer keys) are public in the repository | Low | Open | 2026-11-17 |
| [SEC-006](#sec-006) | Personal email address in commit metadata | Medium | Open | 2026-11-18 |
| [SEC-007](#sec-007) | Quarto and TinyTeX downloads are not checksum-verified | Low | Open | 2026-11-18 |
| [SEC-008](#sec-008) | Notebook outputs and machine details could be committed | Low | Fixed | 2026-11-16 |
| [SEC-009](#sec-009) | Jupyter kernel talks over unencrypted TCP on 127.0.0.1 | Low | Accepted | 2026-11-16 |
| [SEC-010](#sec-010) | The original explorer loaded fonts from Google | Low | Fixed | 2026-11-16 |
| [SEC-011](#sec-011) | "Copy as NumPy" code could carry injected lines | Low | Fixed | 2026-11-16 |
| [SEC-012](#sec-012) | No private channel for vulnerability reports yet | Low | Open | 2026-11-18 |

### SEC-001

**`picomatch` ReDoS in build tools.** Low (advisory: high). Closed 2026-11-18: advisory withdrawn.

- **Advisory:** [GHSA-fc5q-39xc-vjpf](https://github.com/advisories/GHSA-fc5q-39xc-vjpf),
  "picomatch vulnerable to ReDoS through single-branch repeated extglobs",
  `picomatch <= 4.0.7`.
- **Where:** `vite`, `vite-plugin-singlefile`, `vitest`, `tinyglobby` and `fdir`
  depend on it. `npm audit` counts that as 6 high-severity findings, all this
  one advisory.
- **Exposure:** build and test time only, on glob patterns this repository
  writes. Nothing untrusted reaches it, and it is not in the built explorer, the
  Python package or anything kids run.
- **Action:** none possible yet. 4.0.7 is the newest release (checked
  2026-11-17). `npm audit fix --force` would *downgrade* Vite and Vitest by
  major versions, so don't. When a fixed `picomatch` ships: `npm update`,
  `make check`, mark Fixed.
- **Closed 2026-11-18:** GitHub withdrew the advisory (withdrawn at
  2026-11-18 15:38 UTC; the advisory still lists no patched version) and
  `npm audit` stopped reporting it. Nothing changed here: `picomatch` is still
  4.0.7. If the advisory is reinstated, `make check` fails again and this
  entry should be reopened.

### SEC-002

**Vector names could inject HTML into the explorer.** Medium. Fixed 2026-11-16.

- **Details:** the original page built its markup with `innerHTML` and the
  vector names, which were fixed letters. In the port, names come from callers
  (`explore_angles(..., names=[...])`), so a name like `<img onerror=…>` would run
  script in the page.
- **Fix:** every interpolated name goes through `esc()` (`explorer/src/format.ts`);
  the standalone footer is escaped too.
- **Kept fixed by:** `explorer/src/render.test.ts` ("names are escaped everywhere
  they are drawn"), and `explorer/e2e/python.spec.ts` (a `<x>` name renders as text).

### SEC-003

**`explore_angles` output could break out of its `<script>`.** Medium. Fixed 2026-11-16.

- **Details:** `explore_angles` puts the explorer program and the caller's
  vectors and names inside one `<script>` in the cell output. A `</script>` in a
  name, or in the program, would end the script early and let HTML after it run.
- **Fix:** the options are JSON with `<`, `>` and `&` escaped as `<` etc.;
  any `</script` in the program is rewritten to `<\/script`
  (`python/src/vecdraw/explore.py`). Names are also checked (1 to 8 characters).
- **Kept fixed by:** `python/tests/test_explore.py`
  (`test_html_cannot_break_out_of_the_script_tag`,
  `test_a_script_end_tag_inside_the_bundle_is_neutralised`).

### SEC-004

**Colab installs `vecdraw` from a moving branch.** Medium. Open.

- **Details:** each notebook's setup cell runs
  `pip install "vecdraw @ git+https://github.com/frcusaca/admath@jia#subdirectory=python"`,
  and `explore_angles` then runs the bundled JavaScript. Whatever is on `jia` at
  that moment is what kids run, so anyone who can push to `jia` (or a
  compromised account) changes the code in every classroom.
- **Action:**
  1. Turn on two-factor authentication for every account that can push.
  2. Protect `jia` on GitHub (no force-pushes; require pull requests if more
     people join).
  3. During a term, pin `ref` in `course.toml` to a tag (or a commit id), then
     `make sync-setup` (maintainer guide §8). A tag can still be moved by
     someone with push access; a commit id cannot.

### SEC-005

**Teacher guides (answer keys) are public in the repository.** Low. Open.

- **Details:** the repository is public, and `notebooks/*_teacher_guide.ipynb`
  hold the answer keys. The website leaves them out (tested by
  `explorer/e2e-site/site.spec.ts`), but anyone, including students, can read
  them on GitHub after the first push.
- **Exposure:** academic integrity, not safety.
- **Action:** decide before the first push. To keep them private, move the
  teacher guides into a private repository and point the `teacher` Quarto
  profile at a checkout of it.

### SEC-006

**Personal email address in commit metadata.** Medium (privacy). Open.

- **Details:** the commits made locally name the maintainer's personal email
  as author and committer, and so does the repository's "Initial commit",
  which GitHub created and which is **already public** on `jia` (found
  2026-11-18). Each push publishes more of them, and a pushed address can only
  be removed by rewriting public history.
- **Action:**
  1. On GitHub, turn on *Settings → Emails → Keep my email addresses private*
     and *Block command line pushes that expose my email*.
  2. `git config user.email 22866129+frcusaca@users.noreply.github.com` in this
     repository (the account's GitHub noreply address, as shown under
     *Settings → Emails*).
  3. Before the first push: rewrite the unpushed commits to that address, for
     example with `git filter-repo --mailmap`. Their commit ids change, which is
     harmless before they are pushed.
  4. Decide whether to also rewrite the pushed "Initial commit" (a force-push
     of `jia`; cheap in a new repository, but the address may already have been
     copied, so treat it as public either way).

### SEC-007

**Quarto and TinyTeX downloads are not checksum-verified.** Low. Open.

- **Details:** `tools/install_quarto.sh` and `tools/install_tinytex.sh` download
  over HTTPS from GitHub releases, but don't check what they got. A
  compromised release or mirror would run on the maintainer's machine.
- **Action:** pin the SHA-256 of each archive in the scripts and refuse a
  mismatch. Quarto publishes `quarto-1.11.9-checksums.txt` with each release;
  TinyTeX publishes no checksums, so record its hash at the first trusted
  download.

### SEC-008

**Notebook outputs and machine details could be committed.** Low. Fixed 2026-11-16.

- **Details:** outputs can carry local paths, user names and the Python version.
  Quarto writes executed outputs back into the `.ipynb` it renders, and one
  commit picked them up. That commit was rewritten before anything was pushed,
  and all history was checked (no outputs anywhere).
- **Fix:** Quarto never executes `notebooks/` (`tools/stage_site.py` renders
  executed copies in `.build/site/`).
- **Kept fixed by:** `tools/check_clean.py` (`make check-clean`) runs at the start
  and at the end of `make check`, proving the build left the sources untouched.
  `.gitignore` is checked by `tools/check_gitignore.py`.

### SEC-009

**Jupyter kernel talks over unencrypted TCP on 127.0.0.1.** Low. Accepted.

- **Details:** `tools/run_notebooks.py` and Quarto start kernels that listen on
  localhost. Another user on the same machine could connect. IPC sockets would
  avoid it, but socket paths are limited to 108 characters, which deep
  checkouts exceed.
- **Why accepted:** single-user development machines; the notebooks hold no
  secrets.

### SEC-010

**The original explorer loaded fonts from Google.** Low (privacy). Fixed 2026-11-16.

- **Details:** `explorer/reference/angle-explorer.original.html` loads its fonts
  from Google Fonts, which tells Google the viewer's IP address on every load.
  For pages used by children, avoid third-party requests.
- **Fix:** the port inlines both fonts (`explorer/src/ui/fonts.ts`). The
  explorer, the site's explorer page and `explore_angles` make no network
  requests. The reference page is used only by the parity test.

### SEC-011

**"Copy as NumPy" code could carry injected lines.** Low. Fixed 2026-11-16.

- **Details:** kids paste the copied text into a code cell and run it. Names
  are written as Python variable names only when they are plain identifiers
  (not keywords, not `np` or `plt`); any other name goes into a trailing comment
  with line breaks removed, so it cannot start a new statement. Numbers are
  formatted from numbers.
- **Kept fixed by:** `explorer/src/numpy.test.ts` ("a name cannot smuggle code
  into the pasted line").

### SEC-012

**No private channel for vulnerability reports yet.** Low. Open.

- **Action:** turn on private vulnerability reporting in the GitHub repository
  (*Settings → Security → Private vulnerability reporting*), then delete the
  note under "Reporting a vulnerability" and mark this Fixed.

## Review log

| Date | What was checked | Result |
| --- | --- | --- |
| 2026-11-16 | Explorer port: untrusted names, script embedding, network requests, clipboard code | SEC-002, 003, 010, 011 found and fixed, with tests |
| 2026-11-16 | Notebook build: outputs leaking into commits | SEC-008 found, history rewritten before push, fixed |
| 2026-11-17 | `npm audit` after moving to `admath` | SEC-001 opened (no fixed release yet) |
| 2026-11-18 | `npm audit`, `pip-audit` (49 packages: none), secrets in all history (none), commit identities, installer downloads, Colab supply chain, published content | SEC-004 to 007, 009, 012 recorded; this file and `tools/check_security.py` added |
| 2026-11-18 | Commit identities on GitHub | SEC-006 updated: the pushed "Initial commit" already shows the personal email |
| 2026-11-18 | `npm audit` reported 0 advisories | SEC-001 closed: GHSA-fc5q-39xc-vjpf was withdrawn by GitHub |

## Adding a finding

Add a row to the table and a section like this, then a line to the review log.
Keep the advisory id (`GHSA-…`, `PYSEC-…`, `CVE-…`) in the text: that is what
`tools/check_security.py` looks for.

```markdown
### SEC-0NN

**One-line title.** Severity (advisory: …). Status.

- **Advisory / details:** what it is, where it is, the advisory id and link.
- **Exposure:** who or what can reach it in this project.
- **Action:** what to do, or why there's nothing to do yet.
- **Kept fixed by:** the test or check that stops it coming back (once fixed).
```
