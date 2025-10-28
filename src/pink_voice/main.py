#!/usr/bin/env python3
"""
Pink Voice - Voice transcription for macOS.

Entry point for the application.
"""

import os
import signal
import sys
import traceback
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Ensure /usr/local/bin is in PATH
if 'PATH' not in os.environ or '/usr/local/bin' not in os.environ['PATH']:
    os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:' + os.environ.get('PATH', '')

# Suppress pynput accessibility warning
_original_stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

import rumps

# Restore stderr after imports
sys.stderr.close()
sys.stderr = _original_stderr

from pink_voice.config import config
from pink_voice.services.transcribe import TranscribeService
from pink_voice.ui.app import VoiceInputApp


def main() -> None:
    """Main entry point."""
    # Fix locale for proper UTF-8 encoding when launched via Spotlight/LaunchAgent
    if 'LANG' not in os.environ:
        os.environ['LANG'] = 'en_US.UTF-8'
    if 'LC_ALL' not in os.environ:
        os.environ['LC_ALL'] = 'en_US.UTF-8'

    if config.dev_mode:
        print("\n" + "="*50, flush=True)
        print("   🎙️  Pink Voice - Voice Transcription", flush=True)
        print("="*50, flush=True)

    try:
        # Check service BEFORE creating app
        if config.dev_mode:
            if not TranscribeService.health_check():
                print("✗ pink-transcriber service not running", flush=True)
                sys.exit(1)
            print("✓ pink-transcriber is ready (dev mode)", flush=True)
        else:
            if not TranscribeService.wait_for_service():
                # In production, show popup and exit
                rumps.alert(
                    title="Pink Voice - Service Not Found",
                    message="pink-transcriber daemon is not running.\n\n"
                            "Pink Voice requires the pink-transcriber service to transcribe audio.\n\n"
                            "Install from: github.com/pinkhairedboy/pink-transcriber\n\n"
                            "Or check if daemon is running:\n"
                            "  launchctl list | grep pink-transcriber",
                    ok="OK"
                )
                sys.exit(1)

        if config.dev_mode:
            print("✓ pink-transcriber service is ready", flush=True)

        app: VoiceInputApp = VoiceInputApp()

        if config.dev_mode:
            print("\n✅ Ready! Press Ctrl+Q to start recording\n", flush=True)

        # Show notification after app is fully initialized
        app.show_ready_notification()

        def signal_handler(sig: int, frame) -> None:
            app.cleanup()
            os._exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            app.run()
        finally:
            app.cleanup()
            os._exit(0)

    except Exception as e:
        # Top-level exception handler - show popup with error
        error_msg: str = str(e)
        stack_trace: str = traceback.format_exc()

        if config.dev_mode:
            print(f"\n❌ Fatal error: {error_msg}\n", flush=True)
            print(stack_trace, flush=True)

        # Show error popup
        rumps.alert(
            title="Pink Voice Error",
            message=f"An unexpected error occurred:\n\n{error_msg}\n\n"
                    f"Stack trace:\n{stack_trace[:500]}...",
            ok="OK"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
