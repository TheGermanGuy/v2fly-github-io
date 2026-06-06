"""
m3uScan v21.5 GUI - Import/Export Panel
CSV und Textdatei-Operationen für Konten
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime


class ImportExportPanel(ttk.Frame):
    """Panel für Import/Export-Operationen"""

    def __init__(self, parent, on_update=None):
        super().__init__(parent)
        self.on_update = on_update
        self.ledger_data = {}
        self.contacts_data = {}
        self._create_widgets()

    def _create_widgets(self):
        """Erstelle UI-Elemente"""
        # Notebook für Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: CSV Import/Export
        csv_frame = ttk.Frame(self.notebook)
        self.notebook.add(csv_frame, text="CSV")
        self._create_csv_tab(csv_frame)

        # Tab 2: Textdatei-Operationen
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Textdateien")
        self._create_text_tab(text_frame)

        # Tab 3: Backup/Restore
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="Backup")
        self._create_backup_tab(backup_frame)

    def _create_csv_tab(self, parent):
        """CSV Import/Export Tab"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Export
        ttk.LabelFrame(frame, text="CSV EXPORT", padding=10).pack(fill=tk.X, pady=10)
        export_btn_frame = ttk.Frame(frame)
        export_btn_frame.pack(fill=tk.X)
        ttk.Button(export_btn_frame, text="Alle Konten exportieren", command=self._export_all_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_btn_frame, text="Mit Status exportieren", command=self._export_status_csv).pack(side=tk.LEFT, padx=5)

        self.export_info = ttk.Label(frame, text="", foreground="gray")
        self.export_info.pack(fill=tk.X, pady=5)

        # Import
        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.LabelFrame(frame, text="CSV IMPORT", padding=10).pack(fill=tk.X, pady=10)
        import_btn_frame = ttk.Frame(frame)
        import_btn_frame.pack(fill=tk.X)
        ttk.Button(import_btn_frame, text="CSV-Datei laden", command=self._import_csv).pack(side=tk.LEFT, padx=5)

        self.import_info = ttk.Label(frame, text="", foreground="gray")
        self.import_info.pack(fill=tk.X, pady=5)

        # Preview
        ttk.LabelFrame(frame, text="VORSCHAU", padding=10).pack(fill=tk.BOTH, expand=True, pady=10)
        self.csv_preview = tk.Text(frame, height=10)
        self.csv_preview.pack(fill=tk.BOTH, expand=True)

    def _create_text_tab(self, parent):
        """Textdatei-Operationen Tab"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Import Links aus Textdatei
        ttk.Label(frame, text="Links aus Text-Dateien einfügen", font=("Arial", 11, "bold")).pack(pady=5)
        text_area = tk.Text(frame, height=15)
        text_area.pack(fill=tk.BOTH, expand=True, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Aus Datei laden",
                  command=lambda: self._load_text_file(text_area)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Alle einlesen",
                  command=lambda: self._import_from_text(text_area)).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Löschen",
                  command=lambda: text_area.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=2)

        self.text_import_info = ttk.Label(frame, text="", foreground="gray")
        self.text_import_info.pack(fill=tk.X)

    def _create_backup_tab(self, parent):
        """Backup/Restore Tab"""
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Backup erstellen
        ttk.Label(frame, text="DATENSICHERUNG", font=("Arial", 11, "bold")).pack(pady=5)
        backup_btn_frame = ttk.Frame(frame)
        backup_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(backup_btn_frame, text="💾 Backup erstellen", command=self._create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(backup_btn_frame, text="📂 Backup-Ordner öffnen", command=self._open_backups).pack(side=tk.LEFT, padx=5)

        self.backup_info = ttk.Label(frame, text="", foreground="gray")
        self.backup_info.pack(fill=tk.X, pady=5)

        # Restore
        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, pady=10)
        ttk.Label(frame, text="WIEDERHERSTELLUNG", font=("Arial", 11, "bold")).pack(pady=5)
        restore_btn_frame = ttk.Frame(frame)
        restore_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(restore_btn_frame, text="📥 Aus Backup wiederherstellen", command=self._restore_backup).pack(side=tk.LEFT, padx=5)

        self.restore_info = ttk.Label(frame, text="", foreground="gray")
        self.restore_info.pack(fill=tk.X, pady=5)

        # Backup-Liste
        ttk.LabelFrame(frame, text="Verfügbare Backups", padding=10).pack(fill=tk.BOTH, expand=True, pady=10)
        self.backup_list = tk.Listbox(frame)
        self.backup_list.pack(fill=tk.BOTH, expand=True)
        self._refresh_backup_list()

    def refresh(self, ledger_data: dict, contacts_data: dict):
        """Aktualisiere mit neuen Daten"""
        self.ledger_data = ledger_data
        self.contacts_data = contacts_data

    def _export_all_csv(self):
        """Exportiere alle Konten als CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if not filename:
                return

            lines = ["Link;Person;Gerät;Notizen;Status"]
            for key, data in self.ledger_data.items():
                assignments = data.get("assignments", []) if isinstance(data, dict) else data
                for a in assignments:
                    if isinstance(a, dict):
                        person = a.get("person", "")
                        device = a.get("device", "")
                        notes = a.get("notes", "").replace(";", ",")
                        status = a.get("status", "active")
                        lines.append(f"{key};{person};{device};{notes};{status}")

            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.export_info.config(text=f"✓ Exportiert: {filename}", foreground="green")
            messagebox.showinfo("Erfolg", f"{len(lines)-1} Einträge exportiert")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export-Fehler: {e}")

    def _export_status_csv(self):
        """Exportiere mit Status und Details"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if not filename:
                return

            lines = ["Link;Person;Gerät;Status;ZugewiesenAm;Notizen"]
            count = 0
            for key, data in self.ledger_data.items():
                assignments = data.get("assignments", []) if isinstance(data, dict) else data
                for a in assignments:
                    if isinstance(a, dict):
                        person = a.get("person", "")
                        device = a.get("device", "")
                        status = a.get("status", "active")
                        date = a.get("date", "")[:10]
                        notes = a.get("notes", "").replace(";", ",")
                        lines.append(f"{key};{person};{device};{status};{date};{notes}")
                        count += 1

            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            self.export_info.config(text=f"✓ {count} Einträge exportiert", foreground="green")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export-Fehler: {e}")

    def _import_csv(self):
        """Importiere CSV-Datei"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            if not filename:
                return

            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                self.csv_preview.delete("1.0", tk.END)
                self.csv_preview.insert("1.0", content[:1000])

                lines = content.strip().split("\n")[1:]  # Skip header
                count = 0
                for line in lines:
                    parts = line.split(";")
                    if len(parts) >= 2:
                        key = parts[0]
                        person = parts[1]
                        if key not in self.ledger_data:
                            self.ledger_data[key] = {"assignments": [], "metadata": {}}
                        self.ledger_data[key]["assignments"].append({
                            "person": person,
                            "device": parts[2] if len(parts) > 2 else "imported",
                            "notes": parts[3] if len(parts) > 3 else "",
                            "status": parts[4] if len(parts) > 4 else "active",
                            "date": datetime.now().isoformat()
                        })
                        count += 1

                self.import_info.config(text=f"✓ {count} Einträge importiert", foreground="green")
                if self.on_update:
                    self.on_update()
        except Exception as e:
            messagebox.showerror("Fehler", f"Import-Fehler: {e}")

    def _load_text_file(self, text_widget):
        """Lade Text-Datei in Text-Widget"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if filename:
                with open(filename, "r", encoding="utf-8") as f:
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", f.read())
                self.text_import_info.config(text=f"Geladen: {filename}", foreground="green")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden: {e}")

    def _import_from_text(self, text_widget):
        """Importiere Links aus Text-Widget"""
        text = text_widget.get("1.0", tk.END)
        lines = text.strip().split("\n")
        count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if "://" in line and ("username" in line or "password" in line):
                # Versuche user:pass zu extrahieren
                try:
                    from urllib.parse import urlparse, parse_qs
                    qs = parse_qs(line.split("?")[1] if "?" in line else "")
                    user = qs.get("username", ["unknown"])[0]
                    pwd = qs.get("password", ["unknown"])[0]
                    key = f"{user}:{pwd}"
                    if key not in self.ledger_data:
                        self.ledger_data[key] = {"assignments": [], "metadata": {}}
                        self.ledger_data[key]["assignments"].append({
                            "person": "imported",
                            "device": "text",
                            "status": "active",
                            "date": datetime.now().isoformat(),
                            "notes": ""
                        })
                        count += 1
                except:
                    pass

        self.text_import_info.config(text=f"✓ {count} Links importiert", foreground="green")
        if self.on_update:
            self.on_update()

    def _create_backup(self):
        """Erstelle Backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)

            backup_file = os.path.join(backup_dir, f"link_ledger_backup_{timestamp}.json")
            data = {
                "version": "2.0",
                "ledger": self.ledger_data,
                "contacts": self.contacts_data
            }
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.backup_info.config(text=f"✓ Backup erstellt: {backup_file}", foreground="green")
            self._refresh_backup_list()
        except Exception as e:
            messagebox.showerror("Fehler", f"Backup-Fehler: {e}")

    def _restore_backup(self):
        """Stelle aus Backup wieder her"""
        try:
            selection = self.backup_list.curselection()
            if not selection:
                messagebox.showwarning("Warnung", "Wähle ein Backup")
                return

            backup_file = self.backup_list.get(selection[0])
            if messagebox.askyesno("Bestätigung", f"Wiederherstellen aus '{backup_file}'?"):
                with open(os.path.join("backups", backup_file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.ledger_data = data.get("ledger", {})
                    self.contacts_data = data.get("contacts", {})

                self.restore_info.config(text=f"✓ Wiederhergestellt aus {backup_file}", foreground="green")
                if self.on_update:
                    self.on_update()
        except Exception as e:
            messagebox.showerror("Fehler", f"Restore-Fehler: {e}")

    def _open_backups(self):
        """Öffne Backup-Ordner"""
        try:
            os.startfile("backups") if os.name == "nt" else os.system("open backups")
        except:
            messagebox.showinfo("Info", "Backup-Ordner: ./backups")

    def _refresh_backup_list(self):
        """Aktualisiere Backup-Liste"""
        self.backup_list.delete(0, tk.END)
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            for f in sorted(os.listdir(backup_dir), reverse=True):
                if f.startswith("link_ledger_backup_") and f.endswith(".json"):
                    self.backup_list.insert(tk.END, f)
