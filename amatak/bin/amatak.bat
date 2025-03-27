@echo off
:: Windows wrapper for amatak CLI

:: Find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    exit /b 1
)

:: Resolve root directory
set AMATAK_ROOT=%~dp0..
set AMATAK_ROOT=%AMATAK_ROOT:~0,-1%

:: Execute the module directly
python -m amatak.bin.amatak %*