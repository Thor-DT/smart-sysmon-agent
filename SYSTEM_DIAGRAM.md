# Orion-Mon: System Architecture

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Windows Operating System                       │
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────────────────┐   │
│  │   All Processes  │         │   Orion-Mon Agent            │   │
│  │                  │         │  (Autonomous Monitor)        │   │
│  │ - Chrome         │         │                              │   │
│  │ - burn.py (CPU↑) │◄────────┤ 1. SENSOR                    │   │
│  │ - VS Code        │         │    └─ scan_and_observe()    │   │
│  │ - Brave          │         │       • CPU, RAM, Disk      │   │
│  │ - ...            │         │       • Filter safelist     │   │
│  └──────────────────┘         │       • Rank by CPU%        │   │
│                                │                              │   │
│                                │ 2. BRAIN                     │   │
│                                │    └─ query_agent_brain()   │   │
│                                │       • Send to Gemini LLM  │   │
│  ┌──────────────────────────┐  │       • JSON schema output  │   │
│  │  Gemini LLM (Cloud)      │◄─┤       • Decisions:         │   │
│  │                          │  │         ALLOW/MONITOR/     │   │
│  │ "You are an autonomous   │  │         TERMINATE          │   │
│  │  system admin. Analyze   │  │                             │   │
│  │  these heavy processes   │  │ 3. EFFECTOR                 │   │
│  │  and decide: ALLOW,      │  │    └─ execute_agent_       │   │
│  │  MONITOR, or TERMINATE"  │  │       verdicts()           │   │
│  └──────────────────────────┘  │       • Safety checks      │   │
│                                │       • User confirmation   │   │
│                                │       • Process termination │   │
│                                │       • Logging             │   │
│                                │                              │   │
│                                └──────────────────────────────┘   │
│                                           ▲                       │
│                                           │                       │
└───────────────────────────────────────────┼───────────────────────┘
                                            │
                                     ┌──────▼──────┐
                                     │ Logs saved  │
                                     │ to disk     │
                                     └─────────────┘
```

## Component Breakdown

### 1. **SENSOR LAYER** (`main.py` → `scan_and_observe()`)
- Continuously monitors system metrics (CPU, RAM, disk)
- Scans all running processes via `psutil`
- Filters out whitelisted apps (Explorer, Chrome, VS Code, etc.)
- Ranks processes by CPU consumption
- Returns top 5 resource hogs

### 2. **BRAIN LAYER** (`agent_brain.py` → `query_agent_brain()`)
- Takes telemetry from sensor
- Sends structured prompt to Google Gemini LLM
- Gemini analyzes process behavior patterns
- Returns decisions in strict JSON format:
  ```json
  {
    "verdict": [
      {
        "action": "TERMINATE",
        "pid": 1234,
        "process_name": "malicious.exe",
        "reasoning": "Sustained 95% CPU with no user interaction"
      }
    ]
  }
  ```

### 3. **EFFECTOR LAYER** (`agent_effector.py` → `execute_agent_verdicts()`)
- Receives decisions from Gemini
- Performs safety checks:
  - Verifies process name hasn't changed
  - Checks if CPU cooled down
  - Requires user confirmation (safe mode)
- Terminates malicious/hung processes gracefully
- Logs all actions

## Data Flow

```
System Metrics ──► Sensor ──► Observations ──► Brain ──► Gemini LLM
                                                           │
                                                           ▼
                                                    Decisions (JSON)
                                                           │
                                                           ▼
Logs ◄─────────── Effector ◄──────────────────────────────┘
       (with action results)
```

## Real-World Scenarios

### Scenario 1: Malicious Cryptominer
```
Detection: unknown.exe consuming 87% CPU
Response: Sends to Gemini → "This is a resource hog with no window"
Action: Terminates after user confirmation
Result: System freed, malware removed
```

### Scenario 2: Hung Application
```
Detection: old_app.exe frozen at 60% CPU for 10 minutes
Response: Sends to Gemini → "Hung process, no activity"
Action: Terminates gracefully
Result: User can restart app properly
```

### Scenario 3: Legitimate High-Load
```
Detection: ffmpeg.exe at 95% CPU
Response: Sends to Gemini → "Video rendering is expected heavy usage"
Action: ALLOW (no termination)
Result: Encoding continues uninterrupted
```

## Safety Architecture

1. **Whitelist**: System-critical processes excluded
2. **Threshold-based**: Only acts on sustained high CPU
3. **Human-in-the-loop**: Requires user confirmation before terminating
4. **Dry-run mode**: Test detection without taking action
5. **Graceful termination**: SIGTERM, not immediate kill
6. **Logging**: Every decision logged to disk

## Deployment

```
┌─────────────────────────────────────────────────────────────┐
│               Windows Scheduled Task (System)               │
│                                                             │
│ Triggers: At system startup                                │
│ Runs as: SYSTEM (elevated privileges)                      │
│ Process: python.exe main.py                                │
│ Output: Logged to logs/orion-mon.log (rotating)           │
└─────────────────────────────────────────────────────────────┘
```
