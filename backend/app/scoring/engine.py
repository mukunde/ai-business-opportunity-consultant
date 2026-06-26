"""The scoring engine (TRD section 6).

A deterministic v1 model. It combines analyst-judged inputs (Impact, Ease,
Strategic Alignment on 1-10, the classic ICE dimensions) with signals derived
from the context graph's completeness:

- confidence  = overall context completeness (the product principle: do not
  evaluate incomplete context as if it were complete).
- roi_score   = ROI readiness (volume + handling time known) -> can we size ROI.
- feasibility = data readiness (is there data to build on).
- risk_score  = rises with missing context and missing data.
- time_to_value = proxied by feasibility (more ready -> faster value).

All sub-scores are on 0-10. The final score uses the TRD weighted aggregation
(final = w1*ROI + w2*ICE + w3*StrategicAlignment - w4*Risk), clamped to 0-10.
"""

# Aggregation weights (must reflect TRD section 6.2).
W_ROI = 0.3
W_ICE = 0.3
W_STRATEGIC = 0.2
W_RISK = 0.2


def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return round(max(low, min(high, value)), 2)


def compute_scores(
    completeness: dict[str, float],
    impact: int,
    ease: int,
    strategic_alignment: int,
) -> dict[str, float]:
    """Return the eight ScoreSnapshot fields from context + analyst inputs."""
    overall = completeness["overall_score"]  # 0-1
    data_readiness = completeness["data_readiness_score"]
    roi_readiness = completeness["roi_readiness_score"]

    confidence_1_10 = max(1.0, overall * 10)  # ICE "Confidence" dimension

    roi_score = _clamp(roi_readiness * 10)
    feasibility_score = _clamp(data_readiness * 10)
    risk_score = _clamp((1 - overall) * 5 + (1 - data_readiness) * 5)
    time_to_value_score = _clamp(data_readiness * 10)
    impact_score = float(impact)
    strategic_score = float(strategic_alignment)

    # Classic ICE (Impact x Confidence x Ease), 1-1000; normalized to 0-10.
    ice = impact * confidence_1_10 * ease
    ice_normalized = ice / 100

    final = (
        W_ROI * roi_score
        + W_ICE * ice_normalized
        + W_STRATEGIC * strategic_score
        - W_RISK * risk_score
    )

    return {
        "roi_score": roi_score,
        "impact_score": impact_score,
        "feasibility_score": feasibility_score,
        "risk_score": risk_score,
        "strategic_alignment_score": strategic_score,
        "time_to_value_score": time_to_value_score,
        "final_score": _clamp(final),
        "confidence": round(overall, 2),
    }
