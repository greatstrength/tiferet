---
name: tiferet-super-trd
description: >
  Dispatch skill for Super-TRD parent issues on the trunk strand.
  Read first when handed a Super-TRD parent to self-identify your role.
  Contains only the state machine and role pointers.
---

# Tiferet Super-TRD — Role Dispatch

## When to use

- You are handed a Super-TRD **parent** issue (child sub-issues exist) on trunk.

## When not to use

- Prototype / RFP work — there is no proto Super-TRD.
- A standalone TRD (no children).
- Doc / skills PRs.

## Canonical source

- `docs/collab/super_trd_workflow.md`
- `docs/collab/process.md`
- `docs/collab/binding.md`

## Inputs

Parent issue number. Binding file for owner/repo.

## Procedure

Evaluate in order. First match wins.

```
Parent status = Done?
  └─ Yes → Exit.

Every child In Review with an implementation-log report?
  └─ No → Does the feature branch exist?
           ├─ No  → STARTER → tiferet-super-trd-implementor
           └─ Yes → Active child In Review with unresolved PR diff comments?
                    ├─ Yes → IMPLEMENTOR (address comments) → tiferet-super-trd-implementor
                    └─ No  → IMPLEMENTOR → tiferet-super-trd-implementor
  └─ Yes → Unresolved PR review comments from the Reviewer?
           ├─ Yes → CLOSER (code fixes) → tiferet-super-trd-closer
           └─ No  → Has the Reviewer posted the combined review?
                    ├─ No  → REVIEWER → tiferet-super-trd-reviewer
                    └─ Yes → CLOSER (addenda after merge) → tiferet-super-trd-closer
```

**Active child** = lowest-numbered open sub-issue in In Progress or In Review. Prefer the name the human gives.

| Role | Skill |
|---|---|
| STARTER / IMPLEMENTOR | `tiferet-super-trd-implementor` |
| REVIEWER | `tiferet-super-trd-reviewer` |
| CLOSER | `tiferet-super-trd-closer` |

Children stay In Review until the verification addendum. Do not treat an implementation log as Done.

## Outputs

None. Hand off to the role skill.

## Guardrails

- Never proto → trunk git.
- Never close a child as Done before the verification addendum (or explicit Reviewer AC acceptance).
- Read binding.md for owner/repo. Do not hardcode another repository.
