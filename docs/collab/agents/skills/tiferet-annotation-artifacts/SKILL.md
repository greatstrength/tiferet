---
name: tiferet-annotation-artifacts
description: Manage annotation artifacts (# ++ todo: and # -- obsolete:) in any Tiferet-family repo. Use this when the user asks to scan, add, or resolve annotation artifacts, or when a milestone session, TRD, or code review session needs a pre-implementation annotation inventory. Covers the formal syntax, when to add each type, the pre-session scan procedure, resolution procedure, and collaboration report integration.
---

# Manage Tiferet Annotation Artifacts

## When to use
Use this when:
- Starting any implementation or code review session in a Tiferet-family repo — run the scan procedure before touching affected files.
- Adding a `# ++ todo:` or `# -- obsolete:` annotation during implementation.
- Resolving (removing) an annotation after the described work is complete.
- Including annotation status in a Collaboration Report.

Canonical source of truth:
https://github.com/greatstrength/tiferet/blob/main/docs/core/code_style.md#annotation-artifacts

---

## Annotation types

### `# ++ todo: <message>`
- **Meaning**: deferred work attached to a specific artifact. `++` = *something to add or grow here*.
- **Remove when**: the described work is done. Never leave a `# ++ todo:` after the work it describes is complete.
- **Issue reference**: when the work is tracked in GitHub, include the issue number: `# ++ todo: #123 — remove attribute_id once tests are migrated`.

### `# -- obsolete: <reason or target version>`
- **Meaning**: the annotated artifact is deprecated and slated for removal. `--` = *something to reduce or remove*.
- **Remove when**: the artifact itself is deleted. Verify no callers remain before deletion.
- **Shorthand**: the `(obsolete)` parenthetical suffix on a `# *` or `# **` label is valid shorthand when no reason is needed. When a reason or target version is meaningful, add `# -- obsolete:` on its own line immediately after the label.

---

## Placement grammar

Annotations appear **immediately after** the structural comment they annotate, on their own line, before the code body:

```python
# * method: remove_service
# ++ todo: remove attribute_id parameter once the dependency with the app event tests has been resolved
def remove_service(self, service_id: str | None = None, attribute_id: str | None = None):
    ...

# * attribute: return_to_data (obsolete)
# -- obsolete: superseded by data_key; remove when callers are fully migrated
return_to_data: bool = Field(default=False, ...)
```

Annotations may appear below `# **` or `# ***` comments when they apply to an entire section or class. Inside method bodies, `# ++ todo:` follows inline-before-snippet placement like any other snippet comment.

---

## Pre-session scan procedure

**Before beginning any implementation session**, run this scan in the repository root and review the results:

```bash
grep -rn "# ++\|# --" tiferet/
```

For a Tiferet-family repo (not the canonical repo), substitute the package directory accordingly.

Review each open annotation and decide:
- Is it in scope for this session? If so, plan to resolve it.
- Is it out of scope? Note it so the Collaboration Report reflects its status.

Include the scan results (or a summary) when authoring a TRD to ensure the scope section accounts for any open annotations that the new work would touch.

---

## Resolution procedure

### Resolving `# ++ todo:`
1. Complete the described work.
2. Remove the `# ++ todo:` line from the source file.
3. If the annotation referenced a GitHub issue, confirm the issue is closed or the sub-task is complete.
4. Note the resolution in the Collaboration Report.

### Retiring `# -- obsolete:` with its artifact
1. Verify no callers reference the annotated artifact (search the codebase).
2. Delete the artifact and its `# -- obsolete:` annotation line together.
3. If the `(obsolete)` parenthetical shorthand was used on the `# *` label, remove that too.
4. Note the retirement in the Collaboration Report.

---

## Collaboration report integration

In the Collaboration Report (Section 2 — Code Components Touched or Section 3 — Deviations), note:

- Any `# ++ todo:` annotations introduced during the session (with the artifact and message).
- Any `# ++ todo:` annotations resolved (with the artifact and what was done).
- Any `# -- obsolete:` annotations introduced or retired (with the artifact and reason).

Example log entry:
> **AI** — Resolved `# ++ todo:` on `AppInterfaceAggregate.remove_service`: removed `attribute_id` parameter and updated all callers.
> **AI** — Retired `# -- obsolete:` on `EventFeatureStep.return_to_data`: deleted attribute, updated `FeatureConfigObject` mapper, confirmed no remaining callers.

---

## Quick reference

| Task | Action |
|---|---|
| Scan for open annotations | `grep -rn "# ++\|# --" tiferet/` |
| Add deferred-work note | `# ++ todo: <message>` after the `# *` label |
| Add obsolete marker with reason | `# -- obsolete: <reason>` after the `# *` label |
| Shorthand obsolete (no reason) | `# * method: foo (obsolete)` on the label line |
| Resolve a todo | Delete the `# ++ todo:` line; note in collab report |
| Retire an obsolete artifact | Delete artifact + annotation; verify no callers; note in collab report |
