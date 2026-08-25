# ADR 0008 - Contradiction detection reads the transcript, not only the context graph

- Status: Accepted
- Date: 2026-07-15
- Deciders: Gael Mukunde

## Context

Contradiction detection ([ADR 0002](0002-llm-semantic-enrichment.md)) reasoned
over the context graph alone: the FACT and ASSUMPTION nodes produced by the
projection. Testing it against its own showcase example exposed a structural
blind spot.

A user was asked to describe their process and said, in the opening message:

> Every client request is unique, each one needs bespoke analysis.

then, three answers later:

> Actually I will contradict myself, it is highly repetitive: three quarters of
> requests are identical.

Nothing was detected. Not a failure of the model, but of what the model was
shown. Two mechanisms erase the conflict before detection runs:

1. **The extractor only keeps what fills one of the four required slots.**
   "Unique" and "repetitive" are neither a volume, a handling time, a data
   situation, nor an owner. Both statements were dropped; they survived only in
   the conversation.
2. **A slot holds a single value.** Had the user contradicted themselves within
   one slot ("500 requests" then "5000 requests"), the second answer would have
   overwritten the first. Again, nothing left to compare.

So the detector saw four mutually consistent facts and correctly reported no
tension. Contradictions were only reachable between two different slots, or
between an assumption and a fact. That is far narrower than the capability the
product claims, and it misses the canonical "repetitive vs every request is
unique" example carried in the Appflow.

## Decision

Give the enrichment step the interview transcript alongside the context nodes,
and let a contradiction be anchored in either place.

- `infer_relationships(elements, transcript)` now receives the conversation as it
  was actually said.
- `InferredContradiction` accepts two shapes. Between two context elements, the
  model sets `node_a_key` and `node_b_key` as before. Between two statements, it
  quotes each side verbatim in `claim_a` and `claim_b` and leaves the keys empty.
- `contradictions` gains nullable `claim_a` and `claim_b` columns (migration
  0012). The node ids were already nullable, since contradictions outlive node
  rebuilds.
- The cockpit renders a transcript-sourced tension as the two quoted statements
  instead of two node labels.

A conflict anchored to neither a node pair nor a claim pair is discarded: we only
persist tensions we can show the user.

## Rationale

- It fixes the capability where it is broken. The conflict exists in what the
  user said; showing the model only the distilled slots hid the evidence.
- It does not weaken context engineering. The four required slots, the gap
  analysis and the completeness calculation are untouched. The transcript is
  extra evidence for one reasoning step, not a new source of truth.
- It keeps the graph honest. Rather than fabricating nodes for statements that
  fill no slot, the contradiction carries the quotes itself. The projection stays
  a faithful projection.
- The alternative, capturing every notable claim as a node, would broaden the
  context model, blur the meaning of a FACT, and risk filling the graph with
  conversational noise. That is a larger change for a smaller gain.

## Consequences

Positive:

- Self-contradiction across turns is detectable, including the documented
  example.
- Quoting the two statements is stronger evidence for the user than two slot
  labels: they read their own words back.
- Enrichment still runs once, on the structuring turn, so cost is unchanged.

Negative / trade-offs:

- The prompt for that step now carries the whole transcript, so its input grows
  with interview length. Acceptable at the scale of a qualification interview
  (a handful of turns), and it remains a single call.
- Quoted claims are model-produced text rather than references to stored rows.
  They are displayed as quotations for that reason, and they cannot be resolved
  or linked the way node-anchored tensions can.
- Opportunities interviewed before this change keep their empty tension list;
  enrichment is not replayed retroactively.
