# Skill template — Tiferet family

Every Tiferet-family skill — process, code-style, and domain — uses this shape. Agents must not invent a different outline.

Canonical process: [process.md](../process.md). Repo-local facts: [binding.md](../binding.md).

```markdown
---
name: <skill-name>
description: >
  Trigger-oriented. Say when to use it and when not to.
  Include the human phrases that should fire this skill.
---

# <Human task title>

## When to use
- …

## When not to use
- …

## Canonical source
- `docs/collab/<file>.md` or `docs/core/<file>.md`
- Do not duplicate the law here. Point, then add only the operator steps.

## Inputs
What must exist before acting (issue number, strand, binding file, TRD/RFP path, freeze id).

## Procedure
Numbered steps. Label strand-specific steps **Trunk** or **Prototype**.

## Outputs
What is produced, and **which GitHub surface** it is posted on (PR vs issue vs tag vs local file).

## Guardrails
- Never commit or merge unless asked.
- Never proto → trunk git.
- Never implement trunk reconstruction from a live proto branch.
- Never author a reconstruction TRD without a freeze id.
- Read `docs/collab/binding.md` in this repo for owner/repo, proto branch, and project ids.
```

Existing skills are rewritten onto this template when they move to `.agents/skills/`. New skills are authored on it from the start.
