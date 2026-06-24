# Tiferet Contribution Standards — Global Agent Rule

This file preserves the recommended **global AI rule** for working on Tiferet-family repositories. It is a *template*: each contributor who uses an AI agent applies it to their own agent, so the Tiferet conventions are followed consistently across every Tiferet repo (`greatstrength/tiferet`, `tiferet-*`, `Tiferet.*`).

The rule is intentionally a **thin pointer** — it references the canonical documentation (`docs/collab/` and `docs/core/`) and the companion agent skills rather than copying their content, so those documents stay the single source of truth and the rule never drifts.

## How to apply it

**Warp:** run `/add-rule` (Auto or Agent mode), or open **Warp Drive → Personal → Rules → Global**, then paste the rule text below. See the [Warp Rules docs](https://docs.warp.dev/agent-platform/warp-agents/rules) for details.

**Other agents/tools:** add the rule text to your tool's global/user-level rules, memory, or system instructions.

> This is a *global* (cross-repo) rule, separate from this repository's `AGENTS.md`, which Warp applies automatically only when you're working inside this repo. Apply the global rule so the conventions also take effect in the other Tiferet repos.

## The rule

```text
Applies to all Tiferet-family repositories (greatstrength/tiferet, and any tiferet-* / Tiferet.* project). Follow the documented Tiferet contribution standards instead of improvising process.

Source of truth (read when relevant): start at CONTRIBUTING.md, which indexes docs/collab/ (stream guides) and docs/core/ (code style). Inside the tiferet repo use those local paths; from any other repo use the GitHub URLs under https://github.com/greatstrength/tiferet/blob/main/.

For these workflows, use the matching skill (each carries the detailed conventions): tiferet-create-milestone (GitHub milestones), tiferet-author-trd (TRDs), tiferet-collab-report (completion reports), tiferet-milestone-session (per-issue release loop), tiferet-pr-code-review (PR review against a source of truth).

Always: tie work to a GitHub issue; write a TRD before non-trivial changes; follow the structured code style (artifact comments, RST docstrings, spacing); keep functional vs docs/config commits separate; add a Co-Authored-By line when an AI agent collaborates; never commit or merge unless asked.
```

## Companion skills

The workflows named in the rule are packaged as agent skills, with canonical copies kept in [agents/skills/](agents/skills/) (see that folder's README to activate them via `~/.agents/skills/` for global use, or a repo's `.agents/skills/` for one project):

- `tiferet-create-milestone`
- `tiferet-author-trd`
- `tiferet-collab-report`
- `tiferet-milestone-session`
- `tiferet-pr-code-review`

See the **Working with AI Agents** section of [CONTRIBUTING.md](../../CONTRIBUTING.md) for the overview.
