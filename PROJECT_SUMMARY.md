# Orion-Mon: Project Assignment Summary

**Course**: Operating Systems  
**Submitted by**: [Your Name]  
**Date**: June 8, 2026  
**GitHub**: [Your GitHub URL]  

## Executive Summary

Orion-Mon is an autonomous system administration agent that combines real-time process monitoring with AI-powered decision-making to detect and safely eliminate malicious/hung processes on Windows systems without human intervention.

## Problem Statement

### Current State
- Users manually detect performance issues by opening Task Manager
- No intelligent analysis of process behavior
- Cryptominers and malware run silently in the background
- Hung applications block user workflows

### Proposed Solution
Deploy an **autonomous agent** that:
1. **Observes** system metrics in real-time (CPU, RAM, disk)
2. **Thinks** using AI/LLM to analyze process behavior
3. **Acts** by safely terminating suspicious processes
4. **Logs** all decisions for audit trails

## Technical Architecture

### Three-Layer Design

```
┌─────────────────────────────┐
│    EFFECTOR (Action)        │  Termination, logging, safety checks
├─────────────────────────────┤
│     BRAIN (Decision)        │  Google Gemini LLM analysis
├─────────────────────────────┤
│     SENSOR (Observation)    │  Process monitoring, metrics collection
└─────────────────────────────┘
```

### Technology Stack
- **Language**: Python 3.10+
- **Process Monitoring**: psutil
- **AI/LLM**: Google Gemini 2.5 Flash API
- **Data Schema**: Pydantic
- **Logging**: Python logging with rotation
- **Deployment**: Windows Scheduled Tasks
- **Testing**: pytest

## Key Features

### 1. Intelligent Detection
- Analyzes CPU usage patterns
- Filters legitimate high-load workloads (rendering, compilation)
- Identifies orphaned/hung processes

### 2. Safe Termination
```python
✓ Verify process name matches intent
✓ Check if CPU cooled down
✓ Require user confirmation (safe mode)
✓ Graceful SIGTERM (not immediate kill)
✓ Log all actions with reasoning
```

### 3. Autonomous Operation
- Runs as Windows service at boot
- Configurable polling interval (default: 30s)
- Dry-run mode for testing without action
- Dry-run mode for AI analysis without API calls

### 4. Production-Ready
- Persistent logging with automatic rotation
- Environment-based configuration
- Error handling and recovery
- Unit tests with 100% pass rate

## Real-World Scenarios Handled

### Scenario 1: Cryptominer Detection
```
Input:  unknown.exe consuming 87% CPU with no window
Output: Gemini decides "TERMINATE - resource hog, no user"
Action: Process safely terminated, system freed
```

### Scenario 2: Hung Application
```
Input:  old_app.exe frozen at 60% CPU for minutes
Output: Gemini decides "TERMINATE - hung process"
Action: User confirms, app terminated, can be restarted
```

### Scenario 3: Legitimate Workload
```
Input:  ffmpeg.exe at 95% CPU (video encoding)
Output: Gemini decides "ALLOW - expected heavy use"
Action: Process left alone, encoding continues
```

## Academic Relevance (OS Concepts)

This project demonstrates:
1. **Process Management**: Creating, monitoring, and terminating processes
2. **System Resource Monitoring**: CPU, memory, disk usage tracking
3. **Priority & Scheduling**: Identifying resource hogs vs. background services
4. **Operating System APIs**: Windows process APIs via psutil
5. **Security & Safety**: Whitelisting, permission checks, audit logging
6. **Autonomous Systems**: Agent-based decision making
7. **Human-in-the-Loop**: Balancing automation with user control

## Deployment

### Quick Start
```bash
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Test (dry-run)
$env:DRY_RUN_MODE = "true"
python main.py

# Deploy as service (run as Administrator)
.\install_service.bat
```

### Testing
```bash
pytest  # 100% pass rate
python burn.py  # Generate CPU spike for testing
```

## Limitations & Future Work

### Current Limitations
- Free-tier Gemini API has 20 requests/day quota
- Windows-only (could extend to Linux/macOS)
- Requires user confirmation in safe mode

### Future Enhancements
1. **Process History**: Track behavior over time, only act on sustained issues
2. **Machine Learning**: Custom classifier for process behavior
3. **Network Monitoring**: Detect data exfiltration
4. **Automatic Responses**: Remove confirmation requirement for trusted scenarios
5. **Web Dashboard**: Real-time monitoring UI
6. **Cross-Platform**: Support Linux and macOS

## Files & Structure

```
smart-sysmon-agent/
├── main.py                 # Main entry point
├── agent_brain.py          # Gemini LLM integration
├── agent_effector.py       # Process termination logic
├── brain_schema.py         # Pydantic models
├── config.py               # Configuration
├── burn.py                 # Test utility (CPU spike generator)
├── tests/                  # Unit tests
├── logs/                   # Persistent logs
├── README.md               # Documentation
├── SYSTEM_DIAGRAM.md       # Architecture
├── requirements.txt        # Dependencies
├── install_service.bat     # Windows service installer
└── service.ps1             # Service management
```

## Conclusion

Orion-Mon demonstrates the power of combining traditional OS-level process management with modern AI/LLM capabilities. The result is an autonomous agent that can detect and respond to system threats with minimal human intervention, while maintaining safety through whitelisting, confirmation prompts, and comprehensive logging.

This project is **production-ready** and can be deployed as a Windows service on any Windows 10/11 machine.

---

**GitHub Repository**: [INSERT YOUR GITHUB URL]  
**Demo Video**: [INSERT ECAMPUS VIDEO LINK]
