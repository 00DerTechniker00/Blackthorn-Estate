#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo 'Python 3 ist nicht installiert. Bitte Python 3 installieren und erneut starten.' >&2
  exit 1
fi
echo 'Blackthorn Estate V6: Öffne http://localhost:8000 im Browser.'
exec "$PYTHON" -m http.server 8000 --bind 127.0.0.1
