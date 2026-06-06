"""
Pydroid Logger
Logging System mit File Rotation für Pydroid 3
"""

import os
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path


class PydroidLogger:
    """Pydroid-optimiertes Logging System"""

    # Logging Levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    _instance = None
    _logger = None
    _log_file = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: Optional[str] = None):
        """
        Initialisiere Logger

        Args:
            log_dir: Directory für Log-Dateien (default: ~/.m3uscan/logs/)
        """
        if PydroidLogger._logger is not None:
            return

        # Bestimme Log-Directory
        if log_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                log_dir = pydroid_storage.get_logs_dir()
            except ImportError:
                log_dir = os.path.expanduser('~/.m3uscan/logs')

        os.makedirs(log_dir, exist_ok=True)

        # Erstelle Logger
        self._logger = logging.getLogger('m3uscan')
        self._logger.setLevel(logging.DEBUG)

        # Entferne alte Handler
        self._logger.handlers = []

        # File Handler mit Rotation
        log_file = os.path.join(log_dir, f"m3uscan_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        file_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)

        # Füge Handler hinzu
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

        self._log_file = log_file

    @staticmethod
    def get_logger():
        """Hole Logger Instance"""
        if PydroidLogger._logger is None:
            PydroidLogger()
        return PydroidLogger._logger

    @staticmethod
    def debug(msg: str, *args, **kwargs):
        """Log DEBUG message"""
        PydroidLogger.get_logger().debug(msg, *args, **kwargs)

    @staticmethod
    def info(msg: str, *args, **kwargs):
        """Log INFO message"""
        PydroidLogger.get_logger().info(msg, *args, **kwargs)

    @staticmethod
    def warning(msg: str, *args, **kwargs):
        """Log WARNING message"""
        PydroidLogger.get_logger().warning(msg, *args, **kwargs)

    @staticmethod
    def error(msg: str, *args, **kwargs):
        """Log ERROR message"""
        PydroidLogger.get_logger().error(msg, *args, **kwargs)

    @staticmethod
    def critical(msg: str, *args, **kwargs):
        """Log CRITICAL message"""
        PydroidLogger.get_logger().critical(msg, *args, **kwargs)

    @staticmethod
    def get_log_file() -> Optional[str]:
        """Hole Log-Datei Pfad"""
        if PydroidLogger._logger is None:
            PydroidLogger()
        return PydroidLogger._instance._log_file

    @staticmethod
    def get_log_content() -> str:
        """Hole Inhalt der aktuellen Log-Datei"""
        log_file = PydroidLogger.get_log_file()
        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading log file: {e}"
        return "No log file found"

    @staticmethod
    def list_log_files(log_dir: Optional[str] = None) -> list:
        """Liste alle Log-Dateien auf"""
        if log_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                log_dir = pydroid_storage.get_logs_dir()
            except ImportError:
                log_dir = os.path.expanduser('~/.m3uscan/logs')

        if os.path.exists(log_dir):
            return sorted([f for f in os.listdir(log_dir) if f.endswith('.log')])
        return []

    @staticmethod
    def cleanup_old_logs(days: int = 7, log_dir: Optional[str] = None):
        """Lösche alte Log-Dateien älter als N Tage"""
        import time

        if log_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                log_dir = pydroid_storage.get_logs_dir()
            except ImportError:
                log_dir = os.path.expanduser('~/.m3uscan/logs')

        if not os.path.exists(log_dir):
            return

        cutoff_time = time.time() - (days * 24 * 60 * 60)
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                try:
                    os.remove(filepath)
                    print(f"[LOG] Deleted old log file: {filename}")
                except Exception as e:
                    print(f"[WARN] Could not delete {filename}: {e}")


# Global Instance
logger = PydroidLogger.get_logger()
