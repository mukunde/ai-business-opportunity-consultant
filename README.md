# AI Business Opportunity Consultant

[![English](https://img.shields.io/badge/English-8A1C34?style=for-the-badge)](README.md)
[![Français](https://img.shields.io/badge/Fran%C3%A7ais-6E6662?style=for-the-badge)](README.fr.md)

Imagine an AI consultant that interviews your teams, understands your business
context, evaluates automation opportunities, and produces a structured,
implementation-ready recommendation.

**AI Business Opportunity Consultant** helps organizations discover, qualify,
prioritize, and validate AI opportunities before investing engineering effort.
It is a stateful reasoning system: adaptive interview, explicit context
engineering, operator-guided scoring, recommendation, human review, and a
generated handoff dossier.

The guiding idea: an AI opportunity is not worth building because a model can do
it. It is worth building when the context is complete enough to decide, and a
human has decided. The system makes that context explicit, and keeps the human in
the loop at every gate.

## Product demo

🎥 **[End-to-end video walkthrough (Loom)](https://www.loom.com/share/f655345c29024669ac4d07ba077a6989)**:
from an inbound customer-mail flow triaged by an n8n workflow, to detected
opportunities, qualification, scoring, human review, portfolio and the generated
handoff dossier. The UI is in French; the API and codebase are in English.

## Why this exists

- Organizations identify many AI ideas but struggle to prioritize them.
- Projects fail because the business context is incomplete when building starts.
- Teams start building before the value, the data and the owner are validated.
- Business and technical stakeholders lack a shared evaluation framework.

Most of the cost of a failed AI initiative is spent before anyone questions the
premise. This system moves that questioning to the front, cheaply and
systematically.

## What it does

```text
signals / raw idea
        |
   Discovery            surface candidate opportunities from business signals
        |
   Interview            adaptive questioning until the context is complete
        |
   Context graph        facts, unknowns, assumptions, typed edges, contradictions
        |
   Scoring              operator-guided criteria, computed priority
        |
   Recommendation       a proposed verdict with its rationale
        |
   Human review         approve or reject (the decision stays human)
        |
   Deliverables         on-demand handoff dossier for the delivery team
```

Alongside the pipeline: a **portfolio** view that places opportunities in a
priority quadrant, and **versioning** that snapshots an opportunity at each
significant transition.

## Example: from business signal to AI opportunity

The scenario from the demo video, end to end:

```text
Business signals (from the mail-triage workflow):
  repeated quote requests, quote follow-ups, complaints with order references
        |
Discovery:
  candidate opportunity detected: "Automated quote generation for kitchen sales"
        |
Promotion + interview:
  the consultant collects the four required context slots:
  business volume, handling time, data availability, process owner
        |
Context graph:
  facts (each backed by evidence), assumptions, remaining unknowns,
  typed relationships and contradictions across them
        |
Scoring (human, guided):
  the operator scores impact, ease and strategic fit on explicit criteria;
  the engine computes ROI, feasibility, risk and a final priority
        |
Recommendation:
  proposed verdict with rationale, e.g. "Quick Win: high impact, ready data"
        |
Human review:
  approved (or rejected), recorded with the reviewer's rationale
        |
Deliverables (on demand):
  condensed brief, implementation roadmap, PRD, TRD, UI/UX outline,
  backend schema, appflow: an implementation-ready dossier
```

## One workflow, two repositories

Discovery does not need a human conversation to start. This repository is the
downstream half of a complete chain; the upstream half lives in
[`ai-mail-triage-poc`](https://github.com/mukunde/ai-mail-triage-poc):

```text
ai-mail-triage-poc                          this repository
------------------                          ---------------
inbound customer mails                      discovery session
  -> n8n + Claude triage                      -> candidate opportunities
     (classify, extract, route)               -> qualification interview
  -> extracted customer needs                 -> scoring, recommendation
     pushed as business signals  ---------->  -> human review
                                              -> portfolio + handoff dossier
```

The idea behind the link: inbound mails express real, recurring frictions.
Instead of only routing them, the chain **turns them into qualified candidates
for automation**. Triage handles the flow; qualification exploits the deposit.

The bridge is plain HTTP, so any upstream system can feed signals the same way:

```text
POST /discovery                      create a session
POST /discovery/{id}/signal          push one business signal
POST /discovery/{id}/detect          run detection over the signals
GET  /discovery/{id}/opportunities   read the candidates
```

## What makes this different

| Generic AI assistants | AI Business Opportunity Consultant |
| --- | --- |
| Answer questions | Build decision context |
| Stateless conversations | Persistent opportunity lifecycle |
| The LLM decides everything | Deterministic rules + LLM reasoning, split on purpose |
| Generate text | Support validated business decisions |
| No traceability | Evidence records, versioning, audit trail |
| Human feedback after generation | Human approval as a workflow gate |

## How it works

**The interview is a turn engine, not a chatbot.** One LangGraph invocation
processes exactly one user turn: fold in the answer, recompute the context gap,
then either ask the next question or structure the opportunity. The multi-turn
loop lives across HTTP calls, with the database as the source of truth. See
`backend/app/interview/graph.py`.

**Context engineering is explicit.** The consultant must fill a fixed set of
required slots (business volume, handling time, data availability, process owner)
before it may structure anything. The gap analysis is deterministic code, not a
model judgement: completeness is simply the fraction of slots filled.

**The context graph is a projection.** Every turn, the interview state is
projected into persistent nodes (FACT / UNKNOWN / ASSUMPTION), each fact backed
by an evidence record. The projection is idempotent: wipe and rebuild, so no
stale node can survive. Once the context is complete, a single LLM pass infers
typed edges (SUPPORTS / DEPENDS_ON / REQUIRES) and contradictions across the
nodes. The model never sees database identifiers; nodes are handed opaque keys.

**A graph does not need a graph database.** Nodes and a typed edge table in
Postgres are enough at this volume, avoid an extra technology, and stay readable
by anyone who knows SQL. See [ADR 0001](docs/ADR/0001-context-graph-storage.md).

## Key design principles

- Deterministic logic where correctness matters; LLM reasoning only where
  ambiguity exists.
- Human approval remains the final decision point.
- Context is stored as a reusable business asset, with evidence.
- Every opportunity transition can be audited (versioning by snapshot).
- Database state is the source of truth; the engine is rebuilt from it each turn.
- Deliverables are generated on demand, never silently.

## Technical architecture

```text
                Next.js frontend (French UI)
                          |
                   FastAPI backend
                          |
    ------------------------------------------------
    |           |            |           |          |
Discovery   Interview     Scoring     Review    Reporting
    |           |            |           |          |
    ------------------------------------------------
                          |
                    Context layer
        (projection + LLM semantic enrichment)
                          |
                  PostgreSQL (Alembic)
                          |
                 LLM provider layer
             Claude API  /  deterministic fake
```

## Repository structure

```text
ai-business-opportunity-consultant/
├── backend/                 FastAPI, SQLAlchemy 2.0, Alembic, LangGraph
│   ├── app/
│   │   ├── api/routes/      context, discovery, interview, opportunities,
│   │   │                    recommendation, reporting, review, scoring, versions
│   │   ├── interview/       LangGraph state machine, nodes, prompts, LLM client
│   │   ├── context/         projection (deterministic) + enrichment (LLM)
│   │   ├── discovery/       upstream phase: signals to candidate opportunities
│   │   ├── scoring/         scoring engine
│   │   ├── recommendation/  verdict + rationale
│   │   ├── review/          human approve / reject
│   │   ├── reporting/       reports and on-demand deliverables
│   │   ├── versioning/      opportunity snapshots
│   │   ├── dashboard/       portfolio aggregation
│   │   └── models/          SQLAlchemy models
│   └── alembic/versions/    migrations 0001 to 0011
├── frontend/                Next.js App Router, TanStack Query, shadcn/ui
├── docs/
│   ├── ADR/                 architecture decision records
│   ├── PRD_v1.md            product requirements
│   ├── TRD_v1.md            technical requirements
│   ├── UX_UI_Design_v1.md
│   ├── Appflow_v1.md
│   ├── Backend_Schema_v1.md
│   └── Implementation_Plan_v1.md
├── docker-compose.yml       local Postgres
├── start-demo.ps1           one command local stack (Windows)
└── README.md
```

## Quickstart

Prerequisites: Docker Desktop, Python with [uv](https://docs.astral.sh/uv/),
Node.js.

```powershell
# 1. Configure the backend
cd backend
cp .env.example .env      # then set ANTHROPIC_API_KEY, or LLM_PROVIDER=fake

# 2. Start everything (Postgres, migrations, API, frontend)
cd ..
./start-demo.ps1
```

The script starts Postgres, waits for its health check, applies pending
migrations, then opens the API and the frontend in their own windows.

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

Flags: `-NoFrontend` (database and API only), `-SkipMigrations`.

### Try the demo

1. Create an opportunity (or feed signals through the discovery API).
2. Answer the adaptive interview questions; watch completeness climb.
3. Review the extracted context: facts, assumptions, unknowns, contradictions.
4. Score the opportunity on the guided criteria.
5. Read the recommendation, then approve or reject it as the human reviewer.
6. Generate the handoff dossier and browse the version history.

### Manual start

```powershell
docker compose up -d db

cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --reload

# in another terminal
cd frontend
npm run dev
```

The API binds `0.0.0.0` so a containerised client (for example the n8n triage
workflow) can reach it through `host.docker.internal:8000`. A loopback-only bind
cannot.

### Running without an API key

Set `LLM_PROVIDER=fake` to exercise the entire flow offline against a
deterministic stub: no key, no cost, and reproducible tests.

## Configuration

Backend settings are read from the environment or `backend/.env`
(see `backend/app/config.py`):

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | local compose Postgres | SQLAlchemy connection string |
| `LLM_PROVIDER` | `claude` | `claude` or `fake` (offline stub) |
| `ANTHROPIC_API_KEY` | none | required when `LLM_PROVIDER=claude` |
| `LLM_MODEL` | `claude-opus-4-8` | model id |
| `CONTEXT_COMPLETENESS_THRESHOLD` | `1.0` | when the interview may structure |
| `CORS_ORIGINS` | `http://localhost:3000` | allowed browser origins |

One more variable lives in a **root** `.env`, read by docker compose rather than
the application: `POSTGRES_HOST_PORT` (default `5432`) sets the host port for the
compose database, which is useful when a native Postgres already holds 5432.

Never commit `.env`. It is gitignored.

## Target users

- Innovation teams and AI labs qualifying use-case ideas before prototyping.
- Consulting firms running AI opportunity assessments.
- Enterprise teams prioritizing automation initiatives across departments.
- Product teams validating AI product ideas against real context.

## Project status

Implemented:

- ✅ Discovery pipeline (interview-driven or signal-driven)
- ✅ Adaptive qualification interview (LangGraph)
- ✅ Context graph with evidence, semantic edges and contradictions
- ✅ Operator-guided scoring and computed priority
- ✅ Recommendation with rationale
- ✅ Human review workflow (approve / reject)
- ✅ Portfolio dashboard (priority quadrant)
- ✅ Opportunity versioning by snapshot
- ✅ On-demand deliverables (brief, roadmap, PRD, TRD, UI/UX, schema, appflow)
- ✅ Upstream mail-triage ingestion (n8n workflow, separate repository)

Next:

- production authentication;
- multi-tenant support;
- systematic evaluation metrics for the LLM steps;
- more upstream connectors (ticketing, CRM) feeding discovery.

## Architecture decisions

- [ADR 0001](docs/ADR/0001-context-graph-storage.md) context graph storage
- [ADR 0002](docs/ADR/0002-llm-semantic-enrichment.md) LLM semantic enrichment
- [ADR 0003](docs/ADR/0003-opportunity-versioning-snapshot.md) versioning by snapshot
- [ADR 0004](docs/ADR/0004-discovery-phase-upstream.md) discovery phase upstream
- [ADR 0005](docs/ADR/0005-on-demand-deliverables.md) on-demand deliverables
- [ADR 0006](docs/ADR/0006-human-review-decision.md) human review decision
- [ADR 0007](docs/ADR/0007-data-readiness-assessed-not-presence.md) data readiness assessed, not presence

## Documents

- [PRD v1](docs/PRD_v1.md)
- [TRD v1](docs/TRD_v1.md)
- [UX/UI Design v1](docs/UX_UI_Design_v1.md)
- [Appflow v1](docs/Appflow_v1.md)
- [Backend Schema v1](docs/Backend_Schema_v1.md)
- [Implementation Plan v1](docs/Implementation_Plan_v1.md)
