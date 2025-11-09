"""Configuration for Pink Voice."""

import os
import platform
from dataclasses import dataclass
from typing import List


# Singleton configuration
VERBOSE_MODE = os.getenv('VERBOSE') == '1'
SINGLETON_IDENTIFIERS = [
    'pink-voice',
    'pink_voice',
    'Pink Voice',
    'Pink Voice.exe',
    'pink_voice.__main__',  # PyInstaller entry point
]


def _detect_platform() -> str:
    """Detect current platform."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "unknown"


def _get_ui_mode() -> str:
    """Get UI mode based on platform and environment."""
    env_ui = os.getenv('PINK_VOICE_UI', '').lower()
    if env_ui in ('macos', 'headless'):
        return env_ui

    detected_platform = _detect_platform()
    if detected_platform == "macos":
        return "macos"
    else:
        return "headless"


def _get_transcribe_command() -> List[str]:
    """Get transcribe command based on platform."""
    detected_platform = _detect_platform()
    if detected_platform == "windows":
        return ['wsl', 'pink-transcriber']
    else:
        return ['pink-transcriber']


def windows_path_to_wsl(path: str) -> str:
    """
    Convert Windows path to WSL path.

    Args:
        path: Windows path (e.g., C:\\Users\\name\\file.wav)

    Returns:
        WSL path (e.g., /mnt/c/Users/name/file.wav)
    """
    if not path:
        return path

    path = path.replace('\\', '/')

    if len(path) >= 2 and path[1] == ':':
        drive = path[0].lower()
        rest = path[2:]
        return f"/mnt/{drive}{rest}"

    return path


# Sound file paths
MACOS_SOUND_PATHS = {
    "start": "/System/Library/Sounds/Ping.aiff",
    "stop": "/System/Library/Sounds/Ping.aiff",
    "done": "/System/Library/Sounds/Glass.aiff",
}

WINDOWS_SOUND_PATHS = {
    "start": r"C:\Windows\Media\Speech On.wav",
    "stop": r"C:\Windows\Media\Speech Sleep.wav",
    "done": r"C:\Windows\Media\Speech Disambiguation.wav",
}


@dataclass
class Config:
    """Application configuration."""

    # Platform detection
    platform: str = ""
    ui_mode: str = ""
    transcribe_command: List[str] = None

    # Service timeouts
    health_check_timeout: int = 2
    service_wait_interval: int = 2
    service_max_attempts: int = 3

    # Audio
    sample_rate: int = 16000

    def __post_init__(self) -> None:
        """Initialize configuration from environment."""
        self.platform = _detect_platform()
        self.ui_mode = _get_ui_mode()
        self.transcribe_command = _get_transcribe_command()

    def convert_path_for_transcribe(self, path: str) -> str:
        """
        Convert path to format suitable for transcribe command.

        Args:
            path: Local file path

        Returns:
            Path in format suitable for transcribe command
        """
        if self.platform == "windows":
            return windows_path_to_wsl(path)
        return path


# Global config instance
config = Config()
