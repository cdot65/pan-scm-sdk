# scm/utils/logging.py

import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """
    Set up and return a configured logger with the given name.

    This function creates a logger with DEBUG level, adds a console handler,
    and sets a formatter for consistent log message formatting.

    Attributes:
        name (str): The name to be assigned to the logger.

    Return:
        logger (logging.Logger): A configured logger instance.
    """

    """Set up and return a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(ch)

    return logger
