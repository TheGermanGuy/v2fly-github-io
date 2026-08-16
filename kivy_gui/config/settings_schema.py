"""
Settings Schema & Management
Persistent configuration for m3uScan Kivy GUI
"""

import os
import json
from typing import Any, Optional, Dict


class SettingsSchema:
    """Defines all available settings"""

    DEFAULTS = {
        # UI Settings
        'dark_mode': True,
        'theme_color': 'blue',
        'font_size_multiplier': 1.0,
        'animations_enabled': True,

        # Network Settings
        'network_timeout': 10.0,
        'retry_count': 3,
        'auto_check_interval': 3600,  # 1 hour

        # Performance Settings
        'max_workers': 0,  # 0 = auto-detect
        'batch_size': 0,   # 0 = auto-detect
        'cache_size_mb': 0,  # 0 = auto-detect

        # Storage Settings
        'backup_enabled': True,
        'backup_retention_days': 7,
        'max_backups': 5,
        'auto_cleanup_enabled': True,

        # Notification Settings
        'notifications_enabled': True,
        'vibration_enabled': True,
        'notification_sound': False,
        'show_status_alerts': True,

        # Debug Settings
        'debug_mode': False,
        'verbose_logging': False,
        'keep_logs_days': 7,

        # App Settings
        'auto_start_check': False,
        'check_on_app_launch': False,
        'offline_mode_enabled': True,
    }

    SCHEMA = {
        # UI
        'dark_mode': {'type': 'bool', 'label': 'Dark Mode', 'restart_needed': False},
        'theme_color': {'type': 'str', 'label': 'Theme Color', 'restart_needed': False},
        'font_size_multiplier': {'type': 'float', 'label': 'Font Size', 'min': 0.5, 'max': 2.0},
        'animations_enabled': {'type': 'bool', 'label': 'Animations', 'restart_needed': False},

        # Network
        'network_timeout': {'type': 'float', 'label': 'Network Timeout (s)', 'min': 5.0, 'max': 60.0},
        'retry_count': {'type': 'int', 'label': 'Retry Count', 'min': 0, 'max': 10},
        'auto_check_interval': {'type': 'int', 'label': 'Auto-Check Interval (s)', 'min': 300},

        # Performance
        'max_workers': {'type': 'int', 'label': 'Max Workers', 'min': 0, 'max': 16},
        'batch_size': {'type': 'int', 'label': 'Batch Size', 'min': 0, 'max': 100},
        'cache_size_mb': {'type': 'int', 'label': 'Cache Size (MB)', 'min': 0, 'max': 1000},

        # Storage
        'backup_enabled': {'type': 'bool', 'label': 'Auto Backup'},
        'backup_retention_days': {'type': 'int', 'label': 'Backup Retention (days)', 'min': 1, 'max': 90},
        'max_backups': {'type': 'int', 'label': 'Max Backups', 'min': 1, 'max': 20},
        'auto_cleanup_enabled': {'type': 'bool', 'label': 'Auto Cleanup'},

        # Notifications
        'notifications_enabled': {'type': 'bool', 'label': 'Notifications'},
        'vibration_enabled': {'type': 'bool', 'label': 'Vibration'},
        'notification_sound': {'type': 'bool', 'label': 'Notification Sound'},
        'show_status_alerts': {'type': 'bool', 'label': 'Status Alerts'},

        # Debug
        'debug_mode': {'type': 'bool', 'label': 'Debug Mode'},
        'verbose_logging': {'type': 'bool', 'label': 'Verbose Logging'},
        'keep_logs_days': {'type': 'int', 'label': 'Keep Logs (days)', 'min': 1, 'max': 90},

        # App
        'auto_start_check': {'type': 'bool', 'label': 'Auto-Start Check'},
        'check_on_app_launch': {'type': 'bool', 'label': 'Check on Launch'},
        'offline_mode_enabled': {'type': 'bool', 'label': 'Offline Mode'},
    }


class SettingsManager:
    """Manages persistent settings"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize Settings Manager

        Args:
            config_dir: Directory for settings file (default: ~/.m3uscan/)
        """
        if config_dir is None:
            config_dir = os.path.expanduser('~/.m3uscan')

        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, 'settings.json')
        self.settings = self._load_settings()

    def _load_settings(self) -> dict:
        """Lade Settings aus Datei oder verwende Defaults"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge mit Defaults (neue Keys hinzufügen)
                    settings = SettingsSchema.DEFAULTS.copy()
                    settings.update(loaded)
                    return settings
            except Exception as e:
                print(f"[WARN] Failed to load settings: {e}, using defaults")

        return SettingsSchema.DEFAULTS.copy()

    def _save_settings(self):
        """Speichere Settings in Datei"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Hole Setting-Wert"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """Setze Setting-Wert"""
        if key not in SettingsSchema.DEFAULTS:
            print(f"[WARN] Unknown setting key: {key}")
            return False

        # Validiere Typ
        schema = SettingsSchema.SCHEMA.get(key, {})
        expected_type = schema.get('type')

        if expected_type == 'bool':
            value = bool(value)
        elif expected_type == 'int':
            value = int(value)
            min_val = schema.get('min')
            max_val = schema.get('max')
            if min_val is not None:
                value = max(value, min_val)
            if max_val is not None:
                value = min(value, max_val)
        elif expected_type == 'float':
            value = float(value)
            min_val = schema.get('min')
            max_val = schema.get('max')
            if min_val is not None:
                value = max(value, min_val)
            if max_val is not None:
                value = min(value, max_val)

        self.settings[key] = value
        self._save_settings()
        return True

    def get_all(self) -> dict:
        """Hole alle Settings"""
        return self.settings.copy()

    def reset_to_defaults(self) -> bool:
        """Setze alle Settings auf Defaults zurück"""
        self.settings = SettingsSchema.DEFAULTS.copy()
        self._save_settings()
        return True

    def validate_setting(self, key: str, value: Any) -> tuple:
        """
        Validiere Setting-Wert

        Returns:
            (is_valid, error_message)
        """
        if key not in SettingsSchema.SCHEMA:
            return (False, f"Unknown setting: {key}")

        schema = SettingsSchema.SCHEMA[key]
        expected_type = schema.get('type')

        try:
            if expected_type == 'bool':
                if not isinstance(value, bool):
                    return (False, f"{key} must be boolean")
            elif expected_type == 'int':
                int(value)
                if schema.get('min') and value < schema['min']:
                    return (False, f"{key} must be >= {schema['min']}")
                if schema.get('max') and value > schema['max']:
                    return (False, f"{key} must be <= {schema['max']}")
            elif expected_type == 'float':
                float(value)
                if schema.get('min') and value < schema['min']:
                    return (False, f"{key} must be >= {schema['min']}")
                if schema.get('max') and value > schema['max']:
                    return (False, f"{key} must be <= {schema['max']}")
            elif expected_type == 'str':
                if not isinstance(value, str):
                    return (False, f"{key} must be string")

            return (True, "")
        except ValueError as e:
            return (False, str(e))

    def print_report(self):
        """Gebe Settings-Report aus"""
        print("\n" + "=" * 60)
        print("Settings Report")
        print("=" * 60)
        for key, value in self.settings.items():
            schema = SettingsSchema.SCHEMA.get(key, {})
            label = schema.get('label', key)
            print(f"{label:30} : {value}")
        print("=" * 60 + "\n")


# Global Instance
settings_manager = SettingsManager()
