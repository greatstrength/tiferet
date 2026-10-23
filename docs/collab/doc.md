# Doc - Documentation and Skills

**Project:** Tiferet Framework
**Repository:** https://github.com/greatstrength/tiferet

[process.md](process.md) is the index. This page is the lightest of the three strands: you are changing the words we use to work, not the software those words describe.

## What belongs here

Standalone documentation and agent-skill changes - collaboration guides, style docs, the README, tutorials, the committed skills in `.agents/skills/`. Not a reconstruction. Not a hotfix. Process-skill rewrites are Doc PRs.

**You do not need an issue or a TRD.** You do not need a milestone, a project-board item, or a release. The pull request *is* the authorizing document. Docs evolve with the situation, so they go straight to a branch and a PR. Write the title and body in the language of this process - trunk, prototype, catalog, freeze, RFP, TRD, issue versus PR - so someone six months from now can tell what you did without a specification sitting next to it.

A Doc PR has no issue, no TRD, no milestone, no project-board item, and no `Closes #N`. Do not open an issue for it. Discussion lives on the PR. It is still a PR: agents never push to `main`. Squash-merge is [qa_operator.md](qa_operator.md) or the maintainer ([process.md § Agent guardrails](process.md#agent-guardrails)).

If a Doc PR body lists acceptance criteria, every box starts unchecked. The reviewer checks each one as it verifies it.

## The branch

From `main`: `docs-<lowercase-hyphenated-context>`.

`docs-process-collab-and-agents-skills` and `docs-contribution-streams` are the idea.

## The loop

1. Cut the branch from `main`.
2. Write the docs or skills. New or rewritten skills follow [agents/SKILL_TEMPLATE.md](agents/SKILL_TEMPLATE.md). Skills stay terse; these guides may take a breath.
3. Open a PR targeting `main`. Title it `Docs - <Capitalized Semantic Title>`. Do not link an issue, add a milestone, or add a project-board item. The body says what changed and why.
4. Review comments and short status notes stay on the PR.
5. After the squash-merge, pull `main` and delete the local branch.

## Guide-doc changes

If you are adding or updating something under `docs/guides/`, start from the matching genre template in [docs/guides/templates/](../guides/templates/) rather than inventing a sibling from memory. The **`tiferet-guide-docs`** skill is the short version of that advice.

## Distillation on proto is not this stream

When an RFP settles a decision and you fold it into the distillation **on the prototype branch**, that is prototype work. It rides with the RFP, not with a Doc PR on trunk.

Bringing that distillation onto trunk happens after a catalog freeze - either as a Doc PR, or as part of the reconstruction milestone. Either way, do not introduce proto vocabulary on trunk that the freeze did not name. Trunk should not have to guess.
