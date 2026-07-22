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

Navigation by task type:
- Implementation work: orient with AGENTS.md (architecture, key concepts, code style) → read tiferet-code-style (mandatory every implementation session) → read the component skill(s) matching what you are modifying.
- Multi-component implementation: also read tiferet-code-architecture before writing code.
- Collaboration/process work (milestones, TRDs, PRs, reports): orient with CONTRIBUTING.md → Working with AI Agents → use the matching collaboration skill.

For collaboration workflows, use the matching skill: tiferet-create-milestone (GitHub milestones), tiferet-author-trd (TRDs), tiferet-collab-report (completion reports), tiferet-milestone-session (per-issue release loop), tiferet-pr-code-review (PR review against a source of truth).

For implementation sessions, read tiferet-code-style first, then the component skill(s) for what you are modifying: tiferet-code-domain (domain objects), tiferet-code-events (domain events), tiferet-code-mappers (aggregates/transfer objects), tiferet-code-interfaces (service interfaces), tiferet-code-contexts (contexts), tiferet-code-repos (repositories), tiferet-code-assets (constants/errors), tiferet-code-blueprints (blueprints), tiferet-code-utils (utilities), tiferet-code-di (DI layer), tiferet-code-testing (test harness). If a skill is not installed, read docs/core/<component>.md directly.

Always: tie work to a GitHub issue; write a TRD before non-trivial changes; follow the structured code style (artifact comments, RST docstrings, spacing); keep functional vs docs/config commits separate; add a Co-Authored-By line when an AI agent collaborates; never commit or merge unless asked.
```

## Companion skills

All skills have canonical copies in [agents/skills/](agents/skills/) (see that folder's README to activate them via `~/.agents/skills/` for global use, or a repo's `.agents/skills/` for one project).

**Collaboration skills:**

- `tiferet-create-milestone`
- `tiferet-author-trd`
- `tiferet-collab-report`
- `tiferet-milestone-session`
- `tiferet-pr-code-review`

**Code style skills** (read `tiferet-code-style` every implementation session; read others as needed):

- `tiferet-code-architecture` — layer graph, import rules, runtime flow
- `tiferet-code-style` — artifact comments, spacing, docstrings (mandatory every session)
- `tiferet-code-domain` — domain objects
- `tiferet-code-events` — domain events
- `tiferet-code-mappers` — aggregates and transfer objects
- `tiferet-code-interfaces` — service interfaces
- `tiferet-code-contexts` — contexts
- `tiferet-code-repos` — repositories
- `tiferet-code-assets` — constants, errors, exceptions
- `tiferet-code-blueprints` — blueprints
- `tiferet-code-utils` — utilities
- `tiferet-code-di` — DI layer
- `tiferet-code-testing` — test harness

See the **Working with AI Agents** section of [CONTRIBUTING.md](../../CONTRIBUTING.md) for the full overview.
