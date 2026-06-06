"""
Pydroid 3 Native Bridge
Brücke zu nativen Android-Funktionen über Jnius mit Fallbacks
"""

import os
from typing import Optional, Callable

try:
    from jnius import autoclass, cast
    HAS_JNIUS = True
except ImportError:
    HAS_JNIUS = False


class PydroidBridge:
    """Zugriff auf native Android-Funktionen mit graceful Fallbacks"""

    # Java-Klassen (lazy-loaded)
    _PythonService = None
    _Clipboard = None
    _Toast = None
    _Intent = None
    _Uri = None

    @staticmethod
    def is_available() -> bool:
        """Prüfe ob Jnius und native Funktionen verfügbar sind"""
        return HAS_JNIUS

    @staticmethod
    def _get_python_service():
        """Hole PythonService Instance"""
        if PydroidBridge._PythonService is None and HAS_JNIUS:
            try:
                from jnius import autoclass
                PythonService = autoclass('org.renpy.android.PythonService')
                PydroidBridge._PythonService = PythonService.mService
            except Exception as e:
                print(f"[WARN] Could not load PythonService: {e}")
        return PydroidBridge._PythonService

    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """Kopiere Text in Android Clipboard"""
        if not HAS_JNIUS:
            print("[INFO] Jnius not available - clipboard copy skipped")
            return False

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            clipboard = context.getSystemService('clipboard')
            clip = autoclass('android.content.ClipData').newPlainText('m3uScan', text)
            clipboard.setPrimaryClip(clip)
            return True
        except Exception as e:
            print(f"[WARN] Clipboard copy failed: {e}")
            return False

    @staticmethod
    def paste_from_clipboard() -> Optional[str]:
        """Lese Text aus Android Clipboard"""
        if not HAS_JNIUS:
            return None

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            clipboard = context.getSystemService('clipboard')
            if clipboard.hasPrimaryClip():
                clip = clipboard.getPrimaryClip()
                item = clip.getItemAt(0)
                return item.getText().toString()
        except Exception as e:
            print(f"[WARN] Clipboard paste failed: {e}")
        return None

    @staticmethod
    def show_toast(message: str, duration: int = 1000) -> bool:
        """
        Zeige Android Toast-Benachrichtigung

        Args:
            message: Text der Benachrichtigung
            duration: Dauer in ms (1000 = kurz, 3500 = lang)
        """
        if not HAS_JNIUS:
            print(f"[TOAST] {message}")
            return False

        try:
            from jnius import autoclass
            Toast = autoclass('android.widget.Toast')
            context = autoclass('android.app.PythonActivity').mActivity
            duration_const = Toast.LENGTH_LONG if duration > 2000 else Toast.LENGTH_SHORT
            toast = Toast.makeText(context, message, duration_const)
            toast.show()
            return True
        except Exception as e:
            print(f"[WARN] Toast failed: {e}")
            return False

    @staticmethod
    def vibrate(duration_ms: int = 100) -> bool:
        """Vibriere Gerät"""
        if not HAS_JNIUS:
            return False

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            vibrator = context.getSystemService('vibrator')
            vibrator.vibrate(duration_ms)
            return True
        except Exception as e:
            print(f"[WARN] Vibrate failed: {e}")
            return False

    @staticmethod
    def get_clipboard_permission() -> bool:
        """Prüfe Clipboard-Berechtigung"""
        if not HAS_JNIUS:
            return False

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            pm = context.getPackageManager()
            perms = pm.getPackageInfo(
                context.getPackageName(),
                autoclass('android.content.pm.PackageManager').GET_PERMISSIONS
            ).requestedPermissions
            return any('CLIPBOARD' in str(p) for p in perms) if perms else False
        except Exception:
            return False

    @staticmethod
    def open_file_picker(on_file_selected: Optional[Callable[[str], None]] = None) -> bool:
        """
        Öffne Android File Picker (via Intent)

        Fallback: Nutze Text-Input statt GUI Picker auf älteren APIs
        """
        if not HAS_JNIUS:
            print("[INFO] File picker not available without Jnius")
            return False

        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            context = autoclass('android.app.PythonActivity').mActivity

            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType('*/*')
            context.startActivityForResult(intent, 1)
            return True
        except Exception as e:
            print(f"[WARN] File picker failed: {e}")
            return False

    @staticmethod
    def share_text(text: str, title: str = "m3uScan Export") -> bool:
        """Teile Text via Android Share Intent"""
        if not HAS_JNIUS:
            print("[INFO] Share not available without Jnius")
            return False

        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            context = autoclass('android.app.PythonActivity').mActivity

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.putExtra(Intent.EXTRA_TEXT, text)
            intent.setType('text/plain')

            chooser = Intent.createChooser(intent, title)
            context.startActivity(chooser)
            return True
        except Exception as e:
            print(f"[WARN] Share intent failed: {e}")
            return False

    @staticmethod
    def set_status_bar_color(color: str = "#1976D2") -> bool:
        """Setze Android Status Bar Farbe (API 21+)"""
        if not HAS_JNIUS:
            return False

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            window = context.getWindow()

            # Parse hex color
            hex_color = color.lstrip('#')
            color_int = int(hex_color, 16)

            # API 21+ (Lollipop)
            if hasattr(window, 'setStatusBarColor'):
                window.setStatusBarColor(color_int)
                return True
        except Exception as e:
            print(f"[WARN] Set status bar color failed: {e}")

        return False

    @staticmethod
    def keep_screen_on(enabled: bool = True) -> bool:
        """Halte Bildschirm an während App läuft"""
        if not HAS_JNIUS:
            return False

        try:
            from jnius import autoclass
            context = autoclass('android.app.PythonActivity').mActivity
            window = context.getWindow()
            WindowManager = autoclass('android.view.WindowManager')

            if enabled:
                window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            else:
                window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            return True
        except Exception as e:
            print(f"[WARN] Keep screen on failed: {e}")
            return False

    @staticmethod
    def get_device_info() -> dict:
        """Hole Geräte-Informationen via Intent"""
        if not HAS_JNIUS:
            return {}

        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            context = autoclass('android.app.PythonActivity').mActivity

            return {
                'device': Build.DEVICE,
                'manufacturer': Build.MANUFACTURER,
                'model': Build.MODEL,
                'brand': Build.BRAND,
                'version_release': Build.VERSION.RELEASE,
                'version_sdk': Build.VERSION.SDK_INT,
            }
        except Exception as e:
            print(f"[WARN] Get device info failed: {e}")
            return {}


# Global Instance
pydroid_bridge = PydroidBridge()
