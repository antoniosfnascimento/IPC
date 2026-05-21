#!/usr/bin/env bash
# CityFlow — terminar e libertar as portas 8000 e 5173 em macOS / Linux.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"

terminate_port() {
    local port="$1"
    local pids
    pids="$(lsof -t -i:"$port" 2>/dev/null || true)"
    if [ -z "$pids" ]; then
        printf '[INFO]  Porta %s já está livre.\n' "$port"
        return
    fi
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            printf '[INFO]  A terminar PID %s que ocupa a porta %s...\n' "$pid" "$port"
            kill -9 "$pid" 2>/dev/null || true
        fi
    done <<< "$pids"
}

terminate_port 8000
terminate_port 5173

if [ -f "$BACKEND_PID_FILE" ]; then
    rm -f "$BACKEND_PID_FILE"
fi

printf '[OK]    CityFlow desligado.\n'
