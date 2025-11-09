"""Transcription service."""

import os
import subprocess
import sys
import time

from pink_voice.config import config


class TranscribeService:
    """Service for transcribing audio using pink-transcriber."""

    @staticmethod
    def health_check() -> bool:
        """
        Check if pink-transcriber service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            if config.platform == "windows":
                # Windows: use wsl bash -lc to load PATH
                command = ['wsl', 'bash', '-lc', 'pink-transcriber --health']
            else:
                command = config.transcribe_command + ['--health']

            result: subprocess.CompletedProcess = subprocess.run(
                command,
                capture_output=True,
                timeout=config.health_check_timeout
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @staticmethod
    def transcribe(audio_path: str) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Absolute path to audio file

        Returns:
            Transcribed text

        Raises:
            RuntimeError: If transcription fails
        """
        transcribe_path = config.convert_path_for_transcribe(audio_path)

        if config.platform == "windows":
            command = ['wsl', 'bash', '-lc', f'pink-transcriber {transcribe_path}']
        else:
            command = config.transcribe_command + [transcribe_path]

        if os.getenv('DEV') == '1':
            print("Transcribing...", flush=True)

        result: subprocess.CompletedProcess = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            raise RuntimeError(f"Transcription failed: {result.stderr}")

        text = result.stdout.strip()

        if os.getenv('DEV') == '1':
            print(f"Result: {text}", flush=True)

        return text

    @staticmethod
    def wait_for_service() -> bool:
        """
        Wait for pink-transcriber service to become available.

        Returns:
            True if service became available, False if timed out
        """
        for attempt in range(config.service_max_attempts):
            if TranscribeService.health_check():
                return True
            if attempt < config.service_max_attempts - 1:
                time.sleep(config.service_wait_interval)

        return False
