"""Hotkey listener for Ctrl+Q."""

import os
import sys
import threading
from typing import Callable, Optional

from pynput import keyboard

from pink_voice.config import config


class HotkeyListener:
    """Listens for Ctrl+Q hotkey combination."""

    def __init__(self, on_trigger: Callable[[], None]) -> None:
        """
        Initialize hotkey listener.

        Args:
            on_trigger: Callback function to call when hotkey is triggered
        """
        self.on_trigger: Callable[[], None] = on_trigger
        self.listener: Optional[keyboard.Listener] = None
        self.ctrl_is_held: bool = False
        self.hotkey_triggered: bool = False

    def start(self) -> None:
        """Start listening for hotkey presses."""
        if os.getenv('DEV') == '1':
            print("Listening for Ctrl+Q", flush=True)

        def on_press(key: keyboard.Key) -> None:
            try:
                key_name: str = key.char if hasattr(key, 'char') else str(key)
            except AttributeError:
                key_name = str(key)

            if key_name in ('Key.ctrl_l', 'Key.ctrl_r', 'Key.ctrl'):
                self.ctrl_is_held = True
                return

            if (key_name == 'q' or key_name == '\x11') and self.ctrl_is_held and not self.hotkey_triggered:
                self.hotkey_triggered = True
                threading.Thread(target=self.on_trigger, daemon=True).start()

        def on_release(key: keyboard.Key) -> None:
            try:
                key_name: str = key.char if hasattr(key, 'char') else str(key)
            except AttributeError:
                key_name = str(key)

            if key_name in ('Key.ctrl_l', 'Key.ctrl_r', 'Key.ctrl'):
                self.ctrl_is_held = False

            # Reset trigger on 'q' OR '\x11' release
            if key_name == 'q' or key_name == '\x11':
                self.hotkey_triggered = False

        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.listener.start()

    def stop(self) -> None:
        """Stop listening for hotkey presses."""
        if self.listener:
            self.listener.stop()
