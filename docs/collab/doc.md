# Doc — Documentation Updates Stream

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose

The Doc stream is for standalone documentation changes — guides, style docs, collaboration docs, README updates, tutorials, and similar content — that are not tied to a milestone or release. It is the simplest of the three contribution streams.

## Branch Conventions

Documentation branches are created from `main`:

- Format: `docs-<lowercase-hyphenated-context>`
- Examples: `docs-contribution-streams`, `docs-toml-guide`, `docs-tutorial-cli`

## Version Field

When documentation references a version (e.g., in a TRD header or guide metadata), use the **latest released version** of the project to match surrounding files, unless the user specifies a different version.

## Workflow

1. **Create branch** from `main`: `docs-<context>`.
2. **Author** and commit the documentation changes.
3. **Submit PR** targeting `main` with the title format: `Docs – <Capitalized Semantic Title>` (e.g., `Docs – Contribution Stream Guidelines`). Return the PR URL to the user.
4. **PR review** follows the same process as the Main stream: if comments are received, address them and re-push.
5. The user **squash-merges** the PR.
6. **Local cleanup:** pull latest from `main` and delete the local docs branch.

## No Milestone or Release

Doc stream changes do not require a milestone, release tag, or GitHub Release. They are merged directly into `main` via pull request.
