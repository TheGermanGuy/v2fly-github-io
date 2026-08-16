"""
Crash Recovery
Auto-recovery from crashes and corrupted state
"""

import os
import json
from datetime import datetime
from typing import Optional


class CrashRecovery:
    """Manages crash recovery and state restoration"""

    RECOVERY_FILE_SUFFIX = '.recovery'

    @staticmethod
    def create_recovery_point(app_state: dict, recovery_dir: Optional[str] = None) -> bool:
        """
        Create recovery point (app state snapshot)

        Args:
            app_state: Current application state
            recovery_dir: Directory for recovery files

        Returns:
            True if recovery point created successfully
        """
        if recovery_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                recovery_dir = os.path.dirname(pydroid_storage.get_app_data_dir())
            except ImportError:
                recovery_dir = os.path.expanduser('~/.m3uscan')

        recovery_file = os.path.join(recovery_dir, f"app_state{CrashRecovery.RECOVERY_FILE_SUFFIX}")

        try:
            # Add timestamp
            app_state['_recovery_timestamp'] = datetime.now().isoformat()

            # Write recovery file atomically
            with open(recovery_file + '.tmp', 'w', encoding='utf-8') as f:
                json.dump(app_state, f, indent=2)

            # Atomic rename
            if os.path.exists(recovery_file):
                os.remove(recovery_file)
            os.rename(recovery_file + '.tmp', recovery_file)

            return True
        except Exception as e:
            print(f"[ERROR] Failed to create recovery point: {e}")
            return False

    @staticmethod
    def restore_recovery_point(recovery_dir: Optional[str] = None) -> Optional[dict]:
        """
        Restore from recovery point

        Returns:
            Restored app state or None if recovery not available
        """
        if recovery_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                recovery_dir = os.path.dirname(pydroid_storage.get_app_data_dir())
            except ImportError:
                recovery_dir = os.path.expanduser('~/.m3uscan')

        recovery_file = os.path.join(recovery_dir, f"app_state{CrashRecovery.RECOVERY_FILE_SUFFIX}")

        if not os.path.exists(recovery_file):
            return None

        try:
            with open(recovery_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to restore recovery point: {e}")
            return None

    @staticmethod
    def cleanup_recovery_point(recovery_dir: Optional[str] = None) -> bool:
        """Remove recovery point after successful recovery"""
        if recovery_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                recovery_dir = os.path.dirname(pydroid_storage.get_app_data_dir())
            except ImportError:
                recovery_dir = os.path.expanduser('~/.m3uscan')

        recovery_file = os.path.join(recovery_dir, f"app_state{CrashRecovery.RECOVERY_FILE_SUFFIX}")

        try:
            if os.path.exists(recovery_file):
                os.remove(recovery_file)
            return True
        except Exception as e:
            print(f"[WARN] Failed to cleanup recovery point: {e}")
            return False

    @staticmethod
    def has_recovery_point(recovery_dir: Optional[str] = None) -> bool:
        """Check if recovery point exists"""
        if recovery_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                recovery_dir = os.path.dirname(pydroid_storage.get_app_data_dir())
            except ImportError:
                recovery_dir = os.path.expanduser('~/.m3uscan')

        recovery_file = os.path.join(recovery_dir, f"app_state{CrashRecovery.RECOVERY_FILE_SUFFIX}")
        return os.path.exists(recovery_file)


class SafeOperation:
    """Context manager for safe operations with automatic recovery"""

    def __init__(self, operation_name: str, app_state: dict = None):
        self.operation_name = operation_name
        self.app_state = app_state or {}
        self.checkpoint_state = None

    def __enter__(self):
        """Save checkpoint before operation"""
        self.checkpoint_state = self.app_state.copy()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Create recovery point if operation failed"""
        if exc_type is not None:
            print(f"[ERROR] Operation '{self.operation_name}' failed: {exc_val}")
            CrashRecovery.create_recovery_point(self.checkpoint_state)
            return False

        # Operation successful - cleanup recovery point
        CrashRecovery.cleanup_recovery_point()
        return False

    @staticmethod
    def execute(operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with automatic error recovery"""
        try:
            return operation_func(*args, **kwargs)
        except Exception as e:
            print(f"[ERROR] Operation '{operation_name}' failed: {e}")
            return None
