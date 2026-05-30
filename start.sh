#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -c "import sys; assert sys.version_info >= (3,11)" 2>/dev/null || {
    echo "Python 3.11+ requis"; exit 1
}

if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel…"
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -r requirements.txt -q
    echo "Installation terminée."
fi

exec .venv/bin/python app.py
