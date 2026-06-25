"""Deterministic LLM double for interview tests (no API key, no network)."""

from app.interview.llm import ExtractedContext, StructuredOpportunity
from app.interview.state import SLOT_KEYS, SLOT_LABELS, OpportunityState


class FakeLLM:
    """Fills one context slot per answer and phrases canned questions.

    Each answer resolves the first still-missing slot, so an interview reaches
    full completeness after exactly len(SLOT_KEYS) answers.
    """

    def extract_context(
        self, raw_input: str, latest_answer: str, known: dict[str, str]
    ) -> ExtractedContext:
        target = next((k for k in SLOT_KEYS if not known.get(k)), None)
        fields: dict[str, object] = {}
        if target is not None:
            fields[target] = latest_answer
        if target == "business_volume":
            fields["assumptions"] = ["Requests are repetitive"]
        return ExtractedContext(**fields)

    def next_question(self, target_slot: str, state: OpportunityState) -> str:
        return f"What is the {SLOT_LABELS[target_slot]}?"

    def structure(self, state: OpportunityState) -> StructuredOpportunity:
        ctx = state.get("context", {})
        return StructuredOpportunity(
            problem_statement="Structured problem from interview.",
            summary="Collected: " + ", ".join(f"{k}={v}" for k, v in ctx.items()),
        )
