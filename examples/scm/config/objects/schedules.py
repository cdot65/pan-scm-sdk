#!/usr/bin/env python3
"""
Example script to manage Schedule objects in Strata Cloud Manager.

This script demonstrates how to:
- Create different types of schedules (daily, weekly, non-recurring)
- Update existing schedules
- List schedules with various filters
- Generate CSV reports of schedules
- Delete schedules
"""

import argparse
import csv
import datetime
import logging
import os
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv

from scm.client import Scm
from scm.config.objects import schedules
from scm.exceptions import (
    AuthenticationError,
    InvalidObjectError,
    NotFoundError,
    NameNotUniqueError,
)
from scm.models.objects import ScheduleUpdateModel

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
logger = logging.getLogger("schedules_example")


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
    logger.info(
        f"{COLORS['BOLD']}{COLORS['BRIGHT_GREEN']}▶ STARTING: {operation}{COLORS['RESET']}"
    )


# Helper function for operation completion
def log_operation_complete(operation, details=None):
    """Log the completion of an operation with success status."""
    if details:
        logger.info(
            f"{COLORS['BOLD']}{COLORS['GREEN']}✓ COMPLETED: {operation} - {details}{COLORS['RESET']}"
        )
    else:
        logger.info(
            f"{COLORS['BOLD']}{COLORS['GREEN']}✓ COMPLETED: {operation}{COLORS['RESET']}"
        )


# Helper function for operation warnings
def log_warning(message):
    """Log a warning message with clear visual indicator."""
    logger.warning(
        f"{COLORS['BOLD']}{COLORS['YELLOW']}⚠ WARNING: {message}{COLORS['RESET']}"
    )


# Helper function for operation errors
def log_error(message, error=None):
    """Log an error message with clear visual indicator."""
    if error:
        logger.error(
            f"{COLORS['BOLD']}{COLORS['RED']}✘ ERROR: {message} - {error}{COLORS['RESET']}"
        )
    else:
        logger.error(
            f"{COLORS['BOLD']}{COLORS['RED']}✘ ERROR: {message}{COLORS['RESET']}"
        )


# Helper function for important information
def log_info(message):
    """Log an informational message."""
    logger.info(f"{COLORS['BRIGHT_BLUE']}{message}{COLORS['RESET']}")


# Helper function for success messages
def log_success(message):
    """Log a success message."""
    logger.info(f"{COLORS['BRIGHT_GREEN']}✓ {message}{COLORS['RESET']}")


