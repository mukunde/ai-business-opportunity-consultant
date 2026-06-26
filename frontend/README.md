# Frontend - AI Business Opportunity Consultant

Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui. Consumes the
FastAPI backend; types are generated from the backend OpenAPI schema, so the API
contract is type-safe end to end.

## Stack

- Next.js + React + TypeScript
- Tailwind CSS + shadcn/ui (base-ui)
- TanStack Query for server state
- `openapi-typescript` generates `src/lib/api-types.ts` from the backend schema

## Getting started

```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Backend must be running (see ../backend/README.md):
#   cd ../backend && uv run uvicorn app.main:app --reload   (LLM_PROVIDER=fake works key-less)

npm run dev                  # http://localhost:3000
```

## Common commands

```bash
npm run dev          # dev server
npm run build        # production build (also type-checks)
npm run lint         # eslint
npm run gen:api      # regenerate API types from the backend OpenAPI schema
```

## Regenerating the API client

`src/lib/api-types.ts` is generated. After changing backend endpoints/schemas:

```bash
# from backend/, dump the schema, then generate types
cd ../backend && uv run python -c "import json,sys; from app.main import app; sys.stdout.write(json.dumps(app.openapi()))" > ../frontend/openapi.json
cd ../frontend && npm run gen:api
```

## Slices

- F1 (this slice): dashboard - list and create opportunities.
- F2: interview cockpit (conversation, live context model, completeness).
- F3: scoring, recommendation, report views.
