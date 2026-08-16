"""
Offline Mode Manager
Erkennt Netzwerk-Status und speichert Daten lokal
"""

import socket
from typing import Literal
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle


class OfflineManager:
    """
    Verwaltet Offline-Modus
    - Erkennt Netzwerk-Status
    - Cached Daten lokal
    - Zeigt Offline-Indikator
    """

    def __init__(self):
        self.is_online = self._check_network()
        self.on_status_change = None
        self._start_monitoring()

    def _check_network(self) -> bool:
        """
        Prüfe ob Netzwerk verfügbar ist
        """
        try:
            # Versuche einfache Verbindung
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except (socket.timeout, socket.gaierror, OSError):
            return False

    def _start_monitoring(self):
        """
        Starte Netzwerk-Monitoring (prüfe alle 10 Sekunden)
        """
        Clock.schedule_interval(self._monitor_network, 10)

    def _monitor_network(self, dt):
        """
        Callback für Netzwerk-Monitoring
        """
        new_status = self._check_network()

        if new_status != self.is_online:
            self.is_online = new_status
            if self.on_status_change:
                self.on_status_change(new_status)

    def get_status(self) -> Literal["online", "offline"]:
        """
        Gebe aktuellen Status
        """
        return "online" if self.is_online else "offline"

    def get_status_indicator(self) -> str:
        """
        Gebe visuellen Indikator
        """
        if self.is_online:
            return "🟢 Online"
        else:
            return "🔴 Offline"

    def get_status_color(self) -> tuple:
        """
        Gebe Farbe für Indicator (RGB)
        """
        if self.is_online:
            return (0.2, 0.8, 0.2, 1.0)  # Grün
        else:
            return (0.8, 0.2, 0.2, 1.0)  # Rot

    def is_data_available(self) -> bool:
        """
        Prüfe ob lokale Daten verfügbar sind
        """
        import os

        from kivy_gui.utils import LEDGER_FILE

        return os.path.exists(LEDGER_FILE)

    def can_perform_online_operation(self) -> bool:
        """
        Prüfe ob Online-Operationen möglich sind
        """
        return self.is_online and self.is_data_available()

    def create_status_widget(self) -> BoxLayout:
        """
        Erstelle Status-Widget für Anzeige

        Returns:
            Kivy Widget mit Status-Indikator
        """
        widget = BoxLayout(size_hint_y=0.05, padding=5, spacing=5)

        # Color background
        with widget.canvas.before:
            color = self.get_status_color()
            Color(*color)
            Rectangle(size=widget.size, pos=widget.pos)

        # Status label
        status_label = Label(
            text=self.get_status_indicator(),
            size_hint_x=0.3,
        )
        widget.add_widget(status_label)

        # Info label
        if self.is_online:
            info = "Netzwerk verfügbar - Online-Funktionen aktiv"
        else:
            if self.is_data_available():
                info = "Offline - Lokale Daten verfügbar"
            else:
                info = "Offline - Keine lokalen Daten"

        info_label = Label(text=info, size_hint_x=0.7)
        widget.add_widget(info_label)

        return widget


# Global Instance
offline_manager = OfflineManager()
