#!/bin/bash
set -e

PLIST_DEST="$HOME/Library/LaunchAgents/com.pink.voice.plist"

echo "Uninstalling pink-voice launch agent"
echo ""

if [ ! -f "$PLIST_DEST" ]; then
    echo "Service not installed"
    exit 0
fi

# Unload the service
echo "Stopping service..."
launchctl unload "$PLIST_DEST" 2>/dev/null || true

# Remove plist file
echo "Removing configuration..."
rm "$PLIST_DEST"

echo ""
echo "✓ Service uninstalled successfully"
echo ""
