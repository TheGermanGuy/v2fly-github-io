"""
LinkLedger Adapter - Wrapper um m3uScan LinkLedger
Kivy-freundliche Schnittstelle zu m3uScan Daten
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
import asyncio

# Import m3uScan Klassen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from m3uScan_v21_5 import LinkLedger, LinkStatusChecker
except ImportError as e:
    print(f"[ERROR] m3uScan_v21_5 nicht gefunden: {e}")
    LinkLedger = None
    LinkStatusChecker = None


class LinkLedgerAdapter:
    """
    Adapter zwischen Kivy UI und m3uScan LinkLedger
    Vereinfacht Datenzugriff und Manipulation
    """

    def __init__(self, ledger_file: str = None):
        """
        Initialisiere Adapter

        Args:
            ledger_file: Pfad zur link_ledger.json (optional)
        """
        if LinkLedger is None:
            raise RuntimeError("LinkLedger Klasse nicht verfügbar")

        self.ledger = LinkLedger()
        self.checker = LinkStatusChecker(cache_ttl=3600)

    # ========== ACCOUNT MANAGEMENT ==========

    def get_all_accounts(self) -> List[Dict]:
        """
        Gebe alle Accounts als UI-freundliche Liste

        Returns:
            Liste von Account-Dicts mit Metadaten
        """
        accounts = []

        for key, data in self.ledger.data.items():
            assignments = data.get("assignments", []) if isinstance(data, dict) else data
            metadata = data.get("metadata", {}) if isinstance(data, dict) else {}

            if not assignments:
                continue

            # Parse user:pass von key
            parts = key.split(":")
            username = parts[0] if len(parts) > 0 else "unknown"
            password = parts[1] if len(parts) > 1 else "unknown"

            accounts.append(
                {
                    "key": key,
                    "username": username,
                    "password": password,
                    "assignment_count": len(set(a.get("person") for a in assignments if isinstance(a, dict))),
                    "last_check": metadata.get("last_status_check"),
                    "quality_score": metadata.get("quality_score"),
                    "tags": metadata.get("tags", []),
                    "assignments": assignments,
                }
            )

        return sorted(accounts, key=lambda x: x["key"])

    def get_account(self, key: str) -> Optional[Dict]:
        """
        Gebe einzelnes Account-Detail
        """
        for account in self.get_all_accounts():
            if account["key"] == key:
                return account
        return None

    def add_assignment(self, key: str, person: str, device: str = None, notes: str = None) -> bool:
        """
        Füge Zuordnung hinzu
        """
        try:
            # Rekonstruiere URL aus key
            parts = key.split(":")
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                url = f"http://dummy:8080/get.php?username={username}&password={password}"
                return self.ledger.assign(url, person, device=device, notes=notes)
        except Exception as e:
            print(f"[ERROR] add_assignment failed: {e}")
        return False

    def remove_assignment(self, key: str, person: str) -> bool:
        """
        Entferne Zuordnung
        """
        try:
            parts = key.split(":")
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                url = f"http://dummy:8080/get.php?username={username}&password={password}"
                return self.ledger.unassign(url, person)
        except Exception as e:
            print(f"[ERROR] remove_assignment failed: {e}")
        return False

    def get_assignments(self, key: str) -> List[Dict]:
        """
        Gebe alle Zuordnungen für einen Account
        """
        account = self.get_account(key)
        if account:
            return account.get("assignments", [])
        return []

    # ========== STATUS CHECKING ==========

    def check_account_sync(self, key: str) -> Dict:
        """
        Synchrone Status-Prüfung (blockierend, aber einfach)
        """
        try:
            parts = key.split(":")
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                url = f"http://dummy:8080/get.php?username={username}&password={password}"
                return self.checker.check_url_sync(url)
        except Exception as e:
            print(f"[ERROR] check_account_sync failed: {e}")

        return {
            "error": "Status Check fehlgeschlagen",
            "url": key,
        }

    async def check_account_async(self, key: str) -> Dict:
        """
        Asynchrone Status-Prüfung (non-blocking)
        """
        try:
            parts = key.split(":")
            if len(parts) >= 2:
                username, password = parts[0], parts[1]
                url = f"http://dummy:8080/get.php?username={username}&password={password}"
                result = await self.checker.check_url_async(url)
                return result
        except Exception as e:
            print(f"[ERROR] check_account_async failed: {e}")

        return {
            "error": "Status Check fehlgeschlagen",
            "url": key,
        }

    async def check_all_async(self, on_progress=None) -> Dict[str, Dict]:
        """
        Batch-Check aller Accounts mit Progress Callback

        Args:
            on_progress: Callback(current, total) für Progress Updates

        Returns:
            Dict mit {key: status_result} pairs
        """
        accounts = self.get_all_accounts()
        results = {}

        for idx, account in enumerate(accounts):
            if on_progress:
                on_progress(idx, len(accounts))

            status = await self.check_account_async(account["key"])
            results[account["key"]] = status

        if on_progress:
            on_progress(len(accounts), len(accounts))

        return results

    # ========== CONTACT MANAGEMENT ==========

    def get_contacts(self) -> Dict[str, Dict]:
        """
        Gebe alle Kontakte
        """
        return self.ledger.contacts

    def add_contact(self, name: str, phone: str = "", email: str = "", notes: str = "") -> bool:
        """
        Füge Kontakt hinzu
        """
        try:
            return self.ledger.add_contact(name, phone, email, notes)
        except Exception as e:
            print(f"[ERROR] add_contact failed: {e}")
            return False

    def get_contact(self, name: str) -> Optional[Dict]:
        """
        Gebe Kontakt-Details
        """
        return self.ledger.get_contact(name)

    def suggest_contacts(self, partial: str) -> List[str]:
        """
        Auto-Complete für Kontaktnamen
        """
        return self.ledger.suggest_contact(partial)

    # ========== IMPORT/EXPORT ==========

    def export_csv(self) -> str:
        """
        Exportiere als CSV-String
        """
        try:
            return self.ledger.export_to_csv()
        except Exception as e:
            print(f"[ERROR] export_csv failed: {e}")
            return ""

    def import_csv(self, csv_content: str) -> int:
        """
        Importiere aus CSV

        Returns:
            Anzahl importierter Einträge
        """
        try:
            return self.ledger.import_from_csv(csv_content)
        except Exception as e:
            print(f"[ERROR] import_csv failed: {e}")
            return 0

    def export_json(self) -> str:
        """
        Exportiere als JSON-String
        """
        import json

        try:
            export = {
                "version": "2.0",
                "ledger": self.ledger.data,
                "contacts": self.ledger.contacts,
            }
            return json.dumps(export, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ERROR] export_json failed: {e}")
            return ""

    def import_json(self, json_content: str) -> bool:
        """
        Importiere aus JSON
        """
        import json

        try:
            data = json.loads(json_content)
            self.ledger.data = data.get("ledger", {})
            self.ledger.contacts = data.get("contacts", {})
            self.ledger.save()
            return True
        except Exception as e:
            print(f"[ERROR] import_json failed: {e}")
            return False

    # ========== UTILITY METHODS ==========

    def get_statistics(self) -> Dict:
        """
        Gebe App-Statistiken
        """
        accounts = self.get_all_accounts()
        total_accounts = len(accounts)
        total_assignments = sum(a["assignment_count"] for a in accounts)
        total_contacts = len(self.ledger.contacts)

        return {
            "total_accounts": total_accounts,
            "total_assignments": total_assignments,
            "total_contacts": total_contacts,
            "accounts_with_quality": sum(1 for a in accounts if a.get("quality_score")),
        }

    def save(self) -> bool:
        """
        Speichere Ledger-Änderungen
        """
        try:
            self.ledger.save()
            return True
        except Exception as e:
            print(f"[ERROR] save failed: {e}")
            return False
