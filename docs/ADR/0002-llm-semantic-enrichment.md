# ADR 0002 - LLM-driven semantic enrichment of the context graph

- Status: Accepted
- Date: 2026-06-27
- Deciders: Gael Mukunde

## Context

ADR 0001 stored the context graph relationally and deliberately left a gap: the
deterministic projection populates nodes (FACT / UNKNOWN / ASSUMPTION), evidence
and completeness, but not the typed edges (SUPPORTS, DEPENDS_ON, REQUIRES) or the
contradictions the schema provides for. Those require reasoning over the *content*
of the collected context, which a rule cannot do without becoming a brittle
keyword heuristic. They were parked until the real Claude client was wired.

With the Anthropic key now in place, this ADR records how that reasoning is
produced and persisted, and when it runs.

Constraints that shape the decision:

- Cost. Each LLM call is billed, so re-inferring on every interview turn is
  wasteful, and the early turns lack enough context to reason over anyway.
- The graph is a projection: the projector wipes and rebuilds an opportunity's
  nodes every turn, so any persisted edge must reference node ids that exist after
  the latest rebuild.
- The offline `FakeLLM` path (and the test suite) must still run end to end with
  no API key.
- The model must never be handed database UUIDs.

## Decision

Add a single capability to the `LLMClient` protocol, `infer_relationships`, that
takes the current context elements and returns typed edges plus contradictions.
Run it **once per interview, on the structuring turn** (when the interview reaches
`done`), as a separate enrichment step (`app/context/enrichment.py`) that follows
the deterministic projection.

- **One call over the complete context.** Enrichment runs only when the context is
  complete, so the model reasons over the whole picture with one request, not a
  partial one per turn.
- **Opaque keys.** Each connectable node (FACT, ASSUMPTION) is handed a synthetic
  key (`n0`, `n1`, ...). The model echoes those keys in its edges; the enrichment
  step maps them back to node ids and drops any unknown or self-referential key.
- **Two channels.** Relationship types are limited to SUPPORTS / DEPENDS_ON /
  REQUIRES. Conflicts flow through a dedicated `contradictions` list carrying a
  short `explanation`, persisted into the `contradictions` table (a new
  `description` column, migration 0007). CONTRADICTS is intentionally not a usable
  edge type, keeping "this relates to that" and "these two conflict" separate.
- **Idempotent.** Enrichment clears the opportunity's prior edges and
  contradictions before writing, mirroring the projection's rebuild semantics.
- **Offline stub.** `FakeLLM.infer_relationships` returns deterministic SUPPORTS
  edges (every element onto the first) and never fabricates contradictions, so the
  persistence path is exercised offline while honest about what a stub can know.

## Rationale

- **Cost and signal.** Gating on completion turns N calls per interview into one,
  on the only turn where the full context exists. Edges no longer flicker as the
  projector rebuilds each turn.
- **Separation of concerns.** The projector stays deterministic and unit-tested;
  the LLM reasoning lives in its own module behind the same provider abstraction
  as the rest of the interview engine.
- **Robustness.** Opaque keys plus defensive mapping mean a hallucinated or stale
  key is dropped, not persisted as a dangling edge.

## Consequences

Positive:

- The decision-phase view shows not just facts but how they connect and where they
  conflict, which is the consultant value the product promises.
- Contradiction explanations are stored and surfaced, not just the fact of a
  conflict.

Negative / trade-offs:

- Relationships appear only once the interview completes, not progressively. This
  matches "reason once the context is whole" and keeps cost bounded; a future
  iteration could re-enrich on demand.
- Re-deriving contradictions each enrichment discards any prior resolution state.
  Acceptable for the MVP (contradictions are surfaced, not yet workflow-managed);
  resolution tracking is a later concern.
- The offline stub cannot demonstrate contradiction detection; that is only
  meaningful against the real model (verified live on `claude-opus-4-8`).
