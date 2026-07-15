# AI Business Opportunity Consultant

A stateful reasoning system that turns a vague business need into a decision-ready,
transferable AI opportunity: adaptive interview, explicit context engineering,
scoring, recommendation, human review, and a generated handoff dossier.

The guiding idea: an AI opportunity is not worth building because a model can do
it. It is worth building when the context is complete enough to decide, and a
human has decided. The system makes that context explicit, and keeps the human in
the loop at every gate.

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

**Deterministic where it must be, model-driven where it pays.** Gap analysis,
routing, scoring arithmetic and completeness are plain code and stay auditable.
Extraction, questioning, structuring, semantic enrichment and document generation
call the model. The split is deliberate and documented in the ADRs.

**A graph does not need a graph database.** Nodes and a typed edge table in
Postgres are enough at this volume, avoid an extra technology, and stay readable
by anyone who knows SQL. See [ADR 0001](docs/ADR/0001-context-graph-storage.md).

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

The API binds `0.0.0.0` so a containerised client (for example an n8n workflow)
can reach it through `host.docker.internal:8000`. A loopback-only bind cannot.

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

## Ingestion beyond the interview

Discovery can be driven by an interview, or fed programmatically: post business
signals to a session and trigger detection, and candidate opportunities emerge
without a human conversation. This is what lets an upstream automation (for
example an n8n workflow that triages inbound customer mail) turn everyday
friction into qualified opportunity candidates.

```text
POST /discovery                      create a session
POST /discovery/{id}/signal          push one business signal
POST /discovery/{id}/detect          run detection over the signals
GET  /discovery/{id}/opportunities   read the candidates
```

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

## Status

The end-to-end flow is implemented and running locally: discovery, adaptive
interview, context graph, scoring, recommendation, human review, portfolio,
versioning, and on-demand deliverables, with a French UI over an English API.
