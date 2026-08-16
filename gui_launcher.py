#!/usr/bin/env python3
"""
m3uScan v21.5 - GUI Launcher
Starte die grafische Oberfläche für Link-Management
"""

import sys
import os

def main():
    """Starte GUI-Anwendung"""
    try:
        # Versuche Tkinter zu importieren
        import tkinter as tk
        print("[INFO] Tkinter gefunden. Starte GUI...")
    except ImportError:
        print("[ERROR] Tkinter nicht installiert!")
        print("Installation:")
        print("  Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  macOS: brew install python-tk")
        print("  Windows: Tkinter sollte mit Python dabei sein")
        sys.exit(1)

    # Importiere und starte GUI
    try:
        from gui_module import MainWindow
        print("[INFO] Starte m3uScan v21.5 GUI Edition...")
        app = MainWindow(ledger_file="link_ledger.json")
        app.mainloop()
    except ImportError as e:
        print(f"[ERROR] Fehler beim Laden der GUI-Module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Fehler beim Starten der GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
