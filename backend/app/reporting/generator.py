"""Deterministic Markdown report generation (Appflow flows 9 and 10).

Pure functions over assembled data, so they are unit-testable without a database.
Sections follow the UX design (executive summary section 9, detailed assessment
section 10).
"""

from dataclasses import dataclass, field


@dataclass
class ReportData:
    """Everything the report generator needs, gathered from persisted entities."""

    title: str
    problem_statement: str | None = None
    summary: str | None = None
    facts: list[tuple[str, str]] = field(default_factory=list)  # (label, value)
    assumptions: list[str] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    completeness: dict[str, float] | None = None
    score: dict[str, float] | None = None
    recommendation_type: str | None = None
    recommendation_rationale: str | None = None


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- (none)"


def build_executive_summary(d: ReportData) -> str:
    """One-page, decision-oriented summary for a business audience."""
    score = d.score or {}
    impact_lines = (
        f"- Priority score: {score['final_score']:.2f} / 10\n"
        f"- ROI readiness: {score['roi_score']:.2f} / 10"
        if d.score
        else "- Not scored yet."
    )
    risk_line = f"- Risk score: {score['risk_score']:.2f} / 10" if d.score else "- Not scored yet."
    if d.recommendation_type:
        rec = f"**{d.recommendation_type}** - {d.recommendation_rationale}"
    else:
        rec = "No recommendation yet."

    return (
        f"# Executive Summary: {d.title}\n\n"
        f"## Business Problem\n{d.problem_statement or 'Not yet structured.'}\n\n"
        f"## Proposed Direction\n{d.summary or 'To be determined.'}\n\n"
        f"## Expected Impact\n{impact_lines}\n\n"
        f"## Risks\n{risk_line}\n"
        f"- Open unknowns: {', '.join(d.unknowns) if d.unknowns else 'none'}\n\n"
        f"## Recommendation\n{rec}\n"
    )


def build_detailed_assessment(d: ReportData) -> str:
    """Full structured breakdown of the reasoning and scoring."""
    facts = "\n".join(f"- {label}: {value}" for label, value in d.facts) if d.facts else "- (none)"

    completeness = "- Not computed yet."
    if d.completeness:
        c = d.completeness
        completeness = (
            f"- Business context: {c['business_context_score']:.2f}\n"
            f"- Process understanding: {c['process_understanding_score']:.2f}\n"
            f"- Data readiness: {c['data_readiness_score']:.2f}\n"
            f"- ROI readiness: {c['roi_readiness_score']:.2f}\n"
            f"- Overall: {c['overall_score']:.2f}"
        )

    scoring = "Not scored yet."
    if d.score:
        s = d.score
        scoring = (
            "| Dimension | Score |\n| --- | --- |\n"
            f"| ROI | {s['roi_score']:.2f} |\n"
            f"| Impact | {s['impact_score']:.2f} |\n"
            f"| Feasibility | {s['feasibility_score']:.2f} |\n"
            f"| Risk | {s['risk_score']:.2f} |\n"
            f"| Strategic alignment | {s['strategic_alignment_score']:.2f} |\n"
            f"| Time to value | {s['time_to_value_score']:.2f} |\n"
            f"| **Final** | **{s['final_score']:.2f}** |\n"
            f"| Confidence | {s['confidence']:.2f} |"
        )

    rec = "No recommendation yet."
    if d.recommendation_type:
        rec = f"**{d.recommendation_type}**\n\n{d.recommendation_rationale}"

    return (
        f"# Detailed Assessment: {d.title}\n\n"
        f"## Context Collected\n{facts}\n\n"
        f"## Assumptions\n{_bullets(d.assumptions)}\n\n"
        f"## Missing Information\n{_bullets(d.unknowns)}\n\n"
        f"## Context Completeness\n{completeness}\n\n"
        f"## Scoring\n{scoring}\n\n"
        f"## Alternatives Considered\nNot evaluated in this version.\n\n"
        f"## Recommendation\n{rec}\n"
    )
