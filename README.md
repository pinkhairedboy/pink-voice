# Pink Voice

Lightweight macOS menu bar client for pink-transcriber voice transcription service.

**⚠️ Requires [pink-transcriber](https://github.com/pinkhairedboy/pink-transcriber) daemon** - records audio only, transcription happens via pink-transcriber service.

Records audio via Ctrl+Q hotkey, sends to pink-transcriber daemon, copies transcribed text to clipboard.

## How it works

Menu bar app captures audio when you press Ctrl+Q. On second press, stops recording, calls `pink-transcriber` CLI with audio file, copies result to clipboard. App is ~50MB, delegates all ML work to pink-transcriber daemon.

## Requirements

- macOS 12+ with Apple Silicon (M1-M5)
- Python 3.12
- **pink-transcriber daemon** (install first from github.com/pinkhairedboy/pink-transcriber)

## Installation

Install pink-transcriber first:
```bash
git clone https://github.com/pinkhairedboy/pink-transcriber.git
cd pink-transcriber
./install.sh
pink-transcriber --health  # Verify daemon is running
```

Then install pink-voice:
```bash
git clone https://github.com/pinkhairedboy/pink-voice.git
cd pink-voice
./build.sh
./install.sh
```

App appears in menu bar, starts automatically on login.

## Usage

Press **Ctrl+Q** to start recording. Press **Ctrl+Q** again to stop. Transcribed text appears in clipboard.

Or click menu bar icon:
- Start Recording
- Stop Recording
- Transcribing... (processing)
- Quit

## Development

```bash
./dev.sh         # Run in terminal with verbose logging
./uninstall.sh   # Remove LaunchAgent and app
```

## Troubleshooting

If recording fails with "service not available":
```bash
pink-transcriber --health           # Check daemon status
launchctl list | grep pink          # Check if running
```

## Architecture

- `src/pink_voice/ui/app.py` - Menu bar interface (rumps)
- `src/pink_voice/services/recorder.py` - Audio recording (sounddevice)
- `src/pink_voice/services/transcribe.py` - pink-transcriber client (subprocess)
- `src/pink_voice/hotkeys/listener.py` - Ctrl+Q handler (pynput)
- Thread-safe dispatch ensures CoreAudio streams managed on main thread
- Uses queue.Queue() for audio data from PortAudio callback