def initialize_client():
    """
    Initialize the SCM client using credentials from environment variables or .env file.
    
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
            log_warning(f"No .env file found in current directory or script directory")
            log_info(f"Searched locations:")
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
        f"TSG ID: {tsg_id[:4]}{'*' * (len(tsg_id)-8) if tsg_id else '****'}{tsg_id[-4:] if tsg_id else '****'}",
    )
    return client


def create_daily_schedule(schedule_client: schedules.Schedule, name: str, description: str, folder: str = "Texas"):
    """Create a daily schedule with a specific time range.
    
    Args:
        schedule_client: The Schedule client instance
        name: Name for the schedule
        description: Description for the schedule
        folder: Folder name in which to create the schedule (default: "Texas")
        
    Returns:
        The created schedule object
    """
    log_info(f"Creating daily schedule: {name}")
    
    try:
        # Create a data dictionary for the schedule - matching the expected model
        data = {
            "name": name,
            "description": description,
            "folder": folder,
            "schedule_type": {
                "recurring": {
                    "daily": ["08:00-17:00"]
                }
            }
        }
        
        schedule = schedule_client.create(data)
        log_success(f"Daily schedule created successfully with ID: {schedule.id}")
        return schedule
    except Exception as e:
        log_error(f"Failed to create daily schedule", str(e))
        raise


def create_weekly_schedule(schedule_client: schedules.Schedule, name: str, description: str, folder: str = "Texas"):
    """Create a weekly schedule with time ranges for specific days.
    
    Args:
        schedule_client: The Schedule client instance
        name: Name for the schedule
        description: Description for the schedule
        folder: Folder name in which to create the schedule (default: "Texas")
        
    Returns:
        The created schedule object
    """
    log_info(f"Creating weekly schedule: {name}")
    
    try:
        # Create a data dictionary for the schedule - matching the expected model
        data = {
            "name": name,
            "description": description,
            "folder": folder,
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                        "wednesday": ["09:00-17:00"],
                        "friday": ["09:00-13:00"]
                    }
                }
            }
        }
        
        schedule = schedule_client.create(data)
        log_success(f"Weekly schedule created successfully with ID: {schedule.id}")
        return schedule
    except Exception as e:
        log_error(f"Failed to create weekly schedule", str(e))
        raise


def create_non_recurring_schedule(schedule_client: schedules.Schedule, name: str, description: str, folder: str = "Texas"):
    """Create a non-recurring schedule with a specific date range.
    
    Args:
        schedule_client: The Schedule client instance
        name: Name for the schedule
        description: Description for the schedule
        folder: Folder name in which to create the schedule (default: "Texas")
        
    Returns:
        The created schedule object
    """
    log_info(f"Creating non-recurring schedule: {name}")
    
    try:
        # Create a schedule for a specific date range
        # Format string according to model requirements
        start_date = "2025/04/05"
        end_date = "2025/04/10"
        start_time = "08:00"
        end_time = "17:00"
        
        # Formatted as YYYY/MM/DD@hh:mm-YYYY/MM/DD@hh:mm
        non_recurring_range = f"{start_date}@{start_time}-{end_date}@{end_time}"
        
        # Create a data dictionary for the schedule - matching the expected model
        data = {
            "name": name,
            "description": description,
            "folder": folder,
            "schedule_type": {
                "non_recurring": [non_recurring_range]
            }
        }
        
        schedule = schedule_client.create(data)
        log_success(f"Non-recurring schedule created successfully with ID: {schedule.id}")
        return schedule
    except Exception as e:
        log_error(f"Failed to create non-recurring schedule", str(e))
        raise


def update_schedule(schedule_client: schedules.Schedule, schedule_id: str, description: str):
    """Update an existing schedule with a new description.
    
    Args:
        schedule_client: The Schedule client instance
        schedule_id: ID of the schedule to update
        description: New description for the schedule
        
    Returns:
        The updated schedule object
    """
    log_info(f"Updating schedule with ID: {schedule_id}")
    
    try:
        # First fetch the existing schedule
        existing_schedule = schedule_client.get(schedule_id)
        
        # Create an update model with id and new description
        update_data = {
            "id": schedule_id,
            "name": existing_schedule.name,
            "description": description,
            "folder": existing_schedule.folder if hasattr(existing_schedule, "folder") else None,
            "schedule_type": existing_schedule.schedule_type
        }
        
        # Convert to a Pydantic model
        schedule_update = ScheduleUpdateModel(**update_data)
        
        # Perform the update
        updated_schedule = schedule_client.update(schedule_update)
        log_success(f"Schedule updated successfully: {updated_schedule.name}")
        return updated_schedule
    except Exception as e:
        log_error(f"Failed to update schedule", str(e))
        raise


def list_schedules(schedule_client: schedules.Schedule, schedule_type=None, folder: str = "Texas"):
    """List schedules with optional filtering.
    
    Args:
        schedule_client: The Schedule client instance
        schedule_type: Optional filter for schedule type ('recurring' or 'non-recurring')
        folder: Folder name to list schedules from (default: "Texas")
        
    Returns:
        List of schedule objects
    """
    log_info(f"Listing schedules from folder '{folder}'" + (f" of type: {schedule_type}" if schedule_type else ""))
    
    try:
        # Schedule list method requires folder, snippet, or device
        # Get all schedules first
        schedules_list = schedule_client.list(folder=folder)
        
        # Filter manually if schedule_type is provided
        if schedule_type:
            if schedule_type == "recurring":
                schedules_list = [
                    s for s in schedules_list 
                    if (hasattr(s.schedule_type, "recurring") and 
                        s.schedule_type.recurring is not None)
                ]
            elif schedule_type == "non-recurring" or schedule_type == "non_recurring":
                schedules_list = [
                    s for s in schedules_list 
                    if (hasattr(s.schedule_type, "non_recurring") and 
                        s.schedule_type.non_recurring is not None)
                ]
        
        log_info(f"Found {len(schedules_list)} schedules")
        return schedules_list
    except Exception as e:
        log_error(f"Failed to list schedules", str(e))
        raise


def fetch_schedule_by_name(schedule_client: schedules.Schedule, name: str, folder: str = "Texas"):
    """Fetch a specific schedule by name.
    
    Args:
        schedule_client: The Schedule client instance
        name: Name of the schedule to fetch
        folder: Folder name to search in (default: "Texas")
        
    Returns:
        The schedule object if found
    """
    log_info(f"Fetching schedule by name: {name} from folder '{folder}'")
    
    try:
        # Schedule fetch method requires folder, snippet, or device
        schedule = schedule_client.fetch(name=name, folder=folder)
        log_success(f"Found schedule with ID: {schedule.id}")
        return schedule
    except Exception as e:
        log_error(f"Failed to fetch schedule", str(e))
        raise


def delete_schedule(schedule_client: schedules.Schedule, schedule_id: str):
    """Delete a schedule by ID.
    
    Args:
        schedule_client: The Schedule client instance
        schedule_id: ID of the schedule to delete
    """
    log_info(f"Deleting schedule with ID: {schedule_id}")
    
    try:
        # Schedule delete takes an object_id parameter
        schedule_client.delete(object_id=schedule_id)
        log_success("Schedule deleted successfully")
    except Exception as e:
        log_error(f"Failed to delete schedule", str(e))
        raise


def generate_schedules_report(schedules_list, filename: str) -> None:
    """Generate a CSV report of schedules.
    
    Args:
        schedules_list: List of schedule objects (Pydantic models)
        filename: Output filename for the CSV report
    """
    log_info(f"Generating schedules report: {filename}")
    
    fieldnames = [
        "id", "name", "description", "folder", "schedule_type", 
        "created_on", "created_by", "modified_on", "modified_by"
    ]
    
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for schedule in schedules_list:
                # Process schedule type info 
                schedule_type_info = ""
                if hasattr(schedule, "schedule_type"):
                    if hasattr(schedule.schedule_type, "recurring") and schedule.schedule_type.recurring:
                        if hasattr(schedule.schedule_type.recurring, "daily") and schedule.schedule_type.recurring.daily:
                            schedule_type_info = "Recurring - Daily"
                        elif hasattr(schedule.schedule_type.recurring, "weekly") and schedule.schedule_type.recurring.weekly:
                            schedule_type_info = "Recurring - Weekly"
                    elif hasattr(schedule.schedule_type, "non_recurring") and schedule.schedule_type.non_recurring:
                        schedule_type_info = "Non-Recurring"
                
                # Convert schedule to dict, handling complex nested attributes  
                row = {
                    "id": str(schedule.id) if hasattr(schedule, "id") else "",
                    "name": schedule.name if hasattr(schedule, "name") else "",
                    "description": schedule.description if hasattr(schedule, "description") else "",
                    "folder": schedule.folder if hasattr(schedule, "folder") else "",
                    "schedule_type": schedule_type_info,
                    "created_on": str(schedule.created_on) if hasattr(schedule, "created_on") else "",
                    "created_by": schedule.created_by if hasattr(schedule, "created_by") else "",
                    "modified_on": str(schedule.modified_on) if hasattr(schedule, "modified_on") else "",
                    "modified_by": schedule.modified_by if hasattr(schedule, "modified_by") else ""
                }
                writer.writerow(row)
                
        log_success(f"Report generated successfully: {filename}")
    except Exception as e:
        log_error(f"Failed to generate report", str(e))
        raise


def parse_arguments():
    """
    Parse command-line arguments for the schedule example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which schedule object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Schedule Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created schedule objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Schedule Type Selection")
    object_group.add_argument(
        "--daily", 
        action="store_true",
        help="Create daily schedule examples"
    )
    object_group.add_argument(
        "--weekly", 
        action="store_true", 
        help="Create weekly schedule examples"
    )
    object_group.add_argument(
        "--non-recurring", 
        action="store_true",
        help="Create non-recurring schedule examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all schedule object types (default behavior)"
    )
    
    # Reporting
    parser.add_argument(
        "--no-report", 
        action="store_true",
        help="Skip CSV report generation"
    )
    
    # Folder
    parser.add_argument(
        "--folder", 
        type=str, 
        default="Texas",
        help="Folder name in SCM to create objects in"
    )
    
    return parser.parse_args()


