"""Base UI interface for Pink Voice."""

import os
import sys
import threading
from abc import ABC, abstractmethod
from typing import Optional

from pink_voice.config import config
from pink_voice.daemon.hotkeys import HotkeyListener
from pink_voice.core.recorder import AudioRecorder
from pink_voice.core.transcribe import TranscribeService


class BaseUI(ABC):
    """Base class for all UI implementations."""

    def __init__(self) -> None:
        """Initialize base UI components."""
        self.recorder: AudioRecorder = AudioRecorder(sample_rate=config.sample_rate)
        self.is_processing: bool = False

    @abstractmethod
    def toggle_recording(self) -> None:
        """Toggle recording on/off. Platform-specific implementation."""
        pass

    def _start_recording(self) -> None:
        """Start audio recording."""
        if self.recorder.start_recording():
            self.update_status("recording")
            self.play_sound("start")

    def _stop_recording(self) -> None:
        """Stop audio recording and start transcription."""
        self.is_processing = True

        # Stop recording FIRST
        audio_path: Optional[str] = self.recorder.stop_recording()

        # Then update UI
        self.play_sound("stop")
        self.update_status("transcribing")

        threading.Thread(target=self._process_recording, args=(audio_path,), daemon=True).start()

    def _process_recording(self, audio_path: Optional[str]) -> None:
        """Process recorded audio: transcribe and copy to clipboard."""
        if not audio_path:
            self.update_status("idle")
            self.is_processing = False
            return

        try:
            text: str = TranscribeService.transcribe(audio_path)

            if not text:
                text = "[No speech detected]"

            self.on_transcription_success(text)
            self.play_sound("done")
            self.copy_to_clipboard(text)
            self.show_notification(
                "Done",
                text[:100] + ("..." if len(text) > 100 else "")
            )
        except Exception as e:
            error_msg: str = str(e)
            self.on_transcription_error(error_msg)
            self.show_notification("Error", f"Transcription failed: {error_msg}")
        finally:
            try:
                os.unlink(audio_path)
            except Exception:
                pass

            self.update_status("idle")
            self.is_processing = False

    @abstractmethod
    def update_status(self, status: str) -> None:
        """
        Update UI status.

        Args:
            status: One of "idle", "recording", "transcribing"
        """
        pass

    def play_sound(self, sound_type: str) -> None:
        """
        Play sound notification.

        Args:
            sound_type: One of "start", "stop", "done"
        """
        from pink_voice.platform.sounds import play_sound
        play_sound(sound_type)

    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to clipboard.

        Args:
            text: Text to copy
        """
        from pink_voice.platform.clipboard import copy_to_clipboard
        copy_to_clipboard(text)

    def show_notification(self, title: str, message: str) -> None:
        """
        Show notification to user.

        Args:
            title: Notification title
            message: Notification message
        """
        from pink_voice.platform.notifications import show_notification
        show_notification("Pink Voice", title, message)

    def on_transcription_success(self, text: str) -> None:
        """
        Called when transcription succeeds.
        Override in subclass to show result in UI.

        Args:
            text: Transcribed text
        """
        pass

    def on_transcription_error(self, error: str) -> None:
        """
        Called when transcription fails.
        Override in subclass to show error in UI.

        Args:
            error: Error message
        """
        pass

    @abstractmethod
    def run(self) -> None:
        """Run the UI main loop."""
        pass

    def cleanup(self) -> None:
        """Cleanup resources before exit."""
        if self.recorder.is_recording():
            self.recorder.stop_recording()
