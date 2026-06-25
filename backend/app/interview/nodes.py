"""LangGraph nodes for the adaptive interview (TRD section 4.1).

Each node is a pure-ish function ``state -> partial state``. Nodes that need the
model are built by factories binding an ``LLMClient``; the gap analysis is
deterministic (explicit context engineering, not delegated to the LLM).
"""

from collections.abc import Callable

from app.interview.llm import LLMClient
from app.interview.state import (
    SLOT_KEYS,
    SLOT_REASONS,
    OpportunityState,
)

Node = Callable[[OpportunityState], dict]


def make_extract_context(llm: LLMClient) -> Node:
    """Node 2 - Context Discovery: fold the latest answer into known context."""

    def extract_context(state: OpportunityState) -> dict:
        answer = state.get("latest_answer", "").strip()
        if not answer:
            return {}  # first turn: nothing to extract yet
        extracted = llm.extract_context(
            state.get("raw_input", ""), answer, state.get("context", {})
        )
        context = dict(state.get("context", {}))
        for key in SLOT_KEYS:
            value = getattr(extracted, key, None)
            if value:
                context[key] = value
        assumptions = list(state.get("assumptions", [])) + list(extracted.assumptions)
        return {"context": context, "assumptions": assumptions}

    return extract_context


def gap_analysis(state: OpportunityState) -> dict:
    """Node 4 - Context Gap Analysis: compute missing slots and completeness."""
    context = state.get("context", {})
    missing = [key for key in SLOT_KEYS if not context.get(key)]
    completeness = (len(SLOT_KEYS) - len(missing)) / len(SLOT_KEYS)
    return {"missing": missing, "completeness": completeness}


def make_ask_question(llm: LLMClient) -> Node:
    """Node 3 - Adaptive Interview Loop: ask the next best question."""

    def ask_question(state: OpportunityState) -> dict:
        missing = state.get("missing", [])
        target = missing[0]
        question = llm.next_question(target, state)
        return {
            "next_question": question,
            "reasoning": SLOT_REASONS[target],
            "phase": "discovery",
            "done": False,
        }

    return ask_question


def make_structure(llm: LLMClient) -> Node:
    """Node 5 - Structuring: synthesize a structured opportunity."""

    def structure(state: OpportunityState) -> dict:
        result = llm.structure(state)
        return {
            "problem_statement": result.problem_statement,
            "summary": result.summary,
            "next_question": None,
            "reasoning": None,
            "phase": "structured",
            "done": True,
        }

    return structure
