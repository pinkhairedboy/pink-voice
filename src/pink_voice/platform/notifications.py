"""Cross-platform notification utilities."""

import platform


def show_notification(title: str, subtitle: str, message: str) -> None:
    """
    Show notification to user (cross-platform).

    Args:
        title: Notification title
        subtitle: Notification subtitle
        message: Notification message
    """
    system = platform.system()

    if system == "Darwin":
        _show_notification_macos(title, subtitle, message)
    elif system == "Windows":
        _show_notification_windows(title, message)
    else:
        pass


def _show_notification_macos(title: str, subtitle: str, message: str) -> None:
    """Show notification on macOS using rumps."""
    try:
        import rumps
        rumps.notification(
            title=title,
            subtitle=subtitle,
            message=message,
            sound=False
        )
    except (ImportError, RuntimeError):
        # RuntimeError: missing Info.plist in dev mode from venv
        pass


def _show_notification_windows(title: str, message: str) -> None:
    """Show notification on Windows."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Pink Voice",
            timeout=5
        )
    except ImportError:
        pass
