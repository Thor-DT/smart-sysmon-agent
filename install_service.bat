@echo off
REM Orion-Mon: Windows Service Setup Script
REM This script creates a scheduled task to run the agent at startup

echo ======================================
echo Orion-Mon Service Setup
echo ======================================

REM Get the full path to the project directory
set PROJECT_DIR=%~dp0
echo Project Directory: %PROJECT_DIR%

REM Create the scheduled task
echo Creating scheduled task...
powershell -NoProfile -Command ^
  "Register-ScheduledTask -TaskName 'OrionMon' -Action (New-ScheduledTaskAction -Execute 'python' -Argument '%PROJECT_DIR%main.py' -WorkingDirectory '%PROJECT_DIR%') -Trigger (New-ScheduledTaskTrigger -AtStartup) -Principal (New-ScheduledTaskPrincipal -UserId SYSTEM -LogonType ServiceAccount -RunLevel Highest) -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries) -Force"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Task created successfully!
    echo.
    echo To start the agent now:
    echo   schtasks /run /tn OrionMon
    echo.
    echo To stop the agent:
    echo   taskkill /f /im python.exe /fi "CMDLINE*main.py"
    echo.
    echo To remove the task:
    echo   Unregister-ScheduledTask -TaskName OrionMon -Confirm:$false
) else (
    echo ✗ Failed to create task. Make sure you run this as Administrator.
)

pause
