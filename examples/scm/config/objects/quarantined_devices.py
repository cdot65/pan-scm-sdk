#!/usr/bin/env python3
"""Comprehensive examples of working with Quarantined Devices objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Quarantined Devices operations commonly
used in enterprise networks, including:

1. Quarantined Devices Operations:
   - Creating quarantined device entries
   - Listing and filtering quarantined devices
   - Managing device quarantine status
   - Bulk operations and error handling

2. Operational examples:
   - Creating quarantined device entries
   - Searching and filtering quarantined devices
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with quarantined devices details
- Optional cleanup skipping with SKIP_CLEANUP=true environment variable
- Progress tracking and execution statistics

Before running this example:
1. Replace the authentication credentials with your own or use a .env file:
   ```
   SCM_CLIENT_ID=your_client_id
   SCM_CLIENT_SECRET=your_client_secret
   SCM_TSG_ID=your_tsg_id
   SCM_LOG_LEVEL=DEBUG  # Optional
   ```

2. Optional environment variables:
   - SKIP_CLEANUP=true: Set this to preserve created quarantined device entries for manual inspection
"""

import argparse
import csv
import datetime
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from scm.client import Scm
from scm.config.objects import QuarantinedDevices
from scm.exceptions import (
    InvalidObjectError,
    AuthenticationError,
    MissingQueryParameterError,
)

# Set up logging with color support and improved formatting
# Define ANSI color codes for colorized output
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BRIGHT_GREEN": "\033[92m",
    "BRIGHT_YELLOW": "\033[93m",
    "BRIGHT_BLUE": "\033[94m",
    "BRIGHT_MAGENTA": "\033[95m",
    "BRIGHT_CYAN": "\033[96m",
}

# Configure logging format and level
log_format = "%(asctime)s %(levelname)-8s %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=log_format, datefmt=date_format)
logger = logging.getLogger("quarantined_devices_example")


# Helper function for formatted section headers
def log_section(title):
    """Log a section header with clear visual separation."""
    separator = "=" * 80
    # Ensure section headers always start with a blank line
    logger.info("")
    logger.info(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}{separator}{COLORS['RESET']}")
    logger.info(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}   {title.upper()}{COLORS['RESET']}")
    logger.info(f"{COLORS['BOLD']}{COLORS['BRIGHT_CYAN']}{separator}{COLORS['RESET']}")


# Helper function for operation start
def log_operation_start(operation):
    """Log the start of an operation with clear visual indicator."""
    logger.info(f"{COLORS['BOLD']}{COLORS['BRIGHT_GREEN']}▶ STARTING: {operation}{COLORS['RESET']}")


# Helper function for operation completion
def log_operation_complete(operation, details=None):
    """Log the completion of an operation with success status."""
    if details:
        logger.info(
            f"{COLORS['BOLD']}{COLORS['GREEN']}✓ COMPLETED: {operation} - {details}{COLORS['RESET']}"
        )
    else:
        logger.info(f"{COLORS['BOLD']}{COLORS['GREEN']}✓ COMPLETED: {operation}{COLORS['RESET']}")


# Helper function for operation warnings
def log_warning(message):
    """Log a warning message with clear visual indicator."""
    logger.warning(f"{COLORS['BOLD']}{COLORS['YELLOW']}⚠ WARNING: {message}{COLORS['RESET']}")


# Helper function for operation errors
def log_error(message, error=None):
    """Log an error message with clear visual indicator."""
    if error:
        logger.error(
            f"{COLORS['BOLD']}{COLORS['RED']}✘ ERROR: {message} - {error}{COLORS['RESET']}"
        )
    else:
        logger.error(f"{COLORS['BOLD']}{COLORS['RED']}✘ ERROR: {message}{COLORS['RESET']}")


# Helper function for important information
def log_info(message):
    """Log an informational message."""
    logger.info(f"{COLORS['BRIGHT_BLUE']}{message}{COLORS['RESET']}")


# Helper function for success messages
def log_success(message):
    """Log a success message."""
    logger.info(f"{COLORS['BRIGHT_GREEN']}✓ {message}{COLORS['RESET']}")


