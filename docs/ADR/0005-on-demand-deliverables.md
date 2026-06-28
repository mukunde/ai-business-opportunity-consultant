# ADR 0005 - On-demand handoff deliverables

- Status: Accepted
- Date: 2026-06-28
- Deciders: Gael Mukunde

## Context

Alfred produces decision-ready outputs (executive summary, detailed assessment,
PDF) but stops at the recommendation. For a validated opportunity, a project team
or a Lab IA needs a richer, ready-to-pick-up dossier: a condensed brief, an
implementation roadmap, a PRD, a TRD, a UI/UX doc, a backend schema, an appflow.
This is the "downstream" the council flagged as the real differentiator (a
directly exploitable output, not one more idea generator).

Unlike the existing reports (deterministic Markdown rendered from data), these
documents are written by the LLM from the opportunity context, so the decision is
how to add LLM-authored documents without sprawl.

## Decision

Extend the existing reporting domain with **on-demand, per-kind deliverables**.

- A new `Deliverable` (opportunity_id, `kind`, markdown_content, generated_at) and
  a `DeliverableKind` enum (CONDENSED_BRIEF, IMPLEMENTATION_ROADMAP, PRD, TRD,
  UIUX, BACKEND_SCHEMA, APPFLOW). Migration 0010.
- **One generic LLM method** `generate_markdown(system, user)` on the existing
  `LLMClient` (Claude implementation + deterministic `FakeLLM` stub), not one
  method per kind. The per-kind difference is data: a `system_prompt(kind)` plus a
  shared `build_context(ReportData)` that **reuses `gather_report_data`** so a
  deliverable and a report always draw on the same assembled context.
- **On demand, one kind at a time** (`POST /opportunities/{id}/deliverables/{kind}`),
  not a batch, to bound cost and let the user pick what they need. Generation
  requires a recommendation (409 otherwise), consistent with reporting. Listing
  and fetching the latest of a kind are read-only.

## Rationale

- Reusing `gather_report_data` + the reporting tables keeps deliverables an
  extension, not a parallel system (one assembly path for "the opportunity's
  state").
- One generic `generate_markdown` + data-driven prompts means adding a document
  type is a prompt entry, not new code or a new model. Avoids the nine-method
  sprawl the council warned against.
- Per-kind, on-demand generation matches how a team actually uses a dossier (you
  generate the PRD when you need the PRD) and caps token spend.

## Consequences

Positive:

- The output is now a usable dossier, closing "vague idea -> exploitable handoff".
- New document types cost a prompt, not a migration.
- Deliverables are persisted and versionable (each generation is a row; latest
  wins on fetch), so they can be regenerated as the assessment evolves.

Negative / trade-offs:

- Quality depends entirely on the live model; the offline `FakeLLM` stub is a
  placeholder document, so the real value only shows against Claude.
- Deliverables read the *current* assessment, not a frozen version; regenerating
  after a re-score yields a different document. Acceptable: they are working
  artifacts, and versioning already snapshots the assessment separately (ADR 0003).
