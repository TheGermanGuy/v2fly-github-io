# Auto-Worker Determination Function - Technical Guide

## Overview

The `_determine_optimal_workers()` function is an intelligent worker pool calculator that determines the optimal number of concurrent scanning workers based on:
- System hardware capabilities (CPU cores, available RAM)
- Device type and architecture (Desktop, Android, Pydroid3, ARM version)
- Input size (unique hosts, total links)

---

## Function Signature

```python
def _determine_optimal_workers(unique_hosts: int = 0, total_links: int = 0) -> dict:
    """
    Intelligente Worker-Bestimmung basierend auf Systemressourcen und Eingabedaten.
    
    Args:
        unique_hosts: Number of unique IPTV hosts in the input
        total_links: Total number of Xtream account links to scan
    
    Returns:
        {
            'workers': int,           # Recommended worker count (actual value used)
            'cpu_cores': int,         # Detected physical CPU cores
            'ram_mb': int,            # Available RAM in MB
            'platform': str,          # Platform name ('Pydroid3 (ARM64)', 'Desktop', etc.)
            'arm_version': str|None,  # ARM architecture ('ARM64', 'ARMv7', None)
            'limiting_factor': str,   # Explanation of what limited the result
        }
    """
```

---

## System Detection Components

### 1. CPU Detection: `_get_cpu_count()`

```python
def _get_cpu_count() -> int:
    """Get physical CPU core count."""
    try:
        if HAS_PSUTIL:
            return psutil.cpu_count(logical=False) or os.cpu_count() or 2
        return os.cpu_count() or 2
    except Exception:
        return 2
```

**How it works**:
1. **Primary**: Uses `os.cpu_count()` - standard Python library
2. **Enhanced**: If psutil available, uses physical cores (ignores hyperthreading)
3. **Fallback**: Returns 2 if detection fails

**Why physical cores matter**:
- Hyperthreaded cores (e.g., 4 physical = 8 logical) don't help I/O-bound tasks
- Network requests are I/O-bound (waiting for responses)
- Using physical cores prevents excessive context switching

---

### 2. Memory Detection: `_get_available_memory_mb()`

```python
def _get_available_memory_mb() -> int:
    """Get available memory in MB."""
    try:
        if HAS_PSUTIL:
            return int(psutil.virtual_memory().available / (1024 * 1024))
        return 512
    except Exception:
        return 512
```

**How it works**:
1. **Primary**: Uses psutil for precise available memory measurement
2. **Fallback**: Conservative estimate of 512MB if unavailable
3. **Unit**: Returns MB for easy calculation

**Why available memory**:
- Each worker buffers ~20-50MB of data during scanning
- Prevents OOM crashes on memory-constrained devices
- Mobile devices (Pydroid3) typically have 2-4GB RAM

---

### 3. ARM Architecture Detection: `_detect_arm_version()`

```python
def _detect_arm_version() -> str:
    """Detect ARM architecture version (v7 vs v8/64)."""
    import platform
    try:
        machine = platform.machine().lower()
        if 'armv8' in machine or 'aarch64' in machine or 'arm64' in machine:
            return 'ARM64'
        elif 'armv7' in machine or 'arm' in machine:
            return 'ARMv7'
    except Exception:
        pass
    return 'Unknown'
```

**How it works**:
- Reads `platform.machine()` to get CPU architecture string
- Matches patterns for ARM64 (fast, modern) vs ARMv7 (slow, legacy)

**Performance differences**:
```
ARM64 (64-bit):
  - Modern Snapdragon (2020+), Apple A-series
  - 2-3x faster than ARMv7 for same task
  - Better memory addressing
  - Pydroid 3: Can handle 6-12 workers

ARMv7 (32-bit):
  - Legacy/budget phones
  - Slower instruction execution
  - Limited memory addressing (max 4GB)
  - Pydroid 3: Limited to 3-6 workers to prevent OOM
```

---

## Worker Calculation Algorithm

### Step 1: Compute Independent Factors

