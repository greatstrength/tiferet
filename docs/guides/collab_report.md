### Guide: How to Generate a Collaboration Summary Report (AI Agent Instructions)

**Trigger Condition**  
Generate this report **only** when the human explicitly confirms that the GitHub issue (story or subtask) is complete — for example, by stating “issue is completed”, “work is done”, “merged and ready”, or similar clear language. Do not generate it proactively.

**Objective**  
Produce a concise, professional, structured summary documenting:  
- The original story/TRD goal  
- Key code components modified (with important implementation highlights)  
- Any intentional deviations or clarifications from the TRD  
- Current Git/branch state  
- Chronological record of significant AI ↔ Human decisions

**Required Format**  
Use **pure Markdown** and follow this exact structure and heading levels:

```markdown
# Collaboration Report: [Exact Story Title] (greatstrength/tiferet#[issue-number])

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [Current date — e.g., February 23, 2026]  
**Version:** [Milestone version — e.g., 1.9.0]

## 1. Story / TRD Summary
- **Issue:** `[exact title]` (greatstrength/tiferet#[issue-number])
- **Goal:** One concise sentence summarizing the purpose, followed by a bullet list of the core requirements from the TRD.

## 2. Code Components Touched
### 2.1 [Component Name or Domain Area]
**File:** `path/to/file.py`  
**Class / Artifact:** `ClassName` (if applicable)  
**Implements / Changes:**
- Bullet list of the most important methods, attributes, or behavioral changes
- Use **bold** for method names and file paths
- Include short, relevant inline code snippets only for critical logic

(Repeat 2.1, 2.2, … for each major area touched. Group logically — avoid listing every file.)

## 3. Deviations / Clarifications vs TRD
Numbered list of intentional differences (only include meaningful ones):

1. **TRD expectation:** Brief quote or paraphrase from the TRD.
   **Implemented behavior:** What was actually done.
   **Rationale:** Why the change was made (e.g., better alignment with existing patterns, bug prevention, consistency, performance).

(If no deviations occurred, state: “No deviations from the TRD were required.”)

## 4. Git / Branch State
- **Branch:** `feature/…` or `main` (include full name)
- **Pull Request:** #NNN – [link to PR]
- **Commits created in this work:**
  1. `short commit message` (abcdef1) – [optional Co-Authored-By note]
  2. …
- **Current state:** pushed / merged / up-to-date with main / tagged, etc.

## 5. Collaboration Log (AI ↔ Human)
Chronological numbered list of key decision points:

1. **AI** – [brief description of proposal, code suggestion, or question]
2. **Human** – [brief summary of feedback, approval, or clarification]
3. **AI** – [how the response was adjusted or implemented]

End the log with:  
“This log captures the essential iterative collaboration between AI and human that produced the final implementation.”

**Tone & Style Rules**
- Professional, concise, factual, neutral
- Prefer bullet points and numbered lists for readability
- Include only short, high-signal code snippets (with file path comment when helpful)
- Never include full files or large blocks of code
- The Collaboration Log section is **mandatory** — even if short

**Length**  
Target 1–2 pages when rendered. Be thorough yet avoid unnecessary detail.

**Output**  
Return **only** the final Markdown report. No additional commentary, explanations, or chat text.

**Delivery Destination**
- Post as a comment on the originating GitHub issue once triggered.
- If the issue is locked or comments restricted → post to the associated PR and include a cross-link to the issue.
- If neither channel is available → return the report in chat and ask the human for preferred delivery method.
```

### Process Conventions (for report generation)
- Use exact calendar dates (e.g., February 23, 2026) — never relative terms like “today” or “yesterday”.
- Include full PR link and short commit hashes (7 characters) in section 4.
- When a release is part of the story, include links to the annotated tag and published GitHub release.
- Keep the report focused on signal: prioritize decisions, changes, and rationale over exhaustive lists.
