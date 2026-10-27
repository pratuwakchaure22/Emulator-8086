#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
if ! command -v apt-get >/dev/null; then echo 'This installer supports Ubuntu/Debian apt-based Linux only.'; exit 1; fi
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nasm libegl1 libopengl0 libxkbcommon-x11-0 libxcb-cursor0
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
printf '\nInstallation finished. Launch with: ./run_ubuntu.sh\n'
