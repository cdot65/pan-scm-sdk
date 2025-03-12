# Strata Cloud Manager SDK Example Utilities

This package provides standardized utilities for Palo Alto Networks Strata Cloud Manager SDK example scripts. The utilities help maintain consistency across examples, enhance visual output, and reduce code duplication.

## Features

- **Enhanced Logging:** Color-coded console output using Rich for improved readability
- **Report Generation:** Standardized CSV and PDF report generation with consistent formatting
- **Client Initialization:** Streamlined authentication and client setup for SDK examples
- **Progress Tracking:** Spinners and progress bars for long-running operations
- **Error Handling:** Consistent error handling patterns and fallback mechanisms

## Installation

To use these utilities, ensure you have the required dependencies:

```bash
pip install rich reportlab python-dotenv
```

These dependencies are optional but recommended for the best experience:
- `rich`: Enhanced terminal formatting (fallback to ANSI color codes if not available)
- `reportlab`: PDF report generation (CSV only if not available)
- `python-dotenv`: .env file support for credentials (direct environment variable use if not available)

## Usage

### Logging

```python
from examples.utils.logging import SDKLogger

# Initialize the logger
logger = SDKLogger("example_name")

# Use the various logger methods
logger.section("CONFIGURATION")
logger.operation_start("Loading configuration")
logger.info("Informational message")
logger.success("Operation completed successfully")
logger.warning("Something might be wrong")
logger.error("Something went wrong", error_object)

# Progress tracking for long operations
with logger.create_progress() as progress:
    task = progress.add_task("Processing items...", total=100)
    for i in range(100):
        # Do work
        progress.update(task, advance=1)

# Tables for displaying data
table = logger.create_table("Results", ["ID", "Name", "Status"])
table.add_row("1", "item1", "Complete")
table.add_row("2", "item2", "Pending")
logger.console.print(table)
```

### Client Initialization

```python
from examples.utils.client import ClientInitializer
from examples.utils.logging import SDKLogger
from scm.client import Scm

# Initialize logger and client
logger = SDKLogger("example_name")
client_init = ClientInitializer(logger)
client = client_init.initialize_client(Scm)

# Use the authenticated client for SDK operations
```

### Report Generation

```python
from examples.utils.report import ReportGenerator
from examples.utils.logging import SDKLogger

# Initialize logger and report generator
logger = SDKLogger("example_name")
report_gen = ReportGenerator("objects", logger)

# Prepare report data
headers = ["ID", "Name", "Type", "Value"]
data = [
    ["123", "object1", "IPv4", "10.0.0.1/32"],
    ["456", "object2", "FQDN", "example.com"]
]
summary = {
    "Total Objects": 2,
    "Generation Time": "2023-01-01 12:00:00"
}

# Generate reports
csv_file = report_gen.generate_csv(headers, data, summary)
pdf_file = report_gen.generate_pdf("Objects Report", headers, data, summary)

logger.success(f"Generated CSV report: {csv_file}")
logger.success(f"Generated PDF report: {pdf_file}")
```

## Example Script Template

Here's a minimal example script template using all the utilities:

```python
#!/usr/bin/env python3
"""
Example script for [object type] in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates working with [object type] objects in SCM, including:
- Creating objects
- Listing and filtering objects
- Updating object configurations
- Report generation
"""

import argparse
import datetime
import uuid
import time

# Import shared utilities
from examples.utils.logging import SDKLogger
from examples.utils.client import ClientInitializer
from examples.utils.report import ReportGenerator

# Import SDK modules
from scm.client import Scm
from scm.config.objects import SomeObject
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)

# Initialize logger
logger = SDKLogger("example_name")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Example Script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Add common arguments
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created objects (don't delete them)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip report generation"
    )
    parser.add_argument(
        "--folder",
        type=str,
        default="Texas",
        help="Folder name in SCM to create objects in"
    )

    return parser.parse_args()

def main():
    """Main function to execute the example script."""
    # Parse arguments
    args = parse_arguments()

    # Track execution time
    start_time = time.time()

    try:
        # Initialize client
        client_init = ClientInitializer(logger)
        client = client_init.initialize_client(Scm)
        if not client:
            return

        # Initialize object manager
        logger.section("OBJECT CONFIGURATION")
        logger.operation_start("Initializing object manager")
        objects = SomeObject(client)
        logger.operation_complete("Object manager initialization")

        # Create objects
        created_objects = []
        # [Object creation code]

        # Generate reports
        if created_objects and not args.no_report:
            logger.section("REPORT GENERATION")
            logger.operation_start("Generating reports")

            # Prepare report data
            # [Report data preparation]

            # Generate reports
            report_gen = ReportGenerator("objects", logger)
            csv_file = report_gen.generate_csv(headers, data, summary)
            pdf_file = report_gen.generate_pdf("Objects Report", headers, data, summary)

            if csv_file:
                logger.success(f"Generated CSV report: {csv_file}")
            if pdf_file:
                logger.success(f"Generated PDF report: {pdf_file}")

        # Cleanup
        if not args.skip_cleanup:
            logger.section("CLEANUP")
            logger.operation_start(f"Cleaning up created objects")
            # [Cleanup code]

        # Display execution summary
        end_time = time.time()
        execution_time = end_time - start_time
        logger.section("EXECUTION SUMMARY")
        logger.success("Example script completed successfully")
        logger.info(f"Total execution time: {execution_time:.2f} seconds")

    except AuthenticationError as e:
        logger.error("Authentication failed", e)
    except KeyboardInterrupt:
        logger.warning("Script execution interrupted by user")
    except Exception as e:
        logger.error("Unexpected error", e)
        import traceback
        logger.info(f"Stack trace: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
```

## Contributing

When creating new example scripts, please use these utilities to maintain consistency across the SDK example scripts.

## Dependencies

- Rich: https://github.com/Textualize/rich
- ReportLab: https://www.reportlab.com/
- python-dotenv: https://github.com/theskumar/python-dotenv
