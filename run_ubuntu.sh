#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
if [ ! -f .venv/bin/python ]; then echo 'Run ./install_ubuntu.sh first'; exit 1; fi
exec .venv/bin/python src/main.py
