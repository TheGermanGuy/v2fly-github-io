"""Screenshot-Analyse mit Gemini.

Wandelt einen Spiel-Screenshot in strukturierte Spielerstatistiken um. Gemini
liefert das Ergebnis als JSON gemäß festem Schema (Function-Calling-/
response_schema-Stil), damit das Parsen deterministisch bleibt.

`google-generativeai` wird erst zur Laufzeit importiert, damit dieses Modul
ohne installiertes Paket importierbar (und der Rest testbar) bleibt.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from .models import Buffs, EnemyComposition, PlayerStats

# Default-Truppentypen (generisch). Für Evony: ground/mounted/ranged/siege.
DEFAULT_TROOP_TYPES = ["infantry", "cavalry", "archer"]


def build_schema_hint(troop_types: List[str]) -> Dict:
    """Erzeugt das Gemini-Zielschema für die gegebenen Truppentypen."""
    troop_map = {t: "int" for t in troop_types}
    return {
        "player_id": "string",
        "power": "integer",
        "available_troops": dict(troop_map),
        "reinforcement_capacity": "integer",
        "buffs": {
            "global_defense": "float (0.25 == +25%)",
            "global_health": "float",
            "defense_by_type": {t: "float" for t in troop_types},
        },
        "enemy_composition": {t: "float fraction" for t in troop_types},
    }


def build_prompt(troop_types: List[str]) -> str:
    return (
        "Du analysierst einen Screenshot des 4X-Mobile-Strategiespiels. "
        "Extrahiere ausschließlich die sichtbaren Werte und gib NUR gültiges JSON "
        "exakt nach folgendem Schema zurück (fehlende Werte = 0 bzw. leeres Objekt). "
        "Erfinde keine Zahlen. Zahlenkürzel wie '1.2M' in ganze Zahlen umrechnen.\n\n"
        "Schema:\n" + json.dumps(build_schema_hint(troop_types), indent=2)
    )


# Rückwärtskompatible Default-Konstanten.
STATS_SCHEMA_HINT = build_schema_hint(DEFAULT_TROOP_TYPES)
PROMPT = build_prompt(DEFAULT_TROOP_TYPES)


class GeminiAnalyzer:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        troop_types: Optional[List[str]] = None,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model
        self.troop_types = troop_types or DEFAULT_TROOP_TYPES
        self.prompt = build_prompt(self.troop_types)
        self._model = None

    def _ensure_model(self):
        if self._model is not None:
            return
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY ist nicht gesetzt.")
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name)

    def analyze(self, png_bytes: bytes) -> Dict:
        """Gibt das von Gemini extrahierte Roh-Dict zurück."""
        self._ensure_model()
        image_part = {"mime_type": "image/png", "data": png_bytes}
        response = self._model.generate_content(
            [self.prompt, image_part],
            generation_config={"response_mime_type": "application/json", "temperature": 0.0},
        )
        return parse_gemini_json(response.text)

    def analyze_to_stats(self, png_bytes: bytes) -> "AnalysisResult":
        raw = self.analyze(png_bytes)
        return build_analysis_result(raw)


class GeminiRestAnalyzer:
    """Gemini-Analyse über die REST-API mit reiner Standardbibliothek.

    Robuster als das `google-generativeai`-SDK (kein gRPC/cryptography-Stack
    nötig). Identische `analyze()`-Schnittstelle wie `GeminiAnalyzer`.

    `ca_bundle` / Env `SSL_CERT_FILE` erlauben das Setzen eines CA-Bündels
    (z. B. hinter einem TLS-intercepting Proxy). Proxies werden aus den
    Umgebungsvariablen HTTP(S)_PROXY übernommen.
    """

    ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        troop_types: Optional[List[str]] = None,
        ca_bundle: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model
        self.troop_types = troop_types or DEFAULT_TROOP_TYPES
        self.prompt = build_prompt(self.troop_types)
        self.ca_bundle = ca_bundle or os.environ.get("SSL_CERT_FILE")
        self.timeout = timeout

    def _ssl_context(self):
        import ssl

        if self.ca_bundle:
            return ssl.create_default_context(cafile=self.ca_bundle)
        return ssl.create_default_context()

    def analyze(self, png_bytes: bytes) -> Dict:
        import base64
        import urllib.request

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY ist nicht gesetzt.")
        url = self.ENDPOINT.format(model=self.model_name) + f"?key={self.api_key}"
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": self.prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": base64.b64encode(png_bytes).decode("ascii"),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.0},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout, context=self._ssl_context()) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        text = payload["candidates"][0]["content"]["parts"][0]["text"]
        return parse_gemini_json(text)

    def analyze_to_stats(self, png_bytes: bytes) -> "AnalysisResult":
        return build_analysis_result(self.analyze(png_bytes))


class AnalysisResult:
    def __init__(self, stats: PlayerStats, buffs: Buffs, enemy: EnemyComposition):
        self.stats = stats
        self.buffs = buffs
        self.enemy = enemy


def parse_gemini_json(text: str) -> Dict:
    """Robustes Parsen: entfernt evtl. Markdown-Codefences."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
        if t.lstrip().startswith("json"):
            t = t.lstrip()[4:]
    return json.loads(t)


def build_analysis_result(raw: Dict) -> AnalysisResult:
    """Reine Funktion: Roh-Dict -> typisierte Modelle. Unit-testbar ohne Gemini."""
    stats = PlayerStats(
        player_id=str(raw.get("player_id", "unknown")),
        power=int(raw.get("power", 0) or 0),
        available_troops={
            k: int(v or 0) for k, v in (raw.get("available_troops") or {}).items()
        },
        reinforcement_capacity=int(raw.get("reinforcement_capacity", 0) or 0),
        raw=raw,
    )
    b = raw.get("buffs") or {}
    buffs = Buffs(
        global_defense=float(b.get("global_defense", 0.0) or 0.0),
        global_health=float(b.get("global_health", 0.0) or 0.0),
        defense_by_type={k: float(v or 0.0) for k, v in (b.get("defense_by_type") or {}).items()},
    )
    enemy = EnemyComposition(
        fractions={k: float(v or 0.0) for k, v in (raw.get("enemy_composition") or {}).items()}
    )
    return AnalysisResult(stats=stats, buffs=buffs, enemy=enemy)
