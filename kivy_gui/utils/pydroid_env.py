"""
Pydroid 3 Environment Manager
Verwaltet Pydroid-spezifische Umgebungsvariablen und Constraints
"""

import os
from .pydroid_detector import pydroid


class PydroidEnvironment:
    """Verwaltet Pydroid-spezifische Umgebung und Constraints"""

    def __init__(self):
        self.detector = pydroid
        self.is_pydroid = self.detector.is_pydroid_3()
        self.mem_info = self.detector.get_memory_info()
        self.cpu_count = self.detector.get_cpu_count()
        self.is_low_memory = self.detector.is_low_memory_device()

    # ========== WORKER & CONCURRENCY OPTIMIZATION ==========

    def get_optimal_workers(self) -> int:
        """
        Berechne optimale Worker-Count basierend auf CPU + Memory

        Strategie:
        - ARM64 mit viel RAM: min(2, cpu_count)
        - ARMv7: max 2
        - Low-Memory: max 1-2
        - Single-Core: 1
        """
        if not self.is_pydroid:
            return 8  # Desktop default

        # Pydroid ARM ist immer single- oder dual-core
        if self.is_low_memory:
            return 1  # Sehr konservativ bei <2GB RAM
        elif self.detector.get_cpu_arch() == 'ARMv7':
            return min(2, self.cpu_count)  # ARMv7 ist langsamer
        else:  # ARM64
            return min(4, max(2, self.cpu_count))

    def get_batch_size(self) -> int:
        """
        Berechne Memory-aware Batch-Größe für Operations

        Strategie:
        - <500MB free: 5 Items
        - 500MB-1GB: 10 Items
        - >1GB: 25 Items
        """
        if not self.is_pydroid:
            return 50  # Desktop default

        available_mb = self.mem_info.get('available_mb', 0)

        if available_mb < 500:
            return 5
        elif available_mb < 1000:
            return 10
        else:
            return 25

    def get_timeout_multiplier(self) -> float:
        """
        Berechne Timeout-Multiplikator für CPU-Speed

        Strategie:
        - Langsame ARM (ARMv7): 2.5x
        - Normale ARM (ARM64): 1.5x
        - Desktop: 1.0x
        """
        if not self.is_pydroid:
            return 1.0

        arch = self.detector.get_cpu_arch()
        if arch == 'ARMv7':
            return 2.5
        elif arch == 'ARM64':
            return 1.5
        else:
            return 1.0

    # ========== MEMORY MANAGEMENT ==========

    def get_safe_cache_size_mb(self) -> int:
        """
        Berechne sichere Cache-Größe

        Strategie:
        - Nutze max 20% des verfügbaren Speichers
        - Minimum: 50MB
        - Maximum: 500MB
        """
        if not self.is_pydroid:
            return 500

        available_mb = self.mem_info.get('available_mb', 0)
        safe_size = max(50, min(500, int(available_mb * 0.2)))
        return safe_size

    def get_max_heap_size_mb(self) -> int:
        """
        Gebe maximale Heap-Größe für Python

        Strategie:
        - Pydroid3: max 70% des gesamten RAM (rest für System)
        - Desktop: unlimited
        """
        if not self.is_pydroid:
            return 2048  # Very permissive on desktop

        total_mb = self.mem_info.get('total_mb', 0)
        return int(total_mb * 0.7)

    def should_aggressive_gc(self) -> bool:
        """
        Sollte aggressives Garbage Collection aktiviert sein?

        True wenn: <30% Memory verfügbar ODER Low-Memory-Device
        """
        percent_used = self.mem_info.get('percent_used', 0)
        return percent_used > 70 or self.is_low_memory

    # ========== STORAGE & I/O ==========

    def get_storage_path(self) -> str:
        """
        Gebe Pydroid-optimierten Storage-Pfad

        Pydroid 3: /storage/emulated/0/Documents/m3uScan/
        QPython: /sdcard/QFiles/...
        Desktop: ~/.m3uscan/
        """
        if not self.is_pydroid:
            return os.path.expanduser('~/.m3uscan')

        # Pydroid 3 Standard-Pfad
        primary = os.path.expanduser('~/Documents/m3uScan')

        # Fallback zu /storage/emulated/0
        if not os.access(os.path.dirname(primary), os.W_OK):
            primary = '/storage/emulated/0/Documents/m3uScan'

        return primary

    def get_cache_path(self) -> str:
        """Gebe Pydroid-Cache-Pfad"""
        base = self.get_storage_path()
        cache_dir = os.path.join(base, '.cache')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

    def get_backup_path(self) -> str:
        """Gebe Pydroid-Backup-Pfad"""
        base = self.get_storage_path()
        backup_dir = os.path.join(base, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def get_logs_path(self) -> str:
        """Gebe Pydroid-Logs-Pfad"""
        base = self.get_storage_path()
        logs_dir = os.path.join(base, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        return logs_dir

    def get_available_storage_mb(self) -> int:
        """Gebe verfügbarer Storage in MB"""
        try:
            import shutil
            stats = shutil.disk_usage(self.get_storage_path())
            return stats.free // (1024 * 1024)
        except Exception:
            return 0

    def is_storage_low(self, threshold_mb: int = 100) -> bool:
        """Prüfe ob Storage niedrig ist"""
        return self.get_available_storage_mb() < threshold_mb

    # ========== NETWORK TUNING ==========

    def get_network_timeout(self, base_timeout: float = 10.0) -> float:
        """
        Gebe Network-Timeout mit Pydroid-Anpassung

        Pydroid ist langsamer → erhöhe Timeouts
        """
        if not self.is_pydroid:
            return base_timeout

        # Pydroid: 1.5x bis 2.5x länger
        multiplier = self.get_timeout_multiplier()
        return base_timeout * min(multiplier, 2.5)  # Cap at 2.5x

    def get_connection_pool_size(self) -> int:
        """Gebe aiohttp Connection-Pool-Größe"""
        if not self.is_pydroid:
            return 10

        # Pydroid: kleinere Pool
        if self.is_low_memory:
            return 2
        else:
            return 5

    # ========== EVENT LOOP TUNING ==========

    def get_event_loop_policy(self) -> str:
        """
        Gebe asyncio Event-Loop-Policy für Pydroid

        Pydroid (Android) muss spezielle Policy nutzen
        """
        if not self.is_pydroid:
            return 'default'

        # Pydroid: ProactorEventLoop ist nicht verfügbar
        # Nutze SelectorEventLoop (default)
        return 'default'

    def get_gc_tuning_params(self) -> dict:
        """Gebe Garbage Collector Tuning-Parameter"""
        import gc

        if not self.is_pydroid:
            return {}

        # Pydroid: Aggressivere GC bei Low-Memory
        if self.is_low_memory:
            return {
                'gc_threshold0': 500,  # Trigger GC sofort bei mehr als 500 Objects
                'gc_threshold1': 10,   # Sehr aggressiv
                'gc_threshold2': 10,
            }
        else:
            return {
                'gc_threshold0': 2000,
                'gc_threshold1': 10,
                'gc_threshold2': 10,
            }

    # ========== UI TUNING ==========

    def get_ui_refresh_rate(self) -> float:
        """
        Gebe UI-Refresh-Rate (FPS) für Pydroid

        Pydroid ARM: 30 FPS (50ms interval)
        Desktop: 60 FPS (16ms interval)
        """
        if not self.is_pydroid:
            return 1/60  # 60 FPS

        if self.is_low_memory:
            return 1/20  # 20 FPS für Low-Memory
        else:
            return 1/30  # 30 FPS

    def should_reduce_animations(self) -> bool:
        """Sollten Animationen reduziert/deaktiviert werden?"""
        if not self.is_pydroid:
            return False

        # Reduziere bei Low-Memory oder High-CPU-Load
        return self.is_low_memory or self.detector.get_memory_info().get('percent_used', 0) > 80

    # ========== DIAGNOSTICS ==========

    def get_optimization_report(self) -> dict:
        """Gebe Pydroid-Optimization-Report"""
        return {
            'is_pydroid': self.is_pydroid,
            'is_low_memory': self.is_low_memory,
            'optimal_workers': self.get_optimal_workers(),
            'batch_size': self.get_batch_size(),
            'timeout_multiplier': self.get_timeout_multiplier(),
            'safe_cache_mb': self.get_safe_cache_size_mb(),
            'max_heap_mb': self.get_max_heap_size_mb(),
            'aggressive_gc': self.should_aggressive_gc(),
            'storage_path': self.get_storage_path(),
            'available_storage_mb': self.get_available_storage_mb(),
            'storage_low': self.is_storage_low(),
            'ui_refresh_rate': self.get_ui_refresh_rate(),
            'reduce_animations': self.should_reduce_animations(),
            'system_info': self.detector.get_system_info(),
        }

    def print_optimization_report(self):
        """Gebe Optimization-Report aus (für Debugging)"""
        report = self.get_optimization_report()
        print("\n" + "=" * 60)
        print("PYDROID OPTIMIZATION REPORT")
        print("=" * 60)
        for key, value in report.items():
            if key != 'system_info':
                print(f"{key:25} : {value}")
        print("=" * 60 + "\n")


# Global Instance
pydroid_env = PydroidEnvironment()
