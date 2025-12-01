"""Audio recording module using multiprocessing for stability."""

import multiprocessing
import os
import time
from typing import Optional

from pink_voice.core.recorder_process import run_recorder


class AudioRecorder:
    """
    Records audio from microphone using a separate process.
    This prevents the main UI process from freezing if the audio driver hangs.
    """

    def __init__(self, sample_rate: int = 16000) -> None:
        """
        Initialize audio recorder.

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate: int = sample_rate
        self.process: Optional[multiprocessing.Process] = None
        self.command_queue: Optional[multiprocessing.Queue] = None
        self.result_queue: Optional[multiprocessing.Queue] = None

    def start_recording(self) -> bool:
        """
        Start recording audio in a separate process.

        Returns:
            True if recording started, False if already recording
        """
        if self.is_recording():
            return False

        self.command_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()

        # Use 'spawn' context for macOS compatibility with CoreAudio
        ctx = multiprocessing.get_context('spawn')
        self.process = ctx.Process(
            target=run_recorder,
            args=(self.command_queue, self.result_queue, self.sample_rate),
            daemon=True
        )
        self.process.start()

        if os.getenv('VERBOSE') == '1':
            print(f"Recording process started (PID: {self.process.pid})", flush=True)

        return True

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save audio to temporary file.

        Returns:
            Path to temporary WAV file, or None if no audio recorded
        """
        if not self.is_recording():
            return None

        result = None

        try:
            if self.command_queue:
                self.command_queue.put('stop')

            # Wait for result while process is alive (max 30s as safety net)
            import queue
            deadline = time.time() + 30

            while self.process and self.process.is_alive() and time.time() < deadline:
                try:
                    result = self.result_queue.get(timeout=0.1)
                    break
                except queue.Empty:
                    continue

            if result is None and time.time() >= deadline:
                if os.getenv('VERBOSE') == '1':
                    print("⚠️  30s timeout waiting for recorder", flush=True)

        finally:
            self._kill_process()

        return result

    def _kill_process(self) -> None:
        """Force kill the recording process."""
        if self.process:
            if self.process.is_alive():
                if os.getenv('VERBOSE') == '1':
                    print(f"Force killing recorder process (PID: {self.process.pid})", flush=True)
                
                self.process.terminate()
                # Give it a tiny bit of time to die gracefully
                self.process.join(timeout=0.1)
                
                # If still alive, kill hard
                if self.process.is_alive():
                    self.process.kill()
            
            self.process = None
            self.command_queue = None
            self.result_queue = None

    def is_recording(self) -> bool:
        """
        Check if currently recording.

        Returns:
            True if recording process is alive
        """
        return self.process is not None and self.process.is_alive()
