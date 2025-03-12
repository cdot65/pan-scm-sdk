#!/usr/bin/env python3
"""
Comprehensive examples of working with Dynamic User Group objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Dynamic User Group configurations and operations commonly
used in enterprise networks, including:

1. Dynamic User Group Types:
   - Simple tag-based user filtering
   - Complex boolean expressions (AND, OR, NOT)
   - Multi-attribute filtering
   - Department-based filtering
   - Role-based filtering

2. Operational examples:
   - Creating dynamic user group objects
   - Searching and filtering dynamic user groups
   - Updating dynamic user group configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with dynamic user group details
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
   - SKIP_CLEANUP=true: Set this to preserve created dynamic user group objects for manual inspection
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
from scm.config.objects import DynamicUserGroup
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
logger = logging.getLogger("dynamic_user_group_example")


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


def create_simple_tag_based_group(user_groups, folder="Texas"):
    """
    Create a simple tag-based dynamic user group.

    This function demonstrates creating a dynamic user group using a simple
    tag expression to filter users based on a single attribute.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        DynamicUserGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating simple tag-based dynamic user group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"exec-users-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the dynamic user group configuration with a simple tag-based filter
    simple_group_config = {
        "name": group_name,
        "description": "Executive users identified by role tag",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Executive"],
        "filter": "tag.role.executive",  # Simple tag-based filter
    }

    log_info("Configuration details:")
    log_info("  - Type: Simple Tag-Based Group")
    log_info(f"  - Filter Expression: {simple_group_config['filter']}")
    log_info(f"  - Tags: {', '.join(simple_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = user_groups.create(simple_group_config)
        log_success(f"Created dynamic user group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_info(f"  - Filter: {new_group.filter}")
        log_operation_complete(
            "Simple tag-based dynamic user group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error("Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid group data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating dynamic user group", str(e))

    return None


def create_complex_boolean_group(user_groups, folder="Texas"):
    """
    Create a dynamic user group with complex boolean expressions.

    This function demonstrates creating a dynamic user group using boolean operators
    (AND, OR, NOT) to create more sophisticated filtering logic.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        DynamicUserGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating complex boolean dynamic user group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"it-admins-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the dynamic user group configuration with a complex boolean filter
    complex_group_config = {
        "name": group_name,
        "description": "IT administrators with specific access requirements",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "IT"],
        # Using AND and OR operators to create complex logic
        "filter": "(tag.department.it AND tag.role.administrator) OR (tag.access.systems AND tag.level.admin)",
    }

    log_info("Configuration details:")
    log_info("  - Type: Complex Boolean Expression Group")
    log_info(f"  - Filter Expression: {complex_group_config['filter']}")
    log_info(f"  - Tags: {', '.join(complex_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = user_groups.create(complex_group_config)
        log_success(f"Created dynamic user group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_info(f"  - Filter: {new_group.filter}")
        log_operation_complete(
            "Complex boolean dynamic user group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error("Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid group data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating dynamic user group", str(e))

    return None


def create_multi_attribute_group(user_groups, folder="Texas"):
    """
    Create a dynamic user group filtering on multiple user attributes.

    This function demonstrates creating a group that filters users based on
    multiple attributes to provide fine-grained targeting.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        DynamicUserGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating multi-attribute dynamic user group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"contractors-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the dynamic user group configuration with multiple attribute filters
    multi_attr_config = {
        "name": group_name,
        "description": "External contractors with specific access requirements",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Contractors"],
        # Filtering on employment status, location, and security clearance
        "filter": "tag.employment.contractor AND tag.location.remote AND tag.clearance.standard",
    }

    log_info("Configuration details:")
    log_info("  - Type: Multi-Attribute Group")
    log_info(f"  - Filter Expression: {multi_attr_config['filter']}")
    log_info(f"  - Tags: {', '.join(multi_attr_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = user_groups.create(multi_attr_config)
        log_success(f"Created dynamic user group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_info(f"  - Filter: {new_group.filter}")
        log_operation_complete(
            "Multi-attribute dynamic user group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error("Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid group data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating dynamic user group", str(e))

    return None


def create_department_based_group(user_groups, folder="Texas"):
    """
    Create a dynamic user group based on department.

    This function demonstrates creating a group that filters users based on
    their department, commonly used for role-based access control.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        DynamicUserGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating department-based dynamic user group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"finance-users-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the dynamic user group configuration for department-based filtering
    department_group_config = {
        "name": group_name,
        "description": "All users in the finance department",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Finance"],
        "filter": "tag.department.finance",  # Simple department tag filtering
    }

    log_info("Configuration details:")
    log_info("  - Type: Department-Based Group")
    log_info(f"  - Filter Expression: {department_group_config['filter']}")
    log_info(f"  - Tags: {', '.join(department_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = user_groups.create(department_group_config)
        log_success(f"Created dynamic user group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_info(f"  - Filter: {new_group.filter}")
        log_operation_complete(
            "Department-based dynamic user group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error("Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid group data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating dynamic user group", str(e))

    return None


def create_role_based_group(user_groups, folder="Texas"):
    """
    Create a dynamic user group based on role.

    This function demonstrates creating a group that filters users based on
    their role within the organization, useful for functional access policies.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        DynamicUserGroupResponseModel: The created group object, or None if creation failed
    """
    log_operation_start("Creating role-based dynamic user group")

    # Generate a unique group name with UUID to avoid conflicts
    group_name = f"developers-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")

    # Create the dynamic user group configuration for role-based filtering
    role_group_config = {
        "name": group_name,
        "description": "Software developers across all departments",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Developers"],
        "filter": "tag.role.developer OR tag.role.engineer",  # Role-based filtering with OR condition
    }

    log_info("Configuration details:")
    log_info("  - Type: Role-Based Group")
    log_info(f"  - Filter Expression: {role_group_config['filter']}")
    log_info(f"  - Tags: {', '.join(role_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = user_groups.create(role_group_config)
        log_success(f"Created dynamic user group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_info(f"  - Filter: {new_group.filter}")
        log_operation_complete("Role-based dynamic user group creation", f"Group: {new_group.name}")
        return new_group
    except NameNotUniqueError as e:
        log_error("Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid group data", e.message)
        if hasattr(e, "details") and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating dynamic user group", str(e))

    return None


def fetch_and_update_dynamic_user_group(user_groups, group_id):
    """
    Fetch a dynamic user group by ID and update its filter expression.

    This function demonstrates how to:
    1. Retrieve an existing dynamic user group using its ID
    2. Modify the group's filter expression
    3. Submit the updated group back to the SCM API

    Args:
        user_groups: The DynamicUserGroup manager instance
        group_id: The UUID of the group to update

    Returns:
        DynamicUserGroupResponseModel: The updated group object, or None if update failed
    """
    logger.info(f"Fetching and updating dynamic user group with ID: {group_id}")

    try:
        # Fetch the group
        user_group = user_groups.get(group_id)
        logger.info(f"Found dynamic user group: {user_group.name}")
        logger.info(f"Current filter: {user_group.filter}")

        # Update the filter expression with more specific criteria
        original_filter = user_group.filter

        # Add additional condition to the filter
        if " AND " in original_filter:
            user_group.filter = f"({original_filter}) AND tag.access.approved"
        else:
            user_group.filter = f"{original_filter} AND tag.access.approved"

        # Update description as well
        if user_group.description:
            user_group.description = f"{user_group.description} - With approved access only"
        else:
            user_group.description = "With approved access only"

        # Perform the update
        updated_group = user_groups.update(user_group)
        logger.info(f"Updated dynamic user group: {updated_group.name}")
        logger.info(f"Original filter: {original_filter}")
        logger.info(f"Updated filter: {updated_group.filter}")
        logger.info(f"Updated description: {updated_group.description}")
        return updated_group

    except NotFoundError as e:
        logger.error(f"Dynamic user group not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid dynamic user group update: {e.message}")
        if hasattr(e, "details") and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_dynamic_user_groups(user_groups):
    """
    List and filter dynamic user group objects.

    This function demonstrates how to:
    1. List all dynamic user groups in a folder
    2. Filter dynamic user groups by name pattern
    3. Display detailed information about each group

    Args:
        user_groups: The DynamicUserGroup manager instance

    Returns:
        list: All retrieved dynamic user group objects
    """
    logger.info("Listing and filtering dynamic user group objects")

    # List all dynamic user groups in the Texas folder
    all_groups = user_groups.list(folder="Texas")
    logger.info(f"Found {len(all_groups)} dynamic user groups in the Texas folder")

    # Filter by name pattern (if supported)
    try:
        developer_groups = user_groups.list(folder="Texas", name="developer")
        logger.info(
            f"Found {len(developer_groups)} dynamic user groups with 'developer' in the name"
        )
    except Exception as e:
        logger.warning(f"Filtering by name is not supported: {str(e)}")

    # Print details of groups
    logger.info("\nDetails of dynamic user group objects:")
    for user_group in all_groups[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Group: {user_group.name}")
        logger.info(f"    ID: {user_group.id}")
        logger.info(
            f"    Description: {user_group.description if hasattr(user_group, 'description') and user_group.description else 'None'}"
        )
        logger.info(f"    Filter: {user_group.filter}")

        # Print tags if available
        if hasattr(user_group, "tag") and user_group.tag:
            logger.info(f"    Tags: {', '.join(user_group.tag)}")

        # Print folder/container info if available
        if hasattr(user_group, "folder") and user_group.folder:
            logger.info(f"    Folder: {user_group.folder}")
        elif hasattr(user_group, "snippet") and user_group.snippet:
            logger.info(f"    Snippet: {user_group.snippet}")
        elif hasattr(user_group, "device") and user_group.device:
            logger.info(f"    Device: {user_group.device}")

        logger.info("")

    return all_groups


def cleanup_dynamic_user_group_objects(user_groups, group_ids):
    """
    Delete the dynamic user group objects created in this example.

    Args:
        user_groups: The DynamicUserGroup manager instance
        group_ids: List of dynamic user group object IDs to delete
    """
    logger.info("Cleaning up dynamic user group objects")

    for group_id in group_ids:
        try:
            user_groups.delete(group_id)
            logger.info(f"Deleted dynamic user group with ID: {group_id}")
        except NotFoundError as e:
            logger.error(f"Dynamic user group not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting dynamic user group: {str(e)}")


def create_bulk_dynamic_user_group_objects(user_groups, folder="Texas"):
    """
    Create multiple dynamic user group objects in a batch.

    This function demonstrates creating multiple dynamic user group objects in a batch,
    which is useful for setting up multiple groups at once.

    Args:
        user_groups: The DynamicUserGroup manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")

    Returns:
        list: List of IDs of created dynamic user group objects, or empty list if creation failed
    """
    logger.info("Creating a batch of dynamic user group objects")

    # Define a list of dynamic user group objects to create
    group_configs = [
        {
            "name": f"hr-users-{uuid.uuid4().hex[:6]}",
            "description": "All HR department users",
            "folder": folder,
            "tag": ["Automation", "Bulk", "HR"],
            "filter": "tag.department.hr",
        },
        {
            "name": f"marketing-users-{uuid.uuid4().hex[:6]}",
            "description": "All marketing department users",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Marketing"],
            "filter": "tag.department.marketing",
        },
        {
            "name": f"admin-level-{uuid.uuid4().hex[:6]}",
            "description": "Users with administrative access",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Admin"],
            "filter": "tag.access.admin AND tag.level.high",
        },
        {
            "name": f"remote-employees-{uuid.uuid4().hex[:6]}",
            "description": "Remote workers requiring VPN access",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Remote"],
            "filter": "tag.location.remote AND tag.status.active",
        },
    ]

    created_groups = []

    # Create each dynamic user group object
    for group_config in group_configs:
        try:
            new_group = user_groups.create(group_config)
            logger.info(f"Created dynamic user group: {new_group.name} with ID: {new_group.id}")
            created_groups.append(new_group.id)
        except Exception as e:
            logger.error(f"Error creating group {group_config['name']}: {str(e)}")

    return created_groups


def generate_dynamic_user_group_report(user_groups, group_ids, execution_time):
    """
    Generate a comprehensive CSV report of all dynamic user group objects created by the script.

    This function fetches detailed information about each dynamic user group object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    Args:
        user_groups: The DynamicUserGroup manager instance used to fetch object details
        group_ids: List of dynamic user group object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"dynamic_user_groups_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Object ID",
        "Name",
        "Description",
        "Filter Expression",
        "Tags",
        "Container Type",
        "Container Name",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each dynamic user group object
    group_data = []
    for idx, group_id in enumerate(group_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(group_ids) - 1:
            log_info(f"Processing dynamic user group {idx + 1} of {len(group_ids)}")

        try:
            # Get the dynamic user group details
            user_group = user_groups.get(group_id)

            # Determine container type and name
            container_type = "Unknown"
            container_name = "Unknown"

            if hasattr(user_group, "folder") and user_group.folder:
                container_type = "Folder"
                container_name = user_group.folder
            elif hasattr(user_group, "snippet") and user_group.snippet:
                container_type = "Snippet"
                container_name = user_group.snippet
            elif hasattr(user_group, "device") and user_group.device:
                container_type = "Device"
                container_name = user_group.device

            # Add group data
            group_data.append(
                [
                    user_group.id,
                    user_group.name,
                    user_group.description
                    if hasattr(user_group, "description") and user_group.description
                    else "None",
                    user_group.filter,
                    ", ".join(user_group.tag)
                    if hasattr(user_group, "tag") and user_group.tag
                    else "None",
                    container_type,
                    container_name,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for dynamic user group ID {group_id}", str(e))
            # Add minimal info for groups that couldn't be retrieved
            group_data.append(
                [
                    group_id,
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
            failed_fetches += 1

    try:
        # Write to CSV file
        with open(report_file, "w", newline="") as csvfile:
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
            writer.writerow(
                ["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            )

        return report_file

    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"dynamic_user_groups_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(group_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the dynamic user group example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which dynamic user group types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Dynamic User Groups Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created dynamic user group objects (don't delete them)",
    )

    # Object types to create
    object_group = parser.add_argument_group("Group Type Selection")
    object_group.add_argument(
        "--simple", action="store_true", help="Create simple tag-based dynamic user group examples"
    )
    object_group.add_argument(
        "--complex", action="store_true", help="Create complex boolean dynamic user group examples"
    )
    object_group.add_argument(
        "--multi", action="store_true", help="Create multi-attribute dynamic user group examples"
    )
    object_group.add_argument(
        "--department",
        action="store_true",
        help="Create department-based dynamic user group examples",
    )
    object_group.add_argument(
        "--role", action="store_true", help="Create role-based dynamic user group examples"
    )
    object_group.add_argument(
        "--bulk", action="store_true", help="Create bulk dynamic user group examples"
    )
    object_group.add_argument(
        "--all", action="store_true", help="Create all dynamic user group types (default behavior)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Folder
    parser.add_argument(
        "--folder", type=str, default="Texas", help="Folder name in SCM to create objects in"
    )

    return parser.parse_args()


def main():
    """
    Execute the comprehensive set of dynamic user group examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of dynamic user groups (simple, complex, multi-attribute, etc.)
    4. Update an existing dynamic user group to demonstrate modification capabilities
    5. List and filter dynamic user groups to show search functionality
    6. Generate a detailed CSV report of all created dynamic user group objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created dynamic user group objects (don't delete them)
        --simple: Create only simple tag-based dynamic user group examples
        --complex: Create only complex boolean dynamic user group examples
        --multi: Create only multi-attribute dynamic user group examples
        --department: Create only department-based dynamic user group examples
        --role: Create only role-based dynamic user group examples
        --bulk: Create only bulk dynamic user group examples
        --all: Create all dynamic user group types (default behavior)
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
    create_all = args.all or not (
        args.simple or args.complex or args.multi or args.department or args.role or args.bulk
    )

    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize DynamicUserGroup object
        log_section("DYNAMIC USER GROUP CONFIGURATION")
        log_operation_start("Initializing DynamicUserGroup object manager")
        user_groups = DynamicUserGroup(client)
        log_operation_complete("DynamicUserGroup object manager initialization")

        # Create various dynamic user group objects
        created_groups = []

        # Simple tag-based dynamic user groups
        if create_all or args.simple:
            log_section("SIMPLE TAG-BASED USER GROUPS")
            log_info("Creating simple tag-based dynamic user group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a simple tag-based dynamic user group
            simple_group = create_simple_tag_based_group(user_groups, folder_name)
            if simple_group:
                created_groups.append(simple_group.id)
                object_count += 1

            log_success("Created simple tag-based dynamic user group")

        # Complex boolean dynamic user groups
        if create_all or args.complex:
            log_section("COMPLEX BOOLEAN USER GROUPS")
            log_info("Creating complex boolean dynamic user group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a complex boolean dynamic user group
            complex_group = create_complex_boolean_group(user_groups, folder_name)
            if complex_group:
                created_groups.append(complex_group.id)
                object_count += 1

            log_success("Created complex boolean dynamic user group")

        # Multi-attribute dynamic user groups
        if create_all or args.multi:
            log_section("MULTI-ATTRIBUTE USER GROUPS")
            log_info("Creating multi-attribute dynamic user group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a multi-attribute dynamic user group
            multi_attr_group = create_multi_attribute_group(user_groups, folder_name)
            if multi_attr_group:
                created_groups.append(multi_attr_group.id)
                object_count += 1

            log_success("Created multi-attribute dynamic user group")

        # Department-based dynamic user groups
        if create_all or args.department:
            log_section("DEPARTMENT-BASED USER GROUPS")
            log_info("Creating department-based dynamic user group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a department-based dynamic user group
            department_group = create_department_based_group(user_groups, folder_name)
            if department_group:
                created_groups.append(department_group.id)
                object_count += 1

            log_success("Created department-based dynamic user group")

        # Role-based dynamic user groups
        if create_all or args.role:
            log_section("ROLE-BASED USER GROUPS")
            log_info("Creating role-based dynamic user group patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a role-based dynamic user group
            role_group = create_role_based_group(user_groups, folder_name)
            if role_group:
                created_groups.append(role_group.id)
                object_count += 1

            log_success("Created role-based dynamic user group")

        # Bulk dynamic user group creation
        if create_all or args.bulk:
            log_section("BULK DYNAMIC USER GROUPS")
            log_info("Creating multiple dynamic user group objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk dynamic user group objects
            bulk_group_ids = create_bulk_dynamic_user_group_objects(user_groups, folder_name)
            if bulk_group_ids:
                created_groups.extend(bulk_group_ids)
                object_count += len(bulk_group_ids)
                log_success(f"Created {len(bulk_group_ids)} bulk dynamic user group objects")

        # Update one of the objects
        if created_groups:
            log_section("UPDATING DYNAMIC USER GROUPS")
            log_info("Demonstrating how to update existing dynamic user group objects")
            fetch_and_update_dynamic_user_group(user_groups, created_groups[0])

        # List and filter dynamic user group objects
        log_section("LISTING AND FILTERING DYNAMIC USER GROUPS")
        log_info("Demonstrating how to search and filter dynamic user group objects")
        list_and_filter_dynamic_user_groups(user_groups)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_groups and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating dynamic user groups CSV report")
            report_file = generate_dynamic_user_group_report(
                user_groups, created_groups, execution_time_so_far
            )
            if report_file:
                log_success(f"Generated dynamic user groups report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_groups)} dynamic user group objects created"
                )
            else:
                log_error("Failed to generate dynamic user groups report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No dynamic user group objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_groups)} dynamic user group objects"
            )
            log_info(
                "To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            log_operation_start(
                f"Cleaning up {len(created_groups)} created dynamic user group objects"
            )
            cleanup_dynamic_user_group_objects(user_groups, created_groups)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total dynamic user group objects created: {object_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(f"Average time per object: {execution_time / max(object_count, 1):.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some dynamic user group objects may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
