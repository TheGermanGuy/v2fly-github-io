"""
m3uScan v21.5 GUI - Hauptfenster
Tkinter-basierte grafische Oberfläche
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
from .account_manager import AccountManager
from .status_monitor import StatusMonitor
from .import_export import ImportExportPanel
from .styles import setup_styles, COLORS


class MainWindow(tk.Tk):
    """Hauptfenster der m3uScan GUI"""

    def __init__(self, ledger_file: str = "link_ledger.json"):
        super().__init__()
        self.title("m3uScan v21.5 - Link Management GUI")
        self.geometry("1200x700")
        self.minsize(900, 500)
        self.ledger_file = ledger_file

        # Setup UI
        setup_styles()
        self._create_menu_bar()
        self._create_main_layout()
        self._create_status_bar()
        self._load_ledger_data()

        # Event-Handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu_bar(self):
        """Erstelle Menü-Leiste"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Ledger neu laden", command=self._load_ledger_data)
        file_menu.add_command(label="Ledger speichern", command=self._save_ledger_data)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self._on_closing)

        # View Menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ansicht", menu=view_menu)
        view_menu.add_command(label="Konten-Manager", command=self._show_accounts_tab)
        view_menu.add_command(label="Status-Überwachung", command=self._show_status_tab)
        view_menu.add_command(label="Import/Export", command=self._show_import_export_tab)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Werkzeuge", menu=tools_menu)
        tools_menu.add_command(label="Alle Status prüfen", command=self._check_all_status)
        tools_menu.add_separator()
        tools_menu.add_command(label="Ledger bereinigen", command=self._cleanup_ledger)
        tools_menu.add_command(label="Backup erstellen", command=self._backup_ledger)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über", command=self._show_about)
        help_menu.add_command(label="Dokumentation", command=self._show_docs)

    def _create_main_layout(self):
        """Erstelle 3-Panel Layout: Links (Tabs) | Details | Log"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Notebook (Tabs) für verschiedene Views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tab 1: Account Manager
        self.account_manager = AccountManager(self.notebook, on_update=self._on_account_update)
        self.notebook.add(self.account_manager, text="Konten-Manager")

        # Tab 2: Status Monitor
        self.status_monitor = StatusMonitor(self.notebook, on_update=self._on_status_update)
        self.notebook.add(self.status_monitor, text="Status-Überwachung")

        # Tab 3: Import/Export
        self.import_export = ImportExportPanel(self.notebook, on_update=self._on_ledger_update)
        self.notebook.add(self.import_export, text="Import/Export")

        # Details Panel (rechts)
        details_frame = ttk.LabelFrame(main_frame, text="Details", padding=10)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))

        self.details_text = tk.Text(details_frame, width=30, height=40, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=details_scroll.set)

    def _create_status_bar(self):
        """Erstelle Status-Leiste unten"""
        self.status_bar = ttk.Label(self, text="Bereit", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_ledger_data(self):
        """Lade LinkLedger JSON und aktualisiere alle Panels"""
        try:
            if os.path.exists(self.ledger_file):
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ledger_data = data.get("ledger", {})
                    self.contacts_data = data.get("contacts", {})
            else:
                self.ledger_data = {}
                self.contacts_data = {}

            self._update_all_panels()
            self._update_status_bar(f"Ledger geladen: {len(self.ledger_data)} Konten, {len(self.contacts_data)} Kontakte")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden des Ledgers: {e}")
            self._update_status_bar(f"Fehler: {e}")

    def _save_ledger_data(self):
        """Speichere Ledger JSON"""
        try:
            export = {
                "version": "2.0",
                "ledger": self.ledger_data,
                "contacts": self.contacts_data
            }
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump(export, f, indent=2, ensure_ascii=False)
            self._update_status_bar("Ledger gespeichert")
            messagebox.showinfo("Erfolg", "Ledger gespeichert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")

    def _update_all_panels(self):
        """Aktualisiere alle Panels mit aktuellen Daten"""
        if hasattr(self, 'account_manager'):
            self.account_manager.refresh(self.ledger_data)
        if hasattr(self, 'status_monitor'):
            self.status_monitor.refresh(self.ledger_data)
        if hasattr(self, 'import_export'):
            self.import_export.refresh(self.ledger_data, self.contacts_data)

    def _on_account_update(self, key: str, person: str, action: str):
        """Handler für Konten-Updates"""
        if action == "add":
            self._update_status_bar(f"Konto hinzugefügt: {person}")
        elif action == "delete":
            self._update_status_bar(f"Konto gelöscht: {person}")
        self._load_ledger_data()

    def _on_status_update(self, status_info: dict):
        """Handler für Status-Updates"""
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, json.dumps(status_info, indent=2, ensure_ascii=False))
        self._update_status_bar(f"Status aktualisiert: {status_info.get('status', 'Unbekannt')}")

    def _on_ledger_update(self):
        """Handler für Ledger-Änderungen (Import/Export)"""
        self._load_ledger_data()
        self._update_status_bar("Ledger aktualisiert")

    def _check_all_status(self):
        """Prüfe alle Konten-Status"""
        self.status_monitor.check_all()

    def _cleanup_ledger(self):
        """Bereinige Ledger (entferne leere Einträge)"""
        initial_count = len(self.ledger_data)
        cleaned = {k: v for k, v in self.ledger_data.items() if v}
        self.ledger_data = cleaned
        self._save_ledger_data()
        messagebox.showinfo("Bereinigt", f"Bereinigt: {initial_count} → {len(cleaned)} Einträge")

    def _backup_ledger(self):
        """Erstelle Backup des Ledgers"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"link_ledger_backup_{timestamp}.json"
        try:
            import shutil
            shutil.copy(self.ledger_file, backup_file)
            messagebox.showinfo("Erfolg", f"Backup erstellt: {backup_file}")
            self._update_status_bar(f"Backup: {backup_file}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup-Fehler: {e}")

    def _show_about(self):
        """Zeige About-Dialog"""
        messagebox.showinfo("Über",
            "m3uScan v21.5 GUI Edition\n"
            "Link-Management für Xtream Codes\n\n"
            "© TheGermanGuy™ 2026\n"
            "Tkinter-basierte GUI")

    def _show_docs(self):
        """Zeige Dokumentation"""
        docs = """
DOKUMENTATION - m3uScan v21.5 GUI

KONTEN-MANAGER:
- Hinzufügen: Neue Konten mit Links und Zuweisungen
- Status: Live-Status aller Konten
- Löschen: Konten aus dem System entfernen

STATUS-ÜBERWACHUNG:
- Live-Überwachung aller Link-Status
- Auto-Refresh alle 60 Sekunden
- Farbcodierung: Grün=OK, Rot=Fehler, Orange=Warnung

IMPORT/EXPORT:
- CSV-Import/Export für Kontenverwaltung
- Datei-Import für Massen-Operationen
- Backup und Wiederherstellung

WERKZEUGE:
- Alle Links prüfen: Batch-Status-Check
- Ledger bereinigen: Entferne leere/ungültige Einträge
- Backup: Erstelle Sicherung
        """
        messagebox.showinfo("Dokumentation", docs)

    def _show_accounts_tab(self):
        """Zeige Konten-Manager Tab"""
        self.notebook.select(0)

    def _show_status_tab(self):
        """Zeige Status-Monitor Tab"""
        self.notebook.select(1)

    def _show_import_export_tab(self):
        """Zeige Import/Export Tab"""
        self.notebook.select(2)

    def _update_status_bar(self, message: str):
        """Aktualisiere Status-Leiste"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")

    def _on_closing(self):
        """Handler für Fenster-Schließung"""
        if messagebox.askokcancel("Beenden", "Wirklich beenden?"):
            self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
