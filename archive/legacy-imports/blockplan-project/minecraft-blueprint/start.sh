#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  python3 -m http.server 8000
elif command -v python >/dev/null 2>&1; then
  python -m http.server 8000
else
  echo "Python wurde nicht gefunden. Öffne index.html direkt im Browser."
  exit 1
fi
