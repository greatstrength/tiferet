# RFP — Request for Prototype

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose

The RFP (Request for Prototype) stream is used for exploratory, experimental, or architectural work that is developed on a prototype branch before being promoted to a stable release. RFPs allow new ideas and significant refactors to be iterated on in isolation, with incremental alpha releases tracking progress and a beta release marking completion.

An RFP may originate from a submitted GitHub issue (**external RFP**) or be initiated internally by a maintainer or AI agent without a prior issue (**internal RFP**).

## TRD Version Field

When a TRD is written for an RFP, the **Version** field must be set to:

```
Version: Request for Prototype
```

Do not use the target release version. The actual version is determined during the tagging process.

## Branch Conventions

### Main Prototype Branch

Each major version line maintains a long-lived prototype branch:

- Format: `v<major>.<minor>-proto`
- Examples: `v0.1-proto`, `v1.0-proto`, `v2.0-proto`

This branch serves as the integration target for all prototype worktree branches within that version line.

### Prototype Worktree Branch

For each RFP, a short-lived worktree branch is created from the main prototype branch:

- Format: `v<major>.<minor>.<patch>b<next_beta>-<context>`
- Examples: `v2.0.0b6-dicontext-varargs`, `v1.0.0b2-mappers-refactor`
- The `<context>` portion is lowercase and hyphen-separated.

The worktree branch is created from and targets the main prototype branch.

## Versioning and Tagging Rules

### Beta Tags

A beta tag is applied to the **main prototype branch** after the worktree branch is rebased into it. The tag marks the completion of the RFP.

- Format: `v<major>.<minor>.<patch>b<N>` (e.g., `v2.0.0b6`)
- The tag description contains condensed release notes summarizing the work.

### Alpha Tags

When a prototype worktree branch requires more than one commit, each commit is tagged with an incremental alpha release on the worktree branch itself.

- Format: `v<major>.<minor>.<patch>a<N>` (e.g., `v2.0.0a11`, `v2.0.0a12`)
- Each alpha tag includes a detailed description of the specific work in that commit (a "mini-release doc").

### Alpha Increment Rules

The alpha counter is **global** to the `<major>.<minor>.<patch>` version and does **not** reset between betas.

**Example:** If `v1.0.0b1` consumed alphas `a1`–`a4`, then a new worktree branch for `v1.0.0b2` starts its first alpha at `a5` (not `a1`).

The alpha and beta counters **reset to 1** only when the major or minor version changes (e.g., moving from `v1.0.x` to `v1.1.x` or `v2.0.x`).

### Discovering the Next Version

To determine the next alpha or beta increment, query existing tags:

```bash
# Find the latest alpha for v2.0.0
git tag --list 'v2.0.0a*' --sort=-version:refname | head -1

# Find the latest beta for v2.0.0
git tag --list 'v2.0.0b*' --sort=-version:refname | head -1
```

## External RFP Workflow (Issue-Driven)

When an RFP originates from a GitHub issue:

1. **Create worktree branch** from the main prototype branch and link it to the originating GitHub issue.
2. **Implement** the changes. If multiple commits are needed, tag each with an incremental alpha release.
3. **Submit PR** against the main prototype branch. Return the PR URL to the user.
4. After PR approval, **rebase-merge** the worktree branch into the main prototype branch.
5. **Delete** the worktree branch (both local and remote).
6. **Tag** the beta release on the main prototype branch with condensed release notes.

## Internal RFP Workflow (No Submitted Issue)

When an RFP is initiated internally (no prior GitHub issue):

1. **Create worktree branch** from the main prototype branch.
2. **Implement** the changes, tagging alpha releases per commit if multi-commit.
3. **Rebase** the worktree branch directly into the main prototype branch (no PR).
4. **Delete** the worktree branch (both local and remote).
5. **Tag** the beta release on the main prototype branch with condensed release notes.
