---
name: tiferet-collab-report
description: Generate a Collaboration Report (AI ↔ Human summary) for a completed Tiferet GitHub issue. Use this ONLY when the human confirms an issue/story/subtask is complete (e.g. "issue is completed", "work is done", "merged and ready") and wants the wrap-up report. Do not generate it proactively. Covers the exact report structure and where to post it.
---

# Generate a Tiferet Collaboration Report

## Trigger condition
Generate this report **only** when the human explicitly confirms the GitHub issue (story or subtask) is complete — e.g. "issue is completed", "work is done", "merged and ready", or similar clear language. Never produce it proactively.

Canonical source of truth:
https://github.com/greatstrength/tiferet/blob/main/docs/collab/collab_report.md

## Required structure
Use pure Markdown with this exact structure and heading levels:

```markdown
# Collaboration Report: [Exact Story Title] (greatstrength/tiferet#[issue-number])

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [exact calendar date — e.g., June 23, 2026]  
**Version:** [milestone version; "Request for Prototype" for RFP work]

## 1. Story / TRD Summary
- **Issue:** `[exact title]` (greatstrength/tiferet#[issue-number])
- **Goal:** one concise sentence + a bullet list of the core TRD requirements.

## 2. Code Components Touched
### 2.1 [Component / Domain Area]
**File:** `path/to/file.py`  
**Class / Artifact:** `ClassName` (if applicable)  
**Implements / Changes:**
- Key methods/attributes/behavioral changes (bold method names + file paths; short snippets only for critical logic)

(Repeat 2.1, 2.2, … per major area. Group logically — don't list every file.)

## 3. Deviations / Clarifications vs TRD
1. **TRD expectation:** … **Implemented behavior:** … **Rationale:** …
(If none: "No deviations from the TRD were required.")

## 4. Git / Branch State
- **Branch:** full name
- **Pull Request:** #NNN – link
- **Commits:** short messages + 7-char hashes (with Co-Authored-By note where applicable)
- **Current state:** pushed / merged / up-to-date / tagged, etc.
(Include RFP-specific fields — prototype worktree branch, alpha tags, beta tag — for RFP work.)

## 5. Collaboration Log (AI ↔ Human)
1. **AI** – [proposal / suggestion / question]
2. **Human** – [feedback / approval / clarification]
3. **AI** – [how it was adjusted or implemented]

End with: "This log captures the essential iterative collaboration between AI and human that produced the final implementation."
```

## Style
Professional, concise, factual, neutral. Prefer bullets and numbered lists. Include only short, high-signal code snippets (never full files). The **Collaboration Log is mandatory**, even if short. Target 1-2 pages. Use exact calendar dates. Output **only** the report — no extra chat text.

## Delivery
- Post as a comment on the originating GitHub issue.
- If the issue is locked / comments restricted → post to the associated PR with a cross-link to the issue.
- If neither channel is available → return the report in chat and ask the human how they'd like it delivered.
