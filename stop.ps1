# CityFlow — terminar e libertar as portas 8000 e 5173 em Windows.
#
# Recomenda-se chamar via `stop.bat` para evitar o bloqueio da
# Execution Policy. Este script é tolerante: se uma porta já estiver
# livre, simplesmente avança.

$ErrorActionPreference = 'Continue'

$ports = @(8000, 5173)
$total = 0

foreach ($port in $ports) {
    $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $connections) {
        Write-Host "[INFO] Porta $port já está livre." -ForegroundColor DarkGray
        continue
    }

    $pidList = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $pidList) {
        try {
            $proc = Get-Process -Id $processId -ErrorAction Stop
            Write-Host "[INFO] A terminar PID $processId ($($proc.ProcessName)) que ocupa a porta $port..." -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction Stop
            $total++
        } catch {
            Write-Host "[AVISO] Não consegui terminar PID $processId : $_" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "[OK] $total processo(s) terminado(s). CityFlow desligado." -ForegroundColor Green
