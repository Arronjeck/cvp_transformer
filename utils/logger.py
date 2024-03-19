from loguru import logger
import os
import sys

ROTATION_TIME = "02:00"

class Logger:
    def __init__(self, name="translation.log", log_dir="cache/logs", debug=False):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file_path = os.path.join(log_dir, name)

        # Remove default loguru handler
        logger.remove()

        # Add console handler with a specific log level
        level = "DEBUG" if debug else "INFO"
        logger.add(sys.stdout, level=level)
        # Add file handler with a specific log level and timed rotation
        logger.add(log_file_path, rotation=ROTATION_TIME, level="DEBUG")
        self.logger = logger

LOGER = Logger(debug=True).logger

def example():
    LOGER.debug("This is a debug message.")
    LOGER.info("This is an info message.")
    LOGER.warning("This is a warning message.")
    LOGER.error("This is an error message.")

example()