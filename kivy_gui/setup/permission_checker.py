"""
Android Permission Checker
Runtime Permission Management für Pydroid 3
"""

from typing import List, Dict


class AndroidPermissions:
    """Android Permission Constants"""
    INTERNET = 'android.permission.INTERNET'
    READ_EXTERNAL_STORAGE = 'android.permission.READ_EXTERNAL_STORAGE'
    WRITE_EXTERNAL_STORAGE = 'android.permission.WRITE_EXTERNAL_STORAGE'
    ACCESS_NETWORK_STATE = 'android.permission.ACCESS_NETWORK_STATE'
    VIBRATE = 'android.permission.VIBRATE'


class PermissionChecker:
    """Prüft und verwaltet Android Permissions"""

    # Erforderliche Permissions für m3uScan
    REQUIRED_PERMISSIONS = [
        (AndroidPermissions.INTERNET, 'Network access for status checks'),
        (AndroidPermissions.ACCESS_NETWORK_STATE, 'Detect offline/online status'),
    ]

    # Optionale Permissions
    OPTIONAL_PERMISSIONS = [
        (AndroidPermissions.READ_EXTERNAL_STORAGE, 'Import accounts from files'),
        (AndroidPermissions.WRITE_EXTERNAL_STORAGE, 'Export and backup data'),
        (AndroidPermissions.VIBRATE, 'Haptic feedback for notifications'),
    ]

    @staticmethod
    def is_available() -> bool:
        """Prüfe ob Permission-System verfügbar ist (nur Android)"""
        try:
            from jnius import autoclass
            return True
        except ImportError:
            return False

    @staticmethod
    def has_permission(permission: str) -> bool:
        """
        Prüfe ob bestimmte Permission vorhanden ist

        Args:
            permission: Permission String (z.B. 'android.permission.INTERNET')

        Returns:
            True wenn Permission vorhanden, False sonst
        """
        if not PermissionChecker.is_available():
            return True  # Desktop: immer True

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            pm = context.getPackageManager()
            package_name = context.getPackageName()

            # API 23+ (Android 6.0)
            result = pm.checkPermission(permission, package_name)
            return result == 0  # PackageManager.PERMISSION_GRANTED
        except Exception as e:
            print(f"[WARN] Permission check failed: {e}")
            return False

    @staticmethod
    def request_permission(permission: str) -> bool:
        """
        Fordere bestimmte Permission an (API 23+)

        Auf älteren APIs wird True zurückgegeben (Permission hat Installation-Zeit)
        """
        if not PermissionChecker.is_available():
            return True

        # Prüfe zuerst ob bereits vorhanden
        if PermissionChecker.has_permission(permission):
            return True

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            Build = autoclass('android.os.Build')

            # Nur API 23+ (Android 6.0) unterstützt Runtime Permissions
            if Build.VERSION.SDK_INT < 23:
                return True  # Installation-Time Permissions

            # API 23+: Request Runtime Permission
            activity = context
            from android.permissions import request_permissions, Permission

            # Mapping von Permission-String zu Permission-Konstante
            perm_map = {
                AndroidPermissions.INTERNET: 'android.permission.INTERNET',
                AndroidPermissions.READ_EXTERNAL_STORAGE: 'android.permission.READ_EXTERNAL_STORAGE',
                AndroidPermissions.WRITE_EXTERNAL_STORAGE: 'android.permission.WRITE_EXTERNAL_STORAGE',
                AndroidPermissions.ACCESS_NETWORK_STATE: 'android.permission.ACCESS_NETWORK_STATE',
                AndroidPermissions.VIBRATE: 'android.permission.VIBRATE',
            }

            perm_name = perm_map.get(permission, permission)
            request_permissions([perm_name])
            return True
        except Exception as e:
            print(f"[WARN] Permission request failed: {e}")
            return False

    @staticmethod
    def request_permissions(permissions: List[str]) -> Dict[str, bool]:
        """
        Fordere mehrere Permissions an

        Returns:
            {permission: granted}
        """
        results = {}
        for permission in permissions:
            results[permission] = PermissionChecker.request_permission(permission)
        return results

    @staticmethod
    def check_required() -> Dict[str, bool]:
        """
        Prüfe alle erforderlichen Permissions

        Returns:
            {permission: granted}
        """
        results = {}
        for permission, description in PermissionChecker.REQUIRED_PERMISSIONS:
            results[permission] = PermissionChecker.has_permission(permission)
        return results

    @staticmethod
    def check_optional() -> Dict[str, bool]:
        """
        Prüfe alle optionalen Permissions

        Returns:
            {permission: granted}
        """
        results = {}
        for permission, description in PermissionChecker.OPTIONAL_PERMISSIONS:
            results[permission] = PermissionChecker.has_permission(permission)
        return results

    @staticmethod
    def request_required() -> bool:
        """
        Fordere alle erforderlichen Permissions an

        Returns:
            True wenn alle vorhanden (oder Desktop)
        """
        if not PermissionChecker.is_available():
            return True

        missing = []
        for permission, description in PermissionChecker.REQUIRED_PERMISSIONS:
            if not PermissionChecker.has_permission(permission):
                missing.append((permission, description))

        if missing:
            print("\n[PERMISSIONS] Requesting required permissions:")
            for perm, desc in missing:
                print(f"  - {desc}")
                PermissionChecker.request_permission(perm)

            # Prüfe nochmal
            for perm, desc in missing:
                if not PermissionChecker.has_permission(perm):
                    print(f"  ⚠️ Permission denied: {desc}")
                else:
                    print(f"  ✅ Permission granted: {desc}")

        return all(PermissionChecker.has_permission(p[0]) for p in PermissionChecker.REQUIRED_PERMISSIONS)

    @staticmethod
    def request_optional() -> Dict[str, bool]:
        """Fordere alle optionalen Permissions an"""
        if not PermissionChecker.is_available():
            return {p[0]: True for p in PermissionChecker.OPTIONAL_PERMISSIONS}

        results = {}
        for permission, description in PermissionChecker.OPTIONAL_PERMISSIONS:
            results[permission] = PermissionChecker.request_permission(permission)

        return results

    @staticmethod
    def print_report():
        """Gebe Permission-Report aus"""
        print("\n" + "=" * 60)
        print("Android Permissions Report")
        print("=" * 60)

        print("\n[REQUIRED PERMISSIONS]")
        for perm, desc in PermissionChecker.REQUIRED_PERMISSIONS:
            status = "✅" if PermissionChecker.has_permission(perm) else "❌"
            print(f"{status} {desc}")

        print("\n[OPTIONAL PERMISSIONS]")
        for perm, desc in PermissionChecker.OPTIONAL_PERMISSIONS:
            status = "✅" if PermissionChecker.has_permission(perm) else "⚠️"
            print(f"{status} {desc}")

        print("\n" + "=" * 60 + "\n")


# Hilfsfunktionen für externe Nutzung
def ensure_required_permissions() -> bool:
    """Stelle sicher dass alle erforderlichen Permissions vorhanden sind"""
    return PermissionChecker.request_required()


def get_optional_permissions() -> Dict[str, bool]:
    """Hole Status aller optionalen Permissions"""
    return PermissionChecker.check_optional()


def print_permission_report():
    """Gebe Permission-Report aus"""
    PermissionChecker.print_report()
