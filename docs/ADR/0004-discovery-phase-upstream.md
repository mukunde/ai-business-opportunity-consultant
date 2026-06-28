# ADR 0004 - Discovery phase upstream of qualification

- Status: Accepted
- Date: 2026-06-28
- Deciders: Gael Mukunde

## Context

Alfred today starts at "I already have an opportunity, qualify it": an adaptive
interview fills four qualification slots, projects a context graph, scores,
recommends, reports. It is strong on qualification and prioritisation but has no
upstream Discovery: exploring a business and its processes to *surface* the
opportunities in the first place.

This ADR adds that upstream phase, scoped by an LLM-council session (2026-06-28)
to one cohesive module, not the nine-agent platform that was initially sketched.
Two constraints shaped the design:

- **Single core, not an agent swarm.** The council's verdict: keep one
  context-graph core; add capabilities incrementally, never as orchestrated silos.
- **Discovery must be feedable without a manual interview.** A separate POC (mail
  triage, see private notes) will later become an ingestion connector that dumps
  signals (volumes, irritants) into the graph. The interview must therefore be
  one *source* among several, not the only writer of context.

## Decision

Add an **additive** `app/discovery/` domain that reuses the shared core and leaves
the tested qualification engine untouched.

- **Reuse, don't refactor.** Discovery gets its own slot set (business context +
  one process + its pain points) and its own adaptive loop, but writes into the
  **same context-graph tables** (`ContextNode` / `Evidence`) and goes through the
  **same `LLMClient` abstraction** (new explicit methods `extract_discovery`,
  `detect_opportunities`; structured calls via `messages.parse`, deterministic
  `FakeLLM` stubs for offline tests). The qualification engine is not modified,
  so its tests are the regression net.
- **Ingestion seam from day one.** Context is written through a single internal
  path that accepts *signals* (a label, a value, an `Evidence` source). The
  interview is one producer of signals; a `DOCUMENT`/`METRIC`-typed ingestion
  endpoint is the seam the future mail connector plugs into. No connector is built
  now; only the seam.
- **Detector then promote.** On completion, an LLM detector turns the discovered
  context + pain points into **candidate opportunities**. Promoting a candidate
  creates a normal `Opportunity`, pre-seeded, entering the existing qualification
  pipeline. Discovery feeds qualification; it does not duplicate it.

## Rationale

- Additive build = zero regression risk on the revenue path (qualification),
  fastest safe delivery for a solo builder.
- One context graph keeps "single core" real; the interview and the future
  connector are interchangeable producers behind the ingestion seam.
- Detector + promote makes Discovery *lead into* qualification rather than
  becoming a parallel system, honouring "one module, not nine agents".

## Consequences

Positive:

- The upstream gap is closed without destabilising what works.
- The mail connector later needs only to call the ingestion seam; no rework.
- Candidate opportunities flow straight into scoring/recommendation/reporting.

Negative / trade-offs:

- A thin amount of loop logic is duplicated between the qualification and
  discovery flows rather than unified. Accepted under rule-of-three: unify only if
  a third flow appears. Premature generalisation of the tested engine carried more
  risk than the duplication.
- Discovery-detected candidates are only as good as the LLM detection; the offline
  `FakeLLM` stub is deterministic and shallow by design (real detection needs the
  live model).
