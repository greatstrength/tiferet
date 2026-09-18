# Collaboration Report

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

This is the closeout diary for a **standalone** trunk TRD, not the review. It always lives on that **issue**. [process.md](process.md) is the index if you are not sure which issue.

## When to write one

Write it when the human says the standalone TRD is done / merged, on **that issue**.

Do not write one on an RFP issue. Do not write one on a Super-TRD child. Do not post it as a PR conversation comment.

A Super-TRD parent closeout (grouped stream, timings, named agents) is not this page's job.

## The shape

```markdown
# Collaboration Report: [Exact Story Title] (greatstrength/tiferet#[issue-number])

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** [a real calendar date — e.g., August 14, 2026]
**Version:** [trunk milestone `2.0.1` if assigned]
**Kind:** Standalone

## 1. Story summary
- **Issue:** `[title]` (greatstrength/tiferet#[n])
- **Authorizing document:** TRD path / freeze id (reconstruction) or "hotfix"
- **Goal:** one sentence, then bullets of the core requirements

## 2. Code components touched
### 2.1 [Area]
**File:** `path`  **Artifact:** `Name`
**Changes:**
- …

## 3. Deviations
1. **Specified:** … **Implemented:** … **Rationale:** …
(If nothing drifted: "No deviations were required.")

## 4. Git / branch state
- **Branch:**
- **Pull Request:** #N – url
- **Commits:** message (abcdef1)
- **Current state:**
For reconstruction, also list the freeze id.

## 5. Collaboration log (Human ↔ Agent)
1. **When** – **Human** – …
2. **When** – **Agent** – …
```

Keep section 5 chronological. Timestamps help. You do not need Agent → subagent voices on a standalone TRD.

## Voice

Professional and factual, but it can sound like a person wrote it. Use a real calendar date. Keep snippets short. The collaboration log is mandatory even when it is only a few lines. Aim for a page or two. When you post, post the report — not a preamble about the report.
