"""
m3uScan Kivy GUI - Utilities
"""

from .constants import (
    APP_NAME,
    APP_VERSION,
    DATA_DIR,
    LEDGER_FILE,
    THEME_DARK,
    THEME_LIGHT,
    STATUS_EMOJIS,
)
from .platform_detect import platform, PlatformDetector
from .theme import theme, ThemeManager
from .responsive import responsive, ResponsiveManager

__all__ = [
    "platform",
    "PlatformDetector",
    "theme",
    "ThemeManager",
    "responsive",
    "ResponsiveManager",
    "APP_NAME",
    "APP_VERSION",
    "DATA_DIR",
    "LEDGER_FILE",
    "THEME_DARK",
    "THEME_LIGHT",
    "STATUS_EMOJIS",
]
