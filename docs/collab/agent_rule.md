# Tiferet Contribution Standards — Global Agent Rule

Template for a **global** AI rule across Tiferet-family repos. Thin pointer — do not copy process law into the rule.

## How to apply it

**Warp:** `/add-rule` or Warp Drive → Personal → Rules → Global, then paste the rule text. Other tools: user-level rules / memory.

This is separate from a repo's `AGENTS.md`.

## The rule

```text
Applies to all Tiferet-family repositories (greatstrength/tiferet, and any tiferet-* / Tiferet.* project). Follow the documented process instead of improvising.

Source of truth: CONTRIBUTING.md → docs/collab/process.md. Inside tiferet use local paths; from another repo use https://github.com/greatstrength/tiferet/blob/main/docs/collab/process.md and that repo's docs/collab/binding.md if present.

Strands: prototype is authorized by an RFP; trunk reconstruction is authorized by a TRD that cites a catalog freeze id; hotfixes are TRDs on trunk with no freeze; docs/skills PRs need no TRD. Never merge proto into trunk. Never implement trunk work by copying proto.

Navigation:
- Implementation: AGENTS.md → tiferet-code-style (every session) → tiferet-code-<component>. Multi-component: tiferet-code-architecture.
- Prototype process: tiferet-author-rfp, tiferet-rfp-session, tiferet-freeze-catalog (human names the cluster first).
- Trunk process: tiferet-author-trd, tiferet-create-milestone, tiferet-milestone-session, tiferet-super-trd (+ role skills).
- Reports and review: tiferet-collab-report (on the issue), tiferet-pr-code-review (diff comments on the PR only).

Always: read binding.md for owner/repo and proto branch; keep functional vs docs commits separate; Co-Authored-By when an AI collaborates; never commit or merge unless asked. Drop stale ~/.agents/skills/tiferet-* copies so they do not shadow the repo's .agents/skills/.
```

## Companion skills

Committed at [`.agents/skills/`](../../.agents/skills/). Template: [SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md). See CONTRIBUTING.md → Working with AI Agents.
