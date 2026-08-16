#!/usr/bin/env python3
"""
m3uScan v21.5 - Kivy GUI Launcher
Läuft auf Android (QPython 3) + Desktop (Windows, macOS, Linux)
"""

import sys
import os


def main():
    """Starte Kivy GUI"""
    print("=" * 60)
    print("m3uScan v21.5 - Kivy GUI Edition")
    print("Cross-platform für Android + Desktop")
    print("=" * 60)

    # Platform Detection
    print("\n[INFO] Platform Detection...")
    from kivy_gui.utils import platform

    print(f"[INFO] Erkannt: {platform.get_platform()}")
    print(f"[INFO] Is Mobile: {platform.is_mobile()}")
    print(f"[INFO] Is QPython: {platform.is_qpython()}")

    # Check Dependencies
    print("\n[INFO] Checking Dependencies...")
    dependencies = ["kivy", "aiohttp", "tqdm"]
    missing = []

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - NOT FOUND")
            missing.append(dep)

    if missing:
        print(f"\n[ERROR] Fehlende Abhängigkeiten: {', '.join(missing)}")
        print(f"Installation:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)

    print("\n✓ Alle Abhängigkeiten gefunden!")

    # Start App
    print("\n[INFO] Starte m3uScan Kivy GUI...")
    print("=" * 60)

    try:
        from kivy_gui.main import M3uScanApp

        app = M3uScanApp()
        app.run()
    except Exception as e:
        print(f"\n[ERROR] GUI Startup fehlgeschlagen:")
        print(f"  {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
