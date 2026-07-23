# Project Fields — Tiferet Projects

**Project:** Tiferet Framework  
**Repository:** https://github.com/greatstrength/tiferet

## Purpose

This document defines the canonical GitHub Project field set used across all Tiferet-related projects (`greatstrength/tiferet`, `tiferet-*`, `Tiferet.*`). It complements the Status states and project assignment in [main.md](main.md) and the field/option IDs and example commands in [commands.md](commands.md). The goal is a single, consistent triage model — Priority, Size, story points, and dates — that an agent or human can apply identically on every project.

## Field Set

### Triage fields (set at triage / during the workflow)

- **Status** — workflow state: Ready → In progress → In review → Done (see [main.md](main.md)). All new issues start at **Ready**; use blocked-by relationships for dependency ordering rather than Backlog.
- **Priority** — `P0`/`P1`/`P2`; sequence and criticality.
- **Size** — `XS`–`XL`; fast t-shirt judgment.
- **Estimate** — numeric story points on a Fibonacci scale; the additive rollup/velocity metric. Kept under GitHub's built-in **Estimate** field name (it stores the point value).
- **Start date** / **End date** — actual cycle-time bounds.

### Automatic / contextual (no policy required)

Milestone, Labels, Repository, Linked pull requests, Assignees, Reviewers, Created, Updated, Closed, Parent issue, Sub-issues progress.

### Deferred

- **Iteration** — not used at this time. Agent-driven throughput is not bound to fixed, recurring human sprint capacity, and the **Milestone** already serves as the scope boundary while Priority + dependency order sequence the work. Keep the field defined (hidden) for future human-team adoption; if a cadence is ever required, treat the Milestone as the iteration rather than adding a parallel time-box.

## Status Workflow

Status tracks each issue through its lifecycle. Transitions are driven by branch, PR, and merge events and mirror the Per-Issue Workflow in [main.md](main.md):

1. **Ready** — issue created and ready to implement. Set **Priority**, **Size**, and **Estimate** at creation.
2. **In progress** — work has started / the feature branch is cut. Set the **Start date**.
3. **In review** — the PR is opened (targeting `main`). If review comments arrive, move back to **In progress**, address them, then return to **In review**.
4. **Done** — the PR is merged. Set the **End date** and **close the issue**.

In short: all new issues start at **Ready**; starting an issue → **In progress**; PR opened → **In review**; PR merged → **Done** + issue closed. **Backlog** is available but not used for new issues — blocked-by relationships communicate dependency ordering without reflecting it in Status.

## Priority

Priority is read off the TRD **Prerequisites** table rather than guessed:

- **P0** — critical path; the issue appears as a prerequisite for other issues (root/unblocker).
- **P1** — required for the milestone, independently workable, blocks little.
- **P2** — trailing or externally gated (tests, docs, companion-coupled work).

For feature releases (as opposed to parity/tracking milestones), Priority may also fold in user/business value.

## Size and Story Points

**Size** is the quick human judgment; **Estimate** is the additive numeric value derived from Size on a Fibonacci scale:

| Size | Estimate (points) | Typical TRD signature |
|------|-------------------|------------------------|
| XS | 1 | one file, trivial or no logic |
| S | 2 | rename-only, ≤ 3 files |
| M | 3 | small net-new unit, contained |
| L | 5 | net-new behavior **or** broad multi-file change |
| XL | 8 | complex net-new with edge cases, or high coupling |

### Sizing rubric (read from the TRD)

Score using signals already present in the TRD:

- number of rows in **Components Affected** (files touched);
- **new files / net-new behavior** vs. rename-only;
- count of **Acceptance Criteria**;
- cross-package risk or "land jointly with companion" coupling;
- number of **Prerequisites**.

Rename-only or few files → XS/S; net-new logic or a wide blast radius → L; coupling or high risk → bump one size.

### Splitting rules

- **XXL (≥ 13) — must split.** No single issue may exceed XL/8 points; break it into multiple TRDs/issues. This matches Agile guidance to decompose oversized stories and reinforces one-TRD-per-issue granularity.
- **XL (8) — consider splitting.** Treat XL as a soft warning rather than a hard stop: it is a gray area, so split when a natural seam exists and the pieces stand on their own; otherwise proceed as a single issue.

## Start / End Date

- **Start date** — set when Status → In progress (feature branch cut).
- **End date** — set when Status → Done (PR merged).

Together these give per-issue and per-milestone cycle time; the automatic **Created**/**Closed** timestamps serve as an audit backup. Agents set these as part of the per-issue workflow in [main.md](main.md) — two field writes, at the In progress and Done transitions.

## Cross-Project Standardization

1. **Same field set everywhere.** Field names, types, option sets, semantics, and the Size→points map above are identical across all Tiferet projects.
2. **IDs are per-project.** Field and option node IDs are unique to each GitHub Project, so automation must resolve them at runtime via `gh project field-list <number> --owner <org> --format json`. Known IDs are recorded in [commands.md](commands.md).
3. **Bootstrapping a new project.** Create the same fields on a fresh project: single-selects for Status, Priority, and Size; a number field for Estimate; and two date fields (Start date, End date). Leave Iteration unused. Then record the resolved IDs in [commands.md](commands.md).

## Worked Example — Milestone 1 (#28)

Applied values for the Domain Infrastructure milestone (≈ 34 points total):

| Issue | Priority | Size | Points |
|-------|----------|------|--------|
| #848 Domain Naming | P0 | S | 2 |
| #849 Mapper Naming | P0 | L | 5 |
| #850 Interfaces | P0 | M | 3 |
| #851 Utils TOML | P1 | M | 3 |
| #852 Request Validation | P1 | L | 5 |
| #853 Logging Settings | P1 | M | 3 |
| #854 Domain Cleanup | P2 | L | 5 |
| #855 Tests Relocation | P2 | L | 5 |
| #856 Docs | P2 | M | 3 |
