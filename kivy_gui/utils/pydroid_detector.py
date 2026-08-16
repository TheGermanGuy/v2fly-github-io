"""
Pydroid 3 Detection & Environment Analysis
Präzise Erkennung von Pydroid vs. andere Android Python Umgebungen
"""

import sys
import os
import platform
from typing import Dict, Optional


class PydroidDetector:
    """Detektiert Pydroid 3 und sammelt Umgebungsinformationen"""

    # Cache für Performance
    _cache = {}

    @staticmethod
    def is_pydroid_3() -> bool:
        """
        Erkenne Pydroid 3 via mehreren Sensoren

        Pydroid 3 Indikatoren:
        - sys.version enthält 'Pydroid'
        - sys.executable enthält 'pydroid' oder 'python'
        - Dateistruktur /data/data/ru.iiec.pydroid3/
        """
        if 'is_pydroid' in PydroidDetector._cache:
            return PydroidDetector._cache['is_pydroid']

        indicators = [
            'PYDROID' in sys.version,
            'pydroid' in sys.executable.lower(),
            '/data/data/ru.iiec.pydroid3/' in sys.executable or
            '/data/data/ru.iiec.pydroid3/' in os.path.expanduser('~'),
            os.path.exists('/data/data/ru.iiec.pydroid3/'),
        ]

        result = any(indicators)
        PydroidDetector._cache['is_pydroid'] = result
        return result

    @staticmethod
    def is_qpython() -> bool:
        """Erkenne QPython (alternative Python IDE auf Android)"""
        if 'is_qpython' in PydroidDetector._cache:
            return PydroidDetector._cache['is_qpython']

        indicators = [
            'QPython' in sys.version,
            'qpython' in sys.executable.lower(),
            '/data/data/org.qpython.qpy' in sys.executable,
        ]

        result = any(indicators)
        PydroidDetector._cache['is_qpython'] = result
        return result

    @staticmethod
    def is_buildozer_apk() -> bool:
        """Erkenne von Buildozer generierte APKs"""
        indicators = [
            'ANDROID_APP_PATH' in os.environ,
            os.path.exists('/data/data/org.test.myapp/'),  # Standard Buildozer Package
            'KIVY_HOME' in os.environ and '/data/data/' in os.environ.get('KIVY_HOME', ''),
        ]
        return any(indicators)

    @staticmethod
    def is_android() -> bool:
        """Erkenne alle Android Python Umgebungen"""
        return (PydroidDetector.is_pydroid_3() or
                PydroidDetector.is_qpython() or
                PydroidDetector.is_buildozer_apk())

    @staticmethod
    def get_pydroid_version() -> Optional[str]:
        """Extrahiere Pydroid-Versionsnummer"""
        try:
            # Pydroid Version ist oft in sys.version
            import re
            match = re.search(r'Pydroid 3[.\d]*', sys.version)
            if match:
                return match.group(0)
        except Exception:
            pass
        return None

    @staticmethod
    def get_android_api_level() -> Optional[int]:
        """Gebe Android API Level"""
        try:
            api_level = os.environ.get('ANDROID_API_LEVEL')
            if api_level:
                return int(api_level)

            # Fallback: aus build.prop
            if os.path.exists('/system/build.prop'):
                with open('/system/build.prop', 'r') as f:
                    for line in f:
                        if 'ro.build.version.sdk' in line:
                            return int(line.split('=')[1].strip())
        except Exception:
            pass
        return None

    @staticmethod
    def get_cpu_arch() -> str:
        """Gebe CPU-Architektur (ARMv7, ARM64, x86, etc.)"""
        try:
            machine = platform.machine()
            if 'arm' in machine.lower():
                # Unterscheide ARM64 vs ARMv7
                if '64' in machine or 'aarch64' in machine:
                    return 'ARM64'
                else:
                    return 'ARMv7'
            elif 'x86' in machine:
                return 'x86'
            else:
                return machine
        except Exception:
            return 'unknown'

    @staticmethod
    def is_emulator() -> bool:
        """Erkenne ob auf Emulator läuft"""
        try:
            # Mehrere Emulator-Indikatoren
            build_props = [
                '/system/build.prop',
                '/data/system/build.prop',
            ]

            for prop_file in build_props:
                if os.path.exists(prop_file):
                    with open(prop_file, 'r') as f:
                        content = f.read()
                        if 'ro.kernel.qemu' in content or 'goldfish' in content:
                            return True

            # Alternative: Check für goldfish/qemu im product model
            product = os.environ.get('ro.product.model', '').lower()
            return 'emulator' in product or 'sdk' in product
        except Exception:
            return False

    @staticmethod
    def get_device_model() -> str:
        """Gebe Gerätmodell (Samsung Galaxy S21, Pixel 5, etc.)"""
        try:
            model = os.environ.get('ro.product.model')
            if model:
                return model

            # Fallback: sys.platform
            if PydroidDetector.is_emulator():
                return f"Emulator ({PydroidDetector.get_cpu_arch()})"
            return "Unknown Android Device"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_python_version() -> str:
        """Gebe Python-Versionsnummer"""
        return platform.python_version()

    @staticmethod
    def get_memory_info() -> Dict[str, int]:
        """
        Gebe Memory-Informationen (in MB)

        Returns:
            {'total_mb': int, 'available_mb': int, 'percent_used': int}
        """
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                'total_mb': mem.total // (1024 * 1024),
                'available_mb': mem.available // (1024 * 1024),
                'percent_used': mem.percent,
            }
        except ImportError:
            # Fallback: /proc/meminfo
            try:
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    mem_total = 0
                    mem_avail = 0
                    for line in lines:
                        if 'MemTotal:' in line:
                            mem_total = int(line.split()[1]) // 1024
                        elif 'MemAvailable:' in line:
                            mem_avail = int(line.split()[1]) // 1024

                    return {
                        'total_mb': mem_total,
                        'available_mb': mem_avail,
                        'percent_used': int((1 - mem_avail / mem_total) * 100) if mem_total > 0 else 0,
                    }
            except Exception:
                return {'total_mb': 0, 'available_mb': 0, 'percent_used': 0}

    @staticmethod
    def get_cpu_count() -> int:
        """Gebe Anzahl der CPU-Cores"""
        try:
            return os.cpu_count() or 1
        except Exception:
            return 1

    @staticmethod
    def is_low_memory_device() -> bool:
        """Erkenne Low-Memory Devices (<2GB RAM)"""
        mem_info = PydroidDetector.get_memory_info()
        return mem_info.get('total_mb', 0) < 2048

    @staticmethod
    def get_system_info() -> Dict:
        """Gebe komplette System-Informationen"""
        return {
            'is_pydroid': PydroidDetector.is_pydroid_3(),
            'is_qpython': PydroidDetector.is_qpython(),
            'is_android': PydroidDetector.is_android(),
            'is_emulator': PydroidDetector.is_emulator(),
            'is_low_memory': PydroidDetector.is_low_memory_device(),
            'pydroid_version': PydroidDetector.get_pydroid_version(),
            'android_api_level': PydroidDetector.get_android_api_level(),
            'cpu_arch': PydroidDetector.get_cpu_arch(),
            'cpu_count': PydroidDetector.get_cpu_count(),
            'python_version': PydroidDetector.get_python_version(),
            'device_model': PydroidDetector.get_device_model(),
            'memory_info': PydroidDetector.get_memory_info(),
            'platform': sys.platform,
            'executable': sys.executable,
        }

    @staticmethod
    def print_debug_info():
        """Gebe Debug-Informationen für Troubleshooting aus"""
        info = PydroidDetector.get_system_info()
        print("\n" + "=" * 60)
        print("PYDROID SYSTEM INFORMATION")
        print("=" * 60)
        for key, value in info.items():
            print(f"{key:20} : {value}")
        print("=" * 60 + "\n")


# Global Instance
pydroid = PydroidDetector()
