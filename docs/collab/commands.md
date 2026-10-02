# Useful Commands Reference

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

Process index: [process.md](process.md). Binding (repo, proto branch, project ids): [binding.md](binding.md).

Proto → trunk git is forbidden. Trunk → proto git is permitted when a human asks; it is not a default step.

This document lists key commands used across all contribution workflow streams. Each entry notes whether the operation is available via **Warp/Oz GitHub MCP tools** (preferred when available) or requires the **`gh` CLI** directly.

## Branch Operations

**Tool availability:** Git shell commands.

```bash
# Create a feature branch from main
git checkout -b <branch-name> main

# Prototype worktree from the proto branch in binding.md
git checkout -b v2.0.0b1-my-context v2.x-proto

# Delete a local branch
git branch -d <branch-name>

# Delete a remote branch
git push origin --delete <branch-name>

# Pull latest from a branch
git pull origin main
```

## Issue and PR Management

**Tool availability:** Available via **Warp/Oz GitHub MCP tools**; fall back to `gh` CLI.

```bash
# Create an issue
gh issue create --repo greatstrength/tiferet --title "<title>" --body "<body>"

# Create a pull request
gh pr create --repo greatstrength/tiferet --base main --head <branch> --title "<title>" --body "<body>"

# GitHub-link a PR to its authorizing issue (development relationship).
# Title mention is not enough. Closing keywords auto-close on default branch
# only; proto PRs must still be linked, then the issue closed by hand.
gh api repos/greatstrength/tiferet/issues/<issue-number>/timeline
# Prefer the GitHub UI "Development" / "Link a pull request" control, or MCP.

# View PR status
gh pr view <pr-number> --repo greatstrength/tiferet

# List open PRs
gh pr list --repo greatstrength/tiferet
```

## Milestone Management

**Tool availability:** **`gh` CLI only** — no MCP equivalent.

```bash
# Create a milestone
gh api repos/greatstrength/tiferet/milestones \
  -f title="v2.1.0" \
  -f description="Description here" \
  -f state="open"

# List open milestones
gh api 'repos/greatstrength/tiferet/milestones?state=open' \
  --jq '.[] | {number, title, state}'

# Close a milestone (replace <number> with milestone number)
gh api repos/greatstrength/tiferet/milestones/<number> \
  -X PATCH -f state="closed"
```

## Project Status Updates

**Tool availability:** **`gh` CLI only** — no MCP equivalent.

```bash
# List project fields (to find the Status field ID and option IDs)
gh project field-list 2 --owner greatstrength --format json

# Update an item's status (requires the project item ID and status option ID)
gh project item-edit \
  --project-id <project-id> \
  --id <item-id> \
  --field-id <status-field-id> \
  --single-select-option-id <option-id>
```

**Status option IDs** for project #2 (Tiferet Framework):

- Backlog: `f75ad846`
- Ready: `08afe404`
- In Progress: `47fc9ee4`
- In Review: `4cc61d42`
- Done: `98236657`

## Project Field Updates

**Tool availability:** **`gh` CLI only** — no MCP equivalent. See [project_fields.md](project_fields.md) for the semantics of each field (Priority, Size, Estimate/points, dates) and the cross-project strategy.

**Project #2 (Tiferet Framework) node id:** `PVT_kwDOCKXjws4A7Y85`

**Field IDs and single-select options** for project #2:

- Status: `PVTSSF_lADOCKXjws4A7Y85zgvs_j4` — Backlog `f75ad846`, Ready `08afe404`, In progress `47fc9ee4`, In review `4cc61d42`, Done `98236657`
- Priority: `PVTSSF_lADOCKXjws4A7Y85zgvs_no` — P0 `79628723`, P1 `0a877460`, P2 `da944a9c`
- Size: `PVTSSF_lADOCKXjws4A7Y85zgvs_ns` — XS `eff732af`, S `9592a5a3`, M `9728cbdc`, L `c53df028`, XL `7b141a16`
- Estimate (number / story points): `PVTF_lADOCKXjws4A7Y85zgvs_nw`
- Start date: `PVTF_lADOCKXjws4A7Y85zgvs_n4`
- End date: `PVTF_lADOCKXjws4A7Y85zgvs_n8`

```bash
# Resolve the project item id for an issue (item-add is idempotent — returns the existing id)
gh project item-add 2 --owner greatstrength --url <issue-url> --format json --jq '.id'

# Set a single-select field (Status / Priority / Size)
gh project item-edit --project-id PVT_kwDOCKXjws4A7Y85 --id <item-id> \
  --field-id <field-id> --single-select-option-id <option-id>

# Set the numeric Estimate (story points)
gh project item-edit --project-id PVT_kwDOCKXjws4A7Y85 --id <item-id> \
  --field-id PVTF_lADOCKXjws4A7Y85zgvs_nw --number 5

# Set a date field (Start date / End date)
gh project item-edit --project-id PVT_kwDOCKXjws4A7Y85 --id <item-id> \
  --field-id PVTF_lADOCKXjws4A7Y85zgvs_n4 --date 2026-06-23
```

Field and option IDs are unique per GitHub Project. Record this repo's ids in [binding.md](binding.md). For any other Tiferet project, resolve them with `gh project field-list <number> --owner <org> --format json` and record them in that repo's `docs/collab/binding.md`.

## Blocked-by (RFP and TRD graphs)

**Tool availability:** **`gh` CLI** / REST. Mirror RFP `Depends on` / `Blocks` and TRD §7 on the issue.

```bash
# Mark ISSUE as blocked by BLOCKER (numeric issue numbers).
gh api repos/greatstrength/tiferet/issues/<issue>/dependencies/blocked_by \
  -f issue_id=<blocker-issue-number>
```

Do not put the PR on a milestone. Assign the **issue** to a milestone if a reviewer asked you to; otherwise leave milestone assignment to the reviewer.

## Release Publishing

**Tool availability:** **`gh` CLI only**.

```bash
# Create a release with tag
gh release create v2.1.0 \
  --repo greatstrength/tiferet \
  --title "Tiferet v2.1.0 – Release Title" \
  --notes-file release-notes.md

# Individuals do not publish releases. Beta closeout is a pre-release;
# trunk closeout is a full release. Shown for orientation only.
gh release create v2.1.0b1 \
  --repo greatstrength/tiferet \
  --prerelease \
  --title "Tiferet v2.1.0b1" \
  --notes-file release-notes.md

# List recent releases
gh release list --repo greatstrength/tiferet --limit 5
```

## Tagging

**Tool availability:** Git shell commands.

```bash
# Do not tag on an individual RFP or TRD merge. Tags belong to milestone closeout.
# Alpha grouping closeout (orientation only):
git tag -a v2.1.0a1 -m "v2.1.0a1"

# Trunk release tag (vX.Y.Z — do not use bN on new trunk tags)
git tag -a v2.0.1 -m "v2.0.1 – release notes"

# Push tags to remote
git push origin --tags

# Push a single tag
git push origin v2.0.1

# List tags matching a pattern
git tag --list 'v2.0.0*' --sort=-version:refname
```

## Issue Linking and Labels

**Tool availability:** Available via **Warp/Oz GitHub MCP tools**; fall back to `gh` CLI.

```bash
# Add a label to an issue
gh issue edit <issue-number> --repo greatstrength/tiferet --add-label "<label>"

# Assign an issue to a milestone (replace <milestone-number>)
gh api repos/greatstrength/tiferet/issues/<issue-number> \
  -X PATCH -f milestone=<milestone-number>

# Close an issue
gh issue close <issue-number> --repo greatstrength/tiferet
```
