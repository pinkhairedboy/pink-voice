# Pink Voice

Cross-platform voice transcription client for pink-transcriber service.

**⚠️ Requires [pink-transcriber](https://github.com/pinkhairedboy/pink-transcriber) daemon**

Records audio via Ctrl+Q hotkey, sends to pink-transcriber daemon, copies transcribed text to clipboard.

## Platforms

- **macOS**: Menu bar app with hotkey
- **Windows**: Headless console app with hotkey (calls WSL pink-transcriber)
- **Linux**: Headless console app with hotkey

## Requirements

- **macOS**: macOS 12+, Python 3.10+
- **Windows**: Windows 10+, Python 3.10+, WSL2 with pink-transcriber installed
- **Linux**: Python 3.10+
- **uv** package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **pink-transcriber daemon** running (macOS/Linux) or in WSL (Windows)

## Installation

### 1. Install pink-transcriber

**macOS/Linux:**
```bash
git clone https://github.com/pinkhairedboy/pink-transcriber.git
cd pink-transcriber
./install.sh
pink-transcriber --health  # Verify daemon is running
```

**Windows (WSL):**
```bash
# In WSL terminal
git clone https://github.com/pinkhairedboy/pink-transcriber.git
cd pink-transcriber
./install.sh
pink-transcriber --health  # Verify daemon is running
```

### 2. Install uv

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Build Pink Voice

**macOS:**
```bash
git clone https://github.com/pinkhairedboy/pink-voice.git
cd pink-voice
./build.sh

# Output: dist/Pink Voice.app
# Install: cp -R "dist/Pink Voice.app" /Applications/
```

**Windows:**
```cmd
git clone https://github.com/pinkhairedboy/pink-voice.git
cd pink-voice
build.bat

REM Output: dist\Pink Voice.exe
```

Build script runs `uv sync` (one command: creates venv + installs dependencies) then builds with PyInstaller.

## Usage

### macOS (Menu Bar App)

Press **Ctrl+Q** to start/stop recording. Menu bar icon shows status.

Menu options:
- Start Recording
- Stop Recording
- Transcribing... (processing)
- Quit

### Windows/Linux (Headless)

Run `Pink Voice.exe` (Windows) or `python -m pink_voice` (Linux).

Console shows:
```
==================================================
   Pink Voice (Headless)
==================================================

Press Ctrl+Q to start recording
Press Ctrl+C to quit

✓ Ready
🎙️  Recording... (press Ctrl+Q to stop)
⏳ Transcribing...

✓ Transcribed: your text here

✓ Ready
```

Press **Ctrl+Q** to record, **Ctrl+C** to quit.

## Development

One command to setup and run:

```bash
# macOS/Linux
git clone https://github.com/pinkhairedboy/pink-voice.git
cd pink-voice

# Setup (one command)
uv sync

# Run with VERBOSE logs
VERBOSE=1 uv run python -m pink_voice

# Force headless mode
PINK_VOICE_UI=headless uv run python -m pink_voice
```

**Windows:**
```cmd
git clone https://github.com/pinkhairedboy/pink-voice.git
cd pink-voice

REM Setup (one command)
uv sync

REM Run with VERBOSE logs
set VERBOSE=1 && uv run python -m pink_voice
```

## Architecture

```
src/pink_voice/
├── main.py                    # Entry point, platform detection
├── config.py                  # Configuration, constants, VERBOSE_MODE
├── daemon/
│   ├── singleton.py          # Single instance enforcement
│   └── hotkeys.py            # Ctrl+Q handler (pynput)
├── ui/
│   ├── base.py               # Base UI class (shared logic)
│   ├── macos.py              # macOS menu bar UI (rumps)
│   └── headless.py           # Headless console UI
├── core/
│   ├── recorder.py           # Audio recording (sounddevice)
│   └── transcribe.py         # pink-transcriber client
└── platform/
    ├── clipboard.py          # Cross-platform clipboard
    ├── sounds.py             # Cross-platform sounds
    └── notifications.py      # Cross-platform notifications
```

**Key features:**
- Automatic platform detection
- Windows: converts paths to WSL format, calls `wsl pink-transcriber`
- macOS: native menu bar with notifications
- Headless: always shows status in console
- No log files, no services, no installation required
