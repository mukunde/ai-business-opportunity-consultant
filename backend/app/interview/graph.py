"""The LangGraph interview state machine.

One invocation processes a single user turn: fold in the latest answer, recompute
the context gap, then either ask the next question or structure the opportunity.
The loop (TRD section 4.3) lives in the conditional edge: keep asking while
context completeness is below the configured threshold.
"""

from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.interview import nodes
from app.interview.llm import LLMClient
from app.interview.state import OpportunityState


def _make_router(threshold: float) -> Callable[[OpportunityState], str]:
    def route(state: OpportunityState) -> str:
        missing = state.get("missing", [])
        complete = state.get("completeness", 0.0) >= threshold
        return "structure" if (complete or not missing) else "ask"

    return route


def build_interview_graph(llm: LLMClient, threshold: float = 1.0) -> Any:
    """Compile the interview graph for a given LLM client and loop threshold."""
    graph = StateGraph(OpportunityState)

    graph.add_node("extract_context", nodes.make_extract_context(llm))
    graph.add_node("gap_analysis", nodes.gap_analysis)
    graph.add_node("ask_question", nodes.make_ask_question(llm))
    graph.add_node("structure", nodes.make_structure(llm))

    graph.add_edge(START, "extract_context")
    graph.add_edge("extract_context", "gap_analysis")
    graph.add_conditional_edges(
        "gap_analysis",
        _make_router(threshold),
        {"ask": "ask_question", "structure": "structure"},
    )
    graph.add_edge("ask_question", END)
    graph.add_edge("structure", END)

    return graph.compile()


def run_turn(llm: LLMClient, state: OpportunityState, threshold: float = 1.0) -> OpportunityState:
    """Run one interview turn and return the updated state."""
    graph = build_interview_graph(llm, threshold)
    result: OpportunityState = graph.invoke(state)
    return result
