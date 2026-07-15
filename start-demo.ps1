<#
.SYNOPSIS
    Starts the local development stack: Postgres, the backend API, the frontend.

.DESCRIPTION
    Brings up the docker-compose Postgres service, waits for it to report
    healthy, applies any pending Alembic migrations, then launches the API and
    the frontend, each in its own PowerShell window.

    The API binds 0.0.0.0 on purpose: a containerised n8n reaches it through
    host.docker.internal:8000, which does not work with a loopback-only bind.

.PARAMETER NoFrontend
    Start the database and the API only.

.PARAMETER SkipMigrations
    Do not run "alembic upgrade head" before starting the API.

.EXAMPLE
    ./start-demo.ps1

.EXAMPLE
    ./start-demo.ps1 -NoFrontend
#>
[CmdletBinding()]
param(
    [switch]$NoFrontend,
    [switch]$SkipMigrations
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

function Write-Step($message) {
    Write-Host ""
    Write-Host ">> $message" -ForegroundColor Cyan
}

# --- 1. Docker must be running -------------------------------------------------
Write-Step "Checking Docker"
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker does not respond. Start Docker Desktop and run this script again."
}
Write-Host "   Docker is up."

# --- 2. Postgres ---------------------------------------------------------------
Write-Step "Starting Postgres (aiboc-db)"
docker compose -f "$root/docker-compose.yml" up -d db
if ($LASTEXITCODE -ne 0) { throw "docker compose failed to start the db service." }

Write-Host "   Waiting for the health check..." -NoNewline
$deadline = (Get-Date).AddSeconds(60)
do {
    Start-Sleep -Seconds 2
    Write-Host "." -NoNewline
    $health = (docker inspect --format "{{.State.Health.Status}}" aiboc-db 2>$null)
    if ($health -eq "healthy") { break }
} while ((Get-Date) -lt $deadline)
Write-Host ""

if ($health -ne "healthy") {
    throw "Postgres is not healthy after 60s (last status: '$health'). Check: docker logs aiboc-db"
}
Write-Host "   Postgres is healthy."

# --- 3. Migrations -------------------------------------------------------------
# Pending migrations are a common cause of runtime 500s (a missing table only
# fails when the feature is first used), so upgrade by default.
if (-not $SkipMigrations) {
    Write-Step "Applying migrations (alembic upgrade head)"
    Push-Location "$root/backend"
    try {
        uv run alembic upgrade head
        if ($LASTEXITCODE -ne 0) { throw "alembic upgrade head failed." }
        Write-Host "   Database schema is up to date."
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Step "Skipping migrations (-SkipMigrations)"
}

# --- 4. Backend ----------------------------------------------------------------
Write-Step "Starting the API in a new window"
$apiCmd = "Set-Location '$root/backend'; uv run uvicorn app.main:app --host 0.0.0.0 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd | Out-Null
Write-Host "   API   -> http://localhost:8000  (docs: /docs)"

# --- 5. Frontend ---------------------------------------------------------------
if (-not $NoFrontend) {
    Write-Step "Starting the frontend in a new window"
    $webCmd = "Set-Location '$root/frontend'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $webCmd | Out-Null
    Write-Host "   Front -> http://localhost:3000"
}
else {
    Write-Step "Skipping the frontend (-NoFrontend)"
}

Write-Host ""
Write-Host "Stack is starting. Close the two windows to stop the API and the frontend." -ForegroundColor Green
Write-Host "Stop the database with: docker compose -f `"$root/docker-compose.yml`" stop db"
