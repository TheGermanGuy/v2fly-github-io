"""
Device Profiles
Pre-tuned configuration profiles for different device types
"""

from typing import Dict, Optional


class DeviceProfile:
    """Represents a device configuration profile"""

    def __init__(self, name: str, settings: Dict):
        self.name = name
        self.settings = settings

    def __str__(self):
        return f"{self.name}: {self.settings}"


class DeviceProfiles:
    """Collection of pre-tuned device profiles"""

    # Low-Memory Device Profile (< 2GB RAM)
    LOW_MEMORY = DeviceProfile(
        "Low-Memory Device",
        {
            'dark_mode': True,
            'animations_enabled': False,
            'max_workers': 1,
            'batch_size': 5,
            'cache_size_mb': 50,
            'notifications_enabled': True,
            'verbose_logging': False,
        }
    )

    # Normal Device Profile (2-4GB RAM)
    NORMAL = DeviceProfile(
        "Normal Device",
        {
            'dark_mode': True,
            'animations_enabled': True,
            'max_workers': 2,
            'batch_size': 10,
            'cache_size_mb': 100,
            'notifications_enabled': True,
            'verbose_logging': False,
        }
    )

    # High-Performance Device Profile (> 4GB RAM)
    HIGH_PERFORMANCE = DeviceProfile(
        "High-Performance Device",
        {
            'dark_mode': True,
            'animations_enabled': True,
            'max_workers': 4,
            'batch_size': 25,
            'cache_size_mb': 300,
            'notifications_enabled': True,
            'verbose_logging': False,
        }
    )

    # Pydroid 3 Optimized Profile
    PYDROID_3 = DeviceProfile(
        "Pydroid 3 Optimized",
        {
            'dark_mode': True,
            'animations_enabled': False,  # ARM CPU is slow
            'max_workers': 2,
            'batch_size': 10,
            'cache_size_mb': 100,
            'network_timeout': 15.0,  # Pydroid network is slow
            'notifications_enabled': True,
            'vibration_enabled': True,  # Native Android
            'offline_mode_enabled': True,
            'verbose_logging': False,
        }
    )

    # Desktop Profile
    DESKTOP = DeviceProfile(
        "Desktop",
        {
            'dark_mode': False,
            'animations_enabled': True,
            'max_workers': 8,
            'batch_size': 50,
            'cache_size_mb': 500,
            'network_timeout': 10.0,
            'notifications_enabled': False,  # Desktop doesn't use native notifications
            'verbose_logging': False,
        }
    )

    # Development Profile (verbose logging)
    DEVELOPMENT = DeviceProfile(
        "Development",
        {
            'dark_mode': True,
            'animations_enabled': True,
            'max_workers': 4,
            'batch_size': 10,
            'cache_size_mb': 200,
            'debug_mode': True,
            'verbose_logging': True,
            'notifications_enabled': True,
            'keep_logs_days': 30,
        }
    )

    @staticmethod
    def get_all_profiles() -> Dict[str, DeviceProfile]:
        """Get all available profiles"""
        return {
            'low_memory': DeviceProfiles.LOW_MEMORY,
            'normal': DeviceProfiles.NORMAL,
            'high_performance': DeviceProfiles.HIGH_PERFORMANCE,
            'pydroid3': DeviceProfiles.PYDROID_3,
            'desktop': DeviceProfiles.DESKTOP,
            'development': DeviceProfiles.DEVELOPMENT,
        }

    @staticmethod
    def get_profile(name: str) -> Optional[DeviceProfile]:
        """Get profile by name"""
        profiles = DeviceProfiles.get_all_profiles()
        return profiles.get(name.lower())

    @staticmethod
    def auto_select_profile() -> DeviceProfile:
        """Auto-select optimal profile based on current device"""
        try:
            from kivy_gui.utils.pydroid_detector import pydroid_detector
            from kivy_gui.utils.pydroid_env import pydroid_env

            # Erkenne Pydroid 3
            if pydroid_detector.is_pydroid_3():
                return DeviceProfiles.PYDROID_3

            # Erkenne Desktop
            if not pydroid_detector.is_android():
                return DeviceProfiles.DESKTOP

            # Basierend auf RAM-Größe
            mem_info = pydroid_detector.get_memory_info()
            total_mb = mem_info.get('total_mb', 0)

            if total_mb < 2048:
                return DeviceProfiles.LOW_MEMORY
            elif total_mb < 4096:
                return DeviceProfiles.NORMAL
            else:
                return DeviceProfiles.HIGH_PERFORMANCE

        except ImportError:
            # Fallback zu Desktop
            return DeviceProfiles.DESKTOP

    @staticmethod
    def apply_profile(profile: DeviceProfile, settings_manager) -> bool:
        """Apply profile settings to SettingsManager"""
        try:
            for key, value in profile.settings.items():
                settings_manager.set(key, value)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to apply profile: {e}")
            return False

    @staticmethod
    def print_profiles():
        """Print all available profiles"""
        print("\n" + "=" * 60)
        print("Available Device Profiles")
        print("=" * 60)
        for name, profile in DeviceProfiles.get_all_profiles().items():
            print(f"\n[{name.upper()}] {profile.name}")
            print("-" * 60)
            for key, value in profile.settings.items():
                print(f"  {key:30} : {value}")
        print("\n" + "=" * 60 + "\n")


# Hilfsfunktionen
def apply_auto_profile(settings_manager) -> str:
    """Auto-select and apply optimal profile"""
    profile = DeviceProfiles.auto_select_profile()
    DeviceProfiles.apply_profile(profile, settings_manager)
    return profile.name
