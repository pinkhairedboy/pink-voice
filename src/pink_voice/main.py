#!/usr/bin/env python3
"""
Pink Voice - Voice transcription client.

Entry point for the application.
"""

# Disable output buffering BEFORE any imports
import os
import sys
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Set process title early
try:
    import setproctitle
    setproctitle.setproctitle('Pink Voice')
except ImportError:
    pass

import signal
import traceback
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Ensure common binary paths are in PATH (needed when launched from Finder)
home = os.path.expanduser('~')
common_paths = [
    f'{home}/.local/bin',
    '/usr/local/bin',
    '/opt/homebrew/bin',
    '/usr/bin',
    '/bin',
    '/usr/sbin',
    '/sbin'
]
os.environ['PATH'] = ':'.join(common_paths) + ':' + os.environ.get('PATH', '')

# Suppress pynput accessibility warning
_original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

# Import rumps only on macOS
import platform
if platform.system() == "Darwin":
    import rumps

# Restore stderr after imports
sys.stderr.close()
sys.stderr = _original_stderr

from pink_voice.config import config
from pink_voice.core.transcribe import TranscribeService
from pink_voice.daemon.hotkeys import HotkeyListener
from pink_voice.daemon.singleton import ensure_single_instance


def main() -> None:
    """Main entry point."""
    if 'LANG' not in os.environ:
        os.environ['LANG'] = 'en_US.UTF-8'
    if 'LC_ALL' not in os.environ:
        os.environ['LC_ALL'] = 'en_US.UTF-8'

    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except Exception:
        pass

    # Ensure only one instance runs
    ensure_single_instance('pink-voice')

    try:
        # Check service BEFORE creating app
        if config.ui_mode == "headless":
            if not TranscribeService.health_check():
                print("✗ pink-transcriber service not running", flush=True)
                sys.exit(1)
            print("✓ pink-transcriber service is ready", flush=True)
        else:
            # macOS production mode - wait with popup on failure
            if not TranscribeService.wait_for_service():
                error_msg = (
                    "pink-transcriber daemon is not running.\n\n"
                    "Pink Voice requires the pink-transcriber service to transcribe audio.\n\n"
                    "Install from: github.com/pinkhairedboy/pink-transcriber"
                )

                import rumps
                rumps.alert(
                    title="Pink Voice - Service Not Found",
                    message=error_msg + "\n\nOr check if daemon is running:\n  launchctl list | grep pink-transcriber",
                    ok="OK"
                )
                sys.exit(1)
            print("✓ pink-transcriber service is ready", flush=True)

        # Request microphone permission upfront
        try:
            import sounddevice as sd
            stream = sd.InputStream(samplerate=config.sample_rate, channels=1, dtype='int16')
            stream.start()
            stream.stop()
            stream.close()
        except Exception:
            pass

        # Create UI based on mode
        if config.ui_mode == "macos":
            from pink_voice.ui.macos import MacOSUI
            app = MacOSUI()

            # Setup hotkey listener
            hotkey_listener = HotkeyListener(on_trigger=app.toggle_recording)
            hotkey_listener.start()

            print("\n" + "="*50, flush=True)
            print("   🎙️  Pink Voice (macOS)", flush=True)
            print("="*50, flush=True)
            print("\n✅ Ready! Listening for Ctrl+Q", flush=True)
            print("Press Ctrl+Q to start/stop recording", flush=True)
            print("Press Ctrl+C to quit\n", flush=True)

            def signal_handler(sig: int, frame) -> None:
                hotkey_listener.stop()
                app.cleanup()
                os._exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            try:
                app.run()
            finally:
                hotkey_listener.stop()
                app.cleanup()
                os._exit(0)

        else:
            from pink_voice.ui.headless import HeadlessUI
            app = HeadlessUI()

            # Setup hotkey listener
            hotkey_listener = HotkeyListener(on_trigger=app.toggle_recording)
            hotkey_listener.start()

            def signal_handler(sig: int, frame) -> None:
                hotkey_listener.stop()
                app.cleanup()
                os._exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            try:
                app.run()
            finally:
                hotkey_listener.stop()
                app.cleanup()
                os._exit(0)

    except Exception as e:
        # Top-level exception handler
        error_msg: str = str(e)
        stack_trace: str = traceback.format_exc()

        # Show error based on UI mode
        if config.ui_mode == "macos":
            import rumps
            rumps.alert(
                title="Pink Voice Error",
                message=f"An unexpected error occurred:\n\n{error_msg}\n\n"
                        f"Stack trace:\n{stack_trace[:500]}...",
                ok="OK"
            )
        else:
            print(f"\n❌ Fatal error: {error_msg}\n{stack_trace}", flush=True)

        sys.exit(1)


if __name__ == "__main__":
    main()
