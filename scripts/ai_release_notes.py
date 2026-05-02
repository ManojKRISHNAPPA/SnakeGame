#!/usr/bin/env python3
"""
AI Release Notes Generator
Reads git log since the last tag (or last 20 commits) and asks the LLM
to generate professional release notes. Saves to ai-release-notes.md
"""

import os
import sys
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ai_utils import ask_llm


def run_git(args, fallback=""):
    try:
        return subprocess.check_output(
            ["git"] + args, stderr=subprocess.DEVNULL, timeout=30
        ).decode().strip()
    except Exception:
        return fallback


def get_commits_since_last_tag():
    """Return git log since last tag, or last 20 commits if no tags."""
    last_tag = run_git(["describe", "--tags", "--abbrev=0"])
    if last_tag:
        return run_git(["log", f"{last_tag}..HEAD", "--oneline", "--no-merges"])
    return run_git(["log", "--oneline", "--no-merges", "-20"])


def main():
    print("[AI Release Notes] Generating release notes...")

    commits       = get_commits_since_last_tag() or "No commits found."
    changed_files = run_git(["diff", "--name-only", "HEAD~5", "HEAD"])
    git_commit    = os.environ.get("GIT_COMMIT", run_git(["rev-parse", "HEAD"]))
    build_number  = os.environ.get("BUILD_NUMBER", "local")
    branch        = os.environ.get("GIT_BRANCH",  run_git(["rev-parse", "--abbrev-ref", "HEAD"]))
    image_name    = os.environ.get("IMAGE_NAME",  "N/A")

    prompt = f"""You are a technical writer generating deployment release notes.

RECENT COMMITS:
{commits[:2000]}

CHANGED FILES:
{changed_files[:800]}

BUILD INFO:
- Build number : {build_number}
- Git commit   : {git_commit[:12] if git_commit else 'unknown'}
- Branch       : {branch}
- Docker image : {image_name}

Generate professional release notes in this exact markdown format:

## What's New
<Bullet list of new features or enhancements inferred from commit messages>

## Bug Fixes
<Bullet list of bug fixes, or "None" if not detected>

## Security & Compliance Updates
<Bullet list of security changes — dependency updates, scan fixes, policy changes>

## Infrastructure / Pipeline Changes
<Bullet list of DevOps, Docker, K8s, or CI changes>

## Breaking Changes
<Bullet list, or "None">

## Deployment Checklist
- [ ] All pipeline stages passed
- [ ] Security scan report reviewed
- [ ] Kubernetes manifests validated
<Add any extra checklist items based on the changes>

Keep it concise. Use past tense. Do not invent features not evidenced in the commits.
"""

    notes = ask_llm(prompt)

    report = f"""# Release Notes — Build #{build_number}

**Date:**    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Commit:**  {git_commit}
**Branch:**  {branch}
**Image:**   {image_name}

---

{notes}
"""

    out_file = "ai-release-notes.md"
    with open(out_file, "w") as f:
        f.write(report)

    print(f"[AI Release Notes] Saved → {out_file}")
    print("\n" + "=" * 60)
    print(report[:2000])
    print("=" * 60)


if __name__ == "__main__":
    main()
