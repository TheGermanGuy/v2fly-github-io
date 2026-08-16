"""
Android Notification System
Toast und Notification Manager mit Fallbacks
"""

from typing import Optional
from enum import Enum
from .pydroid_bridge import pydroid_bridge


class NotificationLevel(Enum):
    """Benachrichtigungs-Schweregrad"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationManager:
    """Verwaltet Android-Benachrichtigungen"""

    # Standard-Nachrichten mit Icons
    MESSAGES = {
        NotificationLevel.INFO: "ℹ️ {}",
        NotificationLevel.SUCCESS: "✅ {}",
        NotificationLevel.WARNING: "⚠️ {}",
        NotificationLevel.ERROR: "❌ {}",
    }

    # Standarddauern
    DURATION_SHORT = 1000  # 1 Sekunde
    DURATION_LONG = 3500   # 3.5 Sekunden

    @staticmethod
    def show(
        message: str,
        level: NotificationLevel = NotificationLevel.INFO,
        duration: int = DURATION_SHORT,
        vibrate: bool = False
    ) -> bool:
        """
        Zeige Benachrichtigung

        Args:
            message: Benachrichtigungstext
            level: Schweregrad (info, success, warning, error)
            duration: Dauer in ms
            vibrate: Vibriere Gerät bei Benachrichtigung
        """
        # Formatiere mit Icon
        formatted_msg = NotificationManager.MESSAGES[level].format(message)

        # Vibriere bei Bedarf
        if vibrate:
            vibrate_duration = 50 if level == NotificationLevel.INFO else 100
            pydroid_bridge.vibrate(vibrate_duration)

        # Zeige Toast
        return pydroid_bridge.show_toast(formatted_msg, duration)

    @staticmethod
    def show_info(message: str, duration: int = DURATION_SHORT) -> bool:
        """Zeige Info-Benachrichtigung"""
        return NotificationManager.show(message, NotificationLevel.INFO, duration)

    @staticmethod
    def show_success(message: str, duration: int = DURATION_SHORT, vibrate: bool = True) -> bool:
        """Zeige Success-Benachrichtigung"""
        return NotificationManager.show(message, NotificationLevel.SUCCESS, duration, vibrate)

    @staticmethod
    def show_warning(message: str, duration: int = DURATION_LONG, vibrate: bool = True) -> bool:
        """Zeige Warning-Benachrichtigung"""
        return NotificationManager.show(message, NotificationLevel.WARNING, duration, vibrate)

    @staticmethod
    def show_error(message: str, duration: int = DURATION_LONG, vibrate: bool = True) -> bool:
        """Zeige Error-Benachrichtigung"""
        return NotificationManager.show(message, NotificationLevel.ERROR, duration, vibrate)


class StatusNotifier:
    """Status-spezifische Benachrichtigungen"""

    @staticmethod
    def account_added(username: str) -> bool:
        """Benachrichtigung: Konto hinzugefügt"""
        return NotificationManager.show_success(f"Konto '{username}' hinzugefügt")

    @staticmethod
    def account_deleted(username: str) -> bool:
        """Benachrichtigung: Konto gelöscht"""
        return NotificationManager.show_info(f"Konto '{username}' gelöscht")

    @staticmethod
    def account_updated(username: str) -> bool:
        """Benachrichtigung: Konto aktualisiert"""
        return NotificationManager.show_success(f"Konto '{username}' aktualisiert")

    @staticmethod
    def check_started(count: int) -> bool:
        """Benachrichtigung: Status-Check gestartet"""
        return NotificationManager.show_info(f"Prüfe {count} Konten...")

    @staticmethod
    def check_completed(total: int, ok: int, errors: int) -> bool:
        """Benachrichtigung: Status-Check abgeschlossen"""
        msg = f"✓ {ok}/{total} OK, ✗ {errors} Fehler"
        return NotificationManager.show_success(msg)

    @staticmethod
    def account_expired(username: str) -> bool:
        """Benachrichtigung: Konto abgelaufen"""
        return NotificationManager.show_warning(f"'{username}' läuft bald ab!")

    @staticmethod
    def account_error(username: str, error: str) -> bool:
        """Benachrichtigung: Konto-Fehler"""
        return NotificationManager.show_error(f"'{username}': {error}")

    @staticmethod
    def network_offline() -> bool:
        """Benachrichtigung: Netzwerk offline"""
        return NotificationManager.show_error("Netzwerk offline", vibrate=True)

    @staticmethod
    def network_online() -> bool:
        """Benachrichtigung: Netzwerk online"""
        return NotificationManager.show_info("Netzwerk online")

    @staticmethod
    def storage_low() -> bool:
        """Benachrichtigung: Speicher knapp"""
        return NotificationManager.show_warning("Speicherplatz knapp!", vibrate=True)

    @staticmethod
    def export_completed(filename: str) -> bool:
        """Benachrichtigung: Export abgeschlossen"""
        return NotificationManager.show_success(f"Export: {filename}")

    @staticmethod
    def import_completed(count: int) -> bool:
        """Benachrichtigung: Import abgeschlossen"""
        return NotificationManager.show_success(f"{count} Konten importiert")


# Global Instances
notification_manager = NotificationManager()
status_notifier = StatusNotifier()
