#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export TK_SILENCE_DEPRECATION=1
if command -v python3 >/dev/null 2>&1; then
    python3 "$DIR/main.py"
else
    python "$DIR/main.py"
fi
