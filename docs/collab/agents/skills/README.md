# Tiferet Agent Skills

Canonical, version-controlled copies of the reusable agent **skills** for Tiferet-family work. They live here so they're shareable and reviewable; to use them, each contributor copies them into an auto-discoverable skills directory.

## Skills in this folder
- **`tiferet-create-milestone`** — create or format a GitHub milestone.
- **`tiferet-author-trd`** — author a Technical Requirements Document.
- **`tiferet-collab-report`** — generate a Collaboration Report when an issue is confirmed complete.
- **`tiferet-milestone-session`** — run a milestone's per-issue branch → PR → merge → report loop.

Each is a directory with a `SKILL.md` (YAML frontmatter + instructions). The skills are thin wrappers that reference `docs/collab/` and `docs/core/` as the source of truth — they don't copy that content, so the docs stay authoritative.

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
Start an agent and ask "what skills do I have?", or invoke one directly such as `/tiferet-create-milestone`. The four `tiferet-*` skills should appear.

## Keep in sync
These repo copies are canonical. When they change here, re-run the copy command above to refresh your active install. Pair the skills with the global rule template in [../../agent_rule.md](../../agent_rule.md).
