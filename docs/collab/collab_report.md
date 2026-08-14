# Collaboration Report

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

Process index: [process.md](process.md).

## When to write one

| Kind | When | Where |
|---|---|---|
| Standalone trunk | Human confirms complete / merged | the issue |
| Super-TRD child **implementation log** | child's code is pushed | the **child** issue |
| Super-TRD child **verification addendum** | after combined review and merge (or Reviewer accepts that child's AC) | the same child issue |
| Super-TRD parent roll-up | after merge | the **parent** issue |
| Prototype / RFP | after the alpha lands | the **RFP** issue |

Never post the report as a PR conversation comment. The PR stays a review surface.

A Super-TRD implementation log is **not** combined-review acceptance. Do not close the child as Done until the verification addendum (or explicit Reviewer AC acceptance).

## Required format

```markdown
# Collaboration Report: [Exact Story Title] (greatstrength/tiferet#[issue-number])

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet
**Date:** [calendar date — e.g., August 14, 2026]
**Version:** [trunk milestone `2.0.1` | proto alpha `v2.0.0a17`]
**Kind:** Implementation log | Verification addendum | Standalone | Parent roll-up | RFP alpha

## 1. Story summary
- **Issue:** `[title]` (greatstrength/tiferet#[n])
- **Authorizing document:** TRD path / freeze id, or RFP id
- **Goal:** one sentence + bullets of the core requirements

## 2. Code components touched
### 2.1 [Area]
**File:** `path`  **Artifact:** `Name`
**Changes:**
- …

## 3. Deviations
1. **Specified:** … **Implemented:** … **Rationale:** …
(If none: "No deviations were required.")

## 4. Git / branch state
- **Branch:**
- **Pull Request:** #N – url
- **Commits:** message (abcdef1)
- **Current state:**
Prototype/RFP also list: proto branch, alpha tag, beta milestone.
Reconstruction also list: freeze id.

## 5. Collaboration log (AI ↔ Human)
1. **AI** – …
2. **Human** – …
3. **AI** – …

End with: "This log captures the essential iterative collaboration between AI and human that produced the final implementation."
```

Verification addenda may be short: which AC passed, which AC the Reviewer amended, any follow-up. Parent roll-ups link each child's log and addendum; they do not rewrite each child's section 5.

## Style

Professional, concise, factual. Exact calendar dates. Short snippets only. Collaboration log is mandatory. Target 1–2 pages for a full report; addenda may be a fraction of that. Output only the report when posting.
