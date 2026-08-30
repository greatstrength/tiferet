---
name: tiferet-collab-report
description: >
  Write a Collaboration Report for trunk TRD work on the GitHub issue (never as
  a PR comment). Kinds: standalone, Super-TRD implementation log, verification
  addendum, and parent roll-up.
---

# Collaboration Report

## When to use

- Standalone trunk TRD: human confirms complete.
- Super-TRD child: code pushed → **implementation log** on the child issue (part of implementor completion). After combined review/merge → **verification addendum**.
- Super-TRD parent: after merge → roll-up on the parent issue.

## When not to use

- As a PR conversation comment.
- For RFP or documentation work.
- Proactively on standalone TRD work the human has not confirmed.

## Canonical source

- `docs/collab/collab_report.md`
- `docs/collab/process.md`

## Inputs

Kind. Issue number. Binding. Conversation links from **issue** threads (and PR reviews only for closer/reviewer narrative).

## Procedure

1. Choose Kind from collab_report.md.
2. Draft the required structure. Exact calendar date. Version = trunk milestone.
3. Super-TRD closer: read child issue threads (logs + addenda) before the parent roll-up. Do not rewrite each child's log.
4. Post on the **issue**. If the issue is locked, say so; do not silently dump it on the PR.

## Outputs

Issue comment.

## Guardrails

- Implementation log ≠ Done.
- Never proto → trunk git language in the report.
