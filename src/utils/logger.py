import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a logger with a standard format and console output.

    Args:
        name: The name for the logger, typically __name__.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a handler that writes to the console
    stream_handler = logging.StreamHandler(sys.stdout)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler.setFormatter(formatter)

    # Add the handler to the logger
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(stream_handler)

    return logger
