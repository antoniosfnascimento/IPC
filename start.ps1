# CityFlow — arranque automatizado em Windows.
#
# Recomenda-se chamar este script através de `start.bat`, que define
# `-ExecutionPolicy Bypass` apenas para esta sessão, evitando o problema
# clássico em que o Windows recusa correr ficheiros .ps1 não assinados.
#
# Se Python ou Node.js não estiverem instalados, o script tenta instalá-los
# via `winget` (disponível por defeito em Windows 10 1809+ e Windows 11).
# Caso o winget não esteja presente, o script informa as URLs de download
# manual e fica de molho.

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $RepoRoot 'backend'
$FrontendDir = Join-Path $RepoRoot 'frontend'

function Write-Section($message) {
    Write-Host ''
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Test-CommandExists([string]$name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

function Refresh-Path {
    # Recarrega a variável PATH a partir do registo, para que comandos
    # instalados durante esta sessão (Python, Node) fiquem disponíveis
    # sem o utilizador ter de reabrir o terminal.
    $machine = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user    = [System.Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
}

function Install-WithWinget([string]$packageId, [string]$displayName) {
    if (-not (Test-CommandExists 'winget')) {
        Write-Host "[ERRO] $displayName não está instalado e o winget não está disponível neste sistema." -ForegroundColor Red
        Write-Host "       Instala manualmente:" -ForegroundColor Yellow
        Write-Host "         - Python 3.10+ : https://www.python.org/downloads/windows/" -ForegroundColor Yellow
        Write-Host "         - Node.js LTS  : https://nodejs.org/en/download" -ForegroundColor Yellow
        Write-Host "       Depois corre novamente este script." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[INFO] A instalar $displayName via winget ($packageId)..." -ForegroundColor Yellow
    & winget install --id $packageId -e --silent --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] A instalação de $displayName falhou (winget exitcode=$LASTEXITCODE)." -ForegroundColor Red
        exit 1
    }
    Refresh-Path
}

function Resolve-Python {
    # Preferimos `py -3` (Python launcher para Windows) porque honra
    # automaticamente a versão 3 mais recente instalada.
    foreach ($candidate in @('py', 'python', 'python3')) {
        if (Test-CommandExists $candidate) {
            $argList = if ($candidate -eq 'py') { @('-3', '--version') } else { @('--version') }
            try {
                $version = & $candidate @argList 2>$null
                if ($LASTEXITCODE -eq 0 -and $version -match 'Python\s+3') {
                    return @{ Exe = $candidate; LauncherArgs = if ($candidate -eq 'py') { @('-3') } else { @() } }
                }
            } catch { }
        }
    }
    return $null
}

# ---------------------------------------------------------------------------
# 1. Garantir Python
# ---------------------------------------------------------------------------
Write-Section 'A verificar Python'
$python = Resolve-Python
if (-not $python) {
    Install-WithWinget -packageId 'Python.Python.3.12' -displayName 'Python 3.12'
    $python = Resolve-Python
    if (-not $python) {
        Write-Host "[ERRO] Python ainda não está acessível após a instalação. Fecha e reabre o terminal." -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] Python detetado: $($python.Exe) $($python.LauncherArgs -join ' ')" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Garantir Node.js
# ---------------------------------------------------------------------------
Write-Section 'A verificar Node.js'
if (-not (Test-CommandExists 'node')) {
    Install-WithWinget -packageId 'OpenJS.NodeJS.LTS' -displayName 'Node.js LTS'
    if (-not (Test-CommandExists 'node')) {
        Write-Host "[ERRO] Node ainda não está acessível após a instalação. Fecha e reabre o terminal." -ForegroundColor Red
        exit 1
    }
}
$npmCmd = if (Test-CommandExists 'npm.cmd') { 'npm.cmd' } else { 'npm' }
Write-Host "[OK] Node detetado: $(node --version)" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Preparar o backend (venv + requirements)
# ---------------------------------------------------------------------------
Write-Section 'A preparar o backend (venv + dependências)'
Push-Location $BackendDir
try {
    $venvDir = Join-Path $BackendDir 'venv'
    $venvPython = Join-Path $venvDir 'Scripts\python.exe'

    if (-not (Test-Path $venvDir)) {
        Write-Host "[INFO] A criar ambiente virtual em $venvDir..." -ForegroundColor Yellow
        & $python.Exe @($python.LauncherArgs + @('-m', 'venv', 'venv'))
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERRO] Falha a criar o venv (exitcode=$LASTEXITCODE)." -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "[INFO] A garantir pip atualizado e a instalar requirements..." -ForegroundColor Yellow
    & $venvPython -m pip install --upgrade pip | Out-Null
    & $venvPython -m pip install -r 'requirements.txt'
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERRO] A instalação dos requirements do backend falhou." -ForegroundColor Red
        exit 1
    }

    Write-Host "[OK] Backend pronto." -ForegroundColor Green
    Write-Host "[INFO] A arrancar o uvicorn em http://localhost:8000..." -ForegroundColor Yellow
    Start-Process -FilePath $venvPython -ArgumentList @('-m', 'uvicorn', 'main:app', '--reload', '--port', '8000') -WorkingDirectory $BackendDir
} finally {
    Pop-Location
}

# ---------------------------------------------------------------------------
# 4. Preparar o frontend (npm install + dev)
# ---------------------------------------------------------------------------
Write-Section 'A preparar o frontend'
Push-Location $FrontendDir
try {
    if (-not (Test-Path (Join-Path $FrontendDir 'node_modules'))) {
        Write-Host "[INFO] A instalar dependências do frontend (npm install)..." -ForegroundColor Yellow
        & $npmCmd install
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERRO] npm install falhou (exitcode=$LASTEXITCODE)." -ForegroundColor Red
            exit 1
        }
    }

    Write-Host "[OK] Frontend pronto." -ForegroundColor Green
    Write-Host "[INFO] A arrancar o servidor de desenvolvimento Vite (Ctrl+C para sair)..." -ForegroundColor Yellow
    & $npmCmd run dev
} finally {
    Pop-Location
}
