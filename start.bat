@echo off
REM CityFlow - arranque no Windows.
REM
REM Este .bat e o ponto de entrada recomendado: faz duplo-clique no
REM Explorer ou executa "start.bat" no PowerShell/CMD.
REM Invoca start.ps1 com -ExecutionPolicy Bypass apenas para esta
REM sessao, sem mexer na politica global do utilizador.

setlocal ENABLEDELAYEDEXPANSION
set "SCRIPT_DIR=%~dp0"

where powershell.exe >nul 2>nul
if errorlevel 1 (
    echo [ERRO] Nao encontrei o powershell.exe no PATH.
    echo        Instala o Windows PowerShell ou o PowerShell 7 e tenta novamente.
    pause
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start.ps1"
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo [AVISO] O start.ps1 terminou com codigo %EXITCODE%.
    pause
)

endlocal & exit /b %EXITCODE%
