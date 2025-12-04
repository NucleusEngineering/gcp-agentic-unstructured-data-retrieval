import logging
import os

def setup_logger(name):
    """
    Sets up a centralized logger with a specific name.

    Args:
        name (str): The name of the logger, typically __name__ of the module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())

    # Ensure handlers are not duplicated if logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger