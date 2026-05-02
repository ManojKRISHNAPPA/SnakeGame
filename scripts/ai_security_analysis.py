#!/usr/bin/env python3
"""
AI Security Analysis Stage
Reads OWASP dependency-check JSON report + Trivy scan output and asks the LLM
to produce a plain-English executive security report with a remediation roadmap.
Saves report to ai-security-report.md
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ai_utils import ask_llm


def load_owasp_vulnerabilities():
    """Parse OWASP dependency-check JSON report; return list of vuln dicts."""
    candidates = [
        "target/dependency-check-report.json",
        "dependency-check-report.json",
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            vulns = []
            for dep in data.get("dependencies", []):
                for v in dep.get("vulnerabilities", []):
                    cvss = (
                        v.get("cvssv3", {}).get("baseScore")
                        or v.get("cvssv2", {}).get("score")
                        or "N/A"
                    )
                    vulns.append({
                        "dependency": dep.get("fileName", "unknown"),
                        "cve":        v.get("name", ""),
                        "severity":   v.get("severity", "UNKNOWN"),
                        "cvss":       cvss,
                        "description": v.get("description", "")[:180],
                    })
            return vulns
        except Exception as e:
            print(f"[AI Security] Could not parse OWASP report at {path}: {e}")
    print("[AI Security] OWASP report not found — run 'mvn dependency-check:check -Dformat=JSON' first.")
    return []


def load_trivy_report():
    if os.path.exists("trivy-report.txt"):
        with open("trivy-report.txt") as f:
            return f.read()[:2000]
    return "trivy-report.txt not found."


def severity_counts(vulns):
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for v in vulns:
        s = v["severity"].upper()
        if s in counts:
            counts[s] += 1
    return counts


def main():
    print("[AI Security Analysis] Starting...")

    vulns   = load_owasp_vulnerabilities()
    trivy   = load_trivy_report()
    counts  = severity_counts(vulns)

    # Limit payload to LLM — top 15 highest-severity vulns
    priority = sorted(
        vulns,
        key=lambda v: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(v["severity"].upper(), 4),
    )[:15]

    vuln_json = json.dumps(priority, indent=2) if priority else "No vulnerabilities found."

    prompt = f"""You are a senior application security engineer.
Analyse the vulnerability scan results below and write a concise executive security report.

OWASP DEPENDENCY SCAN — {len(vulns)} vulnerabilities found
  (CRITICAL: {counts['CRITICAL']}, HIGH: {counts['HIGH']}, MEDIUM: {counts['MEDIUM']}, LOW: {counts['LOW']})

TOP FINDINGS (JSON):
{vuln_json[:2500]}

TRIVY CONTAINER IMAGE SCAN:
{trivy[:800]}

Respond ONLY in this markdown format:

## Executive Summary
<2-3 sentences on overall security posture — is this safe to deploy?>

## Critical / High Findings (Must Fix Before Deploy)
<Numbered list: CVE ID, affected dependency, CVSS score, what it enables, one-line fix>

## Medium Priority (Fix in Next Sprint)
<Numbered list, same format>

## Overall Risk Level
<CRITICAL / HIGH / MEDIUM / LOW — one sentence justification>

## Remediation Roadmap
| Priority | Action | Effort |
|----------|--------|--------|
<Fill table rows: Quick Fix / 1 Sprint / Long Term>

## OWASP Top 10 Mapping
<Which OWASP Top 10 categories are implicated, if any>
"""

    analysis = ask_llm(prompt)

    report = f"""# AI Security Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Build:** #{os.environ.get('BUILD_NUMBER', 'local')}
**OWASP Findings:** {len(vulns)} total — CRITICAL: {counts['CRITICAL']}, HIGH: {counts['HIGH']}, MEDIUM: {counts['MEDIUM']}, LOW: {counts['LOW']}

---

{analysis}
"""

    out_file = "ai-security-report.md"
    with open(out_file, "w") as f:
        f.write(report)

    print(f"[AI Security Analysis] Report saved → {out_file}")
    print("\n" + "=" * 60)
    print(report[:2500])
    print("=" * 60)

    # Exit non-zero if CRITICAL vulns found (optional gate — controlled by env var)
    if counts["CRITICAL"] > 0 and os.environ.get("AI_FAIL_ON_CRITICAL", "false").lower() == "true":
        print(f"[AI Security Analysis] BLOCKING: {counts['CRITICAL']} CRITICAL vulnerability/ies found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
