#!/bin/sh
# Use a stable Python with Tk support and PyInstaller installed.
set -eu

pip3 install -U pyinstaller

cd "$(dirname "$0")/.."
: "${KEYBOARDO_PYTHON:=$PWD/.venv/bin/python}"
if [ "$(uname -s)" != Darwin ]; then
    echo "Build the DMG on macOS." >&2
    exit 1
fi
"$KEYBOARDO_PYTHON" -m PyInstaller --noconfirm --clean --windowed \
    --paths src \
    --icon resources/Keyboardo.icns --add-data "resources:resources" \
    --add-data "documentation/LESSONS.md:documentation" \
    --name Keyboardo --osx-bundle-identifier com.keyboardo.app src/keyboardo/app.py
staging=$(mktemp -d "${TMPDIR:-/tmp}/keyboardo-dmg.XXXXXX")
trap 'rm -rf "$staging"' EXIT
cp -R dist/Keyboardo.app "$staging/"
ln -s /Applications "$staging/Applications"
diskutil image create from --volumeName Keyboardo --format UDZO "$staging" dist/Keyboardo.dmg
