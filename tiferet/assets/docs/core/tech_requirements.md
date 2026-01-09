# Instructions for Creating Technical Requirements Documents in the Tiferet Framework Project

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  

## Purpose
These instructions ensure consistency, clarity, and completeness when drafting Technical Requirements Documents (TRDs) for stories, enhancements, refactors, and subtasks in the Tiferet project. TRDs serve as the primary specification for implementation and review.

## General Guidelines
- **Tone & Style**: Professional, precise, and concise. Use active voice where possible.
- **Formatting**: Pure Markdown with proper headers, tables, code blocks, and lists.
- **Date**: Use the current date (e.g., January 08, 2026).
- **Version**: Use the current milestone version (e.g., 1.7.0). Increment only when instructed.
- **Length**: Aim for completeness without unnecessary verbosity. Typical length: 1–3 pages when rendered.

## Standard Structure
Every TRD must follow this exact structure:

```markdown
# Technical Requirements Document: [Story Title]

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet  
**Date:** [Current Date]  
**Version:** [Current Milestone, e.g., 1.7.0]

## 1. Overview
[High-level summary of the change, purpose, and key outcomes.]

## 2. Scope
### In Scope
- Bullet list of included work.
### Out of Scope
- Bullet list of excluded work.

## 3. Components Affected
| Component       | File/Path                          | Changes                                      |
|-----------------|------------------------------------|----------------------------------------------|
| ...             | ...                                | ...                                          |

## 4. Detailed Requirements
[Numbered subsections with code examples, signatures, behavior descriptions.]

## 5. Acceptance Criteria
1. Numbered list of verifiable outcomes.

## 6. Non-Functional Requirements
- Bullet list (performance, compatibility, style, etc.).

[Optional additional sections: Subtasks, Tests, Verification, etc.]
```

## Specific Rules
- **Title**: Use the exact story title prefixed with document type (e.g., "Commands – Feature: Add AddFeatureCommand Command").
- **Overview**: 3–6 sentences. Include motivation and primary benefits.
- **Scope**: Always include both "In Scope" and "Out of Scope" sections.
- **Components Table**: Use proper Markdown table syntax. Include all directly modified files.
- **Detailed Requirements**: 
  - Use numbered subsections.
  - Include code blocks with language hint and brief path comment when relevant.
  - Describe behavior clearly, including validation, error cases, and return values.
- **Acceptance Criteria**: Numbered, testable statements. Reference tests passing where appropriate.
- **Non-Functional**: Always include consistency with patterns, backward compatibility, and maintainability notes.
- **Subtasks**: For parent stories with subtasks, reference them or include separate linked documents.

## Common Patterns
- **Commands**: Include constructor, execute signature, validation, behavior, return value, and tests via `Command.handle`.
- **Model Methods**: Include signature, behavior, and model tests.
- **Refactors**: Highlight before/after, removed files, and migration steps.
- **New Errors**: Add to constants with ID, name, and message.

## Review Checklist
Before finalizing:
- [ ] All sections present.
- [ ] Table formatted correctly.
- [ ] Code blocks have language hint.
- [ ] Acceptance criteria are verifiable.
- [ ] No placeholder text or unresolved comments.

These instructions ensure all TRDs remain uniform, readable, and actionable across the Tiferet codebase. Follow them strictly for every new document.

## Related Code Style Documentation

Every TRD must include a **"Related Code Style Documentation"** section at the end. This section provides targeted links to component-specific style guides based on the primary artifacts being modified in the story.

**Rule for inclusion:**
- Always include the general `code_style.md`.
- Include a component-specific guide (models.md, commands.md, contexts.md, etc.) **only if the story directly adds, modifies, or refactors code in that component type**.
- Do not include unrelated guides to avoid clutter.

Current available guides (located in `tiferet/assets/docs/core/`):
- **[code_style.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/code_style.md)** – General structured code style (artifact comments, spacing, docstrings, snippets).
- **[models.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/models.md)** – Model-specific conventions (dual role, mutation helpers, factory methods).
- **[commands.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/commands.md)** – Command-specific conventions (dependency injection, validation, return patterns, static commands).
- **[contexts.md](https://github.com/greatstrength/tiferet/blob/v1.x-proto/tiferet/assets/docs/core/contexts.md)** – Context-specific conventions (injection patterns, lifecycle methods, execution flow).

Additional component-specific style guides will be added as the framework evolves. Always consult the relevant documents when implementing or extending components.