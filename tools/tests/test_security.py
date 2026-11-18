# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""tools/check_security.py: advisories must be tracked in SECURITY.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_security as cs  # noqa: E402

# the shape `npm audit --json` really produces (trimmed)
NPM_REPORT = {
    "vulnerabilities": {
        "picomatch": {"via": [{"source": 1115561, "name": "picomatch", "title": "ReDoS", "severity": "high",
                               "url": "https://github.com/advisories/GHSA-fc5q-39xc-vjpf", "range": "<=4.0.7"}]},
        "vite": {"via": ["picomatch", "tinyglobby"]},
        "left-pad": {"via": [{"name": "left-pad", "title": "Bad", "severity": "low",
                              "url": "https://github.com/advisories/GHSA-2222-3333-4444", "range": "<1"}]},
    }
}
PIP_REPORT = {
    "dependencies": [
        {"name": "numpy", "version": "2.5.5", "vulns": []},
        {"name": "jinja2", "version": "3.0", "vulns": [
            {"id": "PYSEC-2026-12", "aliases": ["CVE-2026-1234", "GHSA-5555-6666-7777"], "fix_versions": ["3.1"], "description": "x"}]},
    ]
}


def test_npm_ids_come_from_advisory_urls_and_pointers_are_skipped():
    found = cs.npm_findings(NPM_REPORT)
    assert set(found) == {"GHSA-fc5q-39xc-vjpf", "GHSA-2222-3333-4444"}


def test_untracked_advisories_are_reported():
    findings = cs.npm_findings(NPM_REPORT)
    untracked, gone = cs.compare(findings, cs.tracked_ids("SEC-001 GHSA-fc5q-39xc-vjpf"))
    assert set(untracked) == {"GHSA-2222-3333-4444"}
    assert gone == set()


def test_a_pip_advisory_counts_as_tracked_under_any_alias():
    findings = cs.pip_findings(PIP_REPORT)
    untracked, _ = cs.compare(findings, cs.tracked_ids("see CVE-2026-1234"))
    assert untracked == {}


def test_tracked_ids_nobody_reports_are_listed_for_closing():
    _, gone = cs.compare({}, cs.tracked_ids("GHSA-fc5q-39xc-vjpf was fixed"))
    assert gone == {"GHSA-fc5q-39xc-vjpf"}


def test_the_real_security_md_tracks_the_known_advisory():
    text = (cs.ROOT / "SECURITY.md").read_text()
    assert "GHSA-fc5q-39xc-vjpf" in cs.tracked_ids(text)
    for n in range(1, 13):
        assert f"### SEC-{n:03d}" in text, f"SEC-{n:03d} section"
