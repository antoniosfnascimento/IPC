#!/usr/bin/env bash
# CityFlow — arranque automatizado em macOS / Linux.
#
# Verifica Python 3 e Node.js; se estiverem em falta, tenta instalar
# via Homebrew (macOS) ou apt (Linux Debian/Ubuntu). Cria o virtualenv
# do backend e o node_modules do frontend automaticamente.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
BACKEND_LOG="$SCRIPT_DIR/.backend.log"
BACKEND_PID_FILE="$SCRIPT_DIR/.backend.pid"

section()  { printf '\n==> %s\n' "$1"; }
info()     { printf '[INFO] %s\n'    "$1"; }
ok()       { printf '[OK]   %s\n'    "$1"; }
warn()     { printf '[AVISO] %s\n'   "$1"; }
fatal()    { printf '[ERRO]  %s\n'   "$1" >&2; exit 1; }

has_cmd() { command -v "$1" >/dev/null 2>&1; }

install_with_brew() {
    local formula="$1"
    if ! has_cmd brew; then
        fatal "Homebrew não está instalado. Instala-o em https://brew.sh e tenta novamente."
    fi
    info "A instalar $formula via Homebrew..."
    brew install "$formula"
}

install_with_apt() {
    local pkg="$1"
    if ! has_cmd apt-get; then
        fatal "apt-get não está disponível. Instala $pkg manualmente."
    fi
    info "A instalar $pkg via apt (vai pedir password do sudo)..."
    sudo apt-get update -y
    sudo apt-get install -y "$pkg"
}

ensure_python() {
    if has_cmd python3; then
        return
    fi
    case "$(uname -s)" in
        Darwin) install_with_brew python ;;
        Linux)  install_with_apt python3-venv ;;
        *)      fatal "SO não suportado para instalação automática de Python." ;;
    esac
    has_cmd python3 || fatal "python3 continua em falta após a instalação."
}

ensure_node() {
    if has_cmd node && has_cmd npm; then
        return
    fi
    case "$(uname -s)" in
        Darwin) install_with_brew node ;;
        Linux)  install_with_apt nodejs && install_with_apt npm ;;
        *)      fatal "SO não suportado para instalação automática de Node." ;;
    esac
    has_cmd node || fatal "node continua em falta após a instalação."
    has_cmd npm  || fatal "npm continua em falta após a instalação."
}

# ---------------------------------------------------------------------------
# Pré-requisitos
# ---------------------------------------------------------------------------
section "A verificar Python 3"
ensure_python
ok "Python detetado: $(python3 --version)"

section "A verificar Node.js"
ensure_node
ok "Node detetado: $(node --version) / npm: $(npm --version)"

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
section "A preparar o backend"
cd "$BACKEND_DIR"

if [ ! -d venv ]; then
    info "A criar virtualenv em $BACKEND_DIR/venv ..."
    python3 -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate
info "A atualizar pip e a instalar requirements..."
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
ok "Dependências Python prontas."

info "A arrancar uvicorn em http://localhost:8000 (log: $BACKEND_LOG)..."
nohup python -m uvicorn main:app --reload --port 8000 > "$BACKEND_LOG" 2>&1 &
echo $! > "$BACKEND_PID_FILE"
deactivate
cd "$SCRIPT_DIR"

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------
section "A preparar o frontend"
cd "$FRONTEND_DIR"

if [ ! -d node_modules ]; then
    info "A instalar dependências do frontend (npm install)..."
    npm install
fi

ok "Frontend pronto. A arrancar o servidor de desenvolvimento Vite (Ctrl+C para sair)..."
npm run dev
