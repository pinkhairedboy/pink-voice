"""Cross-platform sound utilities."""

import platform
import subprocess


def play_sound(sound_type: str) -> None:
    """
    Play system sound (cross-platform).

    Args:
        sound_type: One of "start", "stop", "done"
    """
    system = platform.system()

    if system == "Darwin":
        _play_sound_macos(sound_type)
    elif system == "Windows":
        _play_sound_windows(sound_type)
    else:
        pass


def _play_sound_macos(sound_type: str) -> None:
    """Play sound on macOS."""
    sound_map = {
        "start": "/System/Library/Sounds/Ping.aiff",
        "stop": "/System/Library/Sounds/Ping.aiff",
        "done": "/System/Library/Sounds/Glass.aiff",
    }

    sound_path = sound_map.get(sound_type)
    if sound_path:
        subprocess.Popen(
            ['afplay', sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )


def _play_sound_windows(sound_type: str) -> None:
    """Play sound on Windows."""
    try:
        import winsound
        sound_map = {
            "start": r"C:\Windows\Media\Speech On.wav",
            "stop": r"C:\Windows\Media\Speech Sleep.wav",
            "done": r"C:\Windows\Media\Speech Disambiguation.wav",
        }
        sound_path = sound_map.get(sound_type)
        if sound_path:
            winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except (ImportError, RuntimeError):
        pass
