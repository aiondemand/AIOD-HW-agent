# src/hw_agent/utils/logger.py

import logging
import os

def get_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        logger.setLevel(log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
