#!/usr/bin/env bash
# Minecraft Bergkamm-Herrenhaus • Web-Bauanleitung Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
TARGET="file://${DIR}/index.html"

echo "=========================================================="
echo "🏰 Öffne Minecraft Herrenhaus & Kellergewölbe Bauplan..."
echo "Datei: ${TARGET}"
echo "=========================================================="

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "${TARGET}" >/dev/null 2>&1 &
elif command -v chromium >/dev/null 2>&1; then
  chromium "${TARGET}" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
  firefox "${TARGET}" >/dev/null 2>&1 &
elif command -v google-chrome >/dev/null 2>&1; then
  google-chrome "${TARGET}" >/dev/null 2>&1 &
else
  echo "Öffne die Datei index.html einfach in deinem Lieblingsbrowser!"
fi
