@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo [1/3] Checking Docker Desktop...
docker version >nul 2>&1
if errorlevel 1 (
  echo Docker Desktop is not running or Docker is not installed.
  echo Start Docker Desktop and run this file again.
  pause
  exit /b 1
)

echo Starting PostgreSQL + pgvector...
docker compose up -d postgres
if errorlevel 1 (
  echo Docker failed to start PostgreSQL.
  pause
  exit /b 1
)

echo Waiting for PostgreSQL to become healthy...
set /a attempts=0
:waitdb
set /a attempts+=1
set "health="
for /f "delims=" %%H in ('docker inspect -f "{{.State.Health.Status}}" studymate-postgres 2^>nul') do set "health=%%H"
if /i "!health!"=="healthy" goto dbready
if !attempts! GEQ 30 (
  echo PostgreSQL did not become healthy in time.
  docker compose logs postgres --tail 50
  pause
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto waitdb

:dbready
echo PostgreSQL is ready.
echo.
echo [2/3] Preparing Python environment...
if not exist ".venv\Scripts\python.exe" (
  py -3 -m venv .venv >nul 2>&1
  if errorlevel 1 python -m venv .venv
  if errorlevel 1 (
    echo Python 3 was not found. Install Python and run this file again.
    pause
    exit /b 1
  )
)

.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 (
  echo Failed to prepare pip.
  pause
  exit /b 1
)

.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Failed to install Python dependencies.
  pause
  exit /b 1
)

echo.
echo [3/3] Starting STUDYMATE API...
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

endlocal
