# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Every known vulnerability in our dependencies is tracked in SECURITY.md.

    python tools/check_security.py            check (warns and passes when offline)
    python tools/check_security.py --strict   also fail when an audit cannot run

Runs two audits:
  npm audit   on the npm workspace (the explorer's build and test tools)
  pip-audit   on the packages installed in .venv (run with `uvx`, not installed here)
and compares every advisory id they report (GHSA-…, PYSEC-…, CVE-…) with the
ids written in SECURITY.md.

- An advisory that SECURITY.md does not mention fails the check: add an entry.
- An id in SECURITY.md that no audit reports any more is listed, so its entry
  can be marked Fixed (this does not fail).
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECURITY_MD = ROOT / "SECURITY.md"
ADVISORY_ID = re.compile(r"\b(GHSA(?:-[23456789cfghjmpqrvwx]{4}){3}|PYSEC-\d{4}-\d+|CVE-\d{4}-\d{4,})\b")


class AuditUnavailable(Exception):
    """The audit could not run (no network, tool missing, …)."""


def tracked_ids(text):
    return set(ADVISORY_ID.findall(text))


def npm_findings(report):
    """{advisory id: description} from `npm audit --json` output."""
    found = {}
    for name, vuln in report.get("vulnerabilities", {}).items():
        for via in vuln.get("via", []):
            if not isinstance(via, dict):
                continue      # "via": ["other-package"] just points at another entry
            ids = ADVISORY_ID.findall(via.get("url", "") + " " + str(via.get("source", "")))
            for advisory in ids:
                found[advisory] = f"npm {via.get('name', name)} {via.get('range', '')}: {via.get('title', '')} ({via.get('severity', '?')})"
    return found


def pip_findings(report):
    """{advisory id: description} from `pip-audit --format json` output (aliases count as the same issue)."""
    found = {}
    for dep in report.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            ids = [vuln["id"], *vuln.get("aliases", [])]
            text = f"pypi {dep['name']} {dep.get('version', '')}: {vuln.get('description', '')[:80]} (fix: {', '.join(vuln.get('fix_versions', [])) or 'none'})"
            found[" / ".join(ids)] = text
    return found


def run_npm_audit():
    if not shutil.which("npm"):
        raise AuditUnavailable("npm not found")
    result = subprocess.run(["npm", "audit", "--json"], cwd=ROOT, capture_output=True, text=True)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise AuditUnavailable("npm audit gave no report (offline?)") from None
    if "error" in report:
        raise AuditUnavailable(f"npm audit failed: {report['error'].get('summary', report['error'])}")
    return npm_findings(report)


def run_pip_audit():
    python = ROOT / ".venv" / "bin" / "python"
    if not shutil.which("uv") or not python.exists():
        raise AuditUnavailable("needs uv and .venv (make setup)")
    frozen = subprocess.run(
        ["uv", "pip", "freeze", "--python", str(python), "--exclude-editable"],
        capture_output=True, text=True, check=True,
    ).stdout
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(frozen)
        requirements = f.name
    result = subprocess.run(
        ["uvx", "pip-audit", "-r", requirements, "--no-deps", "--disable-pip", "--format", "json", "--progress-spinner", "off"],
        capture_output=True, text=True,
    )
    Path(requirements).unlink(missing_ok=True)
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise AuditUnavailable(f"pip-audit gave no report (offline?): {result.stderr.strip()[-200:]}") from None
    return pip_findings(report)


def compare(findings, tracked):
    """(untracked findings, tracked ids that nothing reports any more)"""
    untracked = {}
    seen = set()
    for key, text in findings.items():
        ids = set(ADVISORY_ID.findall(key))
        seen |= ids
        if not ids & tracked:
            untracked[key] = text
    return untracked, tracked - seen


def main():
    strict = "--strict" in sys.argv
    tracked = tracked_ids(SECURITY_MD.read_text(encoding="utf-8"))
    findings = {}
    skipped = []
    for name, audit in (("npm audit", run_npm_audit), ("pip-audit", run_pip_audit)):
        try:
            got = audit()
        except AuditUnavailable as why:
            skipped.append(f"{name}: {why}")
            continue
        findings.update(got)
        print(f"  {name}: {len(got)} advisories")

    untracked, gone = compare(findings, tracked)
    for line in skipped:
        print(f"WARNING: skipped {line}", file=sys.stderr)
    for advisory in sorted(gone):
        print(f"  note: {advisory} is in SECURITY.md but no audit reports it now; if fixed, mark its entry Fixed")
    if untracked:
        for key, text in sorted(untracked.items()):
            print(f"FAIL: untracked advisory {key}: {text}", file=sys.stderr)
        print("Add an entry for each to SECURITY.md (see 'Adding a finding').", file=sys.stderr)
        sys.exit(1)
    if skipped and strict:
        sys.exit(1)
    print(f"security: {len(findings)} advisories reported, all tracked in SECURITY.md")


if __name__ == "__main__":
    main()
