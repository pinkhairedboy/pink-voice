"""Audio recording module."""

import os
import queue
import sys
import tempfile
from typing import Optional

import numpy as np
import sounddevice as sd
from scipy.io import wavfile


class AudioRecorder:
    """Records audio from microphone."""

    def __init__(self, sample_rate: int = 16000) -> None:
        """
        Initialize audio recorder.

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate: int = sample_rate
        self.recording: bool = False
        self.audio_queue: queue.Queue = queue.Queue()
        self.stream: Optional[sd.InputStream] = None

    def _callback(self, indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        """Audio callback - called from a separate thread by PortAudio."""
        if self.recording:
            self.audio_queue.put(indata.copy())

    def start_recording(self) -> bool:
        """
        Start recording audio.

        Returns:
            True if recording started, False if already recording
        """
        if self.recording:
            return False

        while not self.audio_queue.empty():
            self.audio_queue.get()

        self.recording = True

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            callback=self._callback
        )
        self.stream.start()

        if os.getenv('DEV') == '1':
            print("Recording started", flush=True)

        return True

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save audio to temporary file.

        Returns:
            Path to temporary WAV file, or None if no audio recorded
        """
        self.recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if os.getenv('DEV') == '1':
            print("Recording stopped", flush=True)

        audio_data: list[np.ndarray] = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())

        if not audio_data:
            return None

        audio: np.ndarray = np.concatenate(audio_data, axis=0)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path: str = tmp.name
            wavfile.write(tmp_path, self.sample_rate, audio)

        return tmp_path

    def is_recording(self) -> bool:
        """
        Check if currently recording.

        Returns:
            True if recording, False otherwise
        """
        return self.recording
