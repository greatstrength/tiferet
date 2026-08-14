# Code Review

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. A pull request is where we argue about the diff. An issue is where we remember the session. Mixing those two jobs makes both worse.

## Two kinds of review

### A prototype PR (an RFP)

Read the RFP. Review the proposal, the acceptance criteria, and the distillation sections it cites. Do not review it against trunk. Do not ask the author to make proto look like `main`. That is the opposite of what this strand is for.

### A trunk PR (reconstruction or hotfix)

The first question is always the TRD's acceptance criteria — each child TRD, if this is a Super-TRD.

For reconstruction you *may* open proto, but only for artifacts the freeze and the TRD actually named. You are measuring, not merging. "Make trunk match proto" is almost never the right comment. If trunk is ahead — a later name, a cleaner shape — keep trunk and say so once.

A hotfix is reviewed against the hotfix TRD. Proto does not get a vote.

A Doc or skills PR has no TRD and no RFP. Review the diff against the intent in the PR and the vocabulary in [process.md](process.md).

## How to leave a diff comment

1. `gh pr view <n> --json number,headRefName,baseRefName,files` so you know what you are looking at.
2. Reconstruction measurement only: `git fetch origin <proto>` using the branch in [binding.md](binding.md), then `git diff origin/<proto>..HEAD -- <path>` restricted to AC-named artifacts.
3. Sort what you see:
   - **AC fail** — say so.
   - **Behind proto on a named artifact** — only a finding if it is also an AC fail, or the freeze named that artifact.
   - **Ahead** — note it once, do not ask anyone to revert it.
   - **Out of scope** — leave it alone.
4. A comment about a line goes on that line, and the line has to be in the PR diff. A comment about a missing file or a whole package goes in the review body.
5. Tell the human what you found and wait for a go-ahead before you post anything to GitHub.
6. One consolidated review via the reviews API (`path` + `position`, not `line`). The review body gets the findings summary and `Co-Authored-By: Oz <oz-agent@warp.dev>`. On a Super-TRD, the conversation link belongs on the **parent issue**, not as extra PR chatter.

Do not put implementor session notes, conversation-only logs, or Collaboration Reports on the PR. That is what the issue is for.

## Guardrails

A short, accurate review is kinder than a long one. Never recommend proto → trunk git. Never recommend reverting trunk that is ahead of proto. Check the code before you claim a behavior. Never commit or merge as part of a review.
