### Guide: How to Generate a Collaboration Summary Report (AI Agent Instructions)

**When to trigger this report**  
Generate this report **only** when the human confirms that the GitHub issue (story/subtask) is **complete** (e.g., code merged, tests passing, branch pushed). Use the phrase “issue is completed” or similar as the trigger.

**Objective**  
Produce a concise, professional, structured summary that documents:
- The original story/TRD goal
- All code components touched (with key implementation highlights)
- Deviations/clarifications from the original TRD
- Git/branch state
- A chronological Collaboration Log (AI ↔ Human decisions)

**Required Format**  
Use **pure Markdown** with the following exact structure and heading levels:

```markdown
# Collaboration Report: [Exact Story Title] ([repo#issue-number])

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [Current date, e.g., January 09, 2026]  
**Version:** [Milestone version, e.g., 1.7.0]

## 1. Story / TRD Summary
- **Issue:** `[exact title]` (greatstrength/tiferet#[issue-number]).
- **Goal:** One concise sentence + bullet list of core requirements from TRD.

## 2. Code Components Touched
### 2.1 [Component Name]
**File:** `path/to/file.py`  
**Class:** `ClassName` (if applicable)  
**Implements/Changes:**
- Bullet list of key methods, attributes, or changes (include short code snippets where critical logic was added/modified).
- Use **bold** for method names and file paths.
- Use inline code blocks for short snippets.

(Repeat 2.1, 2.2, etc. for each major component touched.)

## 3. Deviations / Clarifications vs TRD
- Numbered list of intentional deviations.
- For each:
  - **TRD expectation:** Brief quote or paraphrase from TRD.
  - **Implemented behavior:** What actually happened.
  - **Rationale:** Why it was changed (alignment, bug prevention, pattern consistency).

## 4. Git / Branch State
- **Branch:** `full-branch-name`.
- **Commits created in this work:**
  1. `short commit message` (include Co-Authored-By note if applicable)
  2. ...
- State of the branch (pushed, up to date, etc.).

## 5. Collaboration Log (AI ↔ Human)
Chronological list (numbered) of key decision points:
- **AI** – [brief description of what AI did/proposed]
- **Human** – [brief description of human feedback/clarification]
- **AI** – [how AI responded/adjusted]

End with a note like: “This log captures the iterative AI ↔ human collaboration that led to the final implementation.”

**Tone & Style Rules**
- Professional, concise, factual, and non-defensive.
- Use bullet points and numbered lists for readability.
- Include short, relevant code snippets (with file path comment) for critical logic.
- Do **not** include full code files — only highlight key changes.
- Always include the Collaboration Log — it is mandatory.

**Length**: Aim for 1–2 pages when rendered. Be thorough but avoid verbosity.

**Output**: Return only the final Markdown report. No additional commentary.
```