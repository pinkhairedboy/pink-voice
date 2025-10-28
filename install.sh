#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_NAME="Pink Voice.app"
APP_SOURCE="$SCRIPT_DIR/dist/$APP_NAME"
APP_DEST="/Applications/$APP_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/com.pink.voice.plist"

echo "Installing Pink Voice"
echo ""

# Check if .app exists
if [ ! -d "$APP_SOURCE" ]; then
    echo "ERROR: $APP_NAME not found in dist/"
    echo "Run: source venv/bin/activate && pyinstaller PinkVoice.spec"
    exit 1
fi

# Copy .app to /Applications
echo "Copying Pink Voice.app to /Applications..."
if [ -d "$APP_DEST" ]; then
    echo "Removing existing version..."
    rm -rf "$APP_DEST"
fi
cp -R "$APP_SOURCE" "$APP_DEST"

# Generate launch agent plist
echo "Creating launch agent..."
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_DEST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pink.voice</string>

    <key>ProgramArguments</key>
    <array>
        <string>$APP_DEST/Contents/MacOS/Pink Voice</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>ProcessType</key>
    <string>Interactive</string>
</dict>
</plist>
EOF

# Unload if already loaded
if launchctl list | grep -q com.pink.voice; then
    echo "Stopping existing service..."
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# Load the service
echo "Starting service..."
launchctl load "$PLIST_DEST"

echo ""
echo "✓ Pink Voice installed successfully"
echo ""
echo "Commands:"
echo "  Status:  launchctl list | grep pink.voice"
echo "  Stop:    launchctl unload ~/Library/LaunchAgents/com.pink.voice.plist"
echo "  Start:   launchctl load ~/Library/LaunchAgents/com.pink.voice.plist"
echo ""
echo "Pink Voice will start automatically on login"
echo "Look for the icon in your menu bar (top right)"
echo ""
