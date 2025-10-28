#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Pink Voice"
echo ""

# Check Python 3.12 specifically
if ! command -v python3.12 &> /dev/null; then
    echo "ERROR: Python 3.12 not found"
    echo ""
    echo "Install via Homebrew: brew install python@3.12"
    exit 1
fi

# Verify we're actually using 3.12.x
PYTHON_VERSION=$(python3.12 --version | grep -oE '3\.12\.[0-9]+')
if [ -z "$PYTHON_VERSION" ]; then
    echo "ERROR: python3.12 command found but version check failed"
    exit 1
fi

echo "Using Python $PYTHON_VERSION ✓"
echo ""

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.12 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check dependencies
if ! python -c "import pink_voice" &> /dev/null; then
    echo "Installing dependencies (first run)..."
    echo ""

    # Upgrade pip and install build tools
    pip install --upgrade pip setuptools wheel -q

    # Install from pyproject.toml (editable mode for development)
    pip install -e .

    echo ""
    echo "Dependencies installed successfully"
    echo ""
fi

# Start app
echo "Starting Pink Voice..."
echo ""
echo "Press Ctrl+C to stop"
echo ""

DEV=1 python -m pink_voice