```python
# CPU-based: I/O-bound tasks need ~75% of physical cores
cpu_based = max(2, int(cpu_cores * 0.75))

# RAM-based: ~50MB per worker
ram_based = max(2, ram_mb // 50)

# Host-based: Distribute workers across hosts
hosts_based = max(2, unique_hosts // 3) if unique_hosts > 0 else 4
```

**Example calculation (Desktop, 4 cores, 8GB RAM, 100 hosts)**:
- `cpu_based` = max(2, int(4 * 0.75)) = max(2, 3) = 3
- `ram_based` = max(2, 8192 // 50) = max(2, 163) = 163 ← RAM not limiting
- `hosts_based` = max(2, 100 // 3) = max(2, 33) = 33 ← Enough hosts

### Step 2: Apply Device-Specific Constraints

Limits are set based on device capabilities:

```
Platform              Min Workers  Max Workers  Rationale
─────────────────────────────────────────────────────────────
Pydroid3 (ARM64)      6            12           Modern phones, 64-bit
Pydroid3 (ARMv7)      3            6            Legacy phones, 32-bit
Pydroid3 (Unknown)    4            8            Uncertain hardware
Android               4            8            Fallback for unknown
Desktop               8            24           Desktop/laptop capability
```

### Step 3: Final Calculation

```python
workers = min(max(cpu_based, hosts_based), ram_based)
workers = max(min_workers, min(workers, max_workers))
```

**This formula**:
1. Takes the higher of CPU-based or host-based (be aggressive)
2. Caps with RAM-based (safety constraint)
3. Enforces minimum for device type (no underutilization)
4. Enforces maximum for device type (no overload)

### Step 4: Determine Limiting Factor

```python
if workers == cpu_based:
    limiting_factor = f"CPU ({cpu_cores} cores)"
elif workers == ram_based:
    limiting_factor = f"RAM ({ram_mb}MB available)"
elif workers == hosts_based:
    limiting_factor = f"Unique Hosts ({unique_hosts})"
elif workers == min_workers:
    limiting_factor = f"Device minimum ({platform_str})"
elif workers == max_workers:
    limiting_factor = f"Device maximum ({platform_str})"
```

---

## Example Scenarios

### Scenario 1: Pydroid3 on ARM64 Phone, 100 hosts

```python
result = _determine_optimal_workers(100, 1000)
```

**System**:
- CPU: 8 cores (ARM64)
- RAM: 3500MB available
- Platform: Pydroid3

**Calculation**:
- `cpu_based` = max(2, int(8 * 0.75)) = 6
- `ram_based` = max(2, 3500 // 50) = 70
- `hosts_based` = max(2, 100 // 3) = 33
- Device: Pydroid3 ARM64 → min=6, max=12
- `workers` = min(max(6, 33), 70) = 33 → capped to max 12

**Result**: `{workers: 12, limiting_factor: "Device maximum (Pydroid3 (ARM64))"}`

---

### Scenario 2: Pydroid3 on ARMv7 Phone, 50 hosts

```python
result = _determine_optimal_workers(50, 500)
```

**System**:
- CPU: 4 cores (ARMv7)
- RAM: 1200MB available
- Platform: Pydroid3

**Calculation**:
- `cpu_based` = max(2, int(4 * 0.75)) = 3
- `ram_based` = max(2, 1200 // 50) = 24
- `hosts_based` = max(2, 50 // 3) = 16
- Device: Pydroid3 ARMv7 → min=3, max=6
- `workers` = min(max(3, 16), 24) = 16 → capped to max 6

**Result**: `{workers: 6, limiting_factor: "Device maximum (Pydroid3 (ARMv7))"}`

---

### Scenario 3: Desktop, 500 hosts, Low RAM

```python
result = _determine_optimal_workers(500, 5000)
```

**System**:
- CPU: 4 cores
- RAM: 512MB available (memory-constrained VM)
- Platform: Desktop

**Calculation**:
- `cpu_based` = max(2, int(4 * 0.75)) = 3
- `ram_based` = max(2, 512 // 50) = 10
- `hosts_based` = max(2, 500 // 3) = 166
- Device: Desktop → min=8, max=24
- `workers` = min(max(3, 166), 10) = 10

**Result**: `{workers: 10, limiting_factor: "RAM (512MB available)"}`

**This prevents**: Over-allocating workers and crashing with OOM on the VM.

---

## Usage in Scanner

### During Resume Checkpoint Loading

```python
if cfg.workers_auto:
    worker_info = _determine_optimal_workers(unique_hosts, total)
    workers_actual = worker_info['workers']
    print(f"Auto-determined: {workers_actual} workers ({worker_info['limiting_factor']})")
else:
    workers_actual = cfg.workers
```

### During Main Configuration Menu

```python
if cfg.workers_auto:
    worker_info = _determine_optimal_workers(unique_hosts, total)
    workers_actual = worker_info['workers']
else:
    workers_actual = cfg.workers

cfg.workers = workers_actual  # Use this value for scanning
```

---

## Configuration

### Enable/Disable Auto-Worker

```python
# Global setting (default: enabled)
WORKERS_AUTO = True          # False = always use manual WORKERS value
```

### Manual Override

The function is called automatically when `cfg.workers_auto = True`.

To disable:
```python
cfg.workers_auto = False
cfg.workers = 8  # Use fixed value
```

---

## Performance Considerations

### Calculation Cost
- **Execution Time**: <1 millisecond
- **Memory**: ~1KB for returned dictionary
- **Frequency**: Called 1-2 times per scan session
- **Impact**: Negligible

### Memory Allocation Assumption
**50MB per worker** is a conservative estimate based on:
- aiohttp session overhead: ~5MB
- Network buffers: ~10MB
- Regex/string processing: ~10MB
- User data accumulation: ~20-25MB
- Safety margin: ~5-10MB

This prevents OOM crashes on low-RAM devices.

---

## Dependencies

### Required
- Python 3.7+
- `os` module (standard library)
- `platform` module (standard library)

### Optional
- `psutil`: For precise CPU/memory detection
  ```bash
  pip install psutil  # Enhanced detection
  ```
  
**Graceful Degradation**: Code works without psutil using fallbacks.

---

## Troubleshooting

### Issue: Always uses minimum workers (slow scanning)

**Cause**: Limited RAM or CPU.

**Solution**:
- Check available memory: `_get_available_memory_mb()`
- Close other applications
- Reduce host count in input file

### Issue: Always uses maximum workers (crashes with OOM)

**Cause**: Device limit is too high for actual RAM.

**Solution**:
- Manually set: `cfg.workers_auto = False; cfg.workers = 4`
- Or increase available RAM by closing apps

### Issue: Detection shows 'Unknown' platform

**Cause**: ARM architecture not detected correctly.

**Solution**:
- Falls back to safe defaults (Pydroid3: 4-8 workers)
- If crashes, manually set workers lower

---

## Future Enhancements

1. **Logging**: Log worker selection for debugging
   ```python
   if worker_info['limiting_factor'].startswith('RAM'):
       logger.warning(f"Low RAM: {worker_info['ram_mb']}MB")
   ```

2. **User Customization**: Let users adjust limiting factors
   ```python
   # Config file
   WORKERS_MAX_OVERRIDE = 6  # Cap workers to 6 regardless
   ```

3. **Machine Learning**: Learn from historical scans
   ```python
   # Track actual throughput vs. predicted workers
   # Adjust formula for platform-specific optimization
   ```

4. **Dynamic Adjustment**: Decrease workers if OOM detected
   ```python
   except MemoryError:
       cfg.workers = cfg.workers // 2
   ```

---

## References

- Python `os.cpu_count()`: [docs](https://docs.python.org/3/library/os.html#os.cpu_count)
- Python `platform` module: [docs](https://docs.python.org/3/library/platform.html)
- psutil documentation: [psutil](https://psutil.readthedocs.io/)
- asyncio.Semaphore: [docs](https://docs.python.org/3/library/asyncio-sync-primitives.html#semaphore)

---

**Document Version**: 1.0
**Last Updated**: 2026-06-10
**Status**: Production Ready

