# Collaboration Report

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

This is the session diary, not the review. It always lives on an **issue**. [process.md](process.md) is the index if you are not sure which issue.

## When to write one

| Kind | When | Where |
|---|---|---|
| Standalone trunk | the human says the work is done / merged | that issue |
| Super-TRD child **implementation log** | the child's code has been pushed | the **child** issue |
| Super-TRD child **verification addendum** | after combined review and merge, or the Reviewer accepts that child's AC | the same child issue |
| Super-TRD parent roll-up | after merge | the **parent** issue |
| Prototype / RFP | after the alpha lands | the **RFP** issue |

Please do not post this as a PR conversation comment. The PR is already doing a different job.

An implementation log is a record of what landed. It is not combined-review acceptance, and it is not permission to close the child as Done. Wait for the addendum — or for the Reviewer to accept that child's AC out loud.

## The shape

```markdown
# Collaboration Report: [Exact Story Title] (greatstrength/tiferet#[issue-number])

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** [a real calendar date — e.g., August 14, 2026]
**Version:** [trunk milestone `2.0.1` | proto alpha `v2.0.0a17`]
**Kind:** Implementation log | Verification addendum | Standalone | Parent roll-up | RFP alpha

## 1. Story summary
- **Issue:** `[title]` (greatstrength/tiferet#[n])
- **Authorizing document:** TRD path / freeze id, or RFP id
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
For an RFP, also list the proto branch, the alpha tag, and the beta milestone.
For reconstruction, also list the freeze id.

## 5. Collaboration log (AI ↔ Human)
1. **AI** – …
2. **Human** – …
3. **AI** – …

End with: "This log captures the essential iterative collaboration between AI and human that produced the final implementation."
```

A verification addendum can be short: which AC passed, which AC the Reviewer amended, anything still open. A parent roll-up should *link* each child's log and addendum rather than rewriting section 5 for every child. Nobody wants to read the same argument three times.

## Voice

Professional and factual, but it can sound like a person wrote it. Use a real calendar date. Keep snippets short. The collaboration log is mandatory even when it is only a few lines. Aim for a page or two on a full report; an addendum may be a paragraph. When you post, post the report — not a preamble about the report.
