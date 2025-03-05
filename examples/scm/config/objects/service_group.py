#!/usr/bin/env python3
"""
Comprehensive examples of working with Service Group objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Service Group object configurations and operations commonly 
used in enterprise networks, including:

1. Service Group Object Types:
   - Basic service groups with built-in services
   - Mixed service groups with custom and built-in services
   - Hierarchical service groups (referencing other groups)

2. Operational examples:
   - Creating service group objects
   - Searching and filtering service group objects
   - Updating service group object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with service group object details
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
   - SKIP_CLEANUP=true: Set this to preserve created service group objects for manual inspection
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
from scm.config.objects import ServiceGroup
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
logger = logging.getLogger("service_group_example")


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


def create_basic_service_group(service_groups, folder="Texas"):
    """
    Create a service group with basic web services.
    
    This function demonstrates creating a standard service group with common 
    built-in service references, like HTTP and HTTPS.
    
    Args:
        service_groups: The ServiceGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceGroupResponseModel: The created service group object, or None if creation failed
    """
    log_operation_start("Creating basic service group")

    # Generate a unique service group name with timestamp to avoid conflicts
    service_group_name = f"web-services-{uuid.uuid4().hex[:6]}"
    log_info(f"Service group name: {service_group_name}")

    # First, get existing services from the environment
    log_info("Looking up existing services to use in the service group...")
    from scm.config.objects import Service
    service_manager = Service(service_groups.api_client)
    
    try:
        # Get services from the same folder
        existing_services = service_manager.list(folder=folder)
        log_info(f"Found {len(existing_services)} services in folder '{folder}'")
        
        # If we didn't find any services, we need to use custom service names
        # Or create services first before creating groups
        if not existing_services:
            log_warning(f"No existing services found in folder '{folder}'")
            log_info("Creating service group with custom service references that must exist")
            # Use custom service names that might exist in the environment
            service_members = ["custom-http", "custom-https"]
            log_info(f"Using custom service references: {', '.join(service_members)}")
        else:
            # Use the first two services we found
            service_members = [service.name for service in existing_services[:2]]
            log_info(f"Using existing services: {', '.join(service_members)}")
    except Exception as e:
        log_warning(f"Error listing services: {str(e)}")
        log_info("Falling back to custom service references that must exist")
        service_members = ["custom-http", "custom-https"]
    
    # Look up existing tags to use
    from scm.config.objects import Tag
    try:
        tag_manager = Tag(service_groups.api_client)
        # Get tags from the same folder
        existing_tags = tag_manager.list(folder=folder)
        log_info(f"Found {len(existing_tags)} tags in folder '{folder}'")
        
        if existing_tags and len(existing_tags) > 1:
            # Use up to 2 tags
            tag_count = min(2, len(existing_tags))
            tag_members = [tag.name for tag in existing_tags[:tag_count]]
            log_info(f"Using existing tags: {', '.join(tag_members)}")
        else:
            # Create service group with default tag that must exist in your environment
            log_warning(f"No existing tags found in folder '{folder}'")
            log_info("Will use 'Automation' tag that must exist in your environment")
            tag_members = ["Automation"]  # This must be an existing tag in the environment
    except Exception as e:
        log_warning(f"Error listing tags: {str(e)}")
        log_info("Falling back to 'Automation' tag that must exist in your environment")
        tag_members = ["Automation"]  # This must be an existing tag in the environment
    
    # Create the service group configuration
    basic_group_config = {
        "name": service_group_name,
        "description": "Standard web services group",
        "folder": folder,  # Use the provided folder name
        "tag": tag_members,
        "members": service_members
    }

    log_info("Configuration details:")
    log_info(f"  - Members: {', '.join(basic_group_config['members'])}")
    log_info(f"  - Tags: {', '.join(basic_group_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = service_groups.create(basic_group_config)
        log_success(f"Created service group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Basic service group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Service group name conflict", e.message)
        log_info("Try using a different service group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating service group", str(e))

    return None


def create_mixed_service_group(service_groups, folder="Texas"):
    """
    Create a service group with a mix of standard and custom services.
    
    This function demonstrates creating a service group that references both 
    standard built-in services and custom services that might exist in your environment.
    
    Args:
        service_groups: The ServiceGroup manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceGroupResponseModel: The created service group object, or None if creation failed
    """
    log_operation_start("Creating mixed service group")

    # Generate a unique service group name with timestamp to avoid conflicts
    service_group_name = f"mixed-services-{uuid.uuid4().hex[:6]}"
    log_info(f"Service group name: {service_group_name}")

    # First, get existing services from the environment
    log_info("Looking up existing services to use in the service group...")
    from scm.config.objects import Service
    service_manager = Service(service_groups.api_client)
    
    try:
        # Get services from the same folder
        existing_services = service_manager.list(folder=folder)
        log_info(f"Found {len(existing_services)} services in folder '{folder}'")
        
        # If we didn't find any services, we need to use custom service names
        if not existing_services:
            log_warning(f"No existing services found in folder '{folder}'")
            log_info("Creating service group with custom service references that must exist")
            # Use custom service names that might exist in the environment
            service_members = ["custom-http", "custom-https", "custom-ssh", "custom-dns"]
            log_info(f"Using custom service references: {', '.join(service_members)}")
        else:
            # Use up to 4 services that we found
            service_count = min(4, len(existing_services))
            service_members = [service.name for service in existing_services[:service_count]]
            log_info(f"Using existing services: {', '.join(service_members)}")
    except Exception as e:
        log_warning(f"Error listing services: {str(e)}")
        log_info("Falling back to custom service references that must exist")
        service_members = ["custom-http", "custom-https", "custom-ssh", "custom-dns"]
    
    # Look up existing tags to use
    from scm.config.objects import Tag
    try:
        tag_manager = Tag(service_groups.api_client)
        # Get tags from the same folder
        existing_tags = tag_manager.list(folder=folder)
        log_info(f"Found {len(existing_tags)} tags in folder '{folder}'")
        
        if existing_tags and len(existing_tags) > 1:
            # Use up to 2 tags
            tag_count = min(2, len(existing_tags))
            tag_members = [tag.name for tag in existing_tags[:tag_count]]
            log_info(f"Using existing tags: {', '.join(tag_members)}")
        else:
            # Create service group with default tag that must exist in your environment
            log_warning(f"No existing tags found in folder '{folder}'")
            log_info("Will use 'Automation' tag that must exist in your environment")
            tag_members = ["Automation"]  # This must be an existing tag in the environment
    except Exception as e:
        log_warning(f"Error listing tags: {str(e)}")
        log_info("Falling back to 'Automation' tag that must exist in your environment")
        tag_members = ["Automation"]  # This must be an existing tag in the environment
    
    # Create the service group configuration with the services we found or fallback values
    mixed_group_config = {
        "name": service_group_name,
        "description": "Mixed standard and custom services",
        "folder": folder,  # Use the provided folder name
        "tag": tag_members,
        "members": service_members
    }

    log_info("Configuration details:")
    log_info(f"  - Members: {', '.join(mixed_group_config['members'])}")
    log_info(f"  - Tags: {', '.join(mixed_group_config['tag'])}")
    log_info("  - Note: All service references must exist in your environment")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = service_groups.create(mixed_group_config)
        log_success(f"Created service group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Mixed service group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Service group name conflict", e.message)
        log_info("Try using a different service group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
            log_info("Ensure all custom services exist in your environment")
    except Exception as e:
        log_error(f"Unexpected error creating service group", str(e))

    return None


def create_hierarchical_service_group(service_groups, basic_group_name, folder="Texas"):
    """
    Create a hierarchical service group that includes other service groups.
    
    This function demonstrates creating a service group that references 
    both individual services and other service groups, creating a hierarchy.
    
    Args:
        service_groups: The ServiceGroup manager instance
        basic_group_name: Name of an existing service group to include in this group
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceGroupResponseModel: The created service group object, or None if creation failed
    """
    log_operation_start("Creating hierarchical service group")

    # Generate a unique service group name with timestamp to avoid conflicts
    service_group_name = f"hierarchical-services-{uuid.uuid4().hex[:6]}"
    log_info(f"Service group name: {service_group_name}")

    # First, get existing services from the environment
    log_info("Looking up existing services to use in the service group...")
    from scm.config.objects import Service
    service_manager = Service(service_groups.api_client)
    
    try:
        # Get services from the same folder
        existing_services = service_manager.list(folder=folder)
        log_info(f"Found {len(existing_services)} services in folder '{folder}'")
        
        # If we didn't find any services, we need to use custom service names
        if not existing_services:
            log_warning(f"No existing services found in folder '{folder}'")
            log_info("Creating service group with custom service references that must exist")
            # Use custom service names that might exist in the environment
            service_members = [basic_group_name, "custom-dns", "custom-ftp"]
            log_info(f"Using custom service references: {', '.join(service_members)}")
        else:
            # Use up to 2 services that we found plus the basic group name
            service_count = min(2, len(existing_services))
            service_members = [basic_group_name] + [service.name for service in existing_services[:service_count]]
            log_info(f"Using service group and existing services: {', '.join(service_members)}")
    except Exception as e:
        log_warning(f"Error listing services: {str(e)}")
        log_info("Falling back to custom service references that must exist")
        service_members = [basic_group_name, "custom-dns", "custom-ftp"]
    
    # Look up existing tags to use
    from scm.config.objects import Tag
    try:
        tag_manager = Tag(service_groups.api_client)
        # Get tags from the same folder
        existing_tags = tag_manager.list(folder=folder)
        log_info(f"Found {len(existing_tags)} tags in folder '{folder}'")
        
        if existing_tags and len(existing_tags) > 1:
            # Use up to 2 tags
            tag_count = min(2, len(existing_tags))
            tag_members = [tag.name for tag in existing_tags[:tag_count]]
            log_info(f"Using existing tags: {', '.join(tag_members)}")
        else:
            # Create service group with default tag that must exist in your environment
            log_warning(f"No existing tags found in folder '{folder}'")
            log_info("Will use 'Automation' tag that must exist in your environment")
            tag_members = ["Automation"]  # This must be an existing tag in the environment
    except Exception as e:
        log_warning(f"Error listing tags: {str(e)}")
        log_info("Falling back to 'Automation' tag that must exist in your environment")
        tag_members = ["Automation"]  # This must be an existing tag in the environment
    
    # Create the service group configuration with a reference to another group
    hierarchical_group_config = {
        "name": service_group_name,
        "description": "Hierarchical group including other service groups",
        "folder": folder,  # Use the provided folder name
        "tag": tag_members,
        "members": service_members
    }

    log_info("Configuration details:")
    log_info(f"  - Members: {', '.join(hierarchical_group_config['members'])}")
    log_info(f"  - Tags: {', '.join(hierarchical_group_config['tag'])}")
    log_info(f"  - References group: {basic_group_name}")
    log_info("  - Note: All service references must exist in your environment")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_group = service_groups.create(hierarchical_group_config)
        log_success(f"Created service group: {new_group.name}")
        log_info(f"  - Object ID: {new_group.id}")
        log_info(f"  - Members: {', '.join(new_group.members)}")
        log_operation_complete(
            "Hierarchical service group creation", f"Group: {new_group.name}"
        )
        return new_group
    except NameNotUniqueError as e:
        log_error(f"Service group name conflict", e.message)
        log_info("Try using a different service group name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service group data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
            log_info(f"Ensure the referenced group '{basic_group_name}' exists")
    except Exception as e:
        log_error(f"Unexpected error creating service group", str(e))

    return None


def fetch_and_update_service_group(service_groups, group_id):
    """
    Fetch a service group object by ID and update its members and tags.
    
    This function demonstrates how to:
    1. Retrieve an existing service group object using its ID
    2. Modify object properties (members and tags)
    3. Submit the updated object back to the SCM API
    
    Args:
        service_groups: The ServiceGroup manager instance
        group_id: The UUID of the service group object to update
        
    Returns:
        ServiceGroupResponseModel: The updated service group object, or None if update failed
    """
    logger.info(f"Fetching and updating service group with ID: {group_id}")

    try:
        # Fetch the service group
        group = service_groups.get(group_id)
        logger.info(f"Found service group: {group.name}")
        
        # First let's look up existing services to use for the new member
        from scm.config.objects import Service
        service_manager = Service(service_groups.api_client)
        
        # Get folder from the service group
        folder = group.folder if hasattr(group, "folder") else None
        if not folder:
            logger.error("Could not determine folder for service group")
            return None
        
        try:
            # Get services from the same folder
            existing_services = service_manager.list(folder=folder)
            logger.info(f"Found {len(existing_services)} services in folder '{folder}'")
            
            if existing_services and len(existing_services) > 0:
                # Get a service that's not already in the group members
                new_service = None
                for service in existing_services:
                    if service.name not in group.members:
                        new_service = service.name
                        break
                
                if new_service:
                    # Add the new service to the members list
                    group.members = group.members + [new_service]
                    logger.info(f"Adding {new_service} to members list")
                else:
                    logger.info("All available services are already in the group")
            else:
                logger.warning(f"No existing services found in folder '{folder}'")
        except Exception as e:
            logger.warning(f"Error listing services: {str(e)}")
        
        # Look up existing tags to use for the update
        from scm.config.objects import Tag
        try:
            tag_manager = Tag(service_groups.api_client)
            # Get tags from the same folder
            existing_tags = tag_manager.list(folder=folder)
            logger.info(f"Found {len(existing_tags)} tags in folder '{folder}'")
            
            if existing_tags and len(existing_tags) > 0:
                # Get a tag that's not already in the group tag list
                new_tag = None
                for tag in existing_tags:
                    if not group.tag or tag.name not in group.tag:
                        new_tag = tag.name
                        break
                
                if new_tag:
                    # Add the new tag to the tag list
                    group.tag = (group.tag or []) + [new_tag]
                    logger.info(f"Adding tag '{new_tag}' to service group")
                else:
                    logger.info("All available tags are already associated with the group")
            else:
                logger.warning(f"No existing tags found in folder '{folder}'")
                # Add a custom tag if it exists in your environment
                group.tag = (group.tag or []) + ["Automation"]
                logger.info("Adding 'Automation' tag to service group")
        except Exception as e:
            logger.warning(f"Error listing tags: {str(e)}")
            # Add a custom tag if it exists in your environment
            group.tag = (group.tag or []) + ["Automation"]
            logger.info("Adding 'Automation' tag to service group")

        # Perform the update
        updated_group = service_groups.update(group)
        logger.info(f"Updated service group: {updated_group.name}")
        logger.info(f"New members list: {', '.join(updated_group.members)}")
        logger.info(f"New tags: {', '.join(updated_group.tag) if updated_group.tag else 'None'}")
        return updated_group

    except NotFoundError as e:
        logger.error(f"Service group not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid service group update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_service_groups(service_groups):
    """
    List and filter service group objects.
    
    This function demonstrates how to:
    1. List all service group objects in a folder
    2. Filter service group objects by various criteria
    3. Display detailed information about each object
    
    Args:
        service_groups: The ServiceGroup manager instance
        
    Returns:
        list: All retrieved service group objects
    """
    logger.info("Listing and filtering service group objects")

    # List all service group objects in the Texas folder
    all_groups = service_groups.list(folder="Texas")
    logger.info(f"Found {len(all_groups)} service group objects in the Texas folder")

    # Filter by tag
    automation_tagged = service_groups.list(folder="Texas", tags=["Automation"])
    logger.info(f"Found {len(automation_tagged)} service groups with 'Automation' tag")

    # Filter by member values
    try:
        http_groups = service_groups.list(folder="Texas", values=["HTTP"])
        logger.info(f"Found {len(http_groups)} service groups containing 'HTTP'")
        
        https_groups = service_groups.list(folder="Texas", values=["HTTPS"])
        logger.info(f"Found {len(https_groups)} service groups containing 'HTTPS'")
    except Exception as e:
        logger.error(f"Filtering by values failed: {str(e)}")

    # Print details of service groups
    logger.info("\nDetails of service group objects:")
    for group in all_groups[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Service Group: {group.name}")
        logger.info(f"    ID: {group.id}")
        logger.info(f"    Description: {group.description if hasattr(group, 'description') else 'None'}")
        logger.info(f"    Tags: {group.tag}")
        logger.info(f"    Members: {', '.join(group.members)}")
        logger.info("")

    return all_groups


def cleanup_service_group_objects(service_groups, group_ids):
    """
    Delete the service group objects created in this example.
    
    Args:
        service_groups: The ServiceGroup manager instance
        group_ids: List of service group object IDs to delete
    """
    logger.info("Cleaning up service group objects")

    # First, identify any hierarchical relationships between groups
    hierarchical_relationships = {}
    try:
        # Get all groups to analyze relationships
        for group_id in group_ids:
            try:
                group = service_groups.get(group_id)
                
                # Check if this group references other groups
                for member in group.members:
                    # Check if this member is a reference to another group in our list
                    for other_id in group_ids:
                        try:
                            other_group = service_groups.get(other_id)
                            if member == other_group.name:
                                # This group references another group
                                if group_id not in hierarchical_relationships:
                                    hierarchical_relationships[group_id] = []
                                hierarchical_relationships[group_id].append(other_id)
                                logger.info(f"Found hierarchical relationship: {group.name} depends on {other_group.name}")
                        except:
                            pass
            except:
                pass
    except Exception as e:
        logger.warning(f"Error analyzing group relationships: {str(e)}")
    
    # Sort group_ids so that groups referencing other groups are deleted first
    sorted_ids = []
    remaining_ids = group_ids.copy()
    
    # First add all groups that reference other groups
    for group_id in hierarchical_relationships.keys():
        if group_id in remaining_ids:
            sorted_ids.append(group_id)
            remaining_ids.remove(group_id)
    
    # Then add all remaining groups
    sorted_ids.extend(remaining_ids)
    
    # Delete groups in the sorted order
    for group_id in sorted_ids:
        try:
            service_groups.delete(group_id)
            logger.info(f"Deleted service group with ID: {group_id}")
        except NotFoundError as e:
            logger.error(f"Service group not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting service group: {str(e)}")
            # If deletion fails, log a warning and continue with other groups
            logger.warning("This error may occur if other groups reference this service group. You may need to delete dependent groups manually.")


def create_bulk_service_group_objects(service_groups, folder="Texas"):
    """
    Create multiple service group objects in a batch.
    
    This function demonstrates creating multiple service group objects in a batch,
    which is useful for setting up multiple service groups at once.
    
    Args:
        service_groups: The ServiceGroup manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created service group objects, or empty list if creation failed
    """
    logger.info("Creating a batch of service group objects")

    # First, get existing services from the environment
    log_info("Looking up existing services to use in the service groups...")
    from scm.config.objects import Service
    service_manager = Service(service_groups.api_client)
    
    try:
        # Get services from the same folder
        existing_services = service_manager.list(folder=folder)
        log_info(f"Found {len(existing_services)} services in folder '{folder}'")
        
        # Extract service names for use in our service groups
        service_names = []
        if existing_services:
            service_names = [service.name for service in existing_services]
            log_info(f"Found these services: {', '.join(service_names[:5])}{'...' if len(service_names) > 5 else ''}")
        else:
            log_warning(f"No existing services found in folder '{folder}'")
            log_info("Will use custom service names that must exist in your environment")
            # Create a list of fallback custom service names
            service_names = [
                "custom-http", "custom-https", "custom-http-alt", 
                "custom-smtp", "custom-imap", "custom-pop3",
                "custom-ssh", "custom-rdp", "custom-telnet",
                "custom-dns", "custom-dns-tls"
            ]
    except Exception as e:
        log_warning(f"Error listing services: {str(e)}")
        log_info("Falling back to custom service references that must exist")
        service_names = [
            "custom-http", "custom-https", "custom-http-alt", 
            "custom-smtp", "custom-imap", "custom-pop3",
            "custom-ssh", "custom-rdp", "custom-telnet",
            "custom-dns", "custom-dns-tls"
        ]
    
    # Get different subsets of services for different groups
    # Use the services we found for all groups to ensure they exist
    # If we only have a few services, use them repeatedly
    if len(service_names) >= 3:
        web_services = service_names[:3]
        mail_services = service_names[:3]  # Use same services to avoid errors
        remote_services = service_names[:3]  # Use same services to avoid errors
        dns_services = service_names[:3]  # Use same services to avoid errors
    elif len(service_names) > 0:
        # If we have at least one service, use it repeatedly
        web_services = service_names
        mail_services = service_names
        remote_services = service_names
        dns_services = service_names
    else:
        # Fallback to custom names, but these likely won't work unless they exist
        log_warning("No existing services found, bulk groups might fail to create")
        web_services = ["custom-http", "custom-https", "custom-http-alt"]
        mail_services = ["custom-smtp", "custom-imap", "custom-pop3"]
        remote_services = ["custom-ssh", "custom-rdp", "custom-telnet"]
        dns_services = ["custom-dns", "custom-dns-tls"]
    
    # Look up existing tags to use
    from scm.config.objects import Tag
    try:
        tag_manager = Tag(service_groups.api_client)
        # Get tags from the same folder
        existing_tags = tag_manager.list(folder=folder)
        log_info(f"Found {len(existing_tags)} tags in folder '{folder}'")
        
        if existing_tags and len(existing_tags) > 0:
            # Get tag names
            tag_names = [tag.name for tag in existing_tags]
            log_info(f"Found these tags: {', '.join(tag_names[:5])}{'...' if len(tag_names) > 5 else ''}")
            # Use single tag for all service groups
            tag_to_use = [tag_names[0]]
            log_info(f"Using tag: {tag_to_use[0]}")
        else:
            # Create service group with default tag that must exist in your environment
            log_warning(f"No existing tags found in folder '{folder}'")
            log_info("Will use 'Automation' tag that must exist in your environment")
            tag_to_use = ["Automation"]  # This must be an existing tag in the environment
    except Exception as e:
        log_warning(f"Error listing tags: {str(e)}")
        log_info("Falling back to 'Automation' tag that must exist in your environment")
        tag_to_use = ["Automation"]  # This must be an existing tag in the environment
    
    # Define a list of service group objects to create
    group_configs = [
        {
            "name": f"bulk-web-{uuid.uuid4().hex[:6]}",
            "description": "Web services group",
            "folder": folder,
            "tag": tag_to_use,
            "members": web_services
        },
        {
            "name": f"bulk-mail-{uuid.uuid4().hex[:6]}",
            "description": "Mail services group",
            "folder": folder,
            "tag": tag_to_use,
            "members": mail_services
        },
        {
            "name": f"bulk-remote-{uuid.uuid4().hex[:6]}",
            "description": "Remote access services group",
            "folder": folder,
            "tag": tag_to_use,
            "members": remote_services
        },
        {
            "name": f"bulk-dns-{uuid.uuid4().hex[:6]}",
            "description": "DNS services group",
            "folder": folder,
            "tag": tag_to_use,
            "members": dns_services
        }
    ]
    
    log_info("Prepared bulk service group configurations:")
    for config in group_configs:
        log_info(f"  - {config['name']}: {', '.join(config['members'])}")

    created_groups = []

    # Create each service group object
    for group_config in group_configs:
        try:
            new_group = service_groups.create(group_config)
            logger.info(
                f"Created service group: {new_group.name} with ID: {new_group.id}"
            )
            created_groups.append(new_group.id)
        except Exception as e:
            logger.error(f"Error creating service group {group_config['name']}: {str(e)}")

    return created_groups


def generate_service_group_report(service_groups, group_ids, execution_time):
    """
    Generate a comprehensive CSV report of all service group objects created by the script.
    
    This function fetches detailed information about each service group object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        service_groups: The ServiceGroup manager instance used to fetch object details
        group_ids: List of service group object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"service_group_objects_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Description", 
        "Members", 
        "Member Count", 
        "Tags",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each service group object
    group_data = []
    for idx, group_id in enumerate(group_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(group_ids) - 1:
            log_info(f"Processing service group {idx + 1} of {len(group_ids)}")
            
        try:
            # Get the service group details
            group = service_groups.get(group_id)
            
            # Add group data
            group_data.append([
                group.id,
                group.name,
                group.description if hasattr(group, "description") and group.description else "None",
                ", ".join(group.members) if group.members else "None",
                len(group.members) if group.members else 0,
                ", ".join(group.tag) if group.tag else "None",
                group.created_on.strftime("%Y-%m-%d %H:%M:%S") if hasattr(group, "created_on") and group.created_on else "Unknown",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for service group ID {group_id}", str(e))
            # Add minimal info for groups that couldn't be retrieved
            group_data.append([
                group_id, 
                "ERROR", 
                "Failed to retrieve group details", 
                "ERROR",
                "ERROR", 
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
            fallback_file = f"service_group_objects_{timestamp}.csv"
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
    Parse command-line arguments for the service group example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which service group object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Service Group Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created service group objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--basic", 
        action="store_true",
        help="Create basic service group examples"
    )
    object_group.add_argument(
        "--mixed", 
        action="store_true", 
        help="Create mixed service group examples"
    )
    object_group.add_argument(
        "--hierarchical", 
        action="store_true",
        help="Create hierarchical service group examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk service group examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all service group object types (default behavior)"
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
    Execute the comprehensive set of service group object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of service group objects (basic, mixed, hierarchical)
    4. Update an existing service group object to demonstrate modification capabilities
    5. List and filter service group objects to show search functionality
    6. Generate a detailed CSV report of all created service group objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created service group objects (don't delete them)
        --basic: Create only basic service group examples
        --mixed: Create only mixed service group examples
        --hierarchical: Create only hierarchical service group examples
        --bulk: Create only bulk service group examples
        --all: Create all service group object types (default behavior)
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
    create_all = args.all or not (args.basic or args.mixed or args.hierarchical or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize ServiceGroup object
        log_section("SERVICE GROUP OBJECT CONFIGURATION")
        log_operation_start("Initializing ServiceGroup object manager")
        service_groups = ServiceGroup(client)
        log_operation_complete("ServiceGroup object manager initialization")

        # Create various service group objects
        created_groups = []
        basic_group_name = None  # Will be set if we create a basic group

        # Basic Service Group objects
        if create_all or args.basic:
            log_section("BASIC SERVICE GROUP OBJECTS")
            log_info("Creating basic service group object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a basic service group with web services
            basic_group = create_basic_service_group(service_groups, folder_name)
            if basic_group:
                created_groups.append(basic_group.id)
                basic_group_name = basic_group.name
                object_count += 1

            log_success(f"Created {len(created_groups)} basic service group objects so far")

        # Mixed Service Group objects
        if create_all or args.mixed:
            log_section("MIXED SERVICE GROUP OBJECTS")
            log_info("Creating mixed service group object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a mixed service group with standard and custom services
            mixed_group = create_mixed_service_group(service_groups, folder_name)
            if mixed_group:
                created_groups.append(mixed_group.id)
                object_count += 1

            log_success(f"Created mixed service group objects")

        # Hierarchical Service Group objects
        if (create_all or args.hierarchical) and basic_group_name:
            log_section("HIERARCHICAL SERVICE GROUP OBJECTS")
            log_info("Creating hierarchical service group object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a hierarchical service group referencing the basic group
            hierarchical_group = create_hierarchical_service_group(service_groups, basic_group_name, folder_name)
            if hierarchical_group:
                created_groups.append(hierarchical_group.id)
                object_count += 1

            log_success(f"Created hierarchical service group objects")
        elif (create_all or args.hierarchical) and not basic_group_name:
            log_warning("Skipping hierarchical group creation - no basic group was created successfully")

        # Bulk Service Group object creation
        if create_all or args.bulk:
            log_section("BULK SERVICE GROUP OBJECTS")
            log_info("Creating multiple service group objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk service group objects
            bulk_group_ids = create_bulk_service_group_objects(service_groups, folder_name)
            if bulk_group_ids:
                created_groups.extend(bulk_group_ids)
                object_count += len(bulk_group_ids)
                log_success(f"Created {len(bulk_group_ids)} bulk service group objects")

        # Update one of the objects
        if created_groups:
            log_section("UPDATING SERVICE GROUP OBJECTS")
            log_info("Demonstrating how to update existing service group objects")
            updated_group = fetch_and_update_service_group(service_groups, created_groups[0])

        # List and filter service group objects
        log_section("LISTING AND FILTERING SERVICE GROUP OBJECTS")
        log_info("Demonstrating how to search and filter service group objects")
        all_groups = list_and_filter_service_groups(service_groups)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_groups and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating service group objects CSV report")
            report_file = generate_service_group_report(service_groups, created_groups, execution_time_so_far)
            if report_file:
                log_success(f"Generated service group objects report: {report_file}")
                log_info(f"The report contains details of all {len(created_groups)} service group objects created")
            else:
                log_error("Failed to generate service group objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No service group objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_groups)} service group objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_groups)} created service group objects")
            cleanup_service_group_objects(service_groups, created_groups)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total service group objects created: {object_count}")
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
        log_info("Note: Some service group objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()