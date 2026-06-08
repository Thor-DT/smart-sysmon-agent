import os
import sys
import subprocess
import logging

logger = logging.getLogger("OrionMon.Service")


def _is_windows():
    return sys.platform.startswith("win")


if _is_windows():
    import win32event
    import win32service
    import win32serviceutil


    class OrionService(win32serviceutil.ServiceFramework):
        _svc_name_ = "OrionMon"
        _svc_display_name_ = "Orion Monitor Agent"
        _svc_description_ = "LLM-assisted system monitoring and remediation agent."

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.process = None

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            if self.process and self.process.poll() is None:
                try:
                    logger.info("Terminating child agent process (PID %s)", self.process.pid)
                    self.process.terminate()
                except Exception:
                    pass
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self):
            this_dir = os.path.dirname(os.path.abspath(__file__))
            main_py = os.path.join(this_dir, "main.py")
            python_exe = sys.executable or "python"

            logger.info("Starting Orion-Mon agent subprocess: %s %s", python_exe, main_py)
            try:
                self.process = subprocess.Popen(
                    [python_exe, main_py],
                    cwd=this_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
            except Exception as e:
                logger.exception("Failed to start agent subprocess: %s", e)
                return

            self.ReportServiceStatus(win32service.SERVICE_RUNNING)

            while True:
                result = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if result == win32event.WAIT_OBJECT_0:
                    logger.info("Stop signal received. Shutting down child process.")
                    break

                if self.process and self.process.poll() is not None:
                    logger.warning(
                        "Agent subprocess exited unexpectedly with code %s.",
                        self.process.returncode,
                    )
                    break

            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                except Exception:
                    pass


    if __name__ == "__main__":
        # Allow using standard service install/uninstall commands
        win32serviceutil.HandleCommandLine(OrionService)
else:
    if __name__ == "__main__":
        print("service.py is only supported on Windows. Install via python service.py install")