def initialize_client():
    """Initialize the SCM client using credentials from environment variables or .env file.

    This function will:
    1. Load credentials from .env file (first in current directory, then in script directory)
    2. Validate required credentials (client_id, client_secret, tsg_id)
    3. Initialize the SCM client with appropriate credentials

    Returns:
        Scm: An authenticated SCM client instance ready for API calls

    Raises:
        AuthenticationError: If authentication fails due to invalid credentials
    """
    log_section("AUTHENTICATION & INITIALIZATION")
    log_operation_start("Loading credentials and initializing client")

    # Load environment variables from .env file
    # First try to load from current directory
    env_path = Path(".") / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        log_success(f"Loaded environment variables from {env_path.absolute()}")
    else:
        # If not found, try the script's directory
        script_dir = Path(__file__).parent.absolute()
        env_path = script_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            log_success(f"Loaded environment variables from {env_path}")
        else:
            log_warning("No .env file found in current directory or script directory")
            log_info("Searched locations:")
            log_info(f"  - {Path('.').absolute()}/.env")
            log_info(f"  - {script_dir}/.env")
            log_info("Using default or environment credentials instead")

    # Get credentials from environment variables with fallbacks
    client_id = os.environ.get("SCM_CLIENT_ID", None)
    client_secret = os.environ.get("SCM_CLIENT_SECRET", None)
    tsg_id = os.environ.get("SCM_TSG_ID", None)
    log_level = os.environ.get("SCM_LOG_LEVEL", "DEBUG")

    # Validate required credentials
    if not all([client_id, client_secret, tsg_id]):
        missing = []
        if not client_id:
            missing.append("SCM_CLIENT_ID")
        if not client_secret:
            missing.append("SCM_CLIENT_SECRET")
        if not tsg_id:
            missing.append("SCM_TSG_ID")

        log_error(f"Missing required credentials: {', '.join(missing)}")
        log_info("Please provide credentials in .env file or environment variables")
        log_info("Example .env file format:")
        log_info("  SCM_CLIENT_ID=your_client_id")
        log_info("  SCM_CLIENT_SECRET=your_client_secret")
        log_info("  SCM_TSG_ID=your_tsg_id")
        log_info("  SCM_LOG_LEVEL=DEBUG")
    else:
        log_success("All required credentials found")

    log_operation_start("Creating SCM client")

    # Create the client
    client = Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=tsg_id,
        log_level=log_level,
    )

    log_operation_complete(
        "SCM client initialization",
        f"TSG ID: {tsg_id[:4]}{'*' * (len(tsg_id) - 8) if tsg_id else '****'}{tsg_id[-4:] if tsg_id else '****'}",
    )
    return client