def main():
    """
    Execute the comprehensive set of schedule object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of schedule objects (daily, weekly, non-recurring)
    4. Update an existing schedule object to demonstrate modification capabilities
    5. List and filter schedule objects to show search functionality
    6. Generate a detailed CSV report of all created schedule objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created schedule objects (don't delete them)
        --daily: Create only daily schedule examples
        --weekly: Create only weekly schedule examples
        --non-recurring: Create only non-recurring schedule examples
        --all: Create all schedule object types (default behavior)
        --no-report: Skip CSV report generation
        --folder: Folder name in SCM to create objects in (default: "Texas")
    
    Environment Variables:
        SCM_CLIENT_ID: Client ID for SCM authentication (required)
        SCM_CLIENT_SECRET: Client secret for SCM authentication (required)
        SCM_TSG_ID: Tenant Service Group ID for SCM authentication (required)
        SCM_LOG_LEVEL: Logging level, defaults to DEBUG (optional)
        SKIP_CLEANUP: Alternative way to preserve created objects (optional)
    
    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Track execution time for reporting
    start_time = time.time()
    object_count = 0
    
    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"
    
    # Determine which object types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.daily or args.weekly or args.non_recurring)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Schedule object
        log_section("SCHEDULE OBJECT CONFIGURATION")
        log_operation_start("Initializing Schedule object manager")
        schedule_client = schedules.Schedule(client)
        log_operation_complete("Schedule object manager initialization")

        # Create various schedule objects
        created_schedules = []

        # Daily Schedule objects
        if create_all or args.daily:
            log_section("DAILY SCHEDULE OBJECTS")
            log_info("Creating daily schedule object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a daily schedule
            daily_schedule = create_daily_schedule(
                schedule_client=schedule_client,
                name=f"Daily-WorkHours-{uuid.uuid4().hex[:6]}",
                description="Daily schedule for standard work hours",
                folder=folder_name
            )
            if daily_schedule:
                created_schedules.append(daily_schedule)
                object_count += 1

            log_success(f"Created daily schedule objects")

        # Weekly Schedule objects
        if create_all or args.weekly:
            log_section("WEEKLY SCHEDULE OBJECTS")
            log_info("Creating weekly schedule object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a weekly schedule
            weekly_schedule = create_weekly_schedule(
                schedule_client=schedule_client,
                name=f"Weekly-WorkDays-{uuid.uuid4().hex[:6]}",
                description="Weekly schedule for Mon, Wed, Fri work days",
                folder=folder_name
            )
            if weekly_schedule:
                created_schedules.append(weekly_schedule)
                object_count += 1

            log_success(f"Created weekly schedule objects")

        # Non-recurring Schedule objects
        if create_all or args.non_recurring:
            log_section("NON-RECURRING SCHEDULE OBJECTS")
            log_info("Creating non-recurring schedule object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a non-recurring schedule
            non_recurring_schedule = create_non_recurring_schedule(
                schedule_client=schedule_client,
                name=f"NonRecurring-Event-{uuid.uuid4().hex[:6]}",
                description="Schedule for a special one-time event",
                folder=folder_name
            )
            if non_recurring_schedule:
                created_schedules.append(non_recurring_schedule)
                object_count += 1

            log_success(f"Created non-recurring schedule objects")

        # Update one of the objects
        if created_schedules:
            log_section("UPDATING SCHEDULE OBJECTS")
            log_info("Demonstrating how to update existing schedule objects")
            updated_schedule = update_schedule(
                schedule_client=schedule_client,
                schedule_id=created_schedules[0].id,
                description="Updated schedule description"
            )

        # List and filter schedule objects
        log_section("LISTING AND FILTERING SCHEDULE OBJECTS")
        log_info("Demonstrating how to search and filter schedule objects")
        all_schedules = list_schedules(schedule_client, folder=folder_name)
        
        # Also demonstrate filtering by schedule type
        try:
            recurring_schedules = list_schedules(schedule_client, schedule_type="recurring", folder=folder_name)
            log_info(f"Found {len(recurring_schedules)} recurring schedule objects")
        except Exception as e:
            log_warning(f"Failed to filter by schedule type: {str(e)}")
            log_info("Continuing with the rest of the script...")

        # Calculate intermediate execution statistics for the report
        current_time = time.time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_schedules and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating schedule objects CSV report")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"schedules_report_{timestamp}.csv"
            generate_schedules_report(all_schedules, report_filename)
            log_success(f"Generated schedule objects report: {report_filename}")
            log_info(f"The report contains details of all schedules in the system")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No schedule objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        deleted_count = 0
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_schedules)} schedule objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_schedules)} created schedule objects")
            for schedule in created_schedules:
                delete_schedule(schedule_client, schedule.id)
                deleted_count += 1
                log_info(f"Deleted schedule: {schedule.name}")

        # Calculate and display final execution statistics
        end_time = time.time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total schedule objects created: {object_count}")
        log_info(f"Total schedule objects deleted: {deleted_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if object_count > 0:
            log_info(f"Average time per object: {execution_time/object_count:.2f} seconds")

    except AuthenticationError as e:
        log_error(f"Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some schedule objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback
        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()