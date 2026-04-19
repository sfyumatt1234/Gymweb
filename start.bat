@echo off
REM ---------------------------------------------------------------------------
REM  Gymweb - one-click dev server launcher (Windows)
REM
REM  What this does:
REM    1. Creates a local virtualenv in .venv (if missing)
REM    2. Installs requirements
REM    3. Loads .env (if present) so DB_* / DJANGO_* settings are picked up
REM    4. Applies migrations and seeds the default workout program
REM    5. Starts the Django dev server on port 5174 and opens it in the browser
REM ---------------------------------------------------------------------------

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PORT=5174"
set "HOST=127.0.0.1"

REM --- 1. Virtual environment -------------------------------------------------
if not exist ".venv\Scripts\python.exe" (
    echo [gymweb] Creating virtual environment in .venv ...
    py -3 -m venv .venv 2>nul
    if errorlevel 1 (
        python -m venv .venv
        if errorlevel 1 (
            echo [gymweb] ERROR: could not create venv. Install Python 3.10+ from python.org.
            exit /b 1
        )
    )
)

set "PY=.venv\Scripts\python.exe"
set "PIP=.venv\Scripts\pip.exe"

REM --- 2. Dependencies --------------------------------------------------------
echo [gymweb] Installing/updating dependencies ...
"%PY%" -m pip install --upgrade pip >nul
"%PIP%" install -r requirements.txt
if errorlevel 1 (
    echo [gymweb] WARN: mysqlclient may have failed to build. PyMySQL fallback will be used.
)

REM --- 3. Environment ---------------------------------------------------------
if exist ".env" (
    echo [gymweb] Loading .env ...
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set "_k=%%A"
        if not "!_k!"=="" if not "!_k:~0,1!"=="#" set "%%A=%%B"
    )
) else (
    echo [gymweb] No .env found - using defaults ^(DB_ENGINE=mysql, DB_HOST=127.0.0.1, DB_NAME=gymweb^).
    echo [gymweb] Copy .env.example to .env to customize, or set DB_ENGINE=sqlite for a zero-config run.
)

REM --- 4. Migrate + seed ------------------------------------------------------
echo [gymweb] Applying database migrations ...
"%PY%" manage.py migrate --noinput
if errorlevel 1 (
    echo [gymweb] ERROR: migrations failed. Check your MySQL connection ^(or set DB_ENGINE=sqlite^).
    exit /b 1
)

echo [gymweb] Seeding default workout program ^(idempotent^) ...
"%PY%" manage.py seed_program

REM --- 5. Run server ----------------------------------------------------------
echo.
echo [gymweb] Starting development server at http://%HOST%:%PORT%/
echo [gymweb] Press Ctrl+C to stop.
start "" "http://%HOST%:%PORT%/"
"%PY%" manage.py runserver %HOST%:%PORT%

endlocal
