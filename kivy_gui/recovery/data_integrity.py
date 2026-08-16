"""
Data Integrity
JSON validation and automatic repair for corrupted data files
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any


class DataValidator:
    """Validates data integrity"""

    @staticmethod
    def is_valid_json_file(filepath: str) -> bool:
        """Check if JSON file is valid and readable"""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, IOError):
            return False

    @staticmethod
    def validate_ledger_format(ledger_data: dict) -> tuple:
        """
        Validate LinkLedger format

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check required keys
        required_keys = ['version', 'accounts', 'contacts']
        for key in required_keys:
            if key not in ledger_data:
                errors.append(f"Missing required key: {key}")

        # Check version
        if 'version' in ledger_data:
            version = ledger_data['version']
            if not isinstance(version, str) or not version.startswith('v'):
                errors.append(f"Invalid version format: {version}")

        # Check accounts structure
        if 'accounts' in ledger_data:
            if not isinstance(ledger_data['accounts'], dict):
                errors.append("accounts must be dictionary")
            else:
                for acc_id, account in ledger_data['accounts'].items():
                    if 'assignments' not in account:
                        errors.append(f"Account {acc_id} missing 'assignments'")

        # Check contacts structure
        if 'contacts' in ledger_data:
            if not isinstance(ledger_data['contacts'], dict):
                errors.append("contacts must be dictionary")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_settings_format(settings_data: dict) -> tuple:
        """
        Validate settings format

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Settings should be a dict with string keys
        if not isinstance(settings_data, dict):
            errors.append("Settings must be a dictionary")
            return (False, errors)

        # All values should be basic types
        for key, value in settings_data.items():
            if not isinstance(key, str):
                errors.append(f"Setting key must be string: {key}")
            if not isinstance(value, (bool, int, float, str, type(None))):
                errors.append(f"Setting '{key}' has invalid type: {type(value).__name__}")

        return (len(errors) == 0, errors)


class DataRepairManager:
    """Attempts to repair corrupted data"""

    @staticmethod
    def repair_json_file(filepath: str) -> bool:
        """
        Attempt to repair corrupted JSON file

        Strategy:
        1. Try reading with different encodings
        2. Remove trailing commas and comments
        3. Validate structure
        4. Create backup of corrupted file
        """
        if not os.path.exists(filepath):
            return False

        # Create backup
        backup_path = filepath + '.corrupted'
        try:
            os.rename(filepath, backup_path)
        except OSError:
            print(f"[ERROR] Could not create backup of {filepath}")
            return False

        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        content = None

        for encoding in encodings:
            try:
                with open(backup_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"[INFO] Successfully read file with encoding: {encoding}")
                break
            except (UnicodeDecodeError, IOError):
                continue

        if content is None:
            print(f"[ERROR] Could not read file {filepath} with any encoding")
            return False

        # Try to clean and parse
        try:
            # Remove comments (lines starting with //)
            lines = []
            for line in content.split('\n'):
                if not line.strip().startswith('//'):
                    lines.append(line)
            cleaned = '\n'.join(lines)

            # Try parsing
            data = json.loads(cleaned)

            # Write repaired data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"[SUCCESS] Repaired file: {filepath}")
            return True

        except json.JSONDecodeError as e:
            print(f"[ERROR] Could not repair JSON: {e}")
            # Restore backup
            try:
                os.rename(backup_path, filepath)
            except OSError:
                pass
            return False

    @staticmethod
    def repair_ledger_file(filepath: str) -> bool:
        """Repair corrupted ledger file with defaults"""
        if not DataValidator.is_valid_json_file(filepath):
            # Try to repair
            if not DataRepairManager.repair_json_file(filepath):
                # Create new ledger with defaults
                return DataRepairManager._create_default_ledger(filepath)

        return True

    @staticmethod
    def _create_default_ledger(filepath: str) -> bool:
        """Create default ledger structure"""
        default_ledger = {
            'version': 'v2.0',
            'accounts': {},
            'contacts': {},
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
            }
        }

        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_ledger, f, indent=2, ensure_ascii=False)
            print(f"[INFO] Created default ledger: {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not create default ledger: {e}")
            return False

    @staticmethod
    def repair_settings_file(filepath: str, defaults: dict) -> bool:
        """Repair settings file with defaults"""
        if not DataValidator.is_valid_json_file(filepath):
            if not DataRepairManager.repair_json_file(filepath):
                # Use defaults
                return DataRepairManager._create_default_settings(filepath, defaults)

        return True

    @staticmethod
    def _create_default_settings(filepath: str, defaults: dict) -> bool:
        """Create default settings file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(defaults, f, indent=2)
            print(f"[INFO] Created default settings: {filepath}")
            return True
        except Exception as e:
            print(f"[ERROR] Could not create default settings: {e}")
            return False


class IntegrityMonitor:
    """Monitors and maintains data integrity"""

    def __init__(self):
        self.last_check = None
        self.issues_found = 0
        self.issues_fixed = 0

    def check_all_files(self, data_dir: str) -> dict:
        """Check all data files for integrity"""
        results = {
            'checked': 0,
            'valid': 0,
            'corrupted': 0,
            'repaired': 0,
            'issues': [],
        }

        json_files = [
            os.path.join(data_dir, f) for f in os.listdir(data_dir)
            if f.endswith('.json')
        ]

        for filepath in json_files:
            results['checked'] += 1

            if DataValidator.is_valid_json_file(filepath):
                results['valid'] += 1
            else:
                results['corrupted'] += 1
                results['issues'].append(filepath)

                if DataRepairManager.repair_json_file(filepath):
                    results['repaired'] += 1

        self.last_check = datetime.now().isoformat()
        self.issues_found = results['corrupted']
        self.issues_fixed = results['repaired']

        return results

    def print_report(self, results: dict):
        """Print integrity check report"""
        print("\n" + "=" * 60)
        print("Data Integrity Report")
        print("=" * 60)
        print(f"Checked:   {results['checked']}")
        print(f"Valid:     {results['valid']}")
        print(f"Corrupted: {results['corrupted']}")
        print(f"Repaired:  {results['repaired']}")

        if results['issues']:
            print("\nProblematic files:")
            for issue in results['issues']:
                print(f"  - {issue}")

        print("=" * 60 + "\n")
