"""The interview engine state and the context model it fills.

Context engineering is explicit here: the consultant must collect a fixed set of
required context slots before it is allowed to structure the opportunity. Each
slot the model fills reduces the gap; completeness is the fraction filled. This
mirrors the PRD/Appflow examples (volume, handling time, data, ownership).
"""

from typing import Any, TypedDict

# Required context slots, in the order the consultant should pursue them.
# (key, human label, why it matters - used to phrase questions and explain gaps)
REQUIRED_SLOTS: list[tuple[str, str, str]] = [
    ("business_volume", "Business Volume", "drives potential value and ROI sizing"),
    ("handling_time", "Average Handling Time", "needed to estimate workload and savings"),
    ("data_availability", "Data Availability", "determines technical feasibility"),
    ("process_owner", "Process Owner", "needed to validate the problem and constraints"),
]

SLOT_KEYS: list[str] = [key for key, _, _ in REQUIRED_SLOTS]
SLOT_LABELS: dict[str, str] = {key: label for key, label, _ in REQUIRED_SLOTS}
SLOT_REASONS: dict[str, str] = {key: reason for key, _, reason in REQUIRED_SLOTS}


class OpportunityState(TypedDict, total=False):
    """LangGraph state for one interview turn.

    Rebuilt from the database on every HTTP call (DB is the source of truth),
    mutated by the graph nodes, then persisted back.
    """

    opportunity_id: str
    raw_input: str  # the original idea/description
    latest_answer: str  # the user's answer being processed this turn
    context: dict[str, str]  # filled slot_key -> value
    assumptions: list[str]
    missing: list[str]  # slot keys still unknown
    completeness: float
    next_question: str | None
    reasoning: str | None  # why the consultant asked the next question
    problem_statement: str | None
    summary: str | None
    phase: str  # "discovery" | "structured"
    done: bool


def initial_state(opportunity_id: str, raw_input: str) -> OpportunityState:
    """Build the starting state for a new interview."""
    return OpportunityState(
        opportunity_id=opportunity_id,
        raw_input=raw_input,
        latest_answer="",
        context={},
        assumptions=[],
        missing=list(SLOT_KEYS),
        completeness=0.0,
        next_question=None,
        reasoning=None,
        problem_statement=None,
        summary=None,
        phase="discovery",
        done=False,
    )


def from_dict(data: dict[str, Any]) -> OpportunityState:
    """Rehydrate persisted working state, tolerating older/partial payloads."""
    state = initial_state(data.get("opportunity_id", ""), data.get("raw_input", ""))
    state.update(data)  # type: ignore[typeddict-item]
    return state
