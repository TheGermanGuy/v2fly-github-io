"""
Responsive Layout Manager
Touch-optimierte Dimensionen für verschiedene Geräte
"""

from kivy.metrics import dp, Metrics
from typing import Literal


class ResponsiveManager:
    """Berechnet responsive Dimensionen basierend auf Gerät"""

    @staticmethod
    def button_height() -> int:
        """Gebe Button-Höhe zurück (min 48dp für Touch)"""
        return max(dp(48), int(Metrics.density * 48))

    @staticmethod
    def button_width() -> int:
        """Gebe Button-Breite zurück"""
        return dp(100)

    @staticmethod
    def bottom_nav_height() -> int:
        """Android Bottom Navigation = 56dp"""
        return dp(56)

    @staticmethod
    def toolbar_height() -> int:
        """Action Bar / Toolbar = 56dp"""
        return dp(56)

    @staticmethod
    def list_item_height() -> int:
        """ListItem height (48dp single, 72dp double line)"""
        return dp(72)

    @staticmethod
    def dialog_width() -> float:
        """Dialog width prozentual"""
        return 0.9

    @staticmethod
    def dialog_height() -> float:
        """Dialog height prozentual"""
        return 0.7

    @staticmethod
    def padding() -> int:
        """Standard Padding (16dp)"""
        return dp(16)

    @staticmethod
    def spacing() -> int:
        """Standard Spacing zwischen Elementen (8dp)"""
        return dp(8)

    @staticmethod
    def icon_size() -> int:
        """Standard Icon Größe (24dp)"""
        return dp(24)

    @staticmethod
    def icon_size_large() -> int:
        """Großes Icon (48dp)"""
        return dp(48)

    @staticmethod
    def is_tablet() -> bool:
        """Erkenne Tablet (breiter als 600dp)"""
        return Metrics.width > dp(600)

    @staticmethod
    def is_phone() -> bool:
        """Erkenne Handy"""
        return not ResponsiveManager.is_tablet()

    @staticmethod
    def get_screen_category() -> Literal["small", "normal", "large", "xlarge"]:
        """Kategorisiere Bildschirmgröße"""
        width_dp = Metrics.width / Metrics.density

        if width_dp < 320:
            return "small"
        elif width_dp < 600:
            return "normal"
        elif width_dp < 960:
            return "large"
        else:
            return "xlarge"

    @staticmethod
    def get_orientation() -> Literal["portrait", "landscape"]:
        """Erkenne Bildschirm-Orientierung"""
        from kivy.core.window import Window

        return "landscape" if Window.width > Window.height else "portrait"

    @staticmethod
    def scale_for_density(size: int) -> int:
        """Skaliere Größe basierend auf Bildschirm-Dichte"""
        return int(size * Metrics.density)

    @staticmethod
    def get_column_count() -> int:
        """Gebe optimale Spalten-Anzahl zurück (z.B. für Grid)"""
        category = ResponsiveManager.get_screen_category()

        if category == "small":
            return 1
        elif category == "normal":
            return 2
        elif category == "large":
            return 3
        else:
            return 4

    @staticmethod
    def get_max_dialog_width() -> int:
        """Gebe maximale Dialog-Breite zurück"""
        from kivy.core.window import Window

        return int(Window.width * 0.9)

    @staticmethod
    def get_font_size_normal() -> int:
        """Standard Font Size"""
        return int(14 * Metrics.density)

    @staticmethod
    def get_font_size_large() -> int:
        """Large Font Size (Headlines)"""
        return int(20 * Metrics.density)

    @staticmethod
    def get_font_size_small() -> int:
        """Small Font Size (Secondary)"""
        return int(12 * Metrics.density)


# Global Instance
responsive = ResponsiveManager()
