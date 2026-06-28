"""A deterministic LLM double.

Used both by the test suite and by the ``LLM_PROVIDER=fake`` dev mode, so the
whole interview flow can be exercised end to end without an Anthropic API key.
It fills one context slot per answer and phrases canned questions, so an
interview reaches full completeness after exactly len(SLOT_KEYS) answers.
"""

from app.interview.llm import (
    ContextElement,
    DetectedOpportunity,
    DiscoveryExtraction,
    ExtractedContext,
    InferredGraph,
    InferredRelationship,
    OpportunityDetection,
    StructuredOpportunity,
)
from app.interview.state import SLOT_KEYS, SLOT_LABELS, OpportunityState

# Discovery interview slots, in pursuit order (mirrors DiscoveryExtraction fields).
_DISCOVERY_SLOTS = ["sector", "objectives", "process_name", "process_steps"]


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
        if target == "data_availability":
            # Deterministic stub: treat answered = fully data-ready. Real Claude
            # grades this from the content; see ANALYST_SYSTEM.
            fields["data_readiness"] = 1.0
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

    def extract_discovery(
        self, raw_input: str, latest_answer: str, known: dict[str, str]
    ) -> DiscoveryExtraction:
        target = next((k for k in _DISCOVERY_SLOTS if not known.get(k)), None)
        fields: dict[str, object] = {}
        if target is not None:
            fields[target] = latest_answer
        # The last slot (process steps) is where the stub surfaces a pain point.
        if target == "process_steps":
            fields["pain_points"] = ["Recopie manuelle d'informations entre outils"]
        return DiscoveryExtraction(**fields)

    def next_question_for(
        self, label: str, reason: str, raw_input: str, context: dict[str, str]
    ) -> str:
        return f"Quelle est la {label} ?"

    def detect_opportunities(
        self, context: dict[str, str], pain_points: list[str]
    ) -> OpportunityDetection:
        # One candidate per discovered pain point; empty if none surfaced.
        return OpportunityDetection(
            opportunities=[
                DetectedOpportunity(
                    title=f"Automatiser : {pp[:48]}",
                    target_pain_point=pp,
                    rationale="Tache repetitive et documentaire, candidate a une solution IA.",
                )
                for pp in pain_points
            ]
        )
