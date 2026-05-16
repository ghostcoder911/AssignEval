#!/usr/bin/env bash
# Convenience wrapper — run from AssignEval directory
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -m assigneval "$@"
