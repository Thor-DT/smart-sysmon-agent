@echo off
REM Orion-Mon: Windows Service Installer

echo ======================================
echo Orion-Mon Windows Service Installer
echo ======================================

set PROJECT_DIR=%~dp0
set SERVICE_SCRIPT=%PROJECT_DIR%service.py

echo Project Directory: %PROJECT_DIR%

if not exist "%SERVICE_SCRIPT%" (
    echo ✗ Could not find service.py in the project directory.
    goto end
)

echo Installing Orion-Mon service...
python "%SERVICE_SCRIPT%" install
if ERRORLEVEL 1 (
    echo ✗ Service installation failed. Make sure you run this as Administrator and that pywin32 is installed.
    goto end
)

echo.
echo ✓ Orion-Mon service installed.
echo.
echo To start the service:
echo   python "%SERVICE_SCRIPT%" start
 echo To stop the service:
 echo   python "%SERVICE_SCRIPT%" stop
 echo To remove the service:
 echo   python "%SERVICE_SCRIPT%" remove

:end
