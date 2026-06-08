import hashlib
import logging
from typing import Optional

import config

logger = logging.getLogger("OrionMon.Safelist")
logger.setLevel(config.LOG_LEVEL)


def is_safelisted(process_name: Optional[str], exe_path: Optional[str] = None) -> bool:
    """Return True if the process should be treated as safe.

    Checks, in order:
    - exact process name match against `config.SYSTEM_SAFELIST` (case-insensitive)
    - if `exe_path` provided and readable, compute sha256 and compare to `config.SYSTEM_SAFELIST_HASHES`

    NOTE: Name-only checks are a weak heuristic; prefer providing binary hashes.
    """
    if not process_name and not exe_path:
        return False

    if process_name:
        try:
            if process_name.lower() in (n.lower() for n in config.SYSTEM_SAFELIST):
                return True
        except Exception:
            pass

    if exe_path:
        try:
            h = hashlib.sha256()
            with open(exe_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            if h.hexdigest().lower() in config.SYSTEM_SAFELIST_HASHES:
                return True
        except Exception:
            # If we cannot read the file, err on the side of caution (not safelisted)
            logger.debug("Could not compute hash for %s; treating as not safelisted.", exe_path)
            return False

    return False
