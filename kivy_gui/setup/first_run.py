"""
First-Run Setup Wizard
Dependency Checking & Initial Configuration
"""

import sys
import importlib
from typing import List, Dict, Tuple


class DependencyChecker:
    """Prüft und validiert Abhängigkeiten"""

    REQUIRED_MODULES = {
        'kivy': '2.0',
        'aiohttp': '3.7',
        'tqdm': '4.50',
    }

    OPTIONAL_MODULES = {
        'psutil': 'für Memory-Info',
        'jnius': 'für Android Native Features',
        'm3uScan_v21_5': 'Main Scanner Module',
    }

    @staticmethod
    def check_module(module_name: str, min_version: str = None) -> Tuple[bool, str]:
        """
        Prüfe ob Modul installiert ist

        Returns:
            (is_installed, version_string)
        """
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, '__version__', 'unknown')
            return (True, version)
        except ImportError:
            return (False, 'not installed')

    @staticmethod
    def check_all_required() -> Tuple[bool, List[str]]:
        """
        Prüfe alle erforderlichen Module

        Returns:
            (all_ok, missing_modules)
        """
        missing = []
        for module_name, min_version in DependencyChecker.REQUIRED_MODULES.items():
            installed, version = DependencyChecker.check_module(module_name)
            if not installed:
                missing.append(f"{module_name} (required >= {min_version})")

        return (len(missing) == 0, missing)

    @staticmethod
    def check_all_optional() -> Dict[str, Dict]:
        """
        Prüfe alle optionalen Module

        Returns:
            {module_name: {installed, version, purpose}}
        """
        results = {}
        for module_name, purpose in DependencyChecker.OPTIONAL_MODULES.items():
            installed, version = DependencyChecker.check_module(module_name)
            results[module_name] = {
                'installed': installed,
                'version': version,
                'purpose': purpose,
            }
        return results

    @staticmethod
    def get_install_command(module_name: str) -> str:
        """Gebe Installations-Befehl für Modul"""
        if module_name == 'm3uScan_v21_5':
            return f"# Stelle sicher dass {module_name}.py im gleichen Verzeichnis ist"
        return f"pip install {module_name}"

    @staticmethod
    def print_report():
        """Gebe Dependency-Report aus"""
        print("\n" + "=" * 60)
        print("m3uScan Kivy GUI - Dependency Check")
        print("=" * 60)

        # Erforderliche Module
        print("\n[REQUIRED MODULES]")
        all_ok, missing = DependencyChecker.check_all_required()
        for module_name, min_version in DependencyChecker.REQUIRED_MODULES.items():
            installed, version = DependencyChecker.check_module(module_name)
            status = "✅" if installed else "❌"
            print(f"{status} {module_name:15} {version:15} (>= {min_version})")

        if missing:
            print(f"\n❌ Missing: {', '.join(missing)}")
            print("\nInstall with:")
            for module in missing:
                module_name = module.split()[0]
                print(f"  {DependencyChecker.get_install_command(module_name)}")
        else:
            print("\n✅ All required modules installed!")

        # Optionale Module
        print("\n[OPTIONAL MODULES]")
        optional = DependencyChecker.check_all_optional()
        for module_name, info in optional.items():
            status = "✅" if info['installed'] else "⚠️"
            print(f"{status} {module_name:15} {info['version']:15} ({info['purpose']})")

        print("\n" + "=" * 60 + "\n")


class FirstRunWizard:
    """First-Run Setup Wizard"""

    @staticmethod
    def should_run() -> bool:
        """Prüfe ob First-Run Wizard ausgeführt werden sollte"""
        import os
        config_dir = os.path.expanduser('~/.m3uscan')
        first_run_marker = os.path.join(config_dir, '.first_run_done')
        return not os.path.exists(first_run_marker)

    @staticmethod
    def mark_complete():
        """Markiere First-Run als abgeschlossen"""
        import os
        config_dir = os.path.expanduser('~/.m3uscan')
        os.makedirs(config_dir, exist_ok=True)
        first_run_marker = os.path.join(config_dir, '.first_run_done')
        with open(first_run_marker, 'w') as f:
            f.write('# First-run setup completed\n')

    @staticmethod
    def run_cli_wizard():
        """Starte CLI-basierte Setup-Wizard"""
        print("\n" + "=" * 60)
        print("🚀 m3uScan v21.5 Kivy GUI - First-Run Setup")
        print("=" * 60)

        # Prüfe Dependencies
        print("\n1️⃣ Checking dependencies...")
        all_ok, missing = DependencyChecker.check_all_required()

        if not all_ok:
            print(f"\n❌ Missing required modules: {', '.join(missing)}")
            print("\nInstall with:")
            for module in missing:
                module_name = module.split()[0]
                print(f"  pip install {module_name}")
            sys.exit(1)

        print("✅ All dependencies satisfied!")

        # Zeige System Info
        print("\n2️⃣ Detecting platform and device...")
        try:
            from kivy_gui.utils.pydroid_detector import pydroid_detector
            info = pydroid_detector.get_system_info()
            print(f"  Platform: {info.get('platform')}")
            print(f"  Python:   {info.get('python_version')}")
            if info.get('is_android'):
                print(f"  Device:   {info.get('device_model')}")
                print(f"  API Level: {info.get('android_api_level')}")
                print(f"  RAM: {info.get('memory_info', {}).get('total_mb')} MB")
        except ImportError:
            print("  (Platform detection unavailable)")

        # Zeige Optimierungen
        print("\n3️⃣ Optimization Settings...")
        try:
            from kivy_gui.utils.pydroid_env import pydroid_env
            report = pydroid_env.get_optimization_report()
            print(f"  Workers:           {report.get('optimal_workers')}")
            print(f"  Batch Size:        {report.get('batch_size')} items")
            print(f"  Timeout Factor:    {report.get('timeout_multiplier')}x")
            print(f"  Cache Size:        {report.get('safe_cache_mb')} MB")
            print(f"  UI Refresh Rate:   {report.get('ui_refresh_rate')*1000:.0f} ms")
        except ImportError:
            print("  (Optimization unavailable)")

        # Konfiguriere Storage
        print("\n4️⃣ Creating directories...")
        try:
            from kivy_gui.storage.pydroid_storage import pydroid_storage
            pydroid_storage._ensure_directories()
            print("  ✅ Directories created")
        except Exception as e:
            print(f"  ⚠️ Directory creation: {e}")

        # Setze Marker
        FirstRunWizard.mark_complete()

        print("\n" + "=" * 60)
        print("✅ Setup complete! Starting GUI...")
        print("=" * 60 + "\n")

    @staticmethod
    def run():
        """Starte Setup-Wizard wenn nötig"""
        if FirstRunWizard.should_run():
            FirstRunWizard.run_cli_wizard()


# Hilfsfunktionen für externe Nutzung
def check_dependencies() -> bool:
    """Prüfe ob alle erforderlichen Abhängigkeiten installiert sind"""
    all_ok, _ = DependencyChecker.check_all_required()
    return all_ok


def print_dependency_report():
    """Gebe Dependency-Report aus"""
    DependencyChecker.print_report()


def run_first_time_setup():
    """Starte First-Run Setup"""
    FirstRunWizard.run()
