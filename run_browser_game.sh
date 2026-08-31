#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

PORT=8000
HOST=0.0.0.0

printf "Starting browser game server at http://%s:%s/\n" "$HOST" "$PORT"
printf "Open this URL in your browser. In Codespaces, use the forwarded port if needed.\n"

exec /home/codespace/.python/current/bin/python -m http.server "$PORT" --bind "$HOST"
