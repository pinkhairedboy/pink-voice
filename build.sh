#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building Pink Voice.app (macOS)"
echo ""

# Check uv installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv not found"
    echo ""
    echo "Install uv:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    exit 1
fi

# Sync dependencies (creates venv + installs)
echo "Syncing dependencies..."
uv sync

# Install pyinstaller
echo "Installing PyInstaller..."
uv pip install pyinstaller

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build .app
echo "Building .app bundle..."
uv run pyinstaller PinkVoice.spec

echo ""
echo "✓ Build complete!"
echo ""
echo "Output: dist/Pink Voice.app"
echo ""
echo "To run:"
echo "  open \"dist/Pink Voice.app\""
echo ""
echo "To install to /Applications:"
echo "  cp -R \"dist/Pink Voice.app\" /Applications/"
echo ""
