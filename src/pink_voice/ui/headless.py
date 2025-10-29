"""Pink Voice headless UI for Windows/Linux."""

import signal
import sys

from pink_voice.config import config
from pink_voice.ui.base import BaseUI


class HeadlessUI(BaseUI):
    """Headless UI implementation (no visual interface, only hotkey)."""

    def __init__(self) -> None:
        """Initialize headless UI."""
        super().__init__()
        self._running: bool = False

    def toggle_recording(self) -> None:
        """Toggle recording on/off."""
        if self.is_processing:
            return

        if self.recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def update_status(self, status: str) -> None:
        """Update status (always print to console in headless mode)."""
        status_map = {
            "idle": "✓ Ready",
            "recording": "🎙️  Recording... (press Ctrl+Q to stop)",
            "transcribing": "⏳ Transcribing...",
        }
        message = status_map.get(status, status)
        print(message, flush=True)

    def on_transcription_success(self, text: str) -> None:
        """Show transcription result in console."""
        print(f"\n✓ Transcribed: {text}\n", flush=True)

    def on_transcription_error(self, error: str) -> None:
        """Show error in console."""
        print(f"\n✗ Error: {error}\n", flush=True)

    def run(self) -> None:
        """Run the headless app (block until interrupted)."""
        self._running = True

        def signal_handler(sig: int, frame) -> None:
            self._running = False
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print("\n" + "="*50, flush=True)
        print("   🎙️  Pink Voice (Headless)", flush=True)
        print("="*50, flush=True)
        print("\n✅ Ready! Listening for Ctrl+Q", flush=True)
        print("Press Ctrl+Q to start recording", flush=True)
        print("Press Ctrl+C to quit\n", flush=True)

        try:
            while self._running:
                signal.pause()
        except AttributeError:
            import time
            while self._running:
                time.sleep(0.1)
