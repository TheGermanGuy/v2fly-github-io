"""
m3uScan v21.5 GUI - Status Monitor Panel
Live-Überwachung aller Link-Status mit Farbcodierung
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from .styles import COLORS


class StatusMonitor(ttk.Frame):
    """Panel zur Status-Überwachung"""

    def __init__(self, parent, on_update=None):
        super().__init__(parent)
        self.on_update = on_update
        self.ledger_data = {}
        self.monitoring = False
        self.check_thread = None
        self._create_widgets()

    def _create_widgets(self):
        """Erstelle UI-Elemente"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        self.monitor_btn = ttk.Button(toolbar, text="▶️ Überwachung starten", command=self._toggle_monitoring)
        self.monitor_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(toolbar, text="🔄 Jetzt prüfen", command=self._check_now).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📊 Statistiken", command=self._show_stats).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="💾 Exportieren", command=self._export_status).pack(side=tk.LEFT, padx=2)

        # Statusanzeige
        self.status_label = ttk.Label(toolbar, text="Bereit", foreground="blue")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Haupt-Frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Links: Status-Baumview
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(left_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        self.tree = ttk.Treeview(
            left_frame,
            columns=("Status", "Ablauf", "Max", "Aktiv"),
            height=20,
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=self.tree.yview)

        self.tree.column("#0", width=250, heading="Konto")
        self.tree.column("Status", width=80, heading="Status")
        self.tree.column("Ablauf", width=100, heading="Ablauf")
        self.tree.column("Max", width=50, heading="Max")
        self.tree.column("Aktiv", width=50, heading="Aktiv")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Rechts: Details
        right_frame = ttk.LabelFrame(main_frame, text="Details", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))

        self.details_text = tk.Text(right_frame, width=35, height=25, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # Warn-Panel unten
        self.warning_frame = ttk.LabelFrame(self, text="⚠️ Warnungen", padding=5)
        self.warning_frame.pack(fill=tk.X, padx=5, pady=5)
        self.warning_text = tk.Text(self.warning_frame, height=4, wrap=tk.WORD)
        self.warning_text.pack(fill=tk.BOTH, expand=True)

        # Bind Events
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def refresh(self, ledger_data: dict):
        """Lade Daten"""
        self.ledger_data = ledger_data
        self._refresh_tree()

    def _refresh_tree(self):
        """Aktualisiere Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        warnings = []

        for key, data in self.ledger_data.items():
            assignments = data.get("assignments", []) if isinstance(data, dict) else data
            if not assignments:
                continue

            status = "❓"
            exp = "?"
            max_con = 0
            active_con = 0

            parent = self.tree.insert("", "end", text=key[:40])

            # Kinder: Personen
            for a in assignments:
                if isinstance(a, dict):
                    person = a.get("person", "?")
                    device = a.get("device", "-")
                    child_text = f"{person} ({device})"

                    # Status-Icons
                    acc_status = a.get("status", "active")
                    if acc_status == "active":
                        icon = "🟢"
                    else:
                        icon = "🔴"

                    child = self.tree.insert(parent, "end", text=f"{icon} {child_text}")

                    if a.get("days_left"):
                        days = a.get("days_left")
                        if days < 0:
                            status = "🔴"
                            warnings.append(f"[ABGELAUFEN] {person} - {key}")
                        elif days < 3:
                            status = "🔴"
                            warnings.append(f"[KRITISCH] {person} - {days} Tage")
                        elif days < 7:
                            status = "🟡"
                            warnings.append(f"[WARNUNG] {person} - {days} Tage")

            self.tree.set(parent, "Status", status)
            self.tree.set(parent, "Ablauf", exp)
            self.tree.set(parent, "Max", str(max_con))
            self.tree.set(parent, "Aktiv", str(active_con))

        # Update Warnungen
        self.warning_text.delete("1.0", tk.END)
        if warnings:
            for warn in warnings[:10]:  # Max 10 Warnungen
                self.warning_text.insert(tk.END, f"{warn}\n")
        else:
            self.warning_text.insert(tk.END, "✓ Keine Warnungen")

    def _on_select(self, event):
        """Handler für Auswahl"""
        selection = self.tree.selection()
        if selection:
            key = self.tree.item(selection[0], "text")
            if key in self.ledger_data:
                data = self.ledger_data[key]
                self.details_text.delete("1.0", tk.END)
                info = f"Konto: {key}\n\n"
                assignments = data.get("assignments", [])
                for a in assignments:
                    if isinstance(a, dict):
                        info += f"Person: {a.get('person')}\n"
                        info += f"Gerät: {a.get('device')}\n"
                        info += f"Status: {a.get('status')}\n"
                        info += f"Zugewiesen: {a.get('date', '?')[:10]}\n"
                        info += f"Notizen: {a.get('notes', '-')}\n\n"
                self.details_text.insert(tk.END, info)

    def _toggle_monitoring(self):
        """Starte/Stoppe Überwachung"""
        if self.monitoring:
            self.monitoring = False
            self.monitor_btn.config(text="▶️ Überwachung starten")
            self.status_label.config(text="Gestoppt", foreground="red")
        else:
            self.monitoring = True
            self.monitor_btn.config(text="⏸️ Überwachung stoppen")
            self.status_label.config(text="Läuft...", foreground="green")
            self.check_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.check_thread.start()

    def _monitoring_loop(self):
        """Hintergrund-Monitoring-Loop"""
        while self.monitoring:
            try:
                import time
                time.sleep(60)  # 60 Sekunden
                if self.monitoring:
                    self.after(0, self._check_now)
            except:
                break

    def _check_now(self):
        """Prüfe alle Status jetzt"""
        self.status_label.config(text=f"Prüfe... ({datetime.now().strftime('%H:%M:%S')})")
        # Hier würde LinkStatusChecker aufgerufen
        self._refresh_tree()
        self.status_label.config(text="✓ Aktualisiert", foreground="green")

    def check_all(self):
        """Öffentliche Methode zum Prüfen aller Links"""
        self._check_now()

    def _show_stats(self):
        """Zeige Statistiken"""
        total = len(self.ledger_data)
        active = sum(1 for v in self.ledger_data.values() if v)
        warn = sum(1 for v in self.ledger_data.values()
                  if any(a.get("days_left", 999) < 7 for a in (v.get("assignments", []))))

        stats = f"""
STATISTIKEN

Gesamt Konten: {total}
Aktive Konten: {active}
Warnungen: {warn}
"""
        messagebox.showinfo("Statistiken", stats)

    def _export_status(self):
        """Exportiere Status als Datei"""
        try:
            filename = "status_report.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Status Report - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(self.warning_text.get("1.0", tk.END))

            messagebox.showinfo("Erfolg", f"Exportiert zu {filename}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Exportfehler: {e}")
