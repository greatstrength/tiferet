# Tiferet Contribution Standards — Global Agent Rule

A paste-able global rule for Tiferet-family repos. Keep it thin. The law lives in `docs/collab/process.md`; this file only points there so it cannot drift.

## How to apply it

**Warp:** `/add-rule` or Warp Drive → Personal → Rules → Global, then paste the rule text. Other tools: user-level rules / memory.

This is separate from a repo's `AGENTS.md`.

## The rule

```text
Applies to all Tiferet-family repositories (greatstrength/tiferet, and any tiferet-* / Tiferet.* project). Follow the documented process instead of improvising.

Source of truth: CONTRIBUTING.md → docs/collab/process.md. Inside tiferet use local paths; from another repo use https://github.com/greatstrength/tiferet/blob/main/docs/collab/process.md and that repo's docs/collab/binding.md if present.

Strands: prototype is authorized by an RFP; trunk reconstruction is authorized by a TRD that cites an existing catalog freeze id; hotfixes are TRDs on trunk with no freeze; docs/skills PRs need no TRD. Never merge proto into trunk. Never implement trunk work by copying proto. Never tag or bump the package version on an individual PR.

Navigation:
- Implementation: AGENTS.md → tiferet-code-style (every session) → tiferet-code-<component>. Multi-component: tiferet-code-architecture.
- Prototype: tiferet-author-rfp, tiferet-rfp-session.
- Trunk: tiferet-author-trd (freeze id must already exist for reconstruction), tiferet-implement-trd, tiferet-collab-report (standalone TRD closeout on the issue).
- Review: human comments on the PR diff; short status on the issue. GitHub-link each PR to its RFP, standalone TRD, or Super-TRD parent. Wire blocked-by from RFP Depends on/Blocks and TRD §7.

Always: read binding.md for owner/repo and proto branch; keep functional vs docs commits separate; Co-Authored-By when an AI collaborates; never commit or merge unless asked. Drop stale ~/.agents/skills/tiferet-* copies so they do not shadow the repo's .agents/skills/.
```

## Companion skills

Committed at [`.agents/skills/`](../../.agents/skills/). Template: [SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md). See CONTRIBUTING.md → Working with AI Agents.
