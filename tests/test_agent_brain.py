from unittest.mock import MagicMock, patch

import agent_brain
from brain_schema import AgentDecisionBatch, MitigationAction


def test_query_agent_brain_parses_response_schema():
    mock_decision = AgentDecisionBatch(
        verdict=[
            MitigationAction(
                action="ALLOW",
                pid=0,
                process_name="dummy.exe",
                reasoning="No issue detected.",
            )
        ]
    )
    mock_response = MagicMock(parsed=mock_decision)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("agent_brain.genai.Client", return_value=mock_client):
        metrics = {"global_cpu": 25.0, "global_ram": 30.0, "disk_free_gb": 100.0}
        processes = [
            {"pid": 1, "name": "dummy.exe", "cpu_percent": 50.0, "memory_percent": 1.0}
        ]

        result = agent_brain.query_agent_brain(metrics, processes)

        assert result == mock_decision
        mock_client.models.generate_content.assert_called_once()

