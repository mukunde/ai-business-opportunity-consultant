# ADR 0007 - Data readiness is an assessed quality, not slot presence

- Status: Accepted
- Date: 2026-06-27
- Deciders: Gael Mukunde

> Renumbered from 0004. Two ADRs were merged under that number; 0004 stayed with
> the discovery phase, which the code references by number in several modules.
> The Date above records when the decision was actually taken.

## Context

Feasibility on the scoring model is `data_readiness x 10`, and `data_readiness`
was the completeness of the `data_availability` slot: 1.0 if the question was
answered, 0.0 if not. This conflated two different things: "do we know the data
situation?" and "is the data actually usable?".

The bug it caused: a user who states "we have almost no usable data" fills the
slot, so data readiness reads 1.0 and feasibility maxes at 10. Every scored
opportunity landed at feasibility 10, so the portfolio matrix could never place
anything in **Strategic Bets** (high impact, low feasibility), and high-impact
ideas with poor data were mislabeled Quick Wins.

## Decision

Split the two meanings:

- **Context completeness / confidence** stays presence-based. Overall
  completeness is still the fraction of slots filled, because that is the right
  signal for "how much do we know" (it drives the score's confidence).
- **Data readiness becomes an LLM-assessed quality** on 0.0-1.0. The analyst
  extraction (`ExtractedContext.data_readiness`) now grades how usable the stated
  data is (0 = no usable data, 1 = abundant, clean, ready), from the content of
  what the user said. It flows through the interview state into the
  `data_readiness_score` completeness dimension, which feeds feasibility, risk and
  time-to-value. When data was not discussed, it falls back to slot presence, so
  behavior is unchanged where no assessment exists.

The deterministic `FakeLLM` keeps returning 1.0 when it answers the data slot
(offline tests stay stable); only the real model grades content.

## Rationale

- It matches the dimension's stated meaning. The UI tooltip already reads "Is
  there data available to build the AI on?", which is quality, not presence.
- It makes the portfolio quadrant meaningful: feasibility now varies, so Strategic
  Bets can exist.
- It reuses the existing LLM extraction path rather than adding a new mechanism;
  the assessment is grounded in stated facts, consistent with the analyst prompt's
  "do not invent" rule ("we have no data" is a low value, not a fabricated one).

## Consequences

Positive:

- Feasibility, risk and time-to-value reflect the real data situation.
- The scoring story is honest: poor data lowers feasibility and raises risk.

Negative / trade-offs:

- The `data_readiness` dimension is now semantically different from the other
  completeness dimensions (quality vs presence). Each dimension's tooltip carries
  its own meaning, and confidence stays presence-based, so this is acceptable, but
  it is an asymmetry to remember.
- Opportunities scored before this change keep their frozen completeness snapshot;
  they must be re-interviewed to pick up the assessed readiness. New assessments
  are correct from the start.
