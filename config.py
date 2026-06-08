import os
from typing import Final, FrozenSet, Optional

SYSTEM_SAFELIST: Final[FrozenSet[str]] = frozenset({
    "explorer.exe", "taskhostw.exe", "taskmgr.exe", "cmd.exe", "powershell.exe",
    "chrome.exe", "firefox.exe", "msedge.exe", "code.exe", "cursor.exe",
})
# Optional comma-separated list of trusted binary SHA256 hashes (env var)
_HASHES = os.getenv("SYSTEM_SAFELIST_HASHES", "").strip()
if _HASHES:
    SYSTEM_SAFELIST_HASHES = frozenset(h.strip().lower() for h in _HASHES.split(",") if h.strip())
else:
    SYSTEM_SAFELIST_HASHES = frozenset()

CPU_ALERT_THRESHOLD: Final[float] = float(os.getenv("CPU_ALERT_THRESHOLD", "50.0"))
MONITOR_CPU_THRESHOLD: Final[float] = float(os.getenv("MONITOR_CPU_THRESHOLD", "25.0"))
TERMINATION_CPU_CUTOFF: Final[float] = float(os.getenv("TERMINATION_CPU_CUTOFF", "10.0"))
POLL_INTERVAL: Final[int] = int(os.getenv("POLL_INTERVAL", "30"))
TOP_CANDIDATES: Final[int] = int(os.getenv("TOP_CANDIDATES", "5"))
SAFE_MODE: Final[bool] = os.getenv("SAFE_MODE", "true").strip().lower() not in {"0", "false", "no"}
DRY_RUN_MODE: Final[bool] = os.getenv("DRY_RUN_MODE", "false").strip().lower() in {"1", "true", "yes"}
GEMINI_MODEL: Final[str] = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY: Final[Optional[str]] = os.getenv("GEMINI_API_KEY")
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO").upper()
HEURISTIC_THRESHOLD: Final[float] = float(os.getenv("HEURISTIC_THRESHOLD", "0.6"))
NETWORK_BYTES_SPIKE: Final[int] = int(os.getenv("NETWORK_BYTES_SPIKE", str(1024 * 50)))  # 50 KB
IO_WRITE_SPIKE: Final[int] = int(os.getenv("IO_WRITE_SPIKE", str(1024 * 100)))  # 100 KB
