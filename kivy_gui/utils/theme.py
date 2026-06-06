"""
Theme Management - Dark Mode + Color System
"""

from .constants import THEME_DARK, THEME_LIGHT, BUTTON_HEIGHT_DP
from kivy.metrics import dp


class ThemeManager:
    """Verwaltet App-Farben und Erscheinungsbild"""

    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        self.colors = THEME_DARK if dark_mode else THEME_LIGHT

    def set_dark_mode(self, enabled: bool):
        """Ändere Dark Mode"""
        self.dark_mode = enabled
        self.colors = THEME_DARK if enabled else THEME_LIGHT

    def get_color(self, key: str, default: str = None) -> str:
        """Gebe Farb-Wert zurück"""
        return self.colors.get(key, default or self.colors.get('text'))

    def get_bg_color(self) -> tuple:
        """Gebe Background-Farbe als RGBA tuple zurück"""
        return self._hex_to_rgb(self.colors['background'])

    def get_surface_color(self) -> tuple:
        """Gebe Surface-Farbe zurück"""
        return self._hex_to_rgb(self.colors['surface'])

    def get_text_color(self) -> tuple:
        """Gebe Text-Farbe zurück"""
        return self._hex_to_rgb(self.colors['text'])

    def get_primary_color(self) -> tuple:
        """Gebe Primary Brand-Farbe zurück"""
        return self._hex_to_rgb(self.colors['primary'])

    def get_accent_color(self) -> tuple:
        """Gebe Accent-Farbe zurück"""
        return self._hex_to_rgb(self.colors['accent'])

    def get_status_color(self, status: str) -> str:
        """Gebe Farbe basierend auf Status zurück"""
        status_map = {
            'ok': 'success',
            'active': 'success',
            'error': 'error',
            'expired': 'error',
            'warning': 'warning',
            'pending': 'info',
            'offline': 'error',
        }
        color_key = status_map.get(status, 'text')
        return self.colors.get(color_key)

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """Konvertiere Hex zu RGB (0-1 Wertebereich)"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b, 1.0)

    @staticmethod
    def get_elevation_shadow() -> str:
        """Gebe Schatten-Effekt für Elevation zurück"""
        return "rgba(0, 0, 0, 0.2)"

    @staticmethod
    def get_button_size() -> int:
        """Gebe optimale Button-Größe zurück"""
        return dp(BUTTON_HEIGHT_DP)

    def apply_to_widget(self, widget):
        """Wende Theme auf Widget an"""
        widget.canvas.before.clear()
        from kivy.graphics import Color, Rectangle

        with widget.canvas.before:
            Color(*self.get_surface_color())
            Rectangle(size=widget.size, pos=widget.pos)


# Global Theme Instance
theme = ThemeManager(dark_mode=True)
