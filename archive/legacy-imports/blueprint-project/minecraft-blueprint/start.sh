#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  echo "Blackthorn Estate läuft unter http://localhost:8000"
  python3 -m http.server 8000
else
  echo "Python 3 wurde nicht gefunden. Bitte einen lokalen statischen Webserver starten."
  exit 1
fi
