@echo off
REM ---------------------------------------------------------------------------
REM  Gymweb - dev server launcher using .env.local (Windows)
REM
REM  What this does:
REM    1. Creates a local virtualenv in .venv (if missing)
REM    2. Installs requirements
REM    3. Loads .env.local (preferred) or .env so DB_* / DEBUG / SECRET_KEY
REM       / ALLOWED_HOSTS are picked up. Both short names and DJANGO_* names
REM       are accepted by settings.py.
REM    4. Applies migrations and seeds the default workout program
REM    5. Starts the Django dev server on port 5174 and opens it in a browser
REM ---------------------------------------------------------------------------

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PORT=5174"
set "HOST=127.0.0.1"

REM --- Pick env file ----------------------------------------------------------
set "ENV_FILE="
if exist ".env.local" (
    set "ENV_FILE=.env.local"
) else if exist ".env" (
    set "ENV_FILE=.env"
)

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

REM --- 3. Load env ------------------------------------------------------------
if defined ENV_FILE (
    echo [gymweb] Loading %ENV_FILE% ...
    for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
        set "_k=%%A"
        if not "!_k!"=="" if not "!_k:~0,1!"=="#" set "%%A=%%B"
    )
) else (
    echo [gymweb] No .env.local or .env found - using settings.py defaults.
    echo [gymweb] Copy .env.example to .env.local to customize.
)

REM --- 4. Migrate + seed ------------------------------------------------------
echo [gymweb] Applying database migrations ...
"%PY%" manage.py migrate --noinput
if errorlevel 1 (
    echo [gymweb] ERROR: migrations failed. Check your MySQL connection
    echo         ^(DB_HOST=!DB_HOST!, DB_NAME=!DB_NAME!, DB_USER=!DB_USER!^),
    echo         or set DB_ENGINE=sqlite in .env.local for a zero-config run.
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
