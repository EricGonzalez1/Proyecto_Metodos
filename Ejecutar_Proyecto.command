#!/bin/zsh
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export TK_SILENCE_DEPRECATION=1
/usr/bin/python3 "$DIR/main.py"
