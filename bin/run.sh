#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${KEYBOARDO_PYTHON:=$PWD/.venv/bin/python}"
exec "$KEYBOARDO_PYTHON" src/keyboardo/app.py
