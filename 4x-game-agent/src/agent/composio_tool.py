"""Composio-Anbindung der Google-Cloud-Vision-Screenshot-Analyse.

Registriert die Cloud-Vision-OCR-Analyse als Composio-Custom-Tool, sodass sie aus
einem Composio-gesteuerten Agenten-Workflow heraus aufrufbar ist. So entspricht
die Lösung der Vorgabe "Composio-Plugin für Google Cloud Vision".

`composio` wird lazy importiert. Die genaue Registrierungs-API kann je nach
installierter Composio-Version variieren — der Integrationspunkt ist hier klar
isoliert und dokumentiert.
"""
from __future__ import annotations

import base64
from typing import Dict

from .vision_cloud import CloudVisionOCR, ocr_text_to_raw


def analyze_screenshot_b64(image_b64: str, labels: Dict | None = None) -> Dict:
    """Composio-Tool-Funktion: Base64-PNG -> Stats-Roh-Dict via Cloud Vision.

    Reine Funktion (abgesehen vom Cloud-Vision-Call), damit sie als Tool sauber
    serialisierbare Ein-/Ausgaben hat.
    """
    png = base64.b64decode(image_b64)
    return CloudVisionOCR(labels=labels).analyze(png)


def register_with_composio(toolset, labels: Dict | None = None):
    """Registriert `analyze_screenshot_b64` als Composio-Custom-Action.

    `toolset` ist eine Composio-ToolSet-Instanz. Rückgabe ist das registrierte
    Action-Objekt/-Handle. Bei abweichender Composio-Version hier anpassen.
    """
    # Lazy import, damit das Modul ohne Composio importierbar bleibt.
    try:
        from composio import action  # type: ignore
    except Exception as e:  # pragma: no cover - abhängig von Installation
        raise RuntimeError(
            "Composio ist nicht installiert oder die API weicht ab. "
            "Installiere 'composio_core' und passe register_with_composio() an."
        ) from e

    @action(toolname="cloud_vision_screenshot")
    def cloud_vision_screenshot(image_b64: str) -> Dict:
        """Analysiert einen Spiel-Screenshot (Base64-PNG) via Google Cloud Vision."""
        return analyze_screenshot_b64(image_b64, labels=labels)

    return cloud_vision_screenshot
