# scm/utils/logging.py

import logging
import sys


def setup_logger(name: str, log_level: int = logging.ERROR) -> logging.Logger:
    """
    Set up and return a configured logger with the given name.

    This function creates a logger with the specified level, adds a console handler,
    and sets a formatter for consistent log message formatting.

    Args:
        name (str): The name to be assigned to the logger.
        log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).

    Returns:
        logger (logging.Logger): A configured logger instance.
    """

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid adding multiple handlers if they already exist
    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(log_level)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(ch)

    return logger
