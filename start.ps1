Set-Location backend

if (-not (Test-Path "venv")) {
    python -m venv venv
}

.\venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt

Start-Process python -ArgumentList "-m uvicorn main:app --reload --port 8000" -WindowStyle Hidden

Set-Location ..

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev
