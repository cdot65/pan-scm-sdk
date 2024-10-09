import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Set up and return a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(ch)

    return logger
