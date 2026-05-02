#!/usr/bin/env python3
"""
AI Code Review Stage
Reads git diff of the last commit and asks the LLM to review it for
security issues, code quality, and bugs. Saves report to ai-code-review-report.md
"""

import os
import sys
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ai_utils import ask_llm


def get_git_diff():
    """Return diff of Java/Python/JS files changed in the last commit."""
    cmds = [
        ["git", "diff", "HEAD~1", "HEAD", "--", "*.java", "*.py", "*.js", "*.ts"],
        ["git", "show", "HEAD", "--", "*.java", "*.py", "*.js"],
    ]
    for cmd in cmds:
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=30).decode()
            if out.strip():
                return out
        except Exception:
            continue
    return "No diff available (fresh repo or single commit)."


def main():
    print("[AI Code Review] Analysing code changes...")

    diff = get_git_diff()
    diff_snippet = diff[:3500] + ("\n... [truncated]" if len(diff) > 3500 else "")

    prompt = f"""You are a senior software engineer doing a security-focused code review.
Analyse the following git diff and produce a structured report.

GIT DIFF:
```
{diff_snippet}
```

Respond ONLY in this markdown format:

## Summary
<2-3 sentences on what changed>

## Security Issues
<List each issue as: [SEVERITY] Description — Recommendation>
<Use CRITICAL / HIGH / MEDIUM / LOW. If none, write "None found.">

## Code Quality Issues
<List issues with short fix suggestion. If none, write "None found.">

## What Was Done Well
<Positive observations>

## Top 3 Recommendations
1. ...
2. ...
3. ...
"""

    analysis = ask_llm(prompt)

    report = f"""# AI Code Review Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Commit:** {os.environ.get('GIT_COMMIT', 'unknown')}
**Branch:** {os.environ.get('GIT_BRANCH', 'unknown')}
**Build:** #{os.environ.get('BUILD_NUMBER', 'local')}

---

{analysis}
"""

    out_file = "ai-code-review-report.md"
    with open(out_file, "w") as f:
        f.write(report)

    print(f"[AI Code Review] Report saved → {out_file}")
    print("\n" + "=" * 60)
    print(report[:2000])
    print("=" * 60)


if __name__ == "__main__":
    main()
