import hashlib
import logging
import psutil
import time
from typing import List, Dict

import config

logger = logging.getLogger("OrionMon.Detector")
logger.setLevel(config.LOG_LEVEL)


def collect_enriched_telemetry(candidates: List[dict]) -> List[dict]:
    """Given minimal candidate dicts (pid, name, cpu_percent...), collect richer telemetry safely.

    Returns a list of enriched dicts keyed by the original fields plus extra telemetry.
    """
    enriched = []
    for c in candidates:
        pid = c.get("pid")
        try:
            proc = psutil.Process(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        try:
            cmdline = proc.cmdline()
        except Exception:
            cmdline = []

        try:
            exe = proc.exe()
        except Exception:
            exe = None

        try:
            ppid = proc.ppid()
        except Exception:
            ppid = None

        try:
            create_time = proc.create_time()
        except Exception:
            create_time = None

        try:
            io_counters = proc.io_counters()
            write_bytes = getattr(io_counters, "write_bytes", 0)
        except Exception:
            write_bytes = 0

        try:
            conns = proc.connections(kind="inet")
            net_endpoints = [f"{c.laddr}->{c.raddr}({c.status})" for c in conns if c.raddr]
            net_bytes = 0
        except Exception:
            net_endpoints = []
            net_bytes = 0

        try:
            children = [ch.pid for ch in proc.children(recursive=False)]
        except Exception:
            children = []

        sha256 = None
        if exe:
            try:
                with open(exe, "rb") as f:
                    h = hashlib.sha256()
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        h.update(chunk)
                    sha256 = h.hexdigest()
            except Exception:
                sha256 = None

        enriched.append(
            {
                **c,
                "cmdline": cmdline,
                "exe": exe,
                "ppid": ppid,
                "create_time": create_time,
                "write_bytes": write_bytes,
                "net_endpoints": net_endpoints,
                "net_bytes": net_bytes,
                "children": children,
                "sha256": sha256,
            }
        )

    return enriched


def local_heuristic(enriched_candidates: List[dict], system_metrics: Dict) -> Dict[int, float]:
    """Compute a lightweight suspiciousness score for each enriched candidate.

    Returns a mapping pid->score (0.0-1.0). Higher score indicates higher suspicion.
    """
    scores = {}
    for c in enriched_candidates:
        pid = c.get("pid")
        score = 0.0

        # CPU weight (normalized by a heuristic cutoff)
        cpu = float(c.get("cpu_percent", 0.0))
        score += min(cpu / 100.0, 1.0) * 0.5

        # Large sudden IO writes
        write = int(c.get("write_bytes", 0))
        if write >= config.IO_WRITE_SPIKE:
            score += 0.15

        # Network endpoints
        if c.get("net_endpoints"):
            score += 0.15

        # Unexpected children
        if len(c.get("children", [])) >= 3:
            score += 0.1

        # Unusual parent / system user mismatch
        ppid = c.get("ppid")
        if ppid and ppid not in (0, 1):
            score += 0.05

        # Cap and normalize
        scores[pid] = min(score, 1.0)

    logger.debug("Heuristic scores: %s", scores)
    return scores


def should_escalate(scores: Dict[int, float], threshold: float = None) -> bool:
    if threshold is None:
        threshold = config.HEURISTIC_THRESHOLD
    for v in scores.values():
        if v >= threshold:
            return True
    return False
