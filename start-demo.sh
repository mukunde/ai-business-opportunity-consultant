#!/usr/bin/env bash
#
# Starts the local development stack: Postgres, the backend API, the frontend.
#
# Brings up the docker-compose Postgres service, waits for it to report healthy,
# applies any pending Alembic migrations, then launches the API and the frontend.
# This is the macOS and Linux counterpart of start-demo.ps1.
#
# The API binds 0.0.0.0 on purpose: a containerised n8n reaches it through
# host.docker.internal:8000, which does not work with a loopback-only bind.
#
# Usage:
#   ./start-demo.sh
#   ./start-demo.sh --no-frontend
#   ./start-demo.sh --skip-migrations

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
no_frontend=0
skip_migrations=0

for arg in "$@"; do
    case "$arg" in
        --no-frontend) no_frontend=1 ;;
        --skip-migrations) skip_migrations=1 ;;
        -h|--help) sed -n '3,18p' "${BASH_SOURCE[0]}"; exit 0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

step() { printf '\n>> %s\n' "$1"; }

pids=()
cleanup() {
    if [ ${#pids[@]} -gt 0 ]; then
        printf '\nStopping the API and the frontend...\n'
        kill "${pids[@]}" 2>/dev/null || true
        wait "${pids[@]}" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# --- 1. Docker must be running -------------------------------------------------
step "Checking Docker"
if ! docker info >/dev/null 2>&1; then
    echo "Docker does not respond. Start Docker and run this script again." >&2
    exit 1
fi
echo "   Docker is up."

# --- 2. Postgres ---------------------------------------------------------------
step "Starting Postgres (aiboc-db)"
docker compose -f "$root/docker-compose.yml" up -d db

printf '   Waiting for the health check...'
health=""
for _ in $(seq 1 30); do
    sleep 2
    printf '.'
    health="$(docker inspect --format '{{.State.Health.Status}}' aiboc-db 2>/dev/null || true)"
    [ "$health" = "healthy" ] && break
done
printf '\n'

if [ "$health" != "healthy" ]; then
    echo "Postgres is not healthy after 60s (last status: '$health'). Check: docker logs aiboc-db" >&2
    exit 1
fi
echo "   Postgres is healthy."

# --- 3. Migrations -------------------------------------------------------------
# Pending migrations are a common cause of runtime 500s (a missing table only
# fails when the feature is first used), so upgrade by default.
if [ "$skip_migrations" -eq 0 ]; then
    step "Applying migrations (alembic upgrade head)"
    (cd "$root/backend" && uv run alembic upgrade head)
    echo "   Database schema is up to date."
else
    step "Skipping migrations (--skip-migrations)"
fi

# --- 4. Backend ----------------------------------------------------------------
step "Starting the API"
(cd "$root/backend" && uv run uvicorn app.main:app --host 0.0.0.0 --reload) &
pids+=($!)
echo "   API   -> http://localhost:8000  (docs: /docs)"

# --- 5. Frontend ---------------------------------------------------------------
if [ "$no_frontend" -eq 0 ]; then
    step "Starting the frontend"
    (cd "$root/frontend" && npm run dev) &
    pids+=($!)
    echo "   Front -> http://localhost:3000"
else
    step "Skipping the frontend (--no-frontend)"
fi

printf '\nStack is running. Press Ctrl+C to stop the API and the frontend.\n'
printf 'Stop the database with: docker compose -f "%s/docker-compose.yml" stop db\n' "$root"
wait
