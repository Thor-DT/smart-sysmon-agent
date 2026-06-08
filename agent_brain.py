import json
import logging
from google import genai
from google.genai import types

import config
from brain_schema import AgentDecisionBatch

logger = logging.getLogger("OrionMon.Brain")
logger.setLevel(config.LOG_LEVEL)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)


def query_agent_brain(system_metrics: dict, heavy_processes: list) -> AgentDecisionBatch:
    """
    Formulates a telemetry snapshot prompt and sends it to Gemini,
    enforcing a strict JSON response schema.
    """
    client = genai.Client()

    system_instruction = (
        "You are the Core Cognitive Engine of Orion-Mon, an autonomous system admin agent. "
        "Your task is to analyze system telemetry and flag malicious, hung, or rogue processes. "
        "Respond only in the requested JSON format."
    )

    prompt = f"""
[SYSTEM TELEMETRY SNAPSHOT]
Global CPU Utilization: {system_metrics['global_cpu']}%
Global RAM Utilization: {system_metrics['global_ram']}%
Available Storage: {system_metrics['disk_free_gb']} GB remaining

[HEAVY PROCESS CANDIDATES]
The following processes have exceeded nominal resource limits and require evaluation:
{json.dumps(heavy_processes, indent=2)}

You must evaluate each target and choose one of these actions:
- ALLOW
- MONITOR
- TERMINATE

Return a valid JSON object matching the AgentDecisionBatch schema:
{{"verdict":[{{"action":"...", "pid":0, "process_name":"...", "reasoning":"..."}}]}}
"""

    logger.debug("Sending telemetry payload to Gemini Brain.")
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=AgentDecisionBatch,
        ),
    )

    logger.info("Gemini returned %d verdict(s).", len(response.parsed.verdict))
    return response.parsed
