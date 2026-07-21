# Tiferet Agent Skills

Canonical, version-controlled copies of the reusable agent **skills** for Tiferet-family work. They live here so they're shareable and reviewable; to use them, each contributor copies them into an auto-discoverable skills directory.

## Collaboration skills
- **`tiferet-annotation-artifacts`** — scan, add, and resolve `# ++ todo:` / `# -- obsolete:` annotation artifacts; covers the pre-session scan, resolution procedure, and Collaboration Report integration. **Use at the start of every implementation session.**
- **`tiferet-create-milestone`** — create or format a GitHub milestone.
- **`tiferet-author-trd`** — author a Technical Requirements Document.
- **`tiferet-collab-report`** — generate a Collaboration Report when an issue is confirmed complete.
- **`tiferet-milestone-session`** — run a milestone's per-issue branch → PR → merge → report loop.
- **`tiferet-pr-code-review`** — review a PR by comparing its feature branch against a prototype source of truth and posting only actionable comments.

Collaboration skills are thin wrappers that reference `docs/collab/` and `docs/core/` as the source of truth — they don't copy that content, so the docs stay authoritative.

## Code style skills

Twelve self-contained code style skills — one per component — that embed the artifact comment labels, naming conventions, spacing rules, and a minimal working example so an implementation agent can apply the conventions without fetching any external URL. Each skill's **Canonical source** section links to the full `docs/core/` guide as a fallback.

**Read `tiferet-code-style` at the start of every implementation session** (same standing as `tiferet-annotation-artifacts`).

| Skill | Source doc | When to use |
|---|---|---|
| **`tiferet-code-style`** | `docs/core/code_style.md` | Every implementation session — read first |
| **`tiferet-code-domain`** | `docs/core/domain.md` | Adding or modifying domain objects |
| **`tiferet-code-events`** | `docs/core/events.md` | Adding or modifying domain events |
| **`tiferet-code-mappers`** | `docs/core/mappers.md` | Adding or modifying aggregates or config objects |
| **`tiferet-code-interfaces`** | `docs/core/interfaces.md` | Adding or modifying service interfaces |
| **`tiferet-code-repos`** | `docs/core/repos.md` | Adding or modifying repositories |
| **`tiferet-code-contexts`** | `docs/core/contexts.md` | Adding or modifying contexts |
| **`tiferet-code-assets`** | `docs/core/assets.md` | Adding or modifying assets constants, errors, or exceptions |
| **`tiferet-code-blueprints`** | `docs/core/blueprints.md` | Adding or modifying blueprints |
| **`tiferet-code-utils`** | `docs/core/utils.md` | Adding or modifying utilities |
| **`tiferet-code-di`** | `docs/core/di.md` | Adding or modifying DI layer classes or functions |
| **`tiferet-code-testing`** | `docs/core/testing.md` | Writing or extending tests using the harness |

Each is a directory with a `SKILL.md` (YAML frontmatter + instructions). Code style skills are self-contained distillations — they embed key conventions and a working example so agents can apply them without fetching external URLs.

## Why they aren't active from here
Agents only auto-discover skills in specific directories — notably `.agents/skills/` (note the leading dot) at a repository root or in your home folder. This `docs/collab/agents/skills/` path deliberately is **not** one of them, so the templates stay versioned without auto-loading. You activate them by copying into a discoverable location.

## Activate them (auto-discoverable)
Run these from the repository root.

**Option A — Global (every repo on your machine):**
```bash
mkdir -p ~/.agents/skills
cp -R docs/collab/agents/skills/tiferet-* ~/.agents/skills/
```

**Option B — This repository only (commit to share with the team):**
```bash
mkdir -p .agents/skills
cp -R docs/collab/agents/skills/tiferet-* .agents/skills/
```

Other tools work the same way with their own folder names (`.claude/skills/`, `.warp/skills/`, `.codex/skills/`, etc.) — copy into whichever your agent uses.

## Verify
Start an agent and ask "what skills do I have?", or invoke one directly such as `/tiferet-code-style`. All `tiferet-*` skills should appear.

## Keep in sync
These repo copies are canonical. When they change here, re-run the copy command above to refresh your active install. Pair the skills with the global rule template in [../../agent_rule.md](../../agent_rule.md).
