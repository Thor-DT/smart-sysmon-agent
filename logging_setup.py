import logging.handlers
import os
import sys

# Add this to main.py after creating the logger
def setup_file_logging():
    """Configure file-based logging with rotation."""
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "orion-mon.log")
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    ))
    
    logger = logging.getLogger("OrionMon")
    logger.addHandler(file_handler)
    
    return log_file
