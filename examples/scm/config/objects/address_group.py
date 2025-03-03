#!/usr/bin/env python3
"""
Comprehensive examples of working with Address Group objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Address Group object configurations and operations commonly 
used in enterprise networks, including:

1. Address Group Types:
   - Static address groups - explicitly defined member addresses
   - Dynamic address groups - membership based on tag matching
   - Nested groups - groups containing other groups

2. Operational examples:
   - Creating address group objects
   - Searching and filtering address groups
   - Updating address group configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with group object details
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
   - SKIP_CLEANUP=true: Set this to preserve created objects for manual inspection
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
from scm.config.objects import Address, AddressGroup
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError,
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
logger = logging.getLogger("address_group_example")


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


def create_address_objects(address_manager, folder="Texas"):
    """
    Create address objects to be used in address groups.
    
    This function creates several address objects that will be used as members
    in the address groups we create later.
    
    Args:
        address_manager: The Address manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of created address objects, or empty list if creation failed
    """
    log_operation_start("Creating address objects for group membership")
    
    created_addresses = []
    
    # Define the address objects to create
    address_configs = [
        {
            "name": f"server-network-{uuid.uuid4().hex[:6]}",
            "description": "Server network segment",
            "folder": folder,
            "tag": ["Automation", "Servers"],
            "ip_netmask": "10.1.0.0/24",
        },
        {
            "name": f"workstation-network-{uuid.uuid4().hex[:6]}",
            "description": "Workstation network segment",
            "folder": folder,
            "tag": ["Automation", "Workstations"],
            "ip_netmask": "10.2.0.0/24",
        },
        {
            "name": f"guest-network-{uuid.uuid4().hex[:6]}",
            "description": "Guest network segment",
            "folder": folder,
            "tag": ["Automation", "Guest"],
            "ip_netmask": "10.3.0.0/24",
        },
        {
            "name": f"web-server-{uuid.uuid4().hex[:6]}",
            "description": "Web server host",
            "folder": folder,
            "tag": ["Automation", "Web"],
            "ip_netmask": "192.168.1.10/32",
        },
        {
            "name": f"db-server-{uuid.uuid4().hex[:6]}",
            "description": "Database server host",
            "folder": folder,
            "tag": ["Automation", "Database"],
            "ip_netmask": "192.168.1.20/32",
        }
    ]
    
    # Create each address object
    for i, config in enumerate(address_configs):
        log_info(f"Creating address object {i+1}/{len(address_configs)}: {config['name']}")
        
        try:
            new_address = address_manager.create(config)
            log_success(f"Created address object: {new_address.name}")
            log_info(f"  - Object ID: {new_address.id}")
            log_info(f"  - Value: {new_address.ip_netmask}")
            created_addresses.append(new_address)
        except NameNotUniqueError as e:
            log_error(f"Address name conflict", e.message)
        except InvalidObjectError as e:
            log_error(f"Invalid address data", e.message)
            if e.details:
                log_info(f"Error details: {e.details}")
        except Exception as e:
            log_error(f"Unexpected error creating address object", str(e))
    
    log_operation_complete(
        "Address object creation", f"Created {len(created_addresses)} address objects"
    )
    return created_addresses


def create_static_address_group(group_manager, address_objects, folder="Texas"):
    """
    Create a static address group with the given address objects as members.
    
    This function demonstrates creating a static address group, which has
    explicitly defined member addresses.
    
    Args:
        group_manager: The AddressGroup manager instance
        address_objects: List of address objects to include as members
        folder: Folder name in SCM to create the group in (default: "Texas")
        
    Returns:
        AddressGroupResponseModel: The created group, or None if creation failed
    """
    log_operation_start("Creating static address group")

    # Generate a unique group name with timestamp to avoid conflicts
    group_name = f"static-group-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")
    
    # Extract the names of the address objects
    member_names = [addr.name for addr in address_objects]
    
    # Create the group configuration
    static_group_config = {
        "name": group_name,
        "description": "Example static address group",
        "folder": folder,
        "tag": ["Automation", "Example"],
        "static": member_names,
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Static Address Group")
    log_info(f"  - Members: {', '.join(member_names)}")
    log_info(f"  - Tags: {', '.join(static_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = group_manager.create(static_group_config)
        log_success(f"Created static address group: {new_group.name}")
        log_info(f"  - Group ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_operation_complete(
            "Static address group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address group", str(e))

    return None


def create_dynamic_address_group(group_manager, folder="Texas"):
    """
    Create a dynamic address group that matches addresses based on tags.
    
    This function demonstrates creating a dynamic address group, which includes
    members based on tag matching criteria.
    
    Args:
        group_manager: The AddressGroup manager instance
        folder: Folder name in SCM to create the group in (default: "Texas")
        
    Returns:
        AddressGroupResponseModel: The created group, or None if creation failed
    """
    log_operation_start("Creating dynamic address group")

    # Generate a unique group name with timestamp to avoid conflicts
    group_name = f"dynamic-group-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")
    
    # Create a filter using tag matching
    # This will match any address with both the "Automation" and "Web" tags
    tag_filter = "'Automation' and 'Web'"
    
    # Create the group configuration
    dynamic_group_config = {
        "name": group_name,
        "description": "Example dynamic address group",
        "folder": folder,
        "tag": ["Automation", "Example"],
        "dynamic": {
            "filter": tag_filter
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Dynamic Address Group")
    log_info(f"  - Filter: {tag_filter}")
    log_info(f"  - Tags: {', '.join(dynamic_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = group_manager.create(dynamic_group_config)
        log_success(f"Created dynamic address group: {new_group.name}")
        log_info(f"  - Group ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_operation_complete(
            "Dynamic address group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address group", str(e))

    return None


def create_nested_address_group(group_manager, parent_groups, folder="Texas"):
    """
    Create a nested address group that contains other address groups.
    
    This function demonstrates creating a nested address group, which includes
    other address groups as members.
    
    Args:
        group_manager: The AddressGroup manager instance
        parent_groups: List of address group objects to include as members
        folder: Folder name in SCM to create the group in (default: "Texas")
        
    Returns:
        AddressGroupResponseModel: The created group, or None if creation failed
    """
    log_operation_start("Creating nested address group")

    # Generate a unique group name with timestamp to avoid conflicts
    group_name = f"nested-group-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")
    
    # Extract the names of the parent groups
    parent_names = [group.name for group in parent_groups]
    
    # Create the group configuration
    nested_group_config = {
        "name": group_name,
        "description": "Example nested address group",
        "folder": folder,
        "tag": ["Automation", "Example"],
        "static": parent_names,
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Nested Address Group")
    log_info(f"  - Parent Groups: {', '.join(parent_names)}")
    log_info(f"  - Tags: {', '.join(nested_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = group_manager.create(nested_group_config)
        log_success(f"Created nested address group: {new_group.name}")
        log_info(f"  - Group ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_operation_complete(
            "Nested address group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address group", str(e))

    return None


def create_complex_tag_filter_group(group_manager, folder="Texas"):
    """
    Create a dynamic address group with a complex tag filter expression.
    
    This function demonstrates creating a dynamic address group with a more
    complex tag filter expression using logical operators.
    
    Args:
        group_manager: The AddressGroup manager instance
        folder: Folder name in SCM to create the group in (default: "Texas")
        
    Returns:
        AddressGroupResponseModel: The created group, or None if creation failed
    """
    log_operation_start("Creating dynamic address group with complex filter")

    # Generate a unique group name with timestamp to avoid conflicts
    group_name = f"complex-filter-group-{uuid.uuid4().hex[:6]}"
    log_info(f"Group name: {group_name}")
    
    # Create a more complex filter using tag matching with logical operators
    # This will match addresses with the "Automation" tag AND either the "Servers" OR "Database" tags
    # Note: Fix syntax to ensure it's properly formatted - keep it simpler
    tag_filter = "'Automation' and ('Servers' or 'Database')"
    
    # Create the group configuration
    complex_group_config = {
        "name": group_name,
        "description": "Example dynamic address group with complex filter",
        "folder": folder,
        "tag": ["Automation", "Example"],
        "dynamic": {
            "filter": tag_filter
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Dynamic Address Group with Complex Filter")
    log_info(f"  - Filter: {tag_filter}")
    log_info(f"  - Tags: {', '.join(complex_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = group_manager.create(complex_group_config)
        log_success(f"Created complex filter group: {new_group.name}")
        log_info(f"  - Group ID: {new_group.id}")
        log_info(f"  - Description: {new_group.description}")
        log_operation_complete(
            "Complex filter group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Group name conflict", e.message)
        log_info("Try using a different group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address group", str(e))

    return None


# Note: This function was removed as address groups can only be static or dynamic, not both


def fetch_and_update_address_group(group_manager, group_id):
    """
    Fetch an address group by ID and update its description and static members.
    
    This function demonstrates how to:
    1. Retrieve an existing address group using its ID
    2. Modify group properties (description, static members)
    3. Submit the updated group back to the SCM API
    
    Args:
        group_manager: The AddressGroup manager instance
        group_id: The UUID of the address group to update
        
    Returns:
        AddressGroupResponseModel: The updated group, or None if update failed
    """
    logger.info(f"Fetching and updating address group with ID: {group_id}")

    try:
        # Fetch the group
        group = group_manager.get(group_id)
        logger.info(f"Found address group: {group.name}")

        # Update description
        original_description = group.description
        group.description = f"Updated: {original_description}"
        
        # Update tags if they exist
        if hasattr(group, "tag") and group.tag:
            if "Updated" not in group.tag:
                group.tag = group.tag + ["Updated"]
        
        # Add a member to static group if applicable
        if hasattr(group, "static") and group.static:
            logger.info(f"Original static members: {', '.join(group.static)}")
            # Note: In a real scenario, you would want to check if the address exists first
            # This is just for demonstration purposes
            logger.info("Would add additional members here if needed")

        # Perform the update
        updated_group = group_manager.update(group)
        logger.info(
            f"Updated address group: {updated_group.name} with description: {updated_group.description}"
        )
        return updated_group

    except NotFoundError as e:
        logger.error(f"Address group not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid address group update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_address_groups(group_manager):
    """
    List and filter address groups.
    
    This function demonstrates how to:
    1. List all address groups in a folder
    2. Filter address groups by various criteria
    3. Display detailed information about each group
    
    Args:
        group_manager: The AddressGroup manager instance
        
    Returns:
        list: All retrieved address groups
    """
    logger.info("Listing and filtering address groups")

    # List all address groups in the Texas folder
    all_groups = group_manager.list(folder="Texas")
    logger.info(f"Found {len(all_groups)} address groups in the Texas folder")

    # Filter by tag
    automation_tagged = group_manager.list(folder="Texas", tag=["Automation"])
    logger.info(f"Found {len(automation_tagged)} address groups with 'Automation' tag")

    # Filter by name pattern (where supported)
    try:
        static_groups = group_manager.list(folder="Texas", name="static")
        logger.info(f"Found {len(static_groups)} address groups with 'static' in the name")
    except Exception as e:
        logger.error(f"Filtering by name is not supported: {str(e)}")

    # Print details of groups
    logger.info("\nDetails of address groups:")
    for group in all_groups[:5]:  # Print details of up to 5 groups
        logger.info(f"  - Group: {group.name}")
        logger.info(f"    ID: {group.id}")
        logger.info(f"    Description: {group.description or 'None'}")
        logger.info(f"    Tags: {group.tag or 'None'}")
        
        # Determine group type and members/filter
        if hasattr(group, "static") and group.static:
            logger.info(f"    Type: Static Address Group")
            logger.info(f"    Members: {', '.join(group.static)}")
        elif hasattr(group, "dynamic") and group.dynamic:
            logger.info(f"    Type: Dynamic Address Group")
            filter_expr = group.dynamic.filter if hasattr(group.dynamic, "filter") else "N/A"
            logger.info(f"    Filter: {filter_expr}")
        else:
            logger.info(f"    Type: Unknown Group Type")
        
        logger.info("")

    return all_groups


def cleanup_address_objects(address_manager, address_ids):
    """
    Delete the address objects created in this example.
    
    This function will try multiple times to delete objects, giving groups
    time to be deleted first to resolve reference issues.
    
    Args:
        address_manager: The Address manager instance
        address_ids: List of address object IDs to delete
    """
    logger.info("Cleaning up address objects")
    
    # Keep track of successful deletions
    deleted_ids = set()
    
    # Try deletions with retries
    max_retries = 2
    for retry in range(max_retries):
        if retry > 0:
            logger.info(f"Retry attempt {retry} for remaining address objects...")
            # Wait a bit between retries to allow group deletions to complete
            import time
            time.sleep(2)
            
        # Try to delete each address that hasn't been deleted yet
        for address_id in address_ids:
            if address_id in deleted_ids:
                continue
                
            try:
                address_manager.delete(address_id)
                logger.info(f"Deleted address object with ID: {address_id}")
                deleted_ids.add(address_id)
            except NotFoundError as e:
                logger.error(f"Address object not found: {e.message}")
                deleted_ids.add(address_id)  # Consider it deleted if not found
            except ReferenceNotZeroError as e:
                logger.error(f"Address object still in use: {e.message}")
                logger.info("This usually means the address is referenced by another object (like a rule)")
                if retry == max_retries - 1:
                    logger.info(f"Skipping this object after {max_retries} attempts")
            except Exception as e:
                logger.error(f"Error deleting address object: {str(e)}")
    
    # Report results
    if len(deleted_ids) == len(address_ids):
        logger.info(f"Successfully deleted all {len(deleted_ids)} address objects")
    else:
        logger.info(f"Deleted {len(deleted_ids)} out of {len(address_ids)} address objects")
        logger.info(f"Some objects could not be deleted due to dependencies")


def cleanup_address_groups(group_manager, group_ids):
    """
    Delete the address groups created in this example.
    
    This function tries to handle nested dependencies by first sorting the group IDs
    to attempt to delete nested groups first, then the parent groups.
    
    Args:
        group_manager: The AddressGroup manager instance
        group_ids: List of address group IDs to delete
    """
    logger.info("Cleaning up address groups")
    
    # First try to identify nested groups to delete them first
    # Get details of all groups
    group_details = {}
    group_deletion_order = []
    
    # Try to gather information about all groups to determine deletion order
    for group_id in group_ids:
        try:
            group = group_manager.get(group_id)
            # Store info about the group
            group_details[group_id] = {
                "name": group.name,
                "is_nested": False  # Will mark as True if it contains other groups
            }
            
            # Look for groups that might be nested (static groups that contain other groups)
            if hasattr(group, "static") and group.static:
                # Check if any member might be another group
                for member in group.static:
                    if any(g.name == member for g in group_details.values()):
                        group_details[group_id]["is_nested"] = True
                        break
        except Exception:
            # If we can't get info, just add to the list to try deletion anyway
            group_details[group_id] = {"name": f"unknown-{group_id}", "is_nested": False}
    
    # First add groups that are nested (contain other groups)
    for group_id, details in group_details.items():
        if details["is_nested"]:
            group_deletion_order.append(group_id)
    
    # Then add the rest
    for group_id in group_ids:
        if group_id not in group_deletion_order:
            group_deletion_order.append(group_id)
    
    # Try to delete groups in the calculated order
    for group_id in group_deletion_order:
        try:
            group_manager.delete(group_id)
            logger.info(f"Deleted address group with ID: {group_id}")
        except NotFoundError as e:
            logger.error(f"Address group not found: {e.message}")
        except ReferenceNotZeroError as e:
            logger.error(f"Address group still in use: {e.message}")
            logger.info("This usually means the group is referenced by another object (like a rule or another group)")
            # Just note the issue and continue
            logger.info(f"Skipping this group and continuing with cleanup")
        except Exception as e:
            logger.error(f"Error deleting address group: {str(e)}")


def create_bulk_address_groups(group_manager, address_objects, folder="Texas"):
    """
    Create multiple address groups in a batch.
    
    This function demonstrates creating multiple address groups in a batch,
    which is useful for setting up multiple groups at once.
    
    Args:
        group_manager: The AddressGroup manager instance
        address_objects: List of address objects to use as members
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created address groups, or empty list if creation failed
    """
    logger.info("Creating a batch of address groups")
    
    # Make sure we have at least 5 address objects
    if len(address_objects) < 5:
        log_warning(f"Not enough address objects ({len(address_objects)}) for bulk creation example")
        return []

    # Define a list of group configurations
    group_configs = [
        {
            "name": f"servers-group-{uuid.uuid4().hex[:6]}",
            "description": "Server address group",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Servers"],
            "static": [address_objects[0].name, address_objects[1].name],
        },
        {
            "name": f"workstations-group-{uuid.uuid4().hex[:6]}",
            "description": "Workstation address group",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Workstations"],
            "static": [address_objects[2].name],
        },
        {
            "name": f"all-endpoints-group-{uuid.uuid4().hex[:6]}",
            "description": "All endpoints address group",
            "folder": folder,
            "tag": ["Automation", "Bulk"],  # Removed "Endpoints" as it's not a valid tag
            "static": [address_objects[0].name, address_objects[1].name, address_objects[2].name],
        },
        {
            "name": f"filter-web-group-{uuid.uuid4().hex[:6]}",
            "description": "Web servers filter group",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Web"],
            "dynamic": {
                "filter": "'Web' and 'Automation'"
            },
        }
    ]

    created_groups = []

    # Create each address group
    for group_config in group_configs:
        try:
            new_group = group_manager.create(group_config)
            logger.info(
                f"Created address group: {new_group.name} with ID: {new_group.id}"
            )
            created_groups.append(new_group.id)
        except Exception as e:
            logger.error(f"Error creating group {group_config['name']}: {str(e)}")

    return created_groups


def generate_address_group_report(group_manager, address_manager, group_ids, execution_time):
    """
    Generate a comprehensive CSV report of all address groups created by the script.
    
    This function fetches detailed information about each address group and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        group_manager: The AddressGroup manager instance used to fetch group details
        address_manager: The Address manager instance used to fetch address details if needed
        group_ids: List of address group IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"address_groups_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Group ID", 
        "Name",
        "Type",
        "Members/Filter", 
        "Description", 
        "Tags",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each address group
    group_data = []
    for idx, group_id in enumerate(group_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(group_ids) - 1:
            log_info(f"Processing group {idx + 1} of {len(group_ids)}")
            
        try:
            # Get the group details
            group = group_manager.get(group_id)
            
            # Determine group type and members/filter
            group_type = "Unknown"
            members_filter = "None"
            
            if hasattr(group, "static") and group.static:
                group_type = "Static Address Group"
                members_filter = ", ".join(group.static)
            elif hasattr(group, "dynamic") and group.dynamic:
                group_type = "Dynamic Address Group"
                filter_expr = group.dynamic.filter if hasattr(group.dynamic, "filter") else "N/A"
                members_filter = filter_expr
            
            # Add group data
            group_data.append([
                group.id,
                group.name,
                group_type,
                members_filter,
                group.description if group.description else "None",
                ", ".join(group.tag) if group.tag else "None",
                group.created_on.strftime("%Y-%m-%d %H:%M:%S") if hasattr(group, "created_on") and group.created_on else "Unknown",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for group ID {group_id}", str(e))
            # Add minimal info for groups that couldn't be retrieved
            group_data.append([
                group_id, 
                "ERROR", 
                "ERROR", 
                "ERROR",
                f"Failed to retrieve group details: {str(e)}", 
                "",
                "",
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
            writer.writerow(["Total Groups Processed", len(group_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"address_groups_{timestamp}.csv"
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
    Parse command-line arguments for the address group example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which address group types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Address Group Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created address objects and groups (don't delete them)"
    )
    
    # Group types to create
    group_type = parser.add_argument_group("Group Type Selection")
    group_type.add_argument(
        "--static", 
        action="store_true",
        help="Create static address group examples"
    )
    group_type.add_argument(
        "--dynamic", 
        action="store_true", 
        help="Create dynamic address group examples"
    )
    group_type.add_argument(
        "--nested", 
        action="store_true",
        help="Create nested address group examples"
    )
    group_type.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk address group examples"
    )
    group_type.add_argument(
        "--all", 
        action="store_true",
        help="Create all address group types (default behavior)"
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
    Execute the comprehensive set of address group examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create address objects to be used as group members
    4. Create various types of address groups (static, dynamic, nested)
    5. Update an existing address group to demonstrate modification capabilities
    6. List and filter address groups to show search functionality
    7. Generate a detailed CSV report of all created address groups
    8. Clean up created objects (unless skip_cleanup is enabled)
    9. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created objects (don't delete them)
        --static: Create only static address group examples
        --dynamic: Create only dynamic address group examples
        --nested: Create only nested address group examples
        --bulk: Create only bulk address group examples
        --all: Create all address group types (default behavior)
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
    group_count = 0
    
    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"
    
    # Determine which group types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.static or args.dynamic or args.nested or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    # Keep track of created objects for cleanup
    created_addresses = []
    created_address_ids = []
    created_groups = []
    created_group_ids = []

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Address and AddressGroup objects
        log_section("ADDRESS AND GROUP OBJECT CONFIGURATION")
        log_operation_start("Initializing Address and AddressGroup managers")
        addresses = Address(client)
        address_groups = AddressGroup(client)
        log_operation_complete("Address and AddressGroup managers initialization")

        # Create address objects for group membership
        log_section("ADDRESS OBJECT CREATION")
        log_info("Creating address objects to be used in groups")
        log_info(f"Using folder: {folder_name}")
        
        created_addresses = create_address_objects(addresses, folder_name)
        if created_addresses:
            created_address_ids = [addr.id for addr in created_addresses]
            object_count += len(created_addresses)
            log_success(f"Created {len(created_addresses)} address objects")
        else:
            log_error("Failed to create address objects - cannot continue with group creation")
            return

        # Static Address Group
        if create_all or args.static:
            log_section("STATIC ADDRESS GROUP")
            log_info("Creating static address group with explicit members")
            log_info(f"Using folder: {folder_name}")

            static_group = create_static_address_group(address_groups, created_addresses[:3], folder_name)
            if static_group:
                created_groups.append(static_group)
                created_group_ids.append(static_group.id)
                group_count += 1

        # Dynamic Address Group
        if create_all or args.dynamic:
            log_section("DYNAMIC ADDRESS GROUP")
            log_info("Creating dynamic address group with tag filter")
            log_info(f"Using folder: {folder_name}")

            dynamic_group = create_dynamic_address_group(address_groups, folder_name)
            if dynamic_group:
                created_groups.append(dynamic_group)
                created_group_ids.append(dynamic_group.id)
                group_count += 1
                
            # Complex filter group
            log_info("Creating dynamic address group with complex tag filter")
            complex_group = create_complex_tag_filter_group(address_groups, folder_name)
            if complex_group:
                created_groups.append(complex_group)
                created_group_ids.append(complex_group.id)
                group_count += 1
            
            # Note: Address groups are either static or dynamic, not both
            log_info("Note: Address groups can only be static or dynamic, not both")

        # Nested Address Group
        if create_all or args.nested:
            log_section("NESTED ADDRESS GROUP")
            log_info("Creating nested address group with other groups as members")
            log_info(f"Using folder: {folder_name}")
            
            if len(created_groups) >= 2:
                nested_group = create_nested_address_group(address_groups, created_groups[:2], folder_name)
                if nested_group:
                    created_groups.append(nested_group)
                    created_group_ids.append(nested_group.id)
                    group_count += 1
            else:
                log_warning("Not enough groups created to demonstrate nested groups")

        # Bulk Address Group Creation
        if create_all or args.bulk:
            log_section("BULK ADDRESS GROUPS")
            log_info("Creating multiple address groups in bulk")
            log_info(f"Using folder: {folder_name}")

            bulk_group_ids = create_bulk_address_groups(address_groups, created_addresses, folder_name)
            if bulk_group_ids:
                created_group_ids.extend(bulk_group_ids)
                group_count += len(bulk_group_ids)
                log_success(f"Created {len(bulk_group_ids)} bulk address groups")

        # Update one of the groups
        if created_groups:
            log_section("UPDATING ADDRESS GROUPS")
            log_info("Demonstrating how to update existing address groups")
            updated_group = fetch_and_update_address_group(address_groups, created_groups[0].id)

        # List and filter address groups
        log_section("LISTING AND FILTERING ADDRESS GROUPS")
        log_info("Demonstrating how to search and filter address groups")
        all_groups = list_and_filter_address_groups(address_groups)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are groups to report and report generation is not disabled
        if created_group_ids and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating address groups CSV report")
            report_file = generate_address_group_report(address_groups, addresses, created_group_ids, execution_time_so_far)
            if report_file:
                log_success(f"Generated address groups report: {report_file}")
                log_info(f"The report contains details of all {len(created_group_ids)} address groups created")
            else:
                log_error("Failed to generate address groups report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No address groups were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_group_ids)} address groups and {len(created_address_ids)} address objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            # Delete groups first, then addresses
            log_operation_start(f"Cleaning up {len(created_group_ids)} created address groups")
            cleanup_address_groups(address_groups, created_group_ids)
            
            log_operation_start(f"Cleaning up {len(created_address_ids)} created address objects")
            cleanup_address_objects(addresses, created_address_ids)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total address objects created: {object_count}")
        log_info(f"Total address groups created: {group_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(
            f"Average time per object: {execution_time/max(object_count + group_count, 1):.2f} seconds"
        )

    except AuthenticationError as e:
        log_error(f"Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some address objects and groups may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()