"""Handoff-deliverable specs: per-kind label and generation prompt (ADR 0005).

Each deliverable is an LLM-written Markdown document, grounded in the opportunity
context assembled by ``gather_report_data``. The prompts here turn that context
into a project-ready artifact (the "dossier de reprise" a Lab IA or project team
can pick up).
"""

from app.models.reporting import DeliverableKind
from app.reporting.generator import ReportData

_PREAMBLE = (
    "You are a senior AI delivery consultant producing a handoff document for a "
    "validated AI opportunity. Write in clean Markdown, concrete and decision-ready, "
    "grounded ONLY in the provided context (state assumptions explicitly, never "
    "invent facts or numbers). No preamble, start with the document title. Match the "
    "language of the context.\n\nProduce: "
)

KIND_LABELS: dict[DeliverableKind, str] = {
    DeliverableKind.CONDENSED_BRIEF: "Condensed brief",
    DeliverableKind.IMPLEMENTATION_ROADMAP: "Implementation roadmap",
    DeliverableKind.PRD: "PRD",
    DeliverableKind.TRD: "TRD",
    DeliverableKind.UIUX: "UI/UX doc",
    DeliverableKind.BACKEND_SCHEMA: "Backend schema",
    DeliverableKind.APPFLOW: "Appflow",
}

_INSTRUCTIONS: dict[DeliverableKind, str] = {
    DeliverableKind.CONDENSED_BRIEF: (
        "a one-page condensed brief: the problem, the proposed AI solution, expected "
        "value, key risks, and the recommended next step."
    ),
    DeliverableKind.IMPLEMENTATION_ROADMAP: (
        "a phased implementation roadmap: milestones with rough durations, "
        "dependencies, required resources, and Go/No-Go gates."
    ),
    DeliverableKind.PRD: (
        "a Product Requirements Document: context, goals, target users, scope, user "
        "stories, success metrics, and explicit out-of-scope items."
    ),
    DeliverableKind.TRD: (
        "a Technical Requirements Document: target architecture, components, data and "
        "integrations, non-functional requirements, and technical risks."
    ),
    DeliverableKind.UIUX: (
        "a UI/UX document: the key screens, the main user flow, core components and "
        "their states (empty/loading/error), and accessibility notes."
    ),
    DeliverableKind.BACKEND_SCHEMA: (
        "a backend schema: the entities, their fields and types, and relationships, "
        "in clear Markdown (tables or pseudo-DDL)."
    ),
    DeliverableKind.APPFLOW: (
        "an application flow document: the end-to-end flows and state transitions, "
        "as readable text diagrams."
    ),
}


def system_prompt(kind: DeliverableKind) -> str:
    return _PREAMBLE + _INSTRUCTIONS[kind]


def build_context(data: ReportData) -> str:
    """Render the assembled opportunity data into a prompt-ready context block."""
    facts = "\n".join(f"- {label}: {value}" for label, value in data.facts) or "- (none)"
    lines = [
        f"# Opportunity: {data.title}",
        f"\n## Problem\n{data.problem_statement or 'not yet structured'}",
        f"\n## Proposed direction\n{data.summary or 'to be determined'}",
        f"\n## Facts\n{facts}",
        "\n## Assumptions\n" + ("\n".join(f"- {a}" for a in data.assumptions) or "- (none)"),
        "\n## Open unknowns\n" + ("\n".join(f"- {u}" for u in data.unknowns) or "- (none)"),
    ]
    if data.score:
        lines.append(
            f"\n## Scoring\n- Priority: {data.score['final_score']:.1f}/10"
            f"\n- ROI: {data.score['roi_score']:.1f}/10"
            f"\n- Feasibility: {data.score['feasibility_score']:.1f}/10"
            f"\n- Risk: {data.score['risk_score']:.1f}/10"
        )
    if data.recommendation_type:
        lines.append(
            f"\n## Recommendation\n{data.recommendation_type}: {data.recommendation_rationale}"
        )
    return "\n".join(lines)
