#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
if ! python3 -c "import flask" 2>/dev/null; then
  echo "Installing Flask..."
  pip3 install -r requirements.txt
fi
exec python3 -m assigneval.web --host 127.0.0.1 --port 5050 "$@"
