"""Pink Voice macOS menu bar application."""

import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

import rumps
from Foundation import NSObject
import objc

from pink_voice.config import config
from pink_voice.hotkeys.listener import HotkeyListener
from pink_voice.services.recorder import AudioRecorder
from pink_voice.services.transcribe import TranscribeService



class MainThreadDispatcher(NSObject):
    """Helper NSObject to dispatch callbacks to main thread via performSelectorOnMainThread."""

    def initWithCallback_(self, callback):
        """Initialize with callback function."""
        self = objc.super(MainThreadDispatcher, self).init()
        if self is None:
            return None
        self.callback = callback
        return self

    def call(self):
        """Call the callback."""
        self.callback()


class VoiceInputApp(rumps.App):
    """macOS menu bar application for voice input."""

    def __init__(self) -> None:
        """Initialize the application."""
        icon_path: str = str(Path(__file__).parent.parent / "assets" / "icon.png")

        super(VoiceInputApp, self).__init__(
            name="Pink Voice",
            icon=icon_path,
            quit_button="Quit"
        )

        self.recorder: AudioRecorder = AudioRecorder(sample_rate=config.sample_rate)
        self.hotkey_listener: Optional[HotkeyListener] = None
        self.is_processing: bool = False

        # Create main thread dispatcher for thread-safe callbacks
        self._dispatcher: MainThreadDispatcher = MainThreadDispatcher.alloc().initWithCallback_(
            self._toggle_recording
        )

        self.recording_button: rumps.MenuItem = rumps.MenuItem(
            "Start Recording",
            callback=self._menu_toggle_recording
        )

        self.menu = [self.recording_button]

        # Setup permissions in background thread to not block app initialization
        threading.Thread(target=self._setup_permissions, daemon=True).start()

    def _setup_permissions(self) -> None:
        """Setup all permissions in background thread."""
        # First setup hotkey (triggers Input Monitoring popup)
        self._setup_hotkey()
        # Then check microphone (triggers Microphone popup)
        self._check_microphone_permissions()

    def _check_microphone_permissions(self) -> None:
        """Request microphone permissions."""
        try:
            import sounddevice as sd
            stream: sd.InputStream = sd.InputStream(
                samplerate=config.sample_rate,
                channels=1,
                dtype='int16'
            )
            stream.start()
            stream.stop()
            stream.close()
        except Exception:
            pass

    def show_ready_notification(self) -> None:
        """Show ready notification after app starts."""
        rumps.notification(
            title="Pink Voice",
            subtitle="Ready",
            message="Press Ctrl+Q or menu to start recording",
            sound=False
        )

    def _setup_hotkey(self) -> None:
        """Setup keyboard listener for sequential Ctrl then Q press."""
        self.hotkey_listener = HotkeyListener(on_trigger=self.request_toggle)
        self.hotkey_listener.start()

    def _menu_toggle_recording(self, _: rumps.MenuItem) -> None:
        """Handle menu item click."""
        self.request_toggle()

    def request_toggle(self) -> None:
        """
        Request recording toggle from ANY thread.
        This is the SINGLE entry point for all external events (menu, hotkey, future buttons, etc).
        Ensures _toggle_recording is called on main thread.
        """
        from Foundation import NSThread

        if NSThread.isMainThread():
            self._toggle_recording()
        else:
            # Use NSObject dispatcher to execute callback on main thread
            self._dispatcher.performSelectorOnMainThread_withObject_waitUntilDone_(
                'call',
                None,
                False
            )

    def _toggle_recording(self) -> None:
        """Toggle recording on/off. MUST be called from main thread only."""

        if self.is_processing:
            return

        if self.recorder.is_recording():
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Start audio recording."""

        if self.recorder.start_recording():
            self.recording_button.title = "Stop Recording"
            if config.dev_mode:
                print("🎙️  Recording... (press Ctrl+Q to stop)", flush=True)
            self._play_sound(config.sound_start)
        else:
            self.recording_button.title = "Start Recording"

    def _stop_recording(self) -> None:
        """Stop audio recording and start transcription."""

        if not self.recorder.is_recording():
            return

        self.is_processing = True
        if config.dev_mode:
            print("⏹️  Stopped. Transcribing...", flush=True)
        self._play_sound(config.sound_stop)
        self.recording_button.title = "Transcribing..."

        # Stop recording in same thread where stream was created
        audio_path: Optional[str] = self.recorder.stop_recording()

        # Process transcription in background thread
        threading.Thread(target=self._process_recording, args=(audio_path,), daemon=True).start()

    def _process_recording(self, audio_path: Optional[str]) -> None:
        """Process recorded audio: transcribe and copy to clipboard."""

        if not audio_path:
            self.recording_button.title = "Start Recording"
            self.is_processing = False
            return

        try:
            text: str = TranscribeService.transcribe(audio_path)

            if text:
                text_with_disclaimer: str = f"{config.disclaimer} {text}"
                if config.dev_mode:
                    print(f"\n📝 {text_with_disclaimer}\n", flush=True)
            else:
                text_with_disclaimer = "[No speech detected]"
                if config.dev_mode:
                    print(f"\n⚠️  {text_with_disclaimer}\n", flush=True)

            self._play_sound(config.sound_done)
            self._copy_to_clipboard(text_with_disclaimer)

            rumps.notification(
                title="Pink Voice",
                subtitle="Done",
                message=text[:100] + ("..." if len(text) > 100 else "") if text else "No speech detected",
                sound=False
            )
        except Exception as e:
            error_msg: str = str(e)
            if config.dev_mode:
                print(f"\n❌ Transcription error: {error_msg}\n", flush=True)
            rumps.notification(
                title="Pink Voice",
                subtitle="Error",
                message=f"Transcription failed: {error_msg}",
                sound=True
            )
        finally:
            # Always cleanup and reset state even if transcription fails
            try:
                os.unlink(audio_path)
            except Exception:
                pass

            self.recording_button.title = "Start Recording"
            self.is_processing = False

    def _play_sound(self, sound_path: str) -> None:
        """
        Play system sound.

        Args:
            sound_path: Path to sound file
        """
        subprocess.Popen(
            ['afplay', sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def _copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to macOS clipboard.

        Args:
            text: Text to copy
        """
        try:
            process: subprocess.Popen = subprocess.Popen(
                ['pbcopy'],
                stdin=subprocess.PIPE
            )
            process.communicate(str(text).encode('utf-8'))
        except Exception as e:
            if config.dev_mode:
                print(f"Clipboard error: {e}")

    def cleanup(self) -> None:
        """Cleanup resources before exit."""
        if self.recorder.is_recording():
            self.recorder.stop_recording()
        if self.hotkey_listener:
            self.hotkey_listener.stop()
