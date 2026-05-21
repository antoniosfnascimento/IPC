@echo off
REM CityFlow - terminar e limpar portas (Windows).

setlocal ENABLEDELAYEDEXPANSION
set "SCRIPT_DIR=%~dp0"

where powershell.exe >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Nao encontrei o powershell.exe no PATH.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%stop.ps1"
endlocal & exit /b %ERRORLEVEL%
