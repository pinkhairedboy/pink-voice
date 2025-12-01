"""
Isolated recording process module.
Runs in a separate process to prevent audio driver hangs from freezing the main UI.
"""

import os
import queue
import sys
import tempfile
import time
import traceback
from multiprocessing import Queue
from typing import Optional

import numpy as np
import sounddevice as sd
from scipy.io import wavfile


def run_recorder(command_queue: Queue, result_queue: Queue, sample_rate: int = 16000) -> None:
    """
    Main loop for the recording process.
    
    Args:
        command_queue: Queue to receive commands ('stop')
        result_queue: Queue to send results (file path or error)
        sample_rate: Audio sample rate
    """
    # Redirect output for debugging if needed
    if os.getenv('VERBOSE') == '1':
        print(f"[RecorderProcess] Started (PID: {os.getpid()})", flush=True)

    audio_queue: queue.Queue = queue.Queue()
    recording: bool = False
    stream: Optional[sd.InputStream] = None

    def audio_callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
        """Audio callback running in PortAudio thread."""
        if status:
            print(f"[RecorderProcess] Audio status: {status}", file=sys.stderr)
        if recording:
            audio_queue.put(indata.copy())

    try:
        # Start recording immediately upon process start
        recording = True
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            callback=audio_callback
        )
        stream.start()
        
        if os.getenv('VERBOSE') == '1':
            print("[RecorderProcess] Stream started", flush=True)

        # Event loop waiting for stop command
        while True:
            try:
                # Check for commands (non-blocking)
                cmd = command_queue.get(timeout=0.1)
                
                if cmd == 'stop':
                    if os.getenv('VERBOSE') == '1':
                        print("[RecorderProcess] Stop received", flush=True)
                    break
            except queue.Empty:
                continue

        # Stop callback from adding more data
        recording = False
        time.sleep(0.05)  # Let current callback finish

        # Collect audio data BEFORE stopping stream (stop can hang on CoreAudio)
        audio_data: list[np.ndarray] = []
        while not audio_queue.empty():
            audio_data.append(audio_queue.get())

        if not audio_data:
            result_queue.put(None)
            return

        # Save to file
        audio: np.ndarray = np.concatenate(audio_data, axis=0)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path: str = tmp.name
            wavfile.write(tmp_path, sample_rate, audio)

        if os.getenv('VERBOSE') == '1':
            print(f"[RecorderProcess] Saved to {tmp_path}", flush=True)

        # Send result - process will be killed after this, no need to clean up stream
        result_queue.put(tmp_path)

        # Don't call close() - it can hang on CoreAudio
        # Process will be killed by main thread, OS will clean up resources

    except Exception as e:
        error_msg = f"Recorder process error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        result_queue.put(None)
