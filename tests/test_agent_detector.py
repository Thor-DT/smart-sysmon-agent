from agent_detector import local_heuristic, should_escalate


def test_local_heuristic_cpu_only():
    enriched = [
        {"pid": 1, "cpu_percent": 80.0, "write_bytes": 0, "net_endpoints": [], "children": [], "ppid": 1}
    ]
    scores = local_heuristic(enriched, {})
    assert 0.3 < scores[1] <= 1.0


def test_should_escalate():
    scores = {1: 0.7, 2: 0.2}
    assert should_escalate(scores, threshold=0.6) is True
    assert should_escalate({1: 0.5}, threshold=0.6) is False
