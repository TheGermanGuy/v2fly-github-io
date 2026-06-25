"""ADB-Steuerungs- und Capture-Layer (Ersatz für 'OpenClaw').

Spricht über die Android Debug Bridge mit einem Emulator/Gerät (in der
Windows-VM). Reine subprocess-Aufrufe gegen das `adb`-Binary — keine
Python-Abhängigkeiten.
"""
from __future__ import annotations

import subprocess
import time
from typing import List, Optional, Tuple


class AdbError(RuntimeError):
    pass


class AdbController:
    def __init__(self, serial: Optional[str] = None, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.serial = serial

    def _base_cmd(self) -> List[str]:
        cmd = [self.adb_path]
        if self.serial:
            cmd += ["-s", self.serial]
        return cmd

    def _run(self, args: List[str], capture: bool = True) -> bytes:
        try:
            proc = subprocess.run(
                self._base_cmd() + args,
                check=True,
                stdout=subprocess.PIPE if capture else None,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise AdbError(f"adb-Binary nicht gefunden ({self.adb_path}).") from e
        except subprocess.CalledProcessError as e:
            raise AdbError(
                f"adb {' '.join(args)} fehlgeschlagen: {e.stderr.decode(errors='replace')}"
            ) from e
        return proc.stdout or b""

    # --- Verbindung -------------------------------------------------------
    def connect(self, host_port: str) -> None:
        """Mit einem Netzwerk-Emulator verbinden, z. B. '127.0.0.1:5555'."""
        self._run(["connect", host_port], capture=True)
        self.serial = host_port

    def wait_for_device(self, timeout: float = 30.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            out = self._run(["get-state"]).decode(errors="replace").strip()
            if out == "device":
                return
            time.sleep(1.0)
        raise AdbError("Kein verbundenes Gerät innerhalb des Timeouts.")

    # --- Capture ----------------------------------------------------------
    def screencap_png(self) -> bytes:
        """Screenshot als PNG-Bytes (ohne Datei auf dem Gerät)."""
        # exec-out vermeidet CRLF-Probleme der älteren `shell screencap`-Variante.
        return self._run(["exec-out", "screencap", "-p"], capture=True)

    def save_screenshot(self, path: str) -> str:
        data = self.screencap_png()
        with open(path, "wb") as f:
            f.write(data)
        return path

    # --- Eingaben ---------------------------------------------------------
    def tap(self, x: int, y: int) -> None:
        self._run(["shell", "input", "tap", str(x), str(y)], capture=False)

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self._run(
            ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)],
            capture=False,
        )

    def back(self) -> None:
        self._run(["shell", "input", "keyevent", "KEYCODE_BACK"], capture=False)

    # --- Menüführung ------------------------------------------------------
    def navigate(self, steps: List[Tuple[int, int]], delay: float = 1.0) -> None:
        """Eine Folge von Taps abarbeiten, um durch Menüs zu navigieren.

        `steps` sind (x, y)-Koordinaten. Die konkreten Werte stammen aus dem
        Spielprofil (auflösungsabhängig) und werden außerhalb definiert.
        """
        for (x, y) in steps:
            self.tap(x, y)
            time.sleep(delay)
