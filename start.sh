#!/bin/bash

cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

python3 -m pip install -r requirements.txt

python3 -m uvicorn main:app --reload --port 8000 > /dev/null 2>&1 &
cd ..

cd frontend

if [ ! -d "node_modules" ]; then
    npm install
fi

npm run dev