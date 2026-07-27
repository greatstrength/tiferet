---
name: tiferet-super-trd
description: Dispatch skill for Super-TRD parent issues. Read this first when handed a Super-TRD parent issue to self-identify your role, then follow the pointer to the matching role skill. Contains only the state machine and role pointers — no procedural content.
---

# Tiferet Super-TRD — Role Dispatch

## When to use
Read this skill whenever you are handed a **Super-TRD parent issue** — an issue with child sub-issues — and need to determine which role you are playing before doing any work.

## State machine

Evaluate the signals below in order. The first matching branch determines your role.

```
Parent status = Done?
  └─ Yes → Exit. Nothing to do.

All children closed?
  └─ No → Does the feature branch exist?
           ├─ No  → STARTER → read tiferet-super-trd-implementor
           └─ Yes → Is the active child's status "In Review"?
                    ├─ Yes → Does the PR have unresolved review comments?
                    │        ├─ Yes → IMPLEMENTOR (address comments) → read tiferet-super-trd-implementor
                    │        └─ No  → ASK HUMAN: await signal before proceeding
                    └─ No (In Progress) → IMPLEMENTOR → read tiferet-super-trd-implementor
  └─ Yes → Does the PR have unresolved review comments?
           ├─ Yes → CLOSER → read tiferet-super-trd-closer
           └─ No  → REVIEWER → read tiferet-super-trd-reviewer
```

**Active child** = the lowest-numbered open sub-issue whose project status is In Progress or In Review. The human developer typically names it explicitly; if not, infer from the sub-issue list.

## Role pointer map

| Role | Trigger | Skill to read |
|---|---|---|
| **STARTER** | No feature branch yet | `tiferet-super-trd-implementor` |
| **IMPLEMENTOR** | Branch exists; active child In Progress | `tiferet-super-trd-implementor` |
| **IMPLEMENTOR** (review comments) | Active child In Review; unresolved PR comments | `tiferet-super-trd-implementor` |
| **REVIEWER** | All children closed; no unresolved PR comments | `tiferet-super-trd-reviewer` |
| **CLOSER** | All children closed; unresolved PR review comments | `tiferet-super-trd-closer` |

## How to check the signals

```bash
# Parent status and children
gh issue view <parent-number> --repo greatstrength/tiferet --json title,projectItems,subIssues

# List sub-issues and their states
gh issue view <parent-number> --repo greatstrength/tiferet --json subIssues

# Feature branch existence
gh pr list --repo greatstrength/tiferet --head <branch-name>

# PR review comments
gh pr view <pr-number> --repo greatstrength/tiferet --json reviews,comments
```
