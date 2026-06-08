# Orion-Mon: Start/Stop/Status Service Commands

# Start the agent as a background job
function Start-OrionMon {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    Push-Location $scriptDir
    $env:DRY_RUN_MODE = "false"
    Start-Process python -ArgumentList "main.py" -WindowStyle Minimized -PassThru | Out-Null
    Write-Host "✓ Orion-Mon started"
    Pop-Location
}

# Stop the agent
function Stop-OrionMon {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" } | Stop-Process -Force
    Write-Host "✓ Orion-Mon stopped"
}

# Check status
function Get-OrionMonStatus {
    $proc = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($proc) {
        Write-Host "✓ Orion-Mon is running (PID: $($proc.Id))"
    } else {
        Write-Host "✗ Orion-Mon is not running"
    }
}

# Show help
function Get-OrionMonHelp {
    Write-Host @"
Orion-Mon Service Commands:

  Start-OrionMon      - Start the agent in background
  Stop-OrionMon       - Stop the agent
  Get-OrionMonStatus  - Check if agent is running

Example:
  Start-OrionMon
  Get-OrionMonStatus
  Stop-OrionMon
"@
}

# Default: show help if sourced
Get-OrionMonHelp
