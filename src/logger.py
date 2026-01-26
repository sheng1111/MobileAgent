#!/usr/bin/env python3
"""
Logger - Unified logging module for MobileAgent

Usage:
    from src.logger import get_logger
    logger = get_logger(__name__)
    logger.info("message")
"""
import logging
import os
import sys
from datetime import datetime

# Log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Daily log file
LOG_FILE = os.path.join(LOG_DIR, f"mobile_agent_{datetime.now():%Y%m%d}.log")


# Get logger instance
def get_logger(name):
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Format: time | level | module | message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler (DEBUG+)
    fileHandler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    # Console handler (INFO+)
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    return logger


# Global logger for direct import
logger = get_logger("MobileAgent")


if __name__ == "__main__":
    testLogger = get_logger("test")
    testLogger.debug("Debug message")
    testLogger.info("Info message")
    testLogger.warning("Warning message")
    testLogger.error("Error message")
    print(f"Log file: {LOG_FILE}")
