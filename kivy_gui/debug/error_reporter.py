"""
Error Reporter
Crash Reporting mit Device Context für Pydroid 3
"""

import os
import sys
import traceback
from datetime import datetime
from typing import Optional
from .pydroid_logger import PydroidLogger


class ErrorReporter:
    """Verwaltet Crash-Reports mit Device-Kontext"""

    @staticmethod
    def get_device_context() -> dict:
        """Sammle Device-Kontext-Informationen"""
        try:
            from kivy_gui.utils.pydroid_detector import pydroid_detector
            sys_info = pydroid_detector.get_system_info()
        except ImportError:
            sys_info = {}

        return {
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'platform': sys.platform,
            'system_info': sys_info,
        }

    @staticmethod
    def report_crash(exception: Exception, context: Optional[str] = None):
        """
        Berichte Crash mit vollständigem Kontext

        Args:
            exception: Die gefangene Exception
            context: Optionaler Kontext (z.B. 'account_check', 'import_export')
        """
        logger = PydroidLogger.get_logger()

        # Sammle Kontext
        device_ctx = ErrorReporter.get_device_context()
        tb_str = traceback.format_exc()

        # Schreibe Error-Log
        logger.critical(f"CRASH REPORT - Context: {context}")
        logger.critical(f"Exception Type: {type(exception).__name__}")
        logger.critical(f"Exception Message: {str(exception)}")
        logger.critical(f"Device Info: {device_ctx}")
        logger.critical(f"Traceback:\n{tb_str}")

        # Erstelle Error-Datei für Review
        ErrorReporter._create_error_file(exception, context, device_ctx, tb_str)

    @staticmethod
    def _create_error_file(exception: Exception, context: str, device_ctx: dict, tb_str: str):
        """Erstelle Error-Datei für Debugging"""
        try:
            from kivy_gui.storage.pydroid_storage import pydroid_storage
            error_dir = pydroid_storage.get_logs_dir()
        except ImportError:
            error_dir = os.path.expanduser('~/.m3uscan/logs')

        os.makedirs(error_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        error_file = os.path.join(error_dir, f"error_{timestamp}.txt")

        try:
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write("m3uScan Crash Report\n")
                f.write("=" * 70 + "\n\n")

                f.write(f"Timestamp: {device_ctx.get('timestamp')}\n")
                f.write(f"Context: {context}\n")
                f.write(f"Exception: {type(exception).__name__}: {str(exception)}\n\n")

                f.write("DEVICE INFORMATION\n")
                f.write("-" * 70 + "\n")
                f.write(f"Python Version: {device_ctx.get('python_version')}\n")
                f.write(f"Platform: {device_ctx.get('platform')}\n")

                sys_info = device_ctx.get('system_info', {})
                if sys_info:
                    f.write(f"Device Model: {sys_info.get('device_model')}\n")
                    f.write(f"CPU Arch: {sys_info.get('cpu_arch')}\n")
                    f.write(f"Is Pydroid: {sys_info.get('is_pydroid')}\n")
                    mem_info = sys_info.get('memory_info', {})
                    if mem_info:
                        f.write(f"RAM: {mem_info.get('total_mb')} MB\n")
                        f.write(f"Available: {mem_info.get('available_mb')} MB\n")

                f.write("\nTRACEBACK\n")
                f.write("-" * 70 + "\n")
                f.write(tb_str)
                f.write("\n" + "=" * 70 + "\n")

            print(f"[ERROR] Crash report written to: {error_file}")
        except Exception as e:
            print(f"[ERROR] Failed to write crash report: {e}")

    @staticmethod
    def list_error_reports(log_dir: Optional[str] = None) -> list:
        """Liste alle Error-Reports auf"""
        if log_dir is None:
            try:
                from kivy_gui.storage.pydroid_storage import pydroid_storage
                log_dir = pydroid_storage.get_logs_dir()
            except ImportError:
                log_dir = os.path.expanduser('~/.m3uscan/logs')

        if os.path.exists(log_dir):
            return sorted([f for f in os.listdir(log_dir) if f.startswith('error_')])
        return []

    @staticmethod
    def get_error_report_content(filename: str) -> Optional[str]:
        """Lese Inhalt eines Error-Reports"""
        try:
            from kivy_gui.storage.pydroid_storage import pydroid_storage
            log_dir = pydroid_storage.get_logs_dir()
        except ImportError:
            log_dir = os.path.expanduser('~/.m3uscan/logs')

        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading report: {e}"
        return None

    @staticmethod
    def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """
        Global Exception Handler für unbehandelte Exceptions

        Verwende in main.py:
            sys.excepthook = ErrorReporter.handle_uncaught_exception
        """
        logger = PydroidLogger.get_logger()

        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.critical(
            f"Uncaught Exception: {exc_type.__name__}: {exc_value}",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

        # Erstelle Error-Report
        device_ctx = ErrorReporter.get_device_context()
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        ErrorReporter._create_error_file(exc_value, 'uncaught', device_ctx, tb_str)


# Hilfsfunktionen
def setup_crash_reporting():
    """Installiere Global Exception Handler"""
    sys.excepthook = ErrorReporter.handle_uncaught_exception
    print("[DEBUG] Crash reporting installed")


def report_error(exception: Exception, context: str = "unknown"):
    """Kurz-API für Error-Reporting"""
    ErrorReporter.report_crash(exception, context)
