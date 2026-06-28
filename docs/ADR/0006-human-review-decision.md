# ADR 0006 - Human review decision closing the lifecycle

- Status: Accepted
- Date: 2026-06-28
- Deciders: Gael Mukunde

## Context

The lifecycle ends at REVIEW (reached once a report is generated) but nothing
happens there: it is a dead-end. Implementation Plan Epic 8 asks for a review
workflow (Review / Approve / Reject), the Appflow recommends "Expert Review" on
low-confidence cases, and the product's key principle is that every recommendation
must be traceable to the context that produced it.

The decision is how a human sign-off sits on top of the AI recommendation, given
this is a single-operator tool (no real multi-user reviewer).

## Decision

Add a **human review decision** as an append-only record, not a mutable field.

- A new `Review` (opportunity_id, `decision` APPROVE/REJECT, optional `note`,
  created_at). Each decision is a row, so the history is preserved and auditable
  (the "traceable" principle), and re-reviewing is just a newer row.
- Two terminal lifecycle states are added: `APPROVED` and `REJECTED`. Recording a
  review sets the opportunity to the matching state. REVIEW remains the
  "report generated, awaiting sign-off" state.
- A review requires an existing recommendation (409 otherwise): you sign off on a
  decision the system actually made, keeping the audit chain intact.
- `POST /opportunities/{id}/review` records a decision; `GET .../review` returns
  the latest. The UI surfaces an approve/reject card and reflects the verdict;
  the dashboard can filter on the new statuses.

## Rationale

- Append-only record over a status-only field: the value here is governance and
  traceability (who decided what, when, why), which a single mutable flag would
  throw away. It mirrors how scores and recommendations are already append-only.
- Requiring a recommendation keeps every human verdict anchored to an AI output
  and its context, honouring the key product principle.
- For a single operator the "reviewer" is the operator, so this is deliberately a
  lightweight human-in-the-loop sign-off, not a multi-actor workflow. That is the
  right scope: it materialises the governance story (human gate + audit trail) a
  DSIR / Lab IA audience cares about, without inventing roles the tool has no users
  for.

## Consequences

Positive:

- The lifecycle is closed: an opportunity ends Approved or Rejected, on the record.
- The decision is auditable and re-doable; it reinforces the traceability principle.

Negative / trade-offs:

- The reviewer identity is not modelled (no users in the MVP); the decision is
  attributed to the operator implicitly. A real `reviewer_id` waits for auth.
- Adding enum values to the Postgres `opportunity_status` type requires a migration
  that runs `ALTER TYPE ... ADD VALUE` (supported on the project's PostgreSQL 16).
