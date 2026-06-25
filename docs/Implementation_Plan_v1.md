# AI Business Opportunity Consultant - Implementation Plan v1

## 1. Implementation Philosophy

### Guiding Principle

Build the smallest system capable of validating the core hypothesis.

### Core Hypothesis

A context-engineering-based consultant produces better AI opportunity assessments than a static qualification form.

### Therefore

For now, we are not building:

- multi-tenant
- SSO
- complex permissions
- distributed knowledge graph
- enterprise dashboard

We are building: a credible AI consultant.

## 2. Product Development Roadmap

```text
Phase 0
Foundations

  v

Phase 1
MVP

  v

Phase 2
Pilot Version

  v

Phase 3
Portfolio Showcase

  v

Phase 4
Enterprise Ready
```

## 3. Phase 0 - Foundations

### Objective

Validate architecture.

### Deliverables

Repository:

```text
backend/
frontend/
docs/
```

Documentation:

- PRD
- TRD
- UX
- Appflow
- Schema

### Architecture Spike

Validate:

- LangGraph
- LLM provider
- persistence strategy

### Exit Criteria

Able to:

- Create Opportunity
- Run Interview
- Store State

Estimated: `2-3 days`

## 4. Phase 1 - MVP

### Objective

Validate the core consulting workflow.

### Epic 1 - Opportunity Management

Feature: Create Opportunity

Tasks:

- Opportunity model
- CRUD endpoints
- persistence

Deliverable: `POST /opportunities`

### Epic 2 - Interview Engine

Objective: build the adaptive interview.

Tasks - LangGraph Setup:

- State definition
- Graph definition

Nodes:

- Intake
- Context Discovery
- Gap Analysis
- Interview Loop
- Structuring

Transitions:

- continue interview
- stop interview
- contradiction resolution

Deliverable - conversation capable of:

- Ask
- Learn
- Adapt

### Epic 3 - Context Engine

This is the product moat.

Tasks - create:

- Facts
- Unknowns
- Assumptions
- Evidence
- Contradictions

Deliverable: Context Graph stored in DB.

### Epic 4 - Scoring Engine

ROI Model: implement formulas from the qualification framework.

ICE:

- Impact
- Confidence
- Ease

Feasibility:

- Data
- Technical
- Operational

Risk:

- Business
- Technical
- Data

Deliverable: `Priority Score`

### Epic 5 - Recommendation Engine

Objective: generate recommendation.

Outputs:

- Proceed
- Proceed with Conditions
- Defer
- Do Not Pursue

Deliverable: Recommendation + rationale.

### Epic 6 - Reporting

Generate:

- Executive Summary
- Detailed Assessment

Output:

- Markdown
- PDF

### MVP Exit Criteria

User can:

- Create opportunity
- Run interview
- Receive recommendation
- Download report

Estimated: `3-5 weeks`

## 5. Phase 2 - Pilot Version

### Objective

Make the system usable by real teams.

### Epic 7 - Versioning

Features:

- Opportunity versions
- Re-scoring
- Comparison

### Epic 8 - Review Workflow

Features:

- Review
- Approve
- Reject

### Epic 9 - Opportunity Dashboard

Features:

- List
- Sort
- Filter
- Search

### Epic 10 - Opportunity Portfolio

Display:

- Quick Wins
- Strategic Bets
- Low Priority

Estimated: `3-4 weeks`

## 6. Phase 3 - Portfolio Showcase Version

### Objective

Build the version recruiters and hiring managers will see.

### Epic 11 - Consultant Cockpit UI

Implement:

- Context Completeness
- Opportunity Model
- Interview
- Scores

### Epic 12 - Visual Reasoning

Display:

- Known Facts
- Unknowns
- Assumptions
- Evidence

### Epic 13 - Explainability

Show:

- Why Score?
- Why Recommendation?
- Why Question?

### Result

This is the version that demonstrates:

- Product Thinking
- AI Engineering
- Context Engineering
- System Design

Estimated: `2-3 weeks`

## 7. Phase 4 - Enterprise Ready

Only after validation.

### Epic 14 - Authentication

- Auth
- RBAC

### Epic 15 - Collaboration

- Multi-user workshops
- Comments

### Epic 16 - Integrations

- Jira
- Notion
- Slack
- Teams

### Epic 17 - Knowledge Graph

Cross-opportunity learning.

### Epic 18 - Analytics

Measure:

- POCs avoided
- ROI realized
- Opportunity quality

## 8. Recommended Technical Stack

Backend:

- Python
- FastAPI
- LangGraph
- Pydantic

Database:

- Postgres

LLM:

- Claude or GPT

Frontend:

- Next.js
- Tailwind
- shadcn/ui

Reporting:

- Markdown
- PDF generation

## 9. Milestones

| Milestone | Scope |
| --------- | ----- |
| M1 | Opportunity Creation |
| M2 | Interview Engine |
| M3 | Context Graph |
| M4 | Scoring Engine |
| M5 | Recommendation Engine |
| M6 | Reporting |
| M7 | Consultant Cockpit |

## 10. Success Criteria

### Product Success

System successfully identifies, before recommendation:

- missing context
- assumptions
- feasibility risks

### User Success

User reports:

> "This feels like working with a consultant."

### Technical Success

Recommendation is traceable to:

- context
- evidence
- assumptions

## 11. Portfolio Positioning

This project must not be presented as:

- AI Agent
- RAG System
- Chatbot

It must be presented as:

> Context-Engineering-Based AI Business Opportunity Consultant
> for AI Opportunity Discovery, Qualification and Prioritization
