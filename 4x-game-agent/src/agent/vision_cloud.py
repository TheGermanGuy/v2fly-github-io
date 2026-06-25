"""Google-Cloud-Vision-Backend für die Screenshot-Analyse (Alternative/Ergänzung
zu Gemini), angebunden über das Composio-Plugin.

Cloud Vision liefert reines OCR (Texterkennung). Den erkannten Text wandeln wir
über eine konfigurierbare Label→Feld-Zuordnung in das gemeinsame Stats-Schema um,
sodass dieselbe nachgelagerte Pipeline (Speicherung, Strategie, Messenger) ohne
Änderung weiterläuft.

`google-cloud-vision` und `composio` werden erst zur Laufzeit importiert, damit
das Modul ohne diese Pakete importier- und testbar bleibt. Die reine
Text→Schema-Funktion `ocr_text_to_raw` ist unit-getestet.
"""
from __future__ import annotations

import os
import re
from typing import Dict, List, Optional, Tuple

# Standard-Label-Zuordnung für das generische 4X-Profil. Pro Spieltitel anpassen.
DEFAULT_LABELS: Dict[str, List[str]] = {
    "power": ["power", "macht", "kampfkraft"],
    "reinforcement_capacity": ["reinforcement", "verstärkung", "kapazität", "capacity"],
    "available_troops.infantry": ["infantry", "infanterie"],
    "available_troops.cavalry": ["cavalry", "kavallerie"],
    "available_troops.archer": ["archer", "bogen", "schützen"],
}

_NUM = re.compile(r"[-+]?\d[\d.,]*\s*[KkMmBb]?")


def _to_int(token: str) -> int:
    """'12,345' / '12.345' / '1.2K' / '3M' / '15.2 M' -> int."""
    t = token.strip().lower().replace(" ", "")
    mult = 1
    if t.endswith("k"):
        mult, t = 1_000, t[:-1]
    elif t.endswith("m"):
        mult, t = 1_000_000, t[:-1]
    elif t.endswith("b"):
        mult, t = 1_000_000_000, t[:-1]
    t = t.replace(",", "").replace(".", "") if mult == 1 else t.replace(",", "")
    try:
        return int(round(float(t) * mult))
    except ValueError:
        return 0


def ocr_text_to_raw(
    text: str,
    labels: Optional[Dict[str, List[str]]] = None,
    player_id: str = "ocr",
) -> Dict:
    """Reine Funktion: OCR-Rohtext -> Stats-Roh-Dict (gleiches Schema wie Gemini).

    Sucht pro Feld die erste Zeile, die eines der Labels enthält, und extrahiert
    die erste Zahl dieser Zeile.
    """
    labels = labels or DEFAULT_LABELS
    raw: Dict = {
        "player_id": player_id,
        "power": 0,
        "available_troops": {},
        "reinforcement_capacity": 0,
        "buffs": {},
        "enemy_composition": {},
    }
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for field, keys in labels.items():
        value = _find_number_for(lines, keys)
        if value is None:
            continue
        if "." in field:
            top, sub = field.split(".", 1)
            raw.setdefault(top, {})[sub] = value
        else:
            raw[field] = value
    return raw


def _find_number_for(lines: List[str], keys: List[str]) -> Optional[int]:
    for ln in lines:
        low = ln.lower()
        if any(k in low for k in keys):
            m = _NUM.search(ln)
            if m:
                return _to_int(m.group(0))
    return None


class CloudVisionOCR:
    """Dünner Wrapper um die Google-Cloud-Vision-API (DOCUMENT_TEXT_DETECTION)."""

    def __init__(self, labels: Optional[Dict[str, List[str]]] = None):
        self.labels = labels or DEFAULT_LABELS
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            from google.cloud import vision  # lazy import

            self._client = vision.ImageAnnotatorClient()
        return self._client

    def extract_text(self, png_bytes: bytes) -> str:
        from google.cloud import vision  # lazy import

        client = self._ensure_client()
        image = vision.Image(content=png_bytes)
        resp = client.document_text_detection(image=image)
        if resp.error.message:
            raise RuntimeError(f"Cloud-Vision-Fehler: {resp.error.message}")
        return resp.full_text_annotation.text if resp.full_text_annotation else ""

    def analyze(self, png_bytes: bytes) -> Dict:
        """Gibt das Stats-Roh-Dict zurück (kompatibel zu GeminiAnalyzer.analyze)."""
        text = self.extract_text(png_bytes)
        return ocr_text_to_raw(text, self.labels)
