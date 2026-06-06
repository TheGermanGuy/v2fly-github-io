"""
Pydroid 3 Storage Manager
Abstrahiert Dateisystem-Zugriff für Pydroid-spezifische Pfade
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from typing import Optional, List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from kivy_gui.utils.pydroid_env import pydroid_env


class PydroidStorageManager:
    """Verwaltet Dateisystem-Zugriffe für Pydroid"""

    def __init__(self):
        self.env = pydroid_env
        self._ensure_directories()

    def _ensure_directories(self):
        """Erstelle alle nötigen Verzeichnisse"""
        for path_func in [
            self.get_app_data_dir,
            self.get_cache_dir,
            self.get_temp_dir,
            self.get_backups_dir,
            self.get_exports_dir,
            self.get_logs_dir,
        ]:
            try:
                path = path_func()
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                print(f"[WARN] Could not create {path_func.__name__}: {e}")

    # ========== DIRECTORY PATHS ==========

    def get_app_data_dir(self) -> str:
        """
        Gebe App-Daten-Verzeichnis

        Pydroid 3: /storage/emulated/0/Documents/m3uScan/data/
        Desktop: ~/.m3uscan/data/
        """
        return os.path.join(self.env.get_storage_path(), 'data')

    def get_cache_dir(self) -> str:
        """Cache-Verzeichnis für volatile Daten"""
        return os.path.join(self.env.get_storage_path(), '.cache')

    def get_temp_dir(self) -> str:
        """Temporäres Verzeichnis"""
        temp_path = os.path.join(self.env.get_storage_path(), '.tmp')
        return temp_path

    def get_backups_dir(self) -> str:
        """Backup-Verzeichnis"""
        return os.path.join(self.env.get_storage_path(), 'backups')

    def get_exports_dir(self) -> str:
        """Export-Verzeichnis (M3U+ Files)"""
        return os.path.join(self.env.get_storage_path(), 'exports')

    def get_logs_dir(self) -> str:
        """Logs-Verzeichnis"""
        return os.path.join(self.env.get_storage_path(), 'logs')

    # ========== FILE OPERATIONS ==========

    def read_json(self, filename: str, directory: str = None) -> dict:
        """
        Lese JSON-Datei mit Error-Handling

        Args:
            filename: z.B. "link_ledger.json"
            directory: z.B. "data" oder None für get_app_data_dir()
        """
        if directory is None:
            directory = self.get_app_data_dir()
        else:
            # Handle relative directory names
            directory = getattr(self, f'get_{directory}_dir')() if hasattr(self, f'get_{directory}_dir') else os.path.join(self.env.get_storage_path(), directory)

        filepath = os.path.join(directory, filename)

        try:
            if not os.path.exists(filepath):
                return {}

            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode error in {filename}: {e}")
            return {}
        except Exception as e:
            print(f"[ERROR] Error reading {filename}: {e}")
            return {}

    def write_json(self, data: dict, filename: str, directory: str = None) -> bool:
        """
        Schreibe JSON-Datei mit Atomic-Write

        Args:
            data: Dict zum Speichern
            filename: z.B. "link_ledger.json"
            directory: z.B. "data" oder None
        """
        if directory is None:
            directory = self.get_app_data_dir()
        else:
            directory = getattr(self, f'get_{directory}_dir')() if hasattr(self, f'get_{directory}_dir') else os.path.join(self.env.get_storage_path(), directory)

        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)
        temp_filepath = filepath + '.tmp'

        try:
            # Atomic Write: schreibe zu .tmp erst
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic Rename
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_filepath, filepath)

            return True
        except Exception as e:
            print(f"[ERROR] Error writing {filename}: {e}")
            # Cleanup temp file
            try:
                os.remove(temp_filepath)
            except:
                pass
            return False

    def read_text(self, filename: str, directory: str = None) -> str:
        """Lese Text-Datei"""
        if directory is None:
            directory = self.get_app_data_dir()

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[ERROR] Error reading {filename}: {e}")
            return ""

    def write_text(self, content: str, filename: str, directory: str = None) -> bool:
        """Schreibe Text-Datei"""
        if directory is None:
            directory = self.get_app_data_dir()

        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[ERROR] Error writing {filename}: {e}")
            return False

    # ========== BACKUP & RECOVERY ==========

    def create_backup(self, source_filename: str, directory: str = None) -> Optional[str]:
        """
        Erstelle Backup einer Datei

        Returns:
            Backup-Dateinamen oder None bei Error
        """
        if directory is None:
            directory = self.get_app_data_dir()

        source_path = os.path.join(directory, source_filename)
        if not os.path.exists(source_path):
            return None

        # Backup Naming: filename_YYYYMMDD_HHMMSS.bak
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(source_filename)
        backup_filename = f"{name}_{timestamp}.bak"
        backup_path = os.path.join(self.get_backups_dir(), backup_filename)

        try:
            shutil.copy2(source_path, backup_path)
            return backup_filename
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return None

    def cleanup_old_backups(self, keep_days: int = 7, max_backups: int = 5):
        """
        Lösche alte Backups

        Args:
            keep_days: Behalte Backups der letzten N Tage
            max_backups: Behalte max N Backups
        """
        backups_dir = self.get_backups_dir()

        try:
            # Sammle alle .bak Dateien mit Modify-Zeit
            backups = []
            for f in os.listdir(backups_dir):
                if f.endswith('.bak'):
                    path = os.path.join(backups_dir, f)
                    mtime = os.path.getmtime(path)
                    backups.append((path, mtime))

            # Sortiere nach Modify-Zeit (neuste zuerst)
            backups.sort(key=lambda x: x[1], reverse=True)

            # Lösche alte Backups
            cutoff_time = (datetime.now() - timedelta(days=keep_days)).timestamp()

            for path, mtime in backups:
                # Behalte max N Backups
                if len(backups) > max_backups:
                    os.remove(path)
                    backups.pop()
                # Lösche wenn älter als keep_days
                elif mtime < cutoff_time:
                    os.remove(path)
        except Exception as e:
            print(f"[WARN] Backup cleanup failed: {e}")

    def restore_from_backup(self, backup_filename: str, target_filename: str, directory: str = None) -> bool:
        """Stelle aus Backup wieder her"""
        if directory is None:
            directory = self.get_app_data_dir()

        backup_path = os.path.join(self.get_backups_dir(), backup_filename)
        target_path = os.path.join(directory, target_filename)

        if not os.path.exists(backup_path):
            print(f"[ERROR] Backup not found: {backup_filename}")
            return False

        try:
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            return False

    # ========== STORAGE MONITORING ==========

    def get_available_space_mb(self) -> int:
        """Gebe verfügbarer Storage in MB"""
        return self.env.get_available_storage_mb()

    def is_storage_low(self, threshold_mb: int = 100) -> bool:
        """Prüfe ob Storage niedrig"""
        return self.get_available_space_mb() < threshold_mb

    def get_storage_stats(self) -> dict:
        """Gebe Storage-Statistiken"""
        try:
            stats = shutil.disk_usage(self.env.get_storage_path())
            return {
                'total_mb': stats.total // (1024 * 1024),
                'used_mb': stats.used // (1024 * 1024),
                'free_mb': stats.free // (1024 * 1024),
                'percent_used': int((stats.used / stats.total) * 100),
            }
        except Exception as e:
            print(f"[WARN] Could not get storage stats: {e}")
            return {}

    # ========== CACHE MANAGEMENT ==========

    def clear_cache(self) -> bool:
        """Lösche Cache-Verzeichnis"""
        try:
            cache_dir = self.get_cache_dir()
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            return True
        except Exception as e:
            print(f"[ERROR] Cache clear failed: {e}")
            return False

    def cleanup_temp_files(self) -> int:
        """Lösche Temp-Files, gebe Anzahl gelöschter Dateien"""
        count = 0
        temp_dir = self.get_temp_dir()

        try:
            if os.path.exists(temp_dir):
                for f in os.listdir(temp_dir):
                    try:
                        path = os.path.join(temp_dir, f)
                        if os.path.isfile(path):
                            os.remove(path)
                            count += 1
                        elif os.path.isdir(path):
                            shutil.rmtree(path)
                            count += 1
                    except Exception:
                        pass
        except Exception as e:
            print(f"[WARN] Temp cleanup failed: {e}")

        return count

    # ========== PERMISSIONS ==========

    def check_write_permission(self, directory: str = None) -> bool:
        """Prüfe ob Schreibrechte vorhanden"""
        if directory is None:
            directory = self.get_app_data_dir()

        return os.access(directory, os.W_OK)

    def check_read_permission(self, directory: str = None) -> bool:
        """Prüfe ob Leserechte vorhanden"""
        if directory is None:
            directory = self.get_app_data_dir()

        return os.access(directory, os.R_OK)

    # ========== DIAGNOSTICS ==========

    def get_storage_report(self) -> dict:
        """Gebe Storage-Report für Debugging"""
        return {
            'data_dir': self.get_app_data_dir(),
            'cache_dir': self.get_cache_dir(),
            'backups_dir': self.get_backups_dir(),
            'storage_stats': self.get_storage_stats(),
            'available_space_mb': self.get_available_space_mb(),
            'storage_low': self.is_storage_low(),
            'write_permission': self.check_write_permission(),
            'read_permission': self.check_read_permission(),
        }

    def print_storage_report(self):
        """Gebe Storage-Report aus"""
        report = self.get_storage_report()
        print("\n" + "=" * 60)
        print("PYDROID STORAGE REPORT")
        print("=" * 60)
        for key, value in report.items():
            print(f"{key:25} : {value}")
        print("=" * 60 + "\n")


# Global Instance
pydroid_storage = PydroidStorageManager()
