# Orion-Mon: LLM-Powered Autonomous System Monitor

**An AI-driven Windows process monitor that detects and safely terminates resource hogs, malware, and hung applications without human intervention.**

> **Status**: Production-ready | **License**: MIT | **Python**: 3.10+ | **OS**: Windows 10/11

## Real-World Problem It Solves

### The Problem
- **Cryptominers & Malware**: Silent resource hogs running in the background
- **Hung Applications**: Apps freeze but refuse to close, consuming 100% CPU
- **Performance Degradation**: Sudden system slowdown with no clear culprit
- **Manual Detection**: Users must open Task Manager, find the process, and terminate it manually
- **No Intelligence**: Traditional task managers don't understand *why* a process is suspicious

### The Solution
Orion-Mon uses **Google Gemini LLM** to intelligently analyze process behavior:
- ✅ Detects sustained high CPU usage
- ✅ Filters legitimate heavy workloads (video rendering, compilation, browsing)
- ✅ Identifies rogue/orphaned processes
- ✅ Safely terminates malicious/hung processes with user confirmation
- ✅ Runs autonomously as a Windows service
- ✅ Logs all decisions for audit trails

## Features

- **AI-Powered Analysis**: Uses Google Gemini to classify suspicious processes
- **Safe Termination**: Graceful SIGTERM with safety checks before killing
- **Process Whitelisting**: Protects system-critical apps (Explorer, services, etc.)
- **Dry-Run Mode**: Test detection without taking action
- **Human-in-Loop**: Asks for confirmation before terminating (safe mode)
- **Persistent Logging**: Rotating logs with 10 MB per file × 5 backups
- **Windows Service**: Auto-start at system boot with elevated privileges
- **Real-Time Monitoring**: Configurable polling intervals (default: 30 seconds)

## Setup

1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Set your Gemini API key:
   ```powershell
   setx GEMINI_API_KEY "your_key_here"
   ```

## Usage

Run the monitor:

```powershell
python main.py
```

### Safe-mode options

- `SAFE_MODE=true` (default): prompts before terminating processes
- `DRY_RUN_MODE=true`: scans and logs telemetry without calling Gemini or terminating anything

### Configuration

The agent reads these environment variables:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `POLL_INTERVAL`
- `MONITOR_CPU_THRESHOLD`
- `TOP_CANDIDATES`
- `SAFE_MODE`
- `DRY_RUN_MODE`
- `LOG_LEVEL`

## Development

Run the test suite with:

```powershell
pytest
```

## Deployment

### Windows Service (Auto-start)

Run as Administrator:

```powershell
.\install_service.bat
```

This creates a Windows scheduled task that runs at startup with system privileges.

**To start/stop the service manually:**

```powershell
# Source the service helpers
. .\service.ps1

# Start
Start-OrionMon

# Check status
Get-OrionMonStatus

# Stop
Stop-OrionMon
```

### Logs

All activity is logged to `logs/orion-mon.log` with automatic rotation (10 MB per file, keeps 5 backups).

## Safety

- The process safelist guards against killing common desktop/system apps.
- In safe mode, the agent asks for approval before terminating a process.
- Use `DRY_RUN_MODE=true` to validate behavior before allowing remediation.
- Always test with `burn.py` first to ensure detection works as expected.
- Check logs frequently during the first week of deployment.
