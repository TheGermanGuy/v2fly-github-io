"""
Platform Detection für Android/Desktop
"""

import sys
import os
from typing import Literal


class PlatformDetector:
    """Erkennt Betriebssystem und Gerättyp"""

    @staticmethod
    def get_platform() -> Literal["android", "ios", "windows", "linux", "macos"]:
        """Erkenne aktuelle Plattform"""
        if PlatformDetector.is_android():
            return "android"
        elif PlatformDetector.is_ios():
            return "ios"
        elif sys.platform == "win32":
            return "windows"
        elif sys.platform == "darwin":
            return "macos"
        else:
            return "linux"

    @staticmethod
    def is_android() -> bool:
        """Erkenne Android/Pydroid/QPython"""
        android_indicators = [
            'PYDROID' in sys.version,
            'ANDROID_SDK' in os.environ,
            'android' in sys.modules,
            'ANDROID_ROOT' in os.environ,
            '/data/data/' in os.path.expanduser('~'),
        ]
        return any(android_indicators)

    @staticmethod
    def is_ios() -> bool:
        """Erkenne iOS"""
        return sys.platform == 'ios'

    @staticmethod
    def is_mobile() -> bool:
        """Erkenne mobiles Gerät"""
        return PlatformDetector.is_android() or PlatformDetector.is_ios()

    @staticmethod
    def is_desktop() -> bool:
        """Erkenne Desktop"""
        return not PlatformDetector.is_mobile()

    @staticmethod
    def get_screen_size_category() -> Literal["phone", "tablet", "desktop"]:
        """Kategorisiere Gerätetyp basierend auf Bildschirmgröße"""
        from kivy.core.window import Window

        width = Window.width

        if width < 600:
            return "phone"
        elif width < 1024:
            return "tablet"
        else:
            return "desktop"

    @staticmethod
    def is_qpython() -> bool:
        """Erkenne QPython 3"""
        return "QPython" in sys.version or "qpython" in sys.executable.lower()

    @staticmethod
    def get_python_implementation() -> str:
        """Gebe Python-Implementierung zurück"""
        return sys.implementation.name

    @staticmethod
    def get_system_info() -> dict:
        """Gebe System-Informationen zurück"""
        import platform

        return {
            'platform': PlatformDetector.get_platform(),
            'is_android': PlatformDetector.is_android(),
            'is_mobile': PlatformDetector.is_mobile(),
            'is_qpython': PlatformDetector.is_qpython(),
            'screen_category': PlatformDetector.get_screen_size_category(),
            'python_version': sys.version,
            'python_impl': PlatformDetector.get_python_implementation(),
            'platform_info': platform.platform(),
        }


# Global Instance
platform = PlatformDetector()
