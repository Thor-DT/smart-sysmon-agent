from unittest.mock import MagicMock, patch

import main


def make_proc(pid, name, cpu, mem):
    proc = MagicMock()
    proc.info = {"pid": pid, "name": name}
    proc.cpu_percent.return_value = cpu
    proc.memory_percent.return_value = mem
    return proc


@patch("main.time.sleep", return_value=None)
@patch("main.psutil.cpu_percent", return_value=10.0)
@patch("main.psutil.virtual_memory")
@patch("main.psutil.disk_usage")
@patch("main.psutil.process_iter")
def test_scan_and_observe_filters_safelist_and_returns_top_candidates(
    mock_process_iter, mock_disk_usage, mock_virtual_memory, mock_cpu_percent, mock_sleep
):
    mock_virtual_memory.return_value = MagicMock(percent=40.0)
    mock_disk_usage.return_value = MagicMock(free=100 * (1024**3))

    safe_proc = make_proc(101, "chrome.exe", 60.0, 5.0)
    bad_proc = make_proc(202, "suspicious.exe", 55.0, 12.0)
    mock_process_iter.return_value = [safe_proc, bad_proc]

    metrics, candidates = main.scan_and_observe()

    assert metrics["global_cpu"] == 10.0
    assert metrics["global_ram"] == 40.0
    assert len(candidates) == 1
    assert candidates[0]["pid"] == 202
    assert candidates[0]["name"] == "suspicious.exe"
    assert candidates[0]["cpu_percent"] == 55.0
