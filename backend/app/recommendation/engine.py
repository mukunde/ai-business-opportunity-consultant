"""The recommendation engine (Appflow flow 8).

Maps a score snapshot to a decision. Confidence is the first gate: if context is
too incomplete to evaluate reliably, the system defers rather than concluding
(PRD principle: it must be allowed to say "we don't know yet"). Otherwise low
value or high risk -> do not pursue; low feasibility -> proceed with conditions;
else proceed.
"""

from app.models.recommendation import RecommendationType

# Decision thresholds (all sub-scores are on 0-10; confidence is 0-1).
CONFIDENCE_DEFER_BELOW = 0.6
FINAL_SCORE_MIN = 3.0
RISK_MAX = 7.0
FEASIBILITY_MIN = 6.0


def recommend(
    final_score: float,
    confidence: float,
    risk_score: float,
    feasibility_score: float,
) -> tuple[RecommendationType, str]:
    """Return the recommendation type and a human-readable rationale."""
    if confidence < CONFIDENCE_DEFER_BELOW:
        return (
            RecommendationType.DEFER,
            f"Context is too incomplete to evaluate reliably "
            f"(confidence {confidence:.2f}). Gather the missing context before "
            f"deciding.",
        )
    if final_score < FINAL_SCORE_MIN or risk_score >= RISK_MAX:
        return (
            RecommendationType.DO_NOT_PURSUE,
            f"Low priority (score {final_score:.2f}) or high risk "
            f"(risk {risk_score:.2f}). The value does not justify the effort.",
        )
    if feasibility_score < FEASIBILITY_MIN:
        return (
            RecommendationType.PROCEED_WITH_CONDITIONS,
            f"Promising (score {final_score:.2f}) but feasibility is limited "
            f"(feasibility {feasibility_score:.2f}); data preparation is required "
            f"first.",
        )
    return (
        RecommendationType.PROCEED,
        f"Strong opportunity: score {final_score:.2f}, feasibility "
        f"{feasibility_score:.2f}, risk {risk_score:.2f}, confidence "
        f"{confidence:.2f}.",
    )
