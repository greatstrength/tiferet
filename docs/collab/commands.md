# Useful Commands Reference

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

This document lists key commands used across all contribution workflow streams. Each entry notes whether the operation is available via **Warp/Oz GitHub MCP tools** (preferred when available) or requires the **`gh` CLI** directly.

## Branch Operations

**Tool availability:** Git shell commands.

```bash
# Create a feature branch from main
git checkout -b <branch-name> main

# Create a prototype worktree branch from the prototype branch
git checkout -b v2.0.0b6-my-context v2.0-proto

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

# Link a branch to an issue (development branch)
# Use the GitHub UI or MCP tool — no direct gh CLI equivalent.

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

Field and option IDs are unique per GitHub Project. For any other Tiferet project, resolve them with `gh project field-list <number> --owner <org> --format json` and record them here.

## Release Publishing

**Tool availability:** **`gh` CLI only**.

```bash
# Create a release with tag
gh release create v2.1.0 \
  --repo greatstrength/tiferet \
  --title "Tiferet v2.1.0 – Release Title" \
  --notes-file release-notes.md

# Create a pre-release (for alpha/beta tags)
gh release create v2.0.0b6 \
  --repo greatstrength/tiferet \
  --title "Tiferet v2.0.0b6" \
  --prerelease \
  --notes "Condensed release notes here."

# List recent releases
gh release list --repo greatstrength/tiferet --limit 5
```

## Tagging

**Tool availability:** Git shell commands.

```bash
# Create an annotated tag (beta release on prototype branch)
git tag -a v2.0.0b6 -m "v2.0.0b6 – Condensed release notes here."

# Create an annotated tag (alpha release on worktree branch)
git tag -a v2.0.0a11 -m "v2.0.0a11 – Detailed mini-release description."

# Push tags to remote
git push origin --tags

# Push a single tag
git push origin v2.0.0b6

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
