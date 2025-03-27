@echo off
:: Windows wrapper for amatak daemon

:: Find Python
where python3 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_EXEC=python3
) else (
    set PYTHON_EXEC=python
)

:: Resolve paths
set AMATAK_ROOT=%~dp0..
set AMATAK_ROOT=%AMATAK_ROOT:~0,-1%
set DAEMON_SCRIPT=%AMATAK_ROOT%\amatak\servers\daemon.py

:: Set Python path
set PYTHONPATH=%AMATAK_ROOT%;%AMATAK_ROOT%\Lib;%PYTHONPATH%

:: Parse arguments
set COMMAND=%1
if "%COMMAND%"=="" (
    echo Error: No command specified
    goto usage
)

:: Execute the command
if "%COMMAND%"=="start" (
    echo Starting amatakd...
    %PYTHON_EXEC% "%DAEMON_SCRIPT%" --config "%AMATAK_ROOT%\etc\amatakd.conf" --log "%AMATAK_ROOT%\logs\amatakd.log" --pid "%AMATAK_ROOT%\run\amatakd.pid" start
) else if "%COMMAND%"=="stop" (
    echo Stopping amatakd...
    %PYTHON_EXEC% "%DAEMON_SCRIPT%" --pid "%AMATAK_ROOT%\run\amatakd.pid" stop
) else if "%COMMAND%"=="restart" (
    echo Restarting amatakd...
    %PYTHON_EXEC% "%DAEMON_SCRIPT%" --config "%AMATAK_ROOT%\etc\amatakd.conf" --log "%AMATAK_ROOT%\logs\amatakd.log" --pid "%AMATAK_ROOT%\run\amatakd.pid" restart
) else if "%COMMAND%"=="status" (
    %PYTHON_EXEC% "%DAEMON_SCRIPT%" --pid "%AMATAK_ROOT%\run\amatakd.pid" status
) else (
    echo Error: Unknown command "%COMMAND%"
    goto usage
)

goto :eof

:usage
echo Amatak Daemon (amatakd) v0.1.0
echo Usage: amatakd [command]
echo Commands: start, stop, restart, status