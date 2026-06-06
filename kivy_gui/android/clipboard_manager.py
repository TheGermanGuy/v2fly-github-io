"""
Cross-Platform Clipboard Manager
Clipboard-Zugriff mit Fallbacks für alle Plattformen
"""

import os
from typing import Optional
from .pydroid_bridge import pydroid_bridge


class ClipboardManager:
    """Verwaltet Clipboard-Operationen plattformübergreifend"""

    @staticmethod
    def copy(text: str) -> bool:
        """
        Kopiere Text in Clipboard

        Versucht (der Reihe nach):
        1. Android Jnius (Pydroid 3)
        2. xclip (Linux)
        3. pbcopy (macOS)
        4. clip (Windows)
        5. Fallback: False (nicht verfügbar)
        """
        # Versuche Android zuerst
        if pydroid_bridge.is_available():
            return pydroid_bridge.copy_to_clipboard(text)

        # Versuche Linux xclip
        if os.path.exists('/usr/bin/xclip'):
            try:
                import subprocess
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            except Exception:
                pass

        # Versuche macOS pbcopy
        if os.path.exists('/usr/bin/pbcopy'):
            try:
                import subprocess
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            except Exception:
                pass

        # Versuche Windows clip
        if os.name == 'nt':
            try:
                import subprocess
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE
                )
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            except Exception:
                pass

        # Versuche tkinter als letzter Fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(text)
            root.update()
            root.destroy()
            return True
        except Exception:
            pass

        print("[WARN] Clipboard copy not available on this platform")
        return False

    @staticmethod
    def paste() -> Optional[str]:
        """
        Lese Text aus Clipboard

        Versucht (der Reihe nach):
        1. Android Jnius (Pydroid 3)
        2. xclip (Linux)
        3. pbpaste (macOS)
        4. powershell (Windows)
        5. Fallback: None
        """
        # Versuche Android zuerst
        if pydroid_bridge.is_available():
            return pydroid_bridge.paste_from_clipboard()

        # Versuche Linux xclip
        if os.path.exists('/usr/bin/xclip'):
            try:
                import subprocess
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard', '-o'],
                    stdout=subprocess.PIPE
                )
                output, _ = process.communicate()
                if process.returncode == 0:
                    return output.decode('utf-8')
            except Exception:
                pass

        # Versuche macOS pbpaste
        if os.path.exists('/usr/bin/pbpaste'):
            try:
                import subprocess
                process = subprocess.Popen(
                    ['pbpaste'],
                    stdout=subprocess.PIPE
                )
                output, _ = process.communicate()
                if process.returncode == 0:
                    return output.decode('utf-8')
            except Exception:
                pass

        # Versuche Windows PowerShell
        if os.name == 'nt':
            try:
                import subprocess
                process = subprocess.Popen(
                    ['powershell', '-Command', 'Get-Clipboard'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output, _ = process.communicate()
                if process.returncode == 0:
                    return output.decode('utf-8').strip()
            except Exception:
                pass

        # Versuche tkinter als letzter Fallback
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
        except Exception:
            pass

        print("[WARN] Clipboard paste not available on this platform")
        return None

    @staticmethod
    def copy_credentials(username: str, password: str) -> bool:
        """Kopiere Credentials in Format: username:password"""
        credentials = f"{username}:{password}"
        success = ClipboardManager.copy(credentials)
        if success:
            print(f"[INFO] Credentials copied to clipboard")
        return success

    @staticmethod
    def copy_account_string(host: str, port: int, username: str, password: str) -> bool:
        """Kopiere Account in Format: host:port|username:password"""
        account_str = f"{host}:{port}|{username}:{password}"
        success = ClipboardManager.copy(account_str)
        if success:
            print(f"[INFO] Account string copied to clipboard")
        return success

    @staticmethod
    def paste_credentials() -> Optional[tuple]:
        """
        Lese Credentials aus Clipboard als (username, password) Tuple

        Erwartet Format: username:password
        """
        text = ClipboardManager.paste()
        if text and ':' in text:
            parts = text.strip().split(':', 1)
            if len(parts) == 2:
                return (parts[0], parts[1])
        return None

    @staticmethod
    def paste_account_string() -> Optional[tuple]:
        """
        Lese Account aus Clipboard als (host, port, username, password) Tuple

        Erwartet Format: host:port|username:password
        """
        text = ClipboardManager.paste()
        if text and '|' in text:
            parts = text.strip().split('|', 1)
            if len(parts) == 2:
                host_port = parts[0].split(':')
                user_pass = parts[1].split(':', 1)
                if len(host_port) == 2 and len(user_pass) == 2:
                    try:
                        return (host_port[0], int(host_port[1]), user_pass[0], user_pass[1])
                    except ValueError:
                        pass
        return None


# Global Instance
clipboard_manager = ClipboardManager()
