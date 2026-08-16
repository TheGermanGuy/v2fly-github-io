"""
m3uScan v21.5 GUI - Account Manager Panel
Verwaltung von Xtream-Konto-Links mit Visual Status
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from urllib.parse import urlparse, parse_qs
import json


class AccountManager(ttk.Frame):
    """Panel zur Konten-Verwaltung"""

    def __init__(self, parent, on_update=None):
        super().__init__(parent)
        self.on_update = on_update
        self.accounts = {}
        self._create_widgets()

    def _create_widgets(self):
        """Erstelle UI-Elemente"""
        # Toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="➕ Hinzufügen", command=self._add_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ Löschen", command=self._delete_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ Bearbeiten", command=self._edit_account).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 Aktualisieren", command=self._refresh_status).pack(side=tk.LEFT, padx=2)

        # Suchfeld
        ttk.Label(toolbar, text="Suche:").pack(side=tk.LEFT, padx=(20, 2))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_accounts())
        ttk.Entry(toolbar, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=2)

        # Treeview für Konto-Liste
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Host", "Status", "Ablauf", "Verbindungen", "Personen"),
            height=20,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Konfiguriere Spalten
        self.tree.column("#0", width=200, heading="Link (user:pass)")
        self.tree.column("Host", width=150, heading="Host")
        self.tree.column("Status", width=80, heading="Status")
        self.tree.column("Ablauf", width=100, heading="Ablauf")
        self.tree.column("Verbindungen", width=100, heading="Aktiv/Max")
        self.tree.column("Personen", width=100, heading="Personen")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Info-Frame unten
        info_frame = ttk.LabelFrame(self, text="Info", padding=5)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        self.info_label = ttk.Label(info_frame, text="Wähle ein Konto", foreground="gray")
        self.info_label.pack()

        # Bind Events
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._edit_account())

    def refresh(self, ledger_data: dict):
        """Lade Daten aus Ledger"""
        self.accounts = ledger_data
        self._refresh_tree()

    def _refresh_tree(self):
        """Aktualisiere Treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for key, data in self.accounts.items():
            assignments = data.get("assignments", []) if isinstance(data, dict) else data
            if not assignments:
                continue

            # Erstelle Parent-Item für diesen Link
            persons_count = len(set(a.get("person") if isinstance(a, dict) else "" for a in assignments))
            parent = self.tree.insert("", "end", text=key[:40])

            # Extrahiere Host aus beliebigem Assignment
            host = "Unbekannt"
            status = "?"
            expiry = "?"
            connections = "?"

            for a in assignments:
                if isinstance(a, dict) and "url" in a:
                    try:
                        host = urlparse(a["url"]).netloc
                        status = a.get("status", "active")
                        break
                    except:
                        pass

            self.tree.set(parent, "Host", host)
            self.tree.set(parent, "Status", status)
            self.tree.set(parent, "Ablauf", "-")
            self.tree.set(parent, "Verbindungen", "-")
            self.tree.set(parent, "Personen", str(persons_count))

            # Kinder-Items für Personen
            for a in assignments:
                if isinstance(a, dict):
                    person = a.get("person", "?")
                    device = a.get("device", "-")
                    date = a.get("date", "?")[:10]
                    child_text = f"{person} ({device}) - {date}"
                    self.tree.insert(parent, "end", text=child_text)

    def _filter_accounts(self):
        """Filtere Konten nach Suchtext"""
        search_text = self.search_var.get().lower()
        for item in self.tree.get_children():
            text = self.tree.item(item, "text").lower()
            if search_text in text:
                self.tree.item(item, tags=())
            else:
                self.tree.item(item, tags=("hidden",))

    def _add_account(self):
        """Dialog: Neues Konto hinzufügen"""
        dialog = AddAccountDialog(self)
        if dialog.result:
            key = dialog.result.get("key")
            self.accounts[key] = {
                "assignments": [dialog.result.get("assignment")],
                "metadata": {"quality_score": None, "tags": []}
            }
            self._refresh_tree()
            if self.on_update:
                self.on_update(key, dialog.result.get("person"), "add")

    def _delete_account(self):
        """Lösche ausgewähltes Konto"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Wähle ein Konto")
            return

        selected = selection[0]
        key = self.tree.item(selected, "text")

        if messagebox.askyesno("Bestätigung", f"Konto '{key}' wirklich löschen?"):
            if key in self.accounts:
                del self.accounts[key]
                self._refresh_tree()
                if self.on_update:
                    self.on_update(key, "unknown", "delete")

    def _edit_account(self):
        """Bearbeite ausgewähltes Konto"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Wähle ein Konto")
            return

        selected = selection[0]
        key = self.tree.item(selected, "text")

        if key in self.accounts:
            data = self.accounts[key]
            assignments = data.get("assignments", [])
            if assignments and isinstance(assignments[0], dict):
                person = assignments[0].get("person", "")
                device = assignments[0].get("device", "")
                notes = assignments[0].get("notes", "")

                new_person = simpledialog.askstring("Bearbeiten", "Person:", initialvalue=person)
                if new_person:
                    assignments[0]["person"] = new_person
                    assignments[0]["device"] = simpledialog.askstring("Bearbeiten", "Gerät:", initialvalue=device) or device
                    assignments[0]["notes"] = simpledialog.askstring("Bearbeiten", "Notizen:", initialvalue=notes) or notes
                    self._refresh_tree()

    def _refresh_status(self):
        """Aktualisiere Status aller Konten"""
        messagebox.showinfo("Info", "Status-Check wird implementiert in Status-Monitor Tab")

    def _on_select(self, event):
        """Handler für Konten-Auswahl"""
        selection = self.tree.selection()
        if selection:
            key = self.tree.item(selection[0], "text")
            if key in self.accounts:
                data = self.accounts[key]
                self.info_label.config(text=f"Konto: {key}", foreground="black")


