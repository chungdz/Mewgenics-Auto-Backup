#!/usr/bin/env bash
# Build Windows MewgenicsBackup.exe from Linux using Docker (Wine + PyInstaller).
# Requires: Docker
# Output: dist/windows/MewgenicsBackup.exe (and dist/MewgenicsBackup.exe copy)

set -e
cd "$(dirname "$0")"
PROJECT_ROOT="$(pwd)"

echo "==> Building Windows executable from Linux (Docker + Wine + PyInstaller)"
echo "    Project root: $PROJECT_ROOT"
echo ""

if ! command -v docker &>/dev/null; then
  echo "Error: Docker is required. Install it (e.g. sudo apt install docker.io) and add your user to the docker group."
  echo "Alternatively, build on Windows with build.bat or see BUILD.md."
  exit 1
fi

if [[ ! -f "$PROJECT_ROOT/icons/app.ico" ]]; then
  echo "Error: icons/app.ico not found. Add it to the repo and run build.sh again."
  exit 1
fi

IMAGE="cdrx/pyinstaller-windows:python3"
echo "==> Using image: $IMAGE"
docker pull "$IMAGE" 2>/dev/null || true

echo "==> Running PyInstaller inside container..."
docker run --rm \
  -v "$PROJECT_ROOT:/src" \
  -w /src \
  "$IMAGE" \
  pyinstaller --onefile --windowed --name MewgenicsBackup --icon=icons/app.ico --add-data "icons/app.ico:icons" --hidden-import=pystray --hidden-import=pystray._win32 src/mewgenics_backup_gui.py

EXE_WIN="dist/windows/MewgenicsBackup.exe"
if [[ -f "$PROJECT_ROOT/$EXE_WIN" ]]; then
  mkdir -p "$PROJECT_ROOT/dist"
  cp "$PROJECT_ROOT/$EXE_WIN" "$PROJECT_ROOT/dist/MewgenicsBackup.exe"
  echo ""
  echo "==> Done. Windows executable:"
  echo "    $PROJECT_ROOT/dist/MewgenicsBackup.exe"
  echo "    (also: $PROJECT_ROOT/$EXE_WIN)"
else
  # Some image versions may write to dist/ instead of dist/windows/
  if [[ -f "$PROJECT_ROOT/dist/MewgenicsBackup.exe" ]]; then
    echo ""
    echo "==> Done. Windows executable: $PROJECT_ROOT/dist/MewgenicsBackup.exe"
  else
    echo ""
    echo "==> Build finished. Check for .exe in: $PROJECT_ROOT/dist/ or $PROJECT_ROOT/dist/windows/"
    exit 1
  fi
fi
