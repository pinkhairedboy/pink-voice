"""Pink Voice macOS menu bar application."""

import os
import sys
import threading
from pathlib import Path

import rumps

from pink_voice.config import config
from pink_voice.ui.base import BaseUI


class MacOSUI(BaseUI, rumps.App):
    """macOS menu bar application for voice input."""

    def __init__(self) -> None:
        """Initialize the application."""
        icon_path: str = str(Path(__file__).parent.parent / "assets" / "icon.png")

        rumps.App.__init__(
            self,
            name="Pink Voice",
            icon=icon_path,
            quit_button="Quit"
        )

        BaseUI.__init__(self)

        self.recording_button: rumps.MenuItem = rumps.MenuItem(
            "Start Recording",
            callback=self._menu_toggle_recording
        )

        self.menu = [self.recording_button]


    def _menu_toggle_recording(self, _: rumps.MenuItem) -> None:
        """Handle menu item click."""
        self.toggle_recording()

    def toggle_recording(self) -> None:
        """
        Toggle recording on/off.
        Ensures _toggle_recording_impl is called on main thread.
        """
        try:
            from AppKit import NSThread

            if NSThread.isMainThread():
                self._toggle_recording_impl()
            else:
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    '_toggle_recording_impl',
                    None,
                    False
                )
        except Exception:
            self._toggle_recording_impl()

    def _toggle_recording_impl(self) -> None:
        """Toggle recording implementation. MUST be called from main thread only."""
        if self.is_processing:
            return

        if self.recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def update_status(self, status: str) -> None:
        """Update menu bar button status."""
        status_map = {
            "idle": "Start Recording",
            "recording": "Stop Recording",
            "transcribing": "Transcribing...",
        }
        self.recording_button.title = status_map.get(status, "Start Recording")

        # Print status to console in DEV mode
        if os.getenv('DEV') == '1':
            console_status_map = {
                "recording": "🎙️  Recording... (press Ctrl+Q to stop)",
                "transcribing": "⏳ Transcribing...",
            }
            message = console_status_map.get(status)
            if message:
                print(message, flush=True)

    def on_transcription_success(self, text: str) -> None:
        """Show transcription result in console."""
        print(f"✓ Transcribed: {text}", flush=True)

    def on_transcription_error(self, error: str) -> None:
        """Show error in console."""
        print(f"✗ Error: {error}", flush=True)

    def run(self) -> None:
        """Run the macOS app."""
        rumps.App.run(self)
