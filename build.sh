#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Building Pink Voice.app"
echo ""

# Check venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: venv not found"
    echo "Run: python3.12 -m venv venv && source venv/bin/activate && pip install -e ."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check pyinstaller installed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist

# Build .app
echo "Building .app bundle..."
pyinstaller PinkVoice.spec

echo ""
echo "✓ Build complete!"
echo ""
echo "Output: dist/Pink Voice.app"
echo ""
echo "Resetting permissions for fresh install..."
tccutil reset All com.pink.voice 2>/dev/null || echo "  (no previous permissions to reset)"
tccutil reset Microphone com.pink.voice 2>/dev/null
tccutil reset ListenEvent com.pink.voice 2>/dev/null
echo ""
echo "Installing to /Applications..."
rm -rf "/Applications/Pink Voice.app"
cp -R "dist/Pink Voice.app" /Applications/
echo "✓ Installed to /Applications/Pink Voice.app"
echo ""
echo "To run: open \"/Applications/Pink Voice.app\""
echo "To setup auto-start: ./install.sh"
echo ""
