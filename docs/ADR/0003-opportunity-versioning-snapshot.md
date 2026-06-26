# ADR 0003 - Opportunity versioning via denormalized snapshots

- Status: Accepted
- Date: 2026-06-27
- Deciders: Gael Mukunde

## Context

Phase 2, Epic 7 calls for opportunity versions, re-scoring and comparison. The
Backend Schema (v1) defines an `OpportunityVersion` entity (a "snapshot of the
opportunity at a point in time") with a single `summary` text field, plus a
`current_version` integer on the opportunity.

A user adds context, re-scores, and wants to compare where the assessment stood
before and after. The question is what a version stores so that two of them can
be compared, given how the underlying data behaves:

- Score snapshots and recommendations are already immutable and append-only
  (each re-score / re-decide inserts a new row; the latest wins).
- The context graph is a projection: the projector wipes and rebuilds an
  opportunity's nodes every interview turn (ADR 0001), so node ids are not stable
  across turns.

## Decision

Store each version as a **denormalized JSON snapshot** of the assessment, not as
a set of foreign keys to the rows that were current at cut time.

- A new `opportunity_versions` table holds `version_number` (monotonic per
  opportunity), an optional `note` (human label), the `snapshot` JSON, and
  `created_at`. `opportunities.current_version` tracks the latest number.
- The snapshot is assembled by reusing the reporting layer's
  `gather_report_data`, so a version and a report always tell the same story. It
  captures title, problem statement, summary, facts, assumptions, unknowns,
  completeness, the score fields, and the recommendation.
- Versions are cut explicitly (`POST /opportunities/{id}/versions`); listing and
  fetching are read-only. Comparison is computed client-side from two snapshots,
  so no diff endpoint is needed.

## Rationale

- **Comparison needs the values, not just references.** Diffing v1 and v2 means
  reading both states' scores, recommendations and completeness. A denormalized
  snapshot makes each version self-contained and trivially comparable.
- **The context graph cannot be referenced safely.** Because nodes are rebuilt
  every turn, foreign keys to facts/assumptions would dangle. Copying their values
  into the snapshot is the only faithful record.
- **A historical record should be frozen.** A version is meant to capture "what we
  believed then". Denormalization makes it immune to later schema or projection
  changes, which is the desired behavior for an audit trail.
- **Reuse over duplication of logic.** Routing the snapshot through
  `gather_report_data` keeps a single assembly path for "the current assessment".

## Consequences

Positive:

- Versions are self-contained, comparable, and stable over time.
- No new assembly logic; the reporting and versioning layers share one source.
- Re-scoring history already exists (append-only score snapshots); versioning
  gives it labeled, comparable checkpoints.

Negative / trade-offs:

- Data is duplicated: a snapshot copies values that also live in their own tables.
  Acceptable for small, opportunity-scoped records and the point of an audit trail.
- A snapshot will not reflect later improvements to scoring or reporting; it is a
  record of the past, by design.
- The schema's lone `summary` field is generalized into a structured snapshot.
  This is a deliberate extension to support the Epic 7 "Comparison" feature.
