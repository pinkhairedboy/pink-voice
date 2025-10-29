"""Configuration for Pink Voice."""

import os
import platform
from dataclasses import dataclass
from typing import List


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

    # UI
    disclaimer: str = "[Voice input - if anything sounds unclear or nonsensical, please ask for clarification]"

    # Development mode
    dev_mode: bool = False

    def __post_init__(self) -> None:
        """Initialize configuration from environment."""
        self.dev_mode = os.getenv('DEV') == '1'
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
