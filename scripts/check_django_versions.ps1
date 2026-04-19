<#
.SYNOPSIS
  Compare Django version in Gymweb vs another local project (default: wiserwiz_gigxmatch).

.DESCRIPTION
  Run from anywhere, e.g.:
    pwsh -File scripts/check_django_versions.ps1
    pwsh -File scripts/check_django_versions.ps1 -OtherProject "D:\code\wiserwiz_gigxmatch"
#>
param(
    [string]$OtherProject = "C:\0_Coding\GitHub\wiserwiz_gigxmatch"
)

$ErrorActionPreference = "SilentlyContinue"

function Show-DjangoFromRequirements {
    param([string]$Root)
    $req = Join-Path $Root "requirements.txt"
    if (Test-Path $req) {
        Get-Content $req | Where-Object { $_ -match '^\s*Django' }
    }
    $py = Join-Path $Root "pyproject.toml"
    if (Test-Path $py) {
        Get-Content $py | Where-Object { $_ -match '[Dd]jango' -and ($_ -match 'dependencies|' -or $_ -match '"' -or $_ -match "'") } | Select-Object -First 5
    }
}

function Show-PipDjango {
    param([string]$Root)
    $py = Join-Path $Root ".venv\Scripts\python.exe"
    if (Test-Path $py) {
        Write-Host "Installed in .venv:" -ForegroundColor DarkGray
        & $py -m pip show Django 2>$null | Select-String "^(Name|Version):"
    }
    else {
        Write-Host "(no .venv\Scripts\python.exe — create venv or run: python -m pip show Django)" -ForegroundColor DarkGray
    }
}

# PSScriptRoot = ...\scripts  -> parent = repo root
$GymwebRoot = Split-Path $PSScriptRoot -Parent

Write-Host "`n=== Gymweb ($GymwebRoot) ===" -ForegroundColor Cyan
Write-Host "requirements.txt Django line(s):"
Show-DjangoFromRequirements $GymwebRoot
Show-PipDjango $GymwebRoot

Write-Host "`n=== Other project ($OtherProject) ===" -ForegroundColor Cyan
if (-not (Test-Path $OtherProject)) {
    Write-Host "Path not found. Pass -OtherProject with the correct folder." -ForegroundColor Yellow
    exit 1
}
Write-Host "requirements.txt / pyproject hints:"
Show-DjangoFromRequirements $OtherProject
Show-PipDjango $OtherProject

Write-Host "`n--- Global (whichever `python` is first on PATH) ---" -ForegroundColor Cyan
python -m pip show Django 2>$null | Select-String "^(Name|Version):"

Write-Host ""