class AddAccountDialog(tk.Toplevel):
    """Dialog zum Hinzufügen eines neuen Kontos"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Konto hinzufügen")
        self.geometry("400x300")
        self.result = None
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self.wait_window()

    def _create_widgets(self):
        """Erstelle Dialog-Elemente"""
        frame = ttk.Frame(self, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Link/URL
        ttk.Label(frame, text="Xtream Link (user:pass):").grid(row=0, column=0, sticky="w", pady=5)
        self.link_entry = ttk.Entry(frame, width=40)
        self.link_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # Person
        ttk.Label(frame, text="Person / Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.person_entry = ttk.Entry(frame, width=40)
        self.person_entry.grid(row=1, column=1, sticky="ew", padx=5)

        # Gerät
        ttk.Label(frame, text="Gerät (z.B. TV1):").grid(row=2, column=0, sticky="w", pady=5)
        self.device_entry = ttk.Entry(frame, width=40)
        self.device_entry.grid(row=2, column=1, sticky="ew", padx=5)

        # Notizen
        ttk.Label(frame, text="Notizen:").grid(row=3, column=0, sticky="nw", pady=5)
        self.notes_text = tk.Text(frame, height=4, width=40)
        self.notes_text.grid(row=3, column=1, sticky="ew", padx=5)

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Hinzufügen", command=self._add).pack(side=tk.RIGHT, padx=2)
        ttk.Button(button_frame, text="Abbrechen", command=self.destroy).pack(side=tk.RIGHT, padx=2)

        frame.columnconfigure(1, weight=1)

    def _add(self):
        """Speichere Konto"""
        link = self.link_entry.get().strip()
        person = self.person_entry.get().strip()
        device = self.device_entry.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        if not link or not person:
            messagebox.showwarning("Warnung", "Link und Person erforderlich")
            return

        # Extrahiere user:pass aus Link
        key = link.split("?")[0] if "?" in link else link
        try:
            qs = parse_qs(link.split("?")[1] if "?" in link else "")
            username = qs.get("username", ["unknown"])[0]
            password = qs.get("password", ["unknown"])[0]
            key = f"{username}:{password}"
        except:
            key = link[:30]

        self.result = {
            "key": key,
            "person": person,
            "assignment": {
                "person": person,
                "device": device or "unbekannt",
                "notes": notes,
                "status": "active",
                "url": link,
                "date": __import__("datetime").datetime.now().isoformat()
            }
        }
        self.destroy()
