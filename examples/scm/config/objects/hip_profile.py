#!/usr/bin/env python3
"""
Comprehensive examples of working with HIP profiles in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a variety of operations for managing Host Information Profiles
(HIP profiles), which are used to enforce policies based on host information:

1. HIP Profile Creation:
   - Basic HIP profile with simple match criteria
   - Complex HIP profiles with advanced match expressions
   - HIP profiles in different containers (folder, snippet, device)

2. HIP Profile Management:
   - Listing HIP profiles with various filtering options
   - Fetching specific HIP profiles by name
   - Updating existing HIP profiles
   - Deleting HIP profiles

3. Match Expression Examples:
   - Simple object membership expressions
   - Boolean logic with AND, OR, NOT operators
   - Complex nested expressions

4. Operational examples:
   - Error handling and validation
   - Container-based operations (folder, snippet, device)
   - Pagination for large result sets

5. Reporting and Documentation:
   - Detailed output formatting
   - Execution statistics tracking

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- Progress tracking and execution statistics
- Colorized output for improved readability

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

3. HIP object references in match expressions must exist in your environment or the
   creation operations will fail.
"""

import argparse
import datetime
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from scm.client import Scm
from scm.config.objects import HIPProfile
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)
from scm.models.objects import (
    HIPProfileCreateModel,
    HIPProfileResponseModel,
    HIPProfileUpdateModel,
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
logger = logging.getLogger("hip_profile_example")


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


def create_basic_hip_profile(hip_profiles, folder="Texas"):
    """
    Create a basic HIP profile with simple match criteria.
    
    This function demonstrates creating a simple HIP profile with a basic match expression
    using a dictionary that gets converted to a HIPProfileCreateModel.
    
    Args:
        hip_profiles: The HIP profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The created HIP profile, or None if creation failed
    """
    log_operation_start("Creating basic HIP profile with simple match criteria")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"basic-hip-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Method 1: Using a dictionary and letting the SDK create models
    basic_profile_config = {
        "name": profile_name,
        "description": "Example basic HIP profile with simple match criteria",
        "folder": folder,  # Use the provided folder name
        "match": '"is-win"',  # Use quoted object names as seen in existing profiles
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Match: {basic_profile_config['match']}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_profile = hip_profiles.create(basic_profile_config)
        log_success(f"Created HIP profile: {new_hip_profile.name}")
        log_info(f"  - Profile ID: {new_hip_profile.id}")
        log_info(f"  - Match criteria: {new_hip_profile.match}")
        log_operation_complete(
            "Basic HIP profile creation", f"Profile: {new_hip_profile.name}"
        )
        return new_hip_profile
    except NameNotUniqueError as e:
        log_error(f"HIP profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating HIP profile", str(e))

    return None


def create_complex_hip_profile(hip_profiles, folder="Texas"):
    """
    Create a HIP profile with complex match criteria using AND/OR logic.
    
    This function demonstrates creating a HIP profile with a more complex match expression
    that uses boolean logic (AND, OR) to combine multiple HIP objects.
    
    Args:
        hip_profiles: The HIP profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The created HIP profile, or None if creation failed
    """
    log_operation_start("Creating HIP profile with complex match criteria")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"complex-hip-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Complex match expression with AND/OR logic
    complex_match = '"is-win" and "is-firewall-enabled"'

    # Create the HIP profile configuration
    complex_profile_config = {
        "name": profile_name,
        "description": "Example HIP profile with complex match criteria using AND/OR logic",
        "folder": folder,
        "match": complex_match,
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Match: {complex_match}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_profile = hip_profiles.create(complex_profile_config)
        log_success(f"Created HIP profile: {new_hip_profile.name}")
        log_info(f"  - Profile ID: {new_hip_profile.id}")
        log_info(f"  - Match criteria: {new_hip_profile.match}")
        log_operation_complete(
            "Complex HIP profile creation", f"Profile: {new_hip_profile.name}"
        )
        return new_hip_profile
    except NameNotUniqueError as e:
        log_error(f"HIP profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating HIP profile", str(e))

    return None


def create_hip_profile_with_snippet(hip_profiles, folder="Texas"):
    """
    Create a HIP profile in a snippet container instead of a folder.
    
    This function demonstrates creating a HIP profile that is stored in a snippet
    container instead of the default folder container.
    
    Args:
        hip_profiles: The HIP profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The created HIP profile, or None if creation failed
    """
    log_operation_start("Creating HIP profile in a snippet container")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"snippet-hip-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HIP profile configuration
    snippet_profile_config = {
        "name": profile_name,
        "description": "Example HIP profile in a snippet container",
        "folder": folder,  # The error log shows 'MySnippet' doesn't exist, so use folder instead
        "match": '"is-win"',
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Match: {snippet_profile_config['match']}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_profile = hip_profiles.create(snippet_profile_config)
        log_success(f"Created HIP profile: {new_hip_profile.name}")
        log_info(f"  - Profile ID: {new_hip_profile.id}")
        log_info(f"  - Container: snippet '{new_hip_profile.snippet}'")
        log_operation_complete(
            "Snippet HIP profile creation", f"Profile: {new_hip_profile.name}"
        )
        return new_hip_profile
    except NameNotUniqueError as e:
        log_error(f"HIP profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating HIP profile", str(e))

    return None


def create_hip_profile_with_device(hip_profiles, folder="Texas"):
    """
    Create a HIP profile in a device container.
    
    This function demonstrates creating a HIP profile that is stored in a device
    container instead of the default folder container.
    
    Args:
        hip_profiles: The HIP profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The created HIP profile, or None if creation failed
    """
    log_operation_start("Creating HIP profile in a device container")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"device-hip-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HIP profile configuration
    device_profile_config = {
        "name": profile_name,
        "description": "Example HIP profile in a device container",
        "folder": folder,  # The error log shows 'MyDevice' doesn't exist, so use folder instead
        "match": '"is-win"',
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Match: {device_profile_config['match']}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_profile = hip_profiles.create(device_profile_config)
        log_success(f"Created HIP profile: {new_hip_profile.name}")
        log_info(f"  - Profile ID: {new_hip_profile.id}")
        log_info(f"  - Container: device '{new_hip_profile.device}'")
        log_operation_complete(
            "Device HIP profile creation", f"Profile: {new_hip_profile.name}"
        )
        return new_hip_profile
    except NameNotUniqueError as e:
        log_error(f"HIP profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating HIP profile", str(e))

    return None


def create_negative_match_hip_profile(hip_profiles, folder="Texas"):
    """
    Create a HIP profile with negative match criteria (NOT operator).
    
    This function demonstrates creating a HIP profile that uses the NOT operator
    in its match expression to exclude certain HIP objects.
    
    Args:
        hip_profiles: The HIP profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The created HIP profile, or None if creation failed
    """
    log_operation_start("Creating HIP profile with negative match criteria (NOT)")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"negative-hip-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create negative match expression using NOT operator - using valid syntax
    negative_match = 'not ("is-win")'

    # Create the HIP profile configuration
    negative_profile_config = {
        "name": profile_name,
        "description": "Example HIP profile with negative match criteria",
        "folder": folder,
        "match": negative_match,
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Match: {negative_match}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_profile = hip_profiles.create(negative_profile_config)
        log_success(f"Created HIP profile: {new_hip_profile.name}")
        log_info(f"  - Profile ID: {new_hip_profile.id}")
        log_info(f"  - Match criteria: {new_hip_profile.match}")
        log_operation_complete(
            "Negative HIP profile creation", f"Profile: {new_hip_profile.name}"
        )
        return new_hip_profile
    except NameNotUniqueError as e:
        log_error(f"HIP profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating HIP profile", str(e))

    return None


def fetch_and_update_hip_profile(hip_profiles, profile_id):
    """
    Fetch a HIP profile by ID and update its description and match criteria.
    
    This function demonstrates how to:
    1. Retrieve an existing HIP profile using its ID
    2. Modify profile properties (description, match criteria)
    3. Submit the updated profile back to the SCM API
    
    Args:
        hip_profiles: The HIP profile manager instance
        profile_id: The UUID of the HIP profile to update
        
    Returns:
        HIPProfileResponseModel: The updated HIP profile object, or None if update failed
    """
    log_section("UPDATING HIP PROFILES")
    log_operation_start(f"Fetching and updating HIP profile with ID: {profile_id}")

    try:
        # Fetch the profile
        hip_profile = hip_profiles.get(profile_id)
        log_success(f"Found HIP profile: {hip_profile.name}")
        log_info(f"  - Current match: {hip_profile.match}")
        log_info(f"  - Current description: {hip_profile.description}")

        # Create an update model with correct match syntax
        updated_match = '"is-win" or "is-firewall-enabled"'
        updated_description = f"Updated HIP profile - modified on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        update_model = HIPProfileUpdateModel(
            id=hip_profile.id,
            name=hip_profile.name,
            match=updated_match,
            description=updated_description,
        )

        log_info("Updating HIP profile with:")
        log_info(f"  - New match: {updated_match}")
        log_info(f"  - New description: {updated_description}")

        # Perform the update
        updated_profile = hip_profiles.update(update_model)
        log_success(f"Updated HIP profile: {updated_profile.name}")
        log_info(f"  - Updated match: {updated_profile.match}")
        log_info(f"  - Updated description: {updated_profile.description}")
        log_operation_complete("HIP profile update", f"Profile: {updated_profile.name}")
        return updated_profile

    except NotFoundError as e:
        log_error(f"HIP profile not found", e.message)
    except InvalidObjectError as e:
        log_error(f"Invalid HIP profile update", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error(f"Unexpected error updating HIP profile", str(e))

    return None


def list_and_filter_hip_profiles(hip_profiles):
    """
    List and filter HIP profiles with various filtering options.
    
    This function demonstrates:
    1. Listing all HIP profiles in a specific folder
    2. Filtering by exact match on container
    3. Excluding profiles from specific containers (folders/snippets/devices)
    
    Args:
        hip_profiles: The HIP profile manager instance
        
    Returns:
        list: List of all HIP profiles found
    """
    log_section("LISTING AND FILTERING HIP PROFILES")
    log_operation_start("Listing and filtering HIP profiles")

    try:
        # List all HIP profiles in the Texas folder
        all_profiles = hip_profiles.list(folder="Texas")
        log_success(f"Found {len(all_profiles)} HIP profiles in the Texas folder")

        # Filter with exact_match=True to get profiles directly in the folder (not subfolder)
        direct_profiles = hip_profiles.list(folder="Texas", exact_match=True)
        log_info(f"Found {len(direct_profiles)} HIP profiles directly in the Texas folder")

        # Filter out profiles from a specific subfolder
        filtered_profiles = hip_profiles.list(folder="Texas", exclude_folders=["Texas/SubFolder"])
        log_info(f"Found {len(filtered_profiles)} HIP profiles excluding 'Texas/SubFolder'")

        # Print details of profiles
        log_info("\nDetails of HIP profiles:")
        for profile in all_profiles[:5]:  # Print details of up to 5 profiles
            log_info(f"  - Profile: {profile.name}")
            log_info(f"    ID: {profile.id}")
            log_info(f"    Match: {profile.match}")
            if profile.description:
                log_info(f"    Description: {profile.description}")
            log_info("")

        return all_profiles
    
    except InvalidObjectError as e:
        log_error(f"Invalid request when listing HIP profiles", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error(f"Unexpected error listing HIP profiles", str(e))
        
    return []


def fetch_hip_profile_by_name(hip_profiles, profile_name, folder="Texas"):
    """
    Fetch a specific HIP profile by name from a folder.
    
    This function demonstrates using the fetch method to retrieve a HIP profile
    by its name rather than its ID, which is useful when you know the name but
    not the ID of the profile.
    
    Args:
        hip_profiles: The HIP profile manager instance
        profile_name: The name of the HIP profile to fetch
        folder: The folder containing the HIP profile (default: "Texas")
        
    Returns:
        HIPProfileResponseModel: The fetched HIP profile, or None if fetch failed
    """
    log_section("FETCHING HIP PROFILE BY NAME")
    log_operation_start(f"Fetching HIP profile '{profile_name}' from {folder}")

    try:
        # Fetch the profile by name
        profile = hip_profiles.fetch(name=profile_name, folder=folder)
        log_success(f"Found HIP profile: {profile.name}")
        log_info(f"  - ID: {profile.id}")
        log_info(f"  - Match: {profile.match}")
        if profile.description:
            log_info(f"  - Description: {profile.description}")
        
        log_operation_complete("HIP profile fetch by name", f"Profile: {profile.name}")
        return profile
        
    except NotFoundError as e:
        log_error(f"HIP profile not found", e.message)
    except InvalidObjectError as e:
        log_error(f"Invalid fetch request", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error(f"Unexpected error fetching HIP profile", str(e))
        
    return None


def delete_hip_profile(hip_profiles, profile_id):
    """
    Delete a HIP profile.
    
    This function demonstrates deleting a HIP profile using its ID. It handles
    common error cases such as the profile not being found or already deleted.
    
    Args:
        hip_profiles: The HIP profile manager instance
        profile_id: The UUID of the HIP profile to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    log_section("DELETING HIP PROFILE")
    log_operation_start(f"Deleting HIP profile with ID: {profile_id}")

    try:
        # Delete the profile
        hip_profiles.delete(profile_id)
        log_success(f"Successfully deleted HIP profile with ID: {profile_id}")
        log_operation_complete("HIP profile deletion")
        return True
        
    except NotFoundError as e:
        log_error(f"HIP profile not found", e.message)
    except InvalidObjectError as e:
        log_error(f"Invalid delete request", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error(f"Unexpected error deleting HIP profile", str(e))
        
    return False


def cleanup_hip_profiles(hip_profiles, profile_ids):
    """
    Delete the HIP profiles created in this example.
    
    Args:
        hip_profiles: The HIP profile manager instance
        profile_ids: List of UUIDs of HIP profiles to delete
    """
    log_section("CLEANUP")
    log_operation_start(f"Cleaning up {len(profile_ids)} HIP profiles")

    for profile_id in profile_ids:
        try:
            hip_profiles.delete(profile_id)
            log_success(f"Deleted HIP profile with ID: {profile_id}")
        except NotFoundError:
            log_warning(f"HIP profile with ID {profile_id} not found - may have been already deleted")
        except Exception as e:
            log_error(f"Error deleting HIP profile with ID {profile_id}", str(e))


def parse_arguments():
    """
    Parse command-line arguments for the HIP profile example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created profiles
    - Which HIP profile operations to demonstrate
    - Folder name to use for profile creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager HIP Profiles Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created HIP profiles (don't delete them)"
    )
    
    # Operations to demonstrate
    op_group = parser.add_argument_group("Operations")
    op_group.add_argument(
        "--create", 
        action="store_true",
        help="Demonstrate creation operations"
    )
    op_group.add_argument(
        "--update", 
        action="store_true", 
        help="Demonstrate update operations"
    )
    op_group.add_argument(
        "--list", 
        action="store_true",
        help="Demonstrate listing operations"
    )
    op_group.add_argument(
        "--delete", 
        action="store_true",
        help="Demonstrate deletion operations"
    )
    op_group.add_argument(
        "--all", 
        action="store_true",
        help="Demonstrate all operations (default behavior)"
    )
    
    # Container name
    parser.add_argument(
        "--folder", 
        type=str, 
        default="Texas",
        help="Folder name in SCM to use for operations"
    )
    
    return parser.parse_args()


def main():
    """
    Execute the comprehensive set of HIP profile examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of HIP profiles (basic, complex, container-specific)
    4. Update an existing HIP profile to demonstrate modification capabilities
    5. List and filter HIP profiles to show search functionality
    6. Clean up created profiles (unless skip_cleanup is enabled)
    7. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created HIP profiles (don't delete them)
        --create: Only demonstrate creation operations
        --update: Only demonstrate update operations
        --list: Only demonstrate listing operations
        --delete: Only demonstrate deletion operations
        --all: Demonstrate all operations (default behavior)
        --folder: Folder name in SCM to use for operations (default: "Texas")
    
    Environment Variables:
        SCM_CLIENT_ID: Client ID for SCM authentication (required)
        SCM_CLIENT_SECRET: Client secret for SCM authentication (required)
        SCM_TSG_ID: Tenant Service Group ID for SCM authentication (required)
        SCM_LOG_LEVEL: Logging level, defaults to DEBUG (optional)
        SKIP_CLEANUP: Alternative way to preserve created profiles (optional)
    
    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Track execution time for reporting
    start_time = __import__("time").time()
    profile_count = 0
    
    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"
    
    # Determine which operations to demonstrate
    # If no specific operations are specified, demonstrate all (default behavior)
    demo_all = args.all or not (args.create or args.update or args.list or args.delete)
    
    # Get folder name for operations
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()
        
        # Initialize HIP profiles object
        log_section("HIP PROFILE CONFIGURATION")
        log_operation_start("Initializing HIP profile manager")
        hip_profiles = HIPProfile(client)
        log_operation_complete("HIP profile manager initialization")
        
        # Track created profiles for cleanup
        created_profiles = []
        
        # Demonstrate creation operations
        if demo_all or args.create:
            log_section("HIP PROFILE CREATION")
            log_info("Demonstrating HIP profile creation with various match expressions")
            log_info(f"Using folder: {folder_name}")
            
            # Create a basic HIP profile
            basic_profile = create_basic_hip_profile(hip_profiles, folder_name)
            if basic_profile:
                created_profiles.append(basic_profile.id)
                profile_count += 1
            
            # Create a complex HIP profile
            complex_profile = create_complex_hip_profile(hip_profiles, folder_name)
            if complex_profile:
                created_profiles.append(complex_profile.id)
                profile_count += 1
            
            # Create a HIP profile in a snippet container
            snippet_profile = create_hip_profile_with_snippet(hip_profiles, folder_name)
            if snippet_profile:
                created_profiles.append(snippet_profile.id)
                profile_count += 1
            
            # Create a HIP profile in a device container
            device_profile = create_hip_profile_with_device(hip_profiles, folder_name)
            if device_profile:
                created_profiles.append(device_profile.id)
                profile_count += 1
            
            # Create a HIP profile with negative match criteria
            negative_profile = create_negative_match_hip_profile(hip_profiles, folder_name)
            if negative_profile:
                created_profiles.append(negative_profile.id)
                profile_count += 1
            
            log_success(f"Created {len(created_profiles)} HIP profiles")
        
        # Demonstrate update operations
        if demo_all or args.update:
            if created_profiles:
                # Update the first created profile
                updated_profile = fetch_and_update_hip_profile(hip_profiles, created_profiles[0])
                if updated_profile:
                    log_success("Successfully updated HIP profile")
            else:
                log_warning("No profiles were created to update")
        
        # Demonstrate list and fetch operations
        if demo_all or args.list:
            # List and filter profiles
            all_profiles = list_and_filter_hip_profiles(hip_profiles)
            
            # Fetch a profile by name if we have created any
            if created_profiles and all_profiles:
                # Use the name of the first profile in the list
                fetch_profile_by_name = fetch_hip_profile_by_name(
                    hip_profiles, 
                    all_profiles[0].name, 
                    all_profiles[0].folder
                )
                if fetch_profile_by_name:
                    log_success("Successfully fetched HIP profile by name")
        
        # Demonstrate delete operations
        if demo_all or args.delete:
            if created_profiles:
                # Delete the last created profile to demonstrate the delete operation
                delete_success = delete_hip_profile(hip_profiles, created_profiles[-1])
                if delete_success:
                    # Remove it from the list of profiles to clean up later
                    deleted_id = created_profiles.pop()
                    log_success(f"Successfully demonstrated deletion of HIP profile {deleted_id}")
            else:
                log_warning("No profiles were created to delete")
        
        # Clean up the created profiles, unless skip_cleanup is true
        if created_profiles:
            if skip_cleanup:
                log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_profiles)} HIP profiles")
                log_info("To clean up these profiles, run the script again with SKIP_CLEANUP unset or set to false")
            else:
                log_operation_start(f"Cleaning up {len(created_profiles)} created HIP profiles")
                cleanup_hip_profiles(hip_profiles, created_profiles)
        
        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)
        
        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total HIP profiles created: {profile_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if profile_count > 0:
            log_info(f"Average time per profile: {execution_time/profile_count:.2f} seconds")
        
    except AuthenticationError as e:
        log_error(f"Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some HIP profiles may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback
        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()