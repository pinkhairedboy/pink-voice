"""Transcription service."""

import os
import subprocess
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
        command = config.transcribe_command + [transcribe_path]

        if config.dev_mode:
            filename = os.path.basename(audio_path)
            print(f"⏳ Transcribing {filename}...", flush=True)

        result: subprocess.CompletedProcess = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Transcription failed: {result.stderr}")

        text = result.stdout.strip()

        if config.dev_mode and text:
            text_with_disclaimer = f"{config.disclaimer} {text}"
            print(f"✓ {text_with_disclaimer}\n", flush=True)

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
                if config.dev_mode:
                    print(f"✓ pink-transcriber is ready (attempt {attempt + 1})", flush=True)
                return True
            if attempt < config.service_max_attempts - 1:
                if config.dev_mode:
                    print(f"⏳ Waiting for pink-transcriber... ({attempt + 1}/{config.service_max_attempts})", flush=True)
                time.sleep(config.service_wait_interval)

        if config.dev_mode:
            print("✗ pink-transcriber failed to start after 6 seconds", flush=True)
        return False
