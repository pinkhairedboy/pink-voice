"""Configuration for Pink Voice."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    # Sounds
    sound_start: str = '/System/Library/Sounds/Ping.aiff'
    sound_stop: str = '/System/Library/Sounds/Ping.aiff'
    sound_done: str = '/System/Library/Sounds/Glass.aiff'

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


# Global config instance
config = Config()
