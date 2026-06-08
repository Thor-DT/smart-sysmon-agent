import logging
import psutil

import config
from brain_schema import AgentDecisionBatch

logger = logging.getLogger("OrionMon.Effector")
logger.setLevel(config.LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)


def execute_agent_verdicts(decision_batch: AgentDecisionBatch):
    """
    EFFECTOR ROUTER: Translates structured decisions returned by the LLM
    into safe operating system actions.
    """
    if not decision_batch.verdict:
        logger.info(" [Agent] No heavy processes require intervention this cycle.")
        return

    logger.info("⚡ Processing %d agent verdict(s)...", len(decision_batch.verdict))

    for judgment in decision_batch.verdict:
        pid = judgment.pid
        name = judgment.process_name
        action = judgment.action
        reason = judgment.reasoning

        logger.info("------------------------------------------------")
        logger.info("📋 Target: %s (PID: %d)", name, pid)
        logger.info("🧠 Brain Reason: %s", reason)
        logger.info("🛠️ Action Recommended: %s", action)

        if action == "ALLOW":
            logger.info("➔ Status: Permitted to run. Skipping intervention.")
            continue

        if action == "MONITOR":
            logger.info("➔ Status: Logged for observation. No actions taken yet.")
            continue

        if action == "TERMINATE":
            if pid <= 0:
                logger.error("➔ [Error] Agent requested termination but provided an invalid PID.")
                continue
            handle_process_termination(pid, name)
            continue

        logger.warning("➔ [Warning] Unsupported action '%s'. Skipping.", action)


def handle_process_termination(pid: int, process_name: str):
    """
    PHYSICAL ACTUATOR: Intervenes directly in the environment by terminating
    the selected process through the OS signal management layer.
    """
    try:
        if not psutil.pid_exists(pid):
            logger.info("➔ Status: Process PID %d closed on its own before execution.", pid)
            return

        proc = psutil.Process(pid)
        actual_name = proc.name()
        if process_name and process_name.lower() not in actual_name.lower() and actual_name.lower() not in process_name.lower():
            logger.warning(
                "➔ [Safety Block] Name mismatch detected! PID %d is running '%s', not '%s'.",
                pid,
                actual_name,
                process_name,
            )
            return

        try:
            current_cpu = proc.cpu_percent(interval=0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.info("➔ Status: Process %s already closed or inaccessible. Skipping.", process_name)
            return

        if config.SAFE_MODE and current_cpu < config.TERMINATION_CPU_CUTOFF:
            logger.info(
                "➔ [Safety Pass] %s cooled down (%.1f%%) below termination cutoff. Skipping.",
                process_name,
                current_cpu,
            )
            return

        if config.SAFE_MODE:
            confirm = input(
                f"\n❓ [SAFE MODE] Allow agent to terminate {process_name} (PID: {pid})? (y/n): "
            )
            if confirm.lower() != "y":
                logger.info("➔ Status: Action manually cancelled by user.")
                return

        logger.info("➔ Actuating: Sending termination signal to PID %d...", pid)
        proc.terminate()
        logger.info("✓ Success: %s has been gracefully terminated.", process_name)

    except psutil.NoSuchProcess:
        logger.info("➔ Status: Process vanished while attempting cleanup.")
    except psutil.AccessDenied:
        logger.error(
            "➔ [Permissions Failure] Access Denied. Cannot kill %s. Run elevated permissions if required.",
            process_name,
        )


if __name__ == "__main__":
    from brain_schema import MitigationAction
    import sys

    current_interpreter = sys.executable
    logger.info("⏳ Launching a temporary background test process...")

    dummy_proc = psutil.Popen([current_interpreter, "-c", "import time; time.sleep(600)"])
    logger.info("📌 Created Dummy Target: Process Name = '%s', PID = %d", dummy_proc.name(), dummy_proc.pid)

    mock_llm_output = AgentDecisionBatch(
        verdict=[
            MitigationAction(
                action="ALLOW",
                pid=0,
                process_name="Chrome Browser",
                reasoning="Process matches standard desktop browser patterns with active user tabs.",
            ),
            MitigationAction(
                action="TERMINATE",
                pid=dummy_proc.pid,
                process_name=dummy_proc.name(),
                reasoning="Process shows background execution with no window focus, likely an orphaned loop.",
            ),
        ]
    )

    execute_agent_verdicts(mock_llm_output)
