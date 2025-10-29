"""Cross-platform clipboard utilities."""

import platform
import subprocess


def copy_to_clipboard(text: str) -> None:
    """
    Copy text to clipboard (cross-platform).

    Args:
        text: Text to copy
    """
    system = platform.system()

    if system == "Darwin":
        _copy_macos(text)
    elif system == "Windows":
        _copy_windows(text)
    elif system == "Linux":
        _copy_linux(text)
    else:
        raise NotImplementedError(f"Clipboard not supported on {system}")


def _copy_macos(text: str) -> None:
    """Copy to clipboard on macOS."""
    process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    process.communicate(text.encode('utf-8'))


def _copy_windows(text: str) -> None:
    """Copy to clipboard on Windows."""
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        raise ImportError("pyperclip not installed. Install with: pip install pyperclip")


def _copy_linux(text: str) -> None:
    """Copy to clipboard on Linux (WSL)."""
    try:
        import pyperclip
        pyperclip.copy(text)
    except ImportError:
        raise ImportError("pyperclip not installed. Install with: pip install pyperclip")
