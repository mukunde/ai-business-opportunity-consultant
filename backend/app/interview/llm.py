"""LLM client abstraction for the interview engine.

The engine depends on the ``LLMClient`` protocol, not on a concrete provider, so
the graph runs identically against real Claude and against a deterministic
``FakeLLM`` in tests (no API key, no network). ``ClaudeClient`` follows the
Anthropic Python SDK patterns from the claude-api reference (model
``claude-opus-4-8``, ``messages.parse`` for structured extraction).
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel

from app.config import Settings
from app.interview import prompts
from app.interview.state import SLOT_LABELS, SLOT_REASONS, OpportunityState


class ExtractedContext(BaseModel):
    """Structured extraction target. Optional fields = "not stated"."""

    business_volume: str | None = None
    handling_time: str | None = None
    data_availability: str | None = None
    process_owner: str | None = None
    assumptions: list[str] = []


class StructuredOpportunity(BaseModel):
    """Synthesizer output once enough context is collected."""

    problem_statement: str
    summary: str


class LLMClient(Protocol):
    """What the interview nodes need from a language model."""

    def extract_context(
        self, raw_input: str, latest_answer: str, known: dict[str, str]
    ) -> ExtractedContext:
        """Pull stated facts/assumptions from the latest answer."""
        ...

    def next_question(self, target_slot: str, state: OpportunityState) -> str:
        """Phrase the single best next question for a missing context slot."""
        ...

    def structure(self, state: OpportunityState) -> StructuredOpportunity:
        """Synthesize the collected context into a structured opportunity."""
        ...


class ClaudeClient:
    """Anthropic Claude implementation of LLMClient."""

    def __init__(self, settings: Settings) -> None:
        import anthropic

        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.llm_model

    def extract_context(
        self, raw_input: str, latest_answer: str, known: dict[str, str]
    ) -> ExtractedContext:
        user = (
            f"Original idea:\n{raw_input}\n\n"
            f"Already known:\n{known or 'nothing yet'}\n\n"
            f"Latest answer from the user:\n{latest_answer}"
        )
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=1024,
            system=prompts.ANALYST_SYSTEM,
            messages=[{"role": "user", "content": user}],
            output_format=ExtractedContext,
        )
        result = response.parsed_output
        assert result is not None
        return result

    def next_question(self, target_slot: str, state: OpportunityState) -> str:
        user = (
            f"Original idea:\n{state.get('raw_input', '')}\n\n"
            f"Context collected so far:\n{state.get('context', {})}\n\n"
            f"You still need to learn the {SLOT_LABELS[target_slot]} "
            f"({SLOT_REASONS[target_slot]}). Ask for it."
        )
        response = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            thinking={"type": "adaptive"},
            output_config={"effort": "low"},
            system=prompts.CONSULTANT_SYSTEM,
            messages=[{"role": "user", "content": user}],
        )
        return next((b.text for b in response.content if b.type == "text"), "").strip()

    def structure(self, state: OpportunityState) -> StructuredOpportunity:
        user = (
            f"Original idea:\n{state.get('raw_input', '')}\n\n"
            f"Collected context:\n{state.get('context', {})}\n\n"
            f"Stated assumptions:\n{state.get('assumptions', [])}"
        )
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=prompts.SYNTHESIZER_SYSTEM,
            messages=[{"role": "user", "content": user}],
            output_format=StructuredOpportunity,
        )
        result = response.parsed_output
        assert result is not None
        return result


def get_llm() -> LLMClient:
    """FastAPI dependency: the LLM client selected by ``LLM_PROVIDER``.

    ``fake`` returns the deterministic offline stub (no API key); anything else
    returns the real Claude client.
    """
    from app.config import get_settings

    settings = get_settings()
    if settings.llm_provider == "fake":
        from app.interview.fake import FakeLLM

        return FakeLLM()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "LLM_PROVIDER is 'claude' but ANTHROPIC_API_KEY is not set. "
            "Add it to backend/.env, or set LLM_PROVIDER=fake to run offline."
        )
    return ClaudeClient(settings)
