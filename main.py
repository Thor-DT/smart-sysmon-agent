import logging
import logging.handlers
import os
import sys
import time
import psutil

import config
from agent_brain import query_agent_brain
from agent_effector import execute_agent_verdicts

logger = logging.getLogger("OrionMon")
logger.setLevel(config.LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    
    # Add file logging with rotation
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "orion-mon.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    ))
    logger.addHandler(file_handler)

def scan_and_observe():
    """
    SENSOR STEP: Reads system health metrics, sorts by absolute heaviest usage,
    and returns only the top resource hogs.
    """
    metrics = {
        "global_cpu": psutil.cpu_percent(interval=None),
        "global_ram": psutil.virtual_memory().percent,
        "disk_free_gb": round(psutil.disk_usage("/").free / (1024**3), 1),
    }

    all_processes = list(psutil.process_iter(["pid", "name"]))

    # Trigger initial delta calculation
    for proc in all_processes:
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(0.5)

    heavy_candidates = []
    for proc in all_processes:
        try:
            pid = proc.info["pid"]
            name = proc.info["name"]
            cpu = proc.cpu_percent(interval=None)
            mem = proc.memory_percent()

            if pid == os.getpid() or name is None or pid == 0:
                continue
            if name.lower() in config.SYSTEM_SAFELIST:
                continue

            if cpu > config.MONITOR_CPU_THRESHOLD:
                heavy_candidates.append(
                    {
                        "pid": pid,
                        "name": name,
                        "cpu_percent": round(cpu, 1),
                        "memory_percent": round(mem, 1),
                    }
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    heavy_candidates.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return metrics, heavy_candidates[: config.TOP_CANDIDATES]

def main():
    if not config.GEMINI_API_KEY and not config.DRY_RUN_MODE:
        logger.error(
            "GEMINI_API_KEY environment variable not found. "
            "Set GEMINI_API_KEY or enable DRY_RUN_MODE for safe testing."
        )
        sys.exit(1)

    logger.info("====================================================")
    logger.info(" Orion-Mon: LLM-Powered Autonomous System Admin Active")
    logger.info(" Checking loops every %d seconds...", config.POLL_INTERVAL)
    logger.info("====================================================\n")

    psutil.cpu_percent(interval=None)
    time.sleep(1)

    try:
        while True:
            logger.info("🔍 [Step 1: Observe] Scanning active operating system states...")
            system_metrics, targets = scan_and_observe()

            logger.info(
                "   System State: CPU: %.1f%% | RAM: %.1f%% | Free Disk: %.1fGB",
                system_metrics["global_cpu"],
                system_metrics["global_ram"],
                system_metrics["disk_free_gb"],
            )

            if not targets:
                logger.info(
                    "   No suspicious background resource hogs found. Sleeping for %ds...",
                    config.POLL_INTERVAL,
                )
                time.sleep(config.POLL_INTERVAL)
                continue

            logger.info("   Found %d candidate(s) crossing resource alerts.", len(targets))

            if config.DRY_RUN_MODE:
                logger.warning(
                    "🧪 [Dry Run] Skipping Gemini call and effector execution."
                )
                time.sleep(config.POLL_INTERVAL)
                continue

            logger.info("🧠 [Step 2: Think] Transmitting telemetry payload to Gemini Brain...")
            try:
                decisions = query_agent_brain(system_metrics, targets)

                logger.info("🛠️ [Step 3: Act] Routing decisions to local OS actuators...")
                execute_agent_verdicts(decisions)

            except Exception as api_err:
                logger.error("   [API Error] Failed to compute decision tree: %s", api_err)

            time.sleep(config.POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("\n[Shutdown] Orion-Mon closing down safely.")


if __name__ == "__main__":
    main()