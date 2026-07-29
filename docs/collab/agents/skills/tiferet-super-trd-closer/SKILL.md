---
name: tiferet-super-trd-closer
description: Close out a Super-TRD after the Reviewer posts findings: address review comments, push, await merge, post Collaboration Report, rename parent TRD to .complete.md, and verify GitHub automation closed the issue. Read after tiferet-super-trd identifies your role as CLOSER.
---

# Tiferet Super-TRD — Closer

## When to use
Read this after `tiferet-super-trd` identifies your role as **CLOSER**. Trigger: Super-TRD project status is In Progress **and** all child sub-issues are closed **and** the linked PR has open/unresolved review comments. This combination means the Reviewer has finished and the branch needs final fixes before merge.

Canonical source of truth:
- https://github.com/greatstrength/tiferet/blob/main/docs/collab/super_trd_workflow.md

## Closing procedure

### 1. Read all review comments
```bash
# pr-comments skill, or:
gh api /repos/greatstrength/tiferet/pulls/<pr-number>/reviews
gh api /repos/greatstrength/tiferet/pulls/<pr-number>/comments
```

Read every unresolved comment before making any code edits.

### 2. Check out the feature branch and address findings
```bash
git checkout <branch-name> && git pull origin <branch-name>
```

Address every actionable finding in code. Follow `tiferet-code-style` conventions. Push when done:
```bash
git push origin <branch-name>
```

### 3. Post a PR comment (optional for trivial fixes)
For non-trivial fixes, post a comment on the PR noting:
- What was addressed (scope-of-work bullets, no out-of-scope context).
- Your Warp conversation link (`https://app.warp.dev/conversation/...`).

For trivial fixes (e.g. a single annotation or comment-only change), the commit message on the push is sufficient — omit the PR comment.

### 4. Await user PR approval and merge
Stop here and wait for the developer to approve and squash-merge the PR.

### 5. Post-merge cleanup
After the PR is merged:
```bash
git checkout main && git pull origin main
git branch -d <branch-name>
```

### 6. Retrieve conversation links before drafting the Collaboration Report

Before drafting **any** part of the Collaboration Report:

1. Retrieve all PR comments: `pr-comments` skill or `gh api /repos/greatstrength/tiferet/pulls/<n>/reviews` + `/comments`.
2. Extract every `https://app.warp.dev/conversation/...` link present — one per Implementor comment, one in the Reviewer's review body.
3. Search each conversation for the AI↔Human exchange.
4. Only then begin drafting any part of the Collaboration Report.

A collaboration log written without consulting these conversations will be incomplete or inaccurate.

Use the `tiferet-collab-report` skill to post the Collaboration Report as a comment on the Super-TRD parent issue.

### 7. Rename the parent TRD file
Rename the Super-TRD parent's `.trd/` file to carry the `.complete.md` extension, signaling the entire Super-TRD workflow is done:
```bash
git mv .trd/<parent-name>.md .trd/<parent-name>.complete.md
git commit -m "Docs – rename Super-TRD parent TRD to .complete.md after merge"
```

### 8. GitHub issue and project status
**Verify automation before acting manually.** For Super-TRD PRs that include `Closes #<n>` in the body, GitHub auto-closes the parent issue on squash-merge and typically sets project status to Done.

- Check issue state: `gh issue view <n> --repo greatstrength/tiferet --json state`
- If already closed: **skip** manual close.
- If not closed: `gh issue close <n> --repo greatstrength/tiferet`
- Check project status in the GitHub UI or via GraphQL; if not Done, set it manually and set the End date via `gh project item-edit`.

### 9. Update the handoff
Update `.handoff/ddd-parity-agent-workflow.handoff.md`: session log, §6 parent tracking (all sub-issues `close: done`), and Super-TRD entry in the parents table (status → closed).
