"""A deterministic LLM double.

Used both by the test suite and by the ``LLM_PROVIDER=fake`` dev mode, so the
whole interview flow can be exercised end to end without an Anthropic API key.
It fills one context slot per answer and phrases canned questions, so an
interview reaches full completeness after exactly len(SLOT_KEYS) answers.
"""

from app.interview.llm import (
    ContextElement,
    ExtractedContext,
    InferredGraph,
    InferredRelationship,
    StructuredOpportunity,
)
from app.interview.state import SLOT_KEYS, SLOT_LABELS, OpportunityState


class FakeLLM:
    """Deterministic, offline implementation of LLMClient."""

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

    def infer_relationships(self, elements: list[ContextElement]) -> InferredGraph:
        # Deterministic, content-free stub: hub every element onto the first with
        # a SUPPORTS edge. Enough to exercise persistence; it never fabricates
        # contradictions (that requires real reasoning over the content).
        if len(elements) < 2:
            return InferredGraph()
        hub = elements[0].key
        return InferredGraph(
            relationships=[
                InferredRelationship(source_key=e.key, target_key=hub, relation_type="SUPPORTS")
                for e in elements[1:]
            ]
        )
