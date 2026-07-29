# Shared

This directory contains common utilities and modules that are used across different parts of the application.

## Files

-   `logger.py`: Provides a `setup_logger` function to ensure consistent, standardized logging across all modules.
-   `sanitizer.py`: Includes helper functions like `sanitize_id` to format data, such as creating valid document IDs from filenames before ingestion.
-   `validator.py`: Contains functions to perform environment and configuration checks, such as verifying that the necessary data stores exist before the application runs.