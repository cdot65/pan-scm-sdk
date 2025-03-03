#!/usr/bin/env python3
"""
Comprehensive examples of working with Application Group objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Application Group configurations and operations commonly 
used in enterprise networks, including:

1. Application Group Types:
   - Basic application groups with predefined applications
   - Application groups with custom applications
   - Nested application groups (groups containing other groups)
   - Mixed application groups (combinations of apps, groups, and filters)

2. Operational examples:
   - Creating application group objects
   - Searching and filtering application groups
   - Updating application group configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with application group details
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

2. Make sure you have a folder named "Texas" in your SCM environment or change the 
   folder name throughout the script.

3. Optional environment variables:
   - SKIP_CLEANUP=true: Set this to preserve created application group objects for manual inspection
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
from scm.config.objects import ApplicationGroup
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
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
logger = logging.getLogger("application_group_example")


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


def create_basic_application_group(app_groups, folder="Texas"):
    """
    Create a basic application group with common predefined applications.
    
    This function demonstrates creating a standard application group with
    commonly used predefined applications.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating basic application group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"basic-apps-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the application group configuration
    basic_group_config = {
        "name": group_name,
        "folder": folder,  # Use the provided folder name
        "members": ["web-browsing", "ssl", "dns"],  # Common web applications
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Basic Application Group")
    log_info(f"  - Members: {', '.join(basic_group_config['members'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = app_groups.create(basic_group_config)
        log_success(f"Created application group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Basic application group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application group", str(e))

    return None


def create_custom_application_group(app_groups, folder="Texas"):
    """
    Create an application group with custom applications.
    
    This function demonstrates creating an application group with
    custom application names that might be specific to an organization.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating custom application group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"custom-apps-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the application group configuration
    # Note: These applications must exist in your environment
    # Using applications known to work based on failure logs
    custom_group_config = {
        "name": group_name,
        "folder": folder,  # Use the provided folder name
        "members": ["web-browsing", "ssl", "ping"],  # Using verified applications
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Custom Application Group")
    log_info(f"  - Members: {', '.join(custom_group_config['members'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = app_groups.create(custom_group_config)
        log_success(f"Created application group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Custom application group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check that all applications in members list exist in your environment")
    except Exception as e:
        log_error(f"Unexpected error creating application group", str(e))

    return None


def create_nested_application_group(app_groups, basic_group_id, custom_group_id, folder="Texas"):
    """
    Create a nested application group containing other application groups.
    
    This function demonstrates creating a hierarchical application group that
    includes references to other application groups.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        basic_group_id: ID of the basic application group to include
        custom_group_id: ID of the custom application group to include
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating nested application group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"nested-group-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # First, get the names of the groups we want to include
    try:
        basic_group = app_groups.get(basic_group_id)
        custom_group = app_groups.get(custom_group_id)
        
        # Create the application group configuration
        nested_group_config = {
            "name": group_name,
            "folder": folder,  # Use the provided folder name
            "members": [basic_group.name, custom_group.name],  # Reference by name, not ID
        }

        log_info("Configuration details:")
        log_info(f"  - Type: Nested Application Group")
        log_info(f"  - Member Groups: {', '.join(nested_group_config['members'])}")

        log_info("Sending request to Strata Cloud Manager API...")
        new_group = app_groups.create(nested_group_config)
        log_success(f"Created application group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Nested application group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NotFoundError as e:
        log_error(f"Referenced group not found", e.message)
        log_info("Ensure both referenced groups exist before creating a nested group")
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating nested application group", str(e))

    return None


def create_mixed_application_group(app_groups, basic_group_id, folder="Texas"):
    """
    Create a mixed application group with apps and existing groups.
    
    This function demonstrates creating an application group that contains 
    both individual applications and references to existing groups.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        basic_group_id: ID of a basic application group to include
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating mixed application group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"mixed-apps-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    try:
        # Get the name of the group we want to include
        basic_group = app_groups.get(basic_group_id)
        
        # Create the application group configuration
        mixed_group_config = {
            "name": group_name,
            "folder": folder,  # Use the provided folder name
            "members": [
                basic_group.name,  # Existing group (referenced by name)
                "ping",           # Individual applications
                "dns",
                "ssl"             # Using applications known to exist in the system
            ],
        }

        log_info("Configuration details:")
        log_info(f"  - Type: Mixed Application Group")
        log_info(f"  - Members: {', '.join(mixed_group_config['members'])}")

        log_info("Sending request to Strata Cloud Manager API...")
        new_group = app_groups.create(mixed_group_config)
        log_success(f"Created application group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Mixed application group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NotFoundError as e:
        log_error(f"Referenced group not found", e.message)
        log_info("Ensure referenced group exists before creating a mixed group")
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating mixed application group", str(e))

    return None


def fetch_and_update_application_group(app_groups, group_id):
    """
    Fetch an application group by ID and update its members.
    
    This function demonstrates how to:
    1. Retrieve an existing application group using its ID
    2. Modify the group's members (add new applications)
    3. Submit the updated group back to the SCM API
    
    Args:
        app_groups: The ApplicationGroup manager instance
        group_id: The UUID of the group to update
        
    Returns:
        ApplicationGroupResponseModel: The updated group object, or None if update failed
    """
    logger.info(f"Fetching and updating application group with ID: {group_id}")

    try:
        # Fetch the group
        app_group = app_groups.get(group_id)
        logger.info(f"Found application group: {app_group.name}")

        # Update the group's members - add new applications
        original_members = app_group.members.copy()
        app_group.members = app_group.members + ["smtp", "pop3"]  # Using apps known to work from logs
        
        # Remove duplicates while preserving order
        seen = set()
        app_group.members = [x for x in app_group.members if not (x in seen or seen.add(x))]

        # Perform the update
        updated_group = app_groups.update(app_group)
        logger.info(f"Updated application group: {updated_group.name}")
        logger.info(f"Original members: {', '.join(original_members)}")
        logger.info(f"Updated members: {', '.join(updated_group.members)}")
        return updated_group

    except NotFoundError as e:
        logger.error(f"Application group not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid application group update: {e.message}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_application_groups(app_groups):
    """
    List and filter application group objects.
    
    This function demonstrates how to:
    1. List all application groups in a folder
    2. Filter application groups by name pattern
    3. Display detailed information about each group
    
    Args:
        app_groups: The ApplicationGroup manager instance
        
    Returns:
        list: All retrieved application group objects
    """
    logger.info("Listing and filtering application group objects")

    # List all application groups in the Texas folder
    all_groups = app_groups.list(folder="Texas")
    logger.info(f"Found {len(all_groups)} application groups in the Texas folder")

    # Filter by name pattern (if supported)
    try:
        basic_groups = app_groups.list(folder="Texas", name="basic")
        logger.info(f"Found {len(basic_groups)} application groups with 'basic' in the name")
    except Exception as e:
        logger.warning(f"Filtering by name is not supported: {str(e)}")

    # Print details of groups
    logger.info("\nDetails of application group objects:")
    for app_group in all_groups[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Group: {app_group.name}")
        logger.info(f"    ID: {app_group.id}")
        
        # Print members
        if hasattr(app_group, "members") and app_group.members:
            logger.info(f"    Members: {', '.join(app_group.members)}")
            
        # Print folder/container info if available
        if hasattr(app_group, "folder") and app_group.folder:
            logger.info(f"    Folder: {app_group.folder}")
        elif hasattr(app_group, "snippet") and app_group.snippet:
            logger.info(f"    Snippet: {app_group.snippet}")
        elif hasattr(app_group, "device") and app_group.device:
            logger.info(f"    Device: {app_group.device}")
            
        logger.info("")

    return all_groups


def cleanup_application_group_objects(app_groups, group_ids):
    """
    Delete the application group objects created in this example.
    
    This function handles dependent groups by making multiple attempts to delete each group,
    with nested groups being deleted before their parent groups.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        group_ids: List of application group object IDs to delete
    """
    logger.info("Cleaning up application group objects")
    
    # Get details about all groups to identify dependencies
    groups_info = {}
    for group_id in group_ids:
        try:
            group = app_groups.get(group_id)
            groups_info[group_id] = {
                "name": group.name,
                "members": group.members
            }
        except Exception:
            # If we can't get info, still keep the ID for deletion attempts
            groups_info[group_id] = {"name": "unknown", "members": []}
    
    # Identify groups that are members of other groups
    dependent_groups = set()
    for group_id, info in groups_info.items():
        for other_id, other_info in groups_info.items():
            if group_id != other_id and info["name"] in other_info["members"]:
                dependent_groups.add(group_id)
    
    # First attempt to delete non-dependent groups
    remaining_ids = set(group_ids)
    
    # First round: Delete groups that are referenced by other groups (nested groups)
    for group_id in list(remaining_ids):
        if group_id not in dependent_groups:
            try:
                app_groups.delete(group_id)
                logger.info(f"Deleted application group with ID: {group_id}")
                remaining_ids.remove(group_id)
            except NotFoundError as e:
                logger.error(f"Application group not found: {e.message}")
                remaining_ids.remove(group_id)
            except Exception as e:
                logger.warning(f"Will retry deletion of group ID {group_id}: {str(e)}")
    
    # Second round: Delete remaining groups (which were likely referenced by others)
    for group_id in list(remaining_ids):
        try:
            app_groups.delete(group_id)
            logger.info(f"Deleted application group with ID: {group_id}")
        except NotFoundError as e:
            logger.error(f"Application group not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting application group: {str(e)}")


def create_bulk_application_group_objects(app_groups, folder="Texas"):
    """
    Create multiple application group objects in a batch.
    
    This function demonstrates creating multiple application group objects in a batch,
    which is useful for setting up multiple groups at once.
    
    Args:
        app_groups: The ApplicationGroup manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created application group objects, or empty list if creation failed
    """
    logger.info("Creating a batch of application group objects")

    # Define a list of application group objects to create
    group_configs = [
        {
            "name": f"bulk-web-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "members": ["web-browsing", "ssl", "dns"],  # Removed invalid 'http'
        },
        {
            "name": f"bulk-email-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "members": ["smtp", "imap", "pop3"],  # These seem to work from the logs
        },
        {
            "name": f"bulk-file-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "members": ["ftp", "tftp", "web-browsing"],  # Removed invalid 'scp'
        },
        {
            "name": f"bulk-mgmt-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "members": ["ping", "dns", "ssl"],  # Changed to known working apps
        }
    ]

    created_groups = []

    # Create each application group object
    for group_config in group_configs:
        try:
            new_group = app_groups.create(group_config)
            logger.info(
                f"Created application group: {new_group.name} with ID: {new_group.id}"
            )
            created_groups.append(new_group.id)
        except Exception as e:
            logger.error(f"Error creating group {group_config['name']}: {str(e)}")

    return created_groups


def generate_application_group_report(app_groups, group_ids, execution_time):
    """
    Generate a comprehensive CSV report of all application group objects created by the script.
    
    This function fetches detailed information about each application group object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        app_groups: The ApplicationGroup manager instance used to fetch object details
        group_ids: List of application group object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"application_groups_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Members",
        "Container Type",
        "Container Name",
        "Number of Members",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each application group object
    group_data = []
    for idx, group_id in enumerate(group_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(group_ids) - 1:
            log_info(f"Processing application group {idx + 1} of {len(group_ids)}")
            
        try:
            # Get the application group details
            app_group = app_groups.get(group_id)
            
            # Determine container type and name
            container_type = "Unknown"
            container_name = "Unknown"
            
            if hasattr(app_group, "folder") and app_group.folder:
                container_type = "Folder"
                container_name = app_group.folder
            elif hasattr(app_group, "snippet") and app_group.snippet:
                container_type = "Snippet"
                container_name = app_group.snippet
            elif hasattr(app_group, "device") and app_group.device:
                container_type = "Device"
                container_name = app_group.device
                
            # Add group data
            group_data.append([
                app_group.id,
                app_group.name,
                ", ".join(app_group.members) if app_group.members else "None",
                container_type,
                container_name,
                len(app_group.members) if app_group.members else 0,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for application group ID {group_id}", str(e))
            # Add minimal info for groups that couldn't be retrieved
            group_data.append([
                group_id, 
                "ERROR", 
                "ERROR", 
                "ERROR",
                "ERROR",
                "ERROR",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            failed_fetches += 1
    
    try:
        # Write to CSV file
        with open(report_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(group_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(group_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"app_groups_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(group_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the application group example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which application group types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Application Groups Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created application group objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Group Type Selection")
    object_group.add_argument(
        "--basic", 
        action="store_true",
        help="Create basic application group examples"
    )
    object_group.add_argument(
        "--custom", 
        action="store_true", 
        help="Create custom application group examples"
    )
    object_group.add_argument(
        "--nested", 
        action="store_true",
        help="Create nested application group examples"
    )
    object_group.add_argument(
        "--mixed", 
        action="store_true",
        help="Create mixed application group examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk application group examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all application group types (default behavior)"
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
    Execute the comprehensive set of application group examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of application groups (basic, custom, nested, mixed)
    4. Update an existing application group to demonstrate modification capabilities
    5. List and filter application groups to show search functionality
    6. Generate a detailed CSV report of all created application group objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created application group objects (don't delete them)
        --basic: Create only basic application group examples
        --custom: Create only custom application group examples
        --nested: Create only nested application group examples
        --mixed: Create only mixed application group examples
        --bulk: Create only bulk application group examples
        --all: Create all application group types (default behavior)
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
    start_time = __import__("time").time()
    object_count = 0
    
    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"
    
    # Determine which object types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.basic or args.custom or args.nested or 
                                args.mixed or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize ApplicationGroup object
        log_section("APPLICATION GROUP CONFIGURATION")
        log_operation_start("Initializing ApplicationGroup object manager")
        app_groups = ApplicationGroup(client)
        log_operation_complete("ApplicationGroup object manager initialization")

        # Create various application group objects
        created_groups = []

        # Basic application groups
        if create_all or args.basic:
            log_section("BASIC APPLICATION GROUPS")
            log_info("Creating basic application group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a basic application group
            basic_group = create_basic_application_group(app_groups, folder_name)
            if basic_group:
                created_groups.append(basic_group.id)
                object_count += 1

            log_success(f"Created basic application group")

        # Custom application groups
        if create_all or args.custom:
            log_section("CUSTOM APPLICATION GROUPS")
            log_info("Creating custom application group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a custom application group
            custom_group = create_custom_application_group(app_groups, folder_name)
            if custom_group:
                created_groups.append(custom_group.id)
                object_count += 1

            log_success(f"Created custom application group")

        # Nested application groups - only if we have basic and custom groups
        if (create_all or args.nested) and len(created_groups) >= 2:
            log_section("NESTED APPLICATION GROUPS")
            log_info("Creating nested application group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a nested application group
            nested_group = create_nested_application_group(
                app_groups, created_groups[0], created_groups[1], folder_name
            )
            if nested_group:
                created_groups.append(nested_group.id)
                object_count += 1

            log_success(f"Created nested application group")
        elif args.nested and len(created_groups) < 2:
            log_warning("Skipping nested group creation: requires at least two existing groups")

        # Mixed application groups - only if we have at least one group
        if (create_all or args.mixed) and created_groups:
            log_section("MIXED APPLICATION GROUPS")
            log_info("Creating mixed application group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a mixed application group
            mixed_group = create_mixed_application_group(
                app_groups, created_groups[0], folder_name
            )
            if mixed_group:
                created_groups.append(mixed_group.id)
                object_count += 1

            log_success(f"Created mixed application group")
        elif args.mixed and not created_groups:
            log_warning("Skipping mixed group creation: requires at least one existing group")

        # Bulk application group creation
        if create_all or args.bulk:
            log_section("BULK APPLICATION GROUPS")
            log_info("Creating multiple application group objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk application groups
            bulk_group_ids = create_bulk_application_group_objects(app_groups, folder_name)
            if bulk_group_ids:
                created_groups.extend(bulk_group_ids)
                object_count += len(bulk_group_ids)
                log_success(f"Created {len(bulk_group_ids)} bulk application group objects")

        # Update one of the objects
        if created_groups:
            log_section("UPDATING APPLICATION GROUPS")
            log_info("Demonstrating how to update existing application group objects")
            updated_group = fetch_and_update_application_group(app_groups, created_groups[0])

        # List and filter application group objects
        log_section("LISTING AND FILTERING APPLICATION GROUPS")
        log_info("Demonstrating how to search and filter application group objects")
        all_groups = list_and_filter_application_groups(app_groups)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_groups and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating application groups CSV report")
            report_file = generate_application_group_report(app_groups, created_groups, execution_time_so_far)
            if report_file:
                log_success(f"Generated application groups report: {report_file}")
                log_info(f"The report contains details of all {len(created_groups)} application group objects created")
            else:
                log_error("Failed to generate application groups report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No application group objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_groups)} application group objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_groups)} created application group objects")
            cleanup_application_group_objects(app_groups, created_groups)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total application group objects created: {object_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(
            f"Average time per object: {execution_time/max(object_count, 1):.2f} seconds"
        )

    except AuthenticationError as e:
        log_error(f"Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some application group objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()