def create_quarantined_device(devices, host_id=None, serial_number=None):
    """Create a quarantined device entry.

    This function demonstrates creating a quarantined device entry with the
    specified host ID and optional serial number.

    Args:
        devices: The QuarantinedDevices manager instance
        host_id: The host ID for the device (default: None, generates a random ID)
        serial_number: The serial number for the device (default: None)

    Returns:
        QuarantinedDevicesResponseModel: The created device, or None if creation failed
    """
    log_operation_start("Creating quarantined device entry")

    # Generate a unique host ID if not provided
    if not host_id:
        host_id = f"host-{uuid.uuid4().hex[:8]}"

    log_info(f"Host ID: {host_id}")

    # Create the device configuration
    device_config = {
        "host_id": host_id,
    }

    # Add serial number if provided
    if serial_number:
        device_config["serial_number"] = serial_number
        log_info(f"Serial Number: {serial_number}")

    log_info("Configuration details:")
    log_info(f"  - Host ID: {device_config['host_id']}")
    if serial_number:
        log_info(f"  - Serial Number: {serial_number}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_device = devices.create(device_config)
        log_success(f"Created quarantined device: {new_device.host_id}")

        if hasattr(new_device, "serial_number") and new_device.serial_number:
            log_info(f"  - Serial Number: {new_device.serial_number}")

        log_operation_complete("Quarantined device creation", f"Host ID: {new_device.host_id}")
        return new_device
    except InvalidObjectError as e:
        log_error("Invalid device data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating quarantined device", str(e))

    return None


def create_quarantined_device_with_serial(devices):
    """Create a quarantined device entry with a serial number.

    This function demonstrates creating a quarantined device entry with both
    a host ID and a serial number.

    Args:
        devices: The QuarantinedDevices manager instance

    Returns:
        QuarantinedDevicesResponseModel: The created device, or None if creation failed
    """
    log_operation_start("Creating quarantined device with serial number")

    # Generate a unique host ID and serial number
    host_id = f"host-{uuid.uuid4().hex[:8]}"
    serial_number = f"PA-{uuid.uuid4().hex[:8]}"

    return create_quarantined_device(devices, host_id, serial_number)


def list_and_filter_devices(devices, host_id=None, serial_number=None):
    """List and filter quarantined devices.

    This function demonstrates how to:
    1. List all quarantined devices
    2. Filter devices by host ID or serial number
    3. Display detailed information about each device

    Args:
        devices: The QuarantinedDevices manager instance
        host_id: Optional host ID filter
        serial_number: Optional serial number filter

    Returns:
        list: All retrieved quarantined devices
    """
    logger.info("Listing and filtering quarantined devices")

    # Determine which filters to apply
    filter_desc = "all"
    if host_id and serial_number:
        filter_desc = f"host ID '{host_id}' and serial number '{serial_number}'"
    elif host_id:
        filter_desc = f"host ID '{host_id}'"
    elif serial_number:
        filter_desc = f"serial number '{serial_number}'"

    log_info(f"Fetching {filter_desc} quarantined devices...")

    try:
        # List devices with optional filters
        all_devices = devices.list(host_id=host_id, serial_number=serial_number)
        logger.info(f"Found {len(all_devices)} quarantined devices matching {filter_desc}")

        # Print details of devices
        logger.info("\nDetails of quarantined devices:")
        for device in all_devices:
            logger.info(f"  - Host ID: {device.host_id}")
            if hasattr(device, "serial_number") and device.serial_number:
                logger.info(f"    Serial Number: {device.serial_number}")
            logger.info("")

        return all_devices

    except Exception as e:
        log_error("Error listing quarantined devices", str(e))
        return []


def cleanup_quarantined_devices(devices, host_ids):
    """Delete the quarantined device entries created in this example.

    Args:
        devices: The QuarantinedDevices manager instance
        host_ids: List of host IDs to delete
    """
    logger.info("Cleaning up quarantined devices")

    for host_id in host_ids:
        try:
            devices.delete(host_id)
            logger.info(f"Deleted quarantined device with host ID: {host_id}")
        except MissingQueryParameterError as e:
            logger.error(f"Missing host ID: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting quarantined device: {str(e)}")


def create_bulk_devices(devices, count=3):
    """Create multiple quarantined device entries in a batch.

    This function demonstrates creating multiple quarantined device entries in a batch,
    which is useful for setting up multiple entries at once.

    Args:
        devices: The QuarantinedDevices manager instance
        count: Number of devices to create (default: 3)

    Returns:
        list: List of host IDs of created devices, or empty list if creation failed
    """
    logger.info(f"Creating a batch of {count} quarantined devices")

    created_devices = []

    # Create multiple devices
    for i in range(count):
        host_id = f"bulk-host-{i + 1}-{uuid.uuid4().hex[:6]}"
        serial_number = f"PA-BULK-{i + 1}-{uuid.uuid4().hex[:6]}"

        device_config = {"host_id": host_id, "serial_number": serial_number}

        try:
            new_device = devices.create(device_config)
            logger.info(
                f"Created quarantined device: {new_device.host_id} with serial number: {new_device.serial_number}"
            )
            created_devices.append(new_device.host_id)
        except Exception as e:
            logger.error(f"Error creating device {host_id}: {str(e)}")

    return created_devices


def generate_devices_report(devices, host_ids, execution_time):
    """Generate a comprehensive CSV report of all quarantined devices created by the script.

    This function fetches detailed information about each device and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    Args:
        devices: The QuarantinedDevices manager instance used to fetch device details
        host_ids: List of host IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"quarantined_devices_report_{timestamp}.csv"

    # Define CSV headers
    headers = ["Host ID", "Serial Number", "Report Generation Time"]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each device
    device_data = []
    for idx, host_id in enumerate(host_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(host_ids) - 1:
            log_info(f"Processing device {idx + 1} of {len(host_ids)}")

        try:
            # Get the devices with this host ID
            device_list = devices.list(host_id=host_id)

            # Check if we found any devices
            if device_list:
                device = device_list[0]  # Take the first match

                # Add device data
                device_data.append(
                    [
                        device.host_id,
                        device.serial_number
                        if hasattr(device, "serial_number") and device.serial_number
                        else "N/A",
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    ]
                )

                successful_fetches += 1
            else:
                # Add minimal info for devices that couldn't be retrieved
                device_data.append(
                    [host_id, "Not Found", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                )
                failed_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for host ID {host_id}", str(e))
            # Add minimal info for devices that couldn't be retrieved
            device_data.append(
                [host_id, "ERROR", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )
            failed_fetches += 1

    try:
        # Write to CSV file
        with open(report_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(device_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Devices Processed", len(host_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(
                ["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )

        return report_file

    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"quarantined_devices_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(device_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """Parse command-line arguments for the quarantined devices example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created devices
    - Which operations to perform
    - Whether to generate a CSV report

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Quarantined Devices Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created quarantined device entries (don't delete them)",
    )

    # Operation types
    operation_group = parser.add_argument_group("Operation Selection")
    operation_group.add_argument(
        "--create", action="store_true", help="Create simple quarantined device examples"
    )
    operation_group.add_argument(
        "--create-with-serial",
        action="store_true",
        help="Create quarantined device examples with serial numbers",
    )
    operation_group.add_argument(
        "--bulk", action="store_true", help="Create bulk quarantined device examples"
    )
    operation_group.add_argument("--list", action="store_true", help="List quarantined devices")
    operation_group.add_argument(
        "--all", action="store_true", help="Perform all operations (default behavior)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Bulk count
    parser.add_argument(
        "--bulk-count", type=int, default=3, help="Number of bulk devices to create"
    )

    return parser.parse_args()


def main():
    """Execute the comprehensive set of quarantined devices examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of quarantined device entries
    4. List and filter quarantined devices to show search functionality
    5. Generate a detailed CSV report of all created devices
    6. Clean up created devices (unless skip_cleanup is enabled)
    7. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created devices (don't delete them)
        --create: Create simple quarantined device examples
        --create-with-serial: Create quarantined device examples with serial numbers
        --bulk: Create bulk quarantined device examples
        --list: List quarantined devices
        --all: Perform all operations (default behavior)
        --no-report: Skip CSV report generation
        --bulk-count: Number of bulk devices to create (default: 3)

    Environment Variables:
        SCM_CLIENT_ID: Client ID for SCM authentication (required)
        SCM_CLIENT_SECRET: Client secret for SCM authentication (required)
        SCM_TSG_ID: Tenant Service Group ID for SCM authentication (required)
        SCM_LOG_LEVEL: Logging level, defaults to DEBUG (optional)
        SKIP_CLEANUP: Alternative way to preserve created devices (optional)

    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Track execution time for reporting
    start_time = __import__("time").time()
    object_count = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine which operations to perform
    # If no specific operations are specified, perform all (default behavior)
    perform_all = args.all or not (args.create or args.create_with_serial or args.bulk or args.list)

    try:
        # Initialize client
        client = initialize_client()

        # Initialize QuarantinedDevices object
        log_section("QUARANTINED DEVICES CONFIGURATION")
        log_operation_start("Initializing QuarantinedDevices object manager")
        devices = QuarantinedDevices(client)
        log_operation_complete("QuarantinedDevices object manager initialization")

        # Create various quarantined device entries
        created_devices = []

        # Simple quarantined device
        if perform_all or args.create:
            log_section("SIMPLE QUARANTINED DEVICE")
            log_info("Creating simple quarantined device entry")

            # Create a simple quarantined device
            simple_device = create_quarantined_device(devices)
            if simple_device:
                created_devices.append(simple_device.host_id)
                object_count += 1

            log_success(f"Created {len(created_devices)} quarantined devices so far")

        # Quarantined device with serial number
        if perform_all or args.create_with_serial:
            log_section("QUARANTINED DEVICE WITH SERIAL NUMBER")
            log_info("Creating quarantined device with serial number")

            # Create a quarantined device with serial number
            serial_device = create_quarantined_device_with_serial(devices)
            if serial_device:
                created_devices.append(serial_device.host_id)
                object_count += 1

            log_success("Created quarantined device with serial number")

        # Bulk quarantined devices
        if perform_all or args.bulk:
            log_section("BULK QUARANTINED DEVICES")
            log_info(f"Creating {args.bulk_count} quarantined devices in bulk")

            # Create bulk quarantined devices
            bulk_device_ids = create_bulk_devices(devices, args.bulk_count)
            if bulk_device_ids:
                created_devices.extend(bulk_device_ids)
                object_count += len(bulk_device_ids)
                log_success(f"Created {len(bulk_device_ids)} bulk quarantined devices")

        # List and filter quarantined devices
        if perform_all or args.list or len(created_devices) > 0:
            log_section("LISTING AND FILTERING QUARANTINED DEVICES")
            log_info("Demonstrating how to list and filter quarantined devices")

            # First list all devices
            list_and_filter_devices(devices)

            # If we've created devices, filter by first created device as an example
            if created_devices:
                log_info("\nFiltering by host ID:")
                list_and_filter_devices(devices, host_id=created_devices[0])

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are devices to report and report generation is not disabled
        if created_devices and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating quarantined devices CSV report")
            report_file = generate_devices_report(devices, created_devices, execution_time_so_far)
            if report_file:
                log_success(f"Generated quarantined devices report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_devices)} quarantined devices created"
                )
            else:
                log_error("Failed to generate quarantined devices report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No quarantined devices were created, skipping report generation")

        # Clean up the created devices, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_devices)} quarantined devices"
            )
            log_info(
                "To clean up these devices, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            log_operation_start(f"Cleaning up {len(created_devices)} created quarantined devices")
            cleanup_quarantined_devices(devices, created_devices)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total quarantined devices created: {object_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(f"Average time per device: {execution_time / max(object_count, 1):.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some quarantined devices may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
