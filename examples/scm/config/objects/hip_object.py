#!/usr/bin/env python3
"""Comprehensive examples of working with HIP (Host Information Profile) objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of HIP object configurations and operations commonly
used in enterprise networks, including:

1. HIP Object Types:
   - Host information based criteria
   - Network information based criteria
   - Patch management based criteria
   - Disk encryption based criteria
   - Mobile device based criteria
   - Certificate based criteria

2. Operational examples:
   - Creating HIP objects
   - Searching and filtering HIP objects
   - Updating HIP object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with HIP object details
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
   - SKIP_CLEANUP=true: Set this to preserve created HIP objects for manual inspection
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
from scm.config.objects import HIPObject
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
logger = logging.getLogger("hip_object_example")


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


def create_host_info_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on host information criteria.

    This function demonstrates creating a HIP object with host information criteria,
    including OS type, domain membership, and managed state.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Host Info based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"host-info-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    host_info_config = {
        "name": hip_name,
        "description": "HIP object for Windows workstations with domain membership",
        "folder": folder,  # Use the provided folder name
        "host_info": {
            "criteria": {
                "os": {"contains": {"Microsoft": "Windows 10"}},
                "domain": {"contains": "example.com"},
                "managed": True,
            }
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Host Information")
    log_info("  - OS: Microsoft Windows 10")
    log_info("  - Domain: example.com")
    log_info("  - Managed: True")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(host_info_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete("Host Info HIP object creation", f"Object: {new_hip_object.name}")
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def create_network_info_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on network information criteria.

    This function demonstrates creating a HIP object with network information criteria,
    specifying requirements for the type of network connection.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Network Info based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"network-info-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    network_info_config = {
        "name": hip_name,
        "description": "HIP object for wired network connections only",
        "folder": folder,  # Use the provided folder name
        "network_info": {"criteria": {"network": {"is_not": {"wifi": {}}}}},
    }

    log_info("Configuration details:")
    log_info("  - Type: Network Information")
    log_info("  - Network Type: Not WiFi")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(network_info_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete("Network Info HIP object creation", f"Object: {new_hip_object.name}")
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def create_patch_management_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on patch management criteria.

    This function demonstrates creating a HIP object with patch management criteria,
    including vendor requirements and patch status checks.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Patch Management based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"patch-mgmt-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    patch_management_config = {
        "name": hip_name,
        "description": "HIP object for endpoints with up-to-date patches",
        "folder": folder,  # Use the provided folder name
        "patch_management": {
            "criteria": {
                "is_installed": True,
                "is_enabled": "yes",
                "missing_patches": {"severity": 4, "check": "has-none"},
            },
            "vendor": [
                {
                    "name": "Microsoft",
                    "product": ["Windows-Update"],  # Fix: Using pattern-compliant product name
                }
            ],
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Patch Management")
    log_info("  - Vendor: Microsoft Windows-Update")
    log_info("  - Missing Patches: None with severity >= 4")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(patch_management_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete(
            "Patch Management HIP object creation", f"Object: {new_hip_object.name}"
        )
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def create_disk_encryption_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on disk encryption criteria.

    This function demonstrates creating a HIP object with disk encryption criteria,
    specifying requirements for encrypted drives.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Disk Encryption based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"disk-encrypt-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    disk_encryption_config = {
        "name": hip_name,
        "description": "HIP object for fully encrypted system drives",
        "folder": folder,  # Use the provided folder name
        "disk_encryption": {
            "criteria": {
                "is_installed": True,
                "is_enabled": "yes",
                "encrypted_locations": [{"name": "C:", "encryption_state": {"is": "encrypted"}}],
            },
            "vendor": [
                {
                    "name": "Microsoft",
                    "product": [
                        "BitLocker-Drive-Encryption"
                    ],  # Fix: Using pattern-compliant product name
                },
                {
                    "name": "Symantec",
                    "product": ["Endpoint-Encryption"],  # Fix: Using pattern-compliant product name
                },
            ],
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Disk Encryption")
    log_info("  - Vendors: Microsoft BitLocker-Drive-Encryption, Symantec Endpoint-Encryption")
    log_info("  - Required Locations: C: drive (fully encrypted)")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(disk_encryption_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete(
            "Disk Encryption HIP object creation", f"Object: {new_hip_object.name}"
        )
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def create_mobile_device_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on mobile device criteria.

    This function demonstrates creating a HIP object with mobile device criteria,
    including jailbreak detection and encryption requirements.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Mobile Device based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"mobile-device-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    mobile_device_config = {
        "name": hip_name,
        "description": "HIP object for secure mobile devices",
        "folder": folder,  # Use the provided folder name
        "mobile_device": {
            "criteria": {
                "jailbroken": False,
                "disk_encrypted": True,
                "passcode_set": True,
                "last_checkin_time": {"days": 7},
                "applications": {
                    "has_malware": {},  # Fix: Changed from boolean to empty object
                    "includes": [{"name": "CompanyMDM", "package": "com.company.mdm"}],
                },
            }
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Mobile Device")
    log_info("  - Requirements: Not jailbroken, Encrypted, Passcode set")
    log_info("  - Check-in: Within last 7 days")
    log_info("  - Required Apps: CompanyMDM")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(mobile_device_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete(
            "Mobile Device HIP object creation", f"Object: {new_hip_object.name}"
        )
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def create_certificate_hip_object(hip_objects, folder="Texas"):
    """Create a HIP object based on certificate criteria.

    This function demonstrates creating a HIP object with certificate criteria,
    specifying required certificate attributes.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        HIPObjectResponseModel: The created HIP object, or None if creation failed
    """
    log_operation_start("Creating Certificate based HIP object")

    # Generate a unique HIP object name with timestamp to avoid conflicts
    hip_name = f"certificate-{uuid.uuid4().hex[:6]}"
    log_info(f"HIP object name: {hip_name}")

    # Create the HIP object configuration
    certificate_config = {
        "name": hip_name,
        "description": "HIP object for certificate validation",
        "folder": folder,  # Use the provided folder name
        "certificate": {
            "criteria": {
                # Remove certificate_profile since it requires a valid reference
                # certificate_profile: "Company-Issued",
                "certificate_attributes": [
                    {
                        "name": "O",
                        "value": "Example-Corp",  # Fix: Using pattern-compliant value
                    },
                    {
                        "name": "OU",
                        "value": "IT-Security",  # Fix: Using pattern-compliant value
                    },
                ]
            }
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Certificate")
    # Update the log message to match the actual configuration
    log_info("  - Required Attributes: O=Example-Corp, OU=IT-Security")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_hip_object = hip_objects.create(certificate_config)
        log_success(f"Created HIP object: {new_hip_object.name}")
        log_info(f"  - Object ID: {new_hip_object.id}")
        log_info(f"  - Description: {new_hip_object.description}")
        log_operation_complete("Certificate HIP object creation", f"Object: {new_hip_object.name}")
        return new_hip_object
    except NameNotUniqueError as e:
        log_error("HIP object name conflict", e.message)
        log_info("Try using a different HIP object name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid HIP object data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HIP object", str(e))

    return None


def fetch_and_update_hip_object(hip_objects, hip_object_id):
    """Fetch a HIP object by ID and update its description and criteria.

    This function demonstrates how to:
    1. Retrieve an existing HIP object using its ID
    2. Modify object properties (description, criteria)
    3. Submit the updated object back to the SCM API

    Args:
        hip_objects: The HIPObject manager instance
        hip_object_id: The UUID of the HIP object to update

    Returns:
        HIPObjectResponseModel: The updated HIP object, or None if update failed
    """
    logger.info(f"Fetching and updating HIP object with ID: {hip_object_id}")

    try:
        # Fetch the HIP object
        hip_object = hip_objects.get(hip_object_id)
        logger.info(f"Found HIP object: {hip_object.name}")

        # Update description
        hip_object.description = f"Updated description for {hip_object.name}"

        # Modify criteria based on HIP object type
        if hip_object.host_info:
            # If it's a host info based HIP object, update the OS criteria
            if hasattr(hip_object.host_info.criteria, "os") and hip_object.host_info.criteria.os:
                hip_object.host_info.criteria.managed = True
        elif hip_object.disk_encryption:
            # If it's a disk encryption based HIP object, add another location
            if hasattr(hip_object.disk_encryption.criteria, "encrypted_locations"):
                # Add D: drive to encrypted locations if it doesn't exist already
                d_drive_exists = False
                for location in hip_object.disk_encryption.criteria.encrypted_locations:
                    if location.name == "D:":
                        d_drive_exists = True
                        break

                if not d_drive_exists:
                    # We would need to create the proper model here
                    # This is a simplified example
                    logger.info("Adding D: drive to encrypted locations")

        # Perform the update
        updated_hip_object = hip_objects.update(hip_object)
        logger.info(
            f"Updated HIP object: {updated_hip_object.name} with description: {updated_hip_object.description}"
        )
        return updated_hip_object

    except NotFoundError as e:
        logger.error(f"HIP object not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid HIP object update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_hip_objects(hip_objects):
    """List and filter HIP objects.

    This function demonstrates how to:
    1. List all HIP objects in a folder
    2. Filter HIP objects by various criteria
    3. Display detailed information about each object

    Args:
        hip_objects: The HIPObject manager instance

    Returns:
        list: All retrieved HIP objects
    """
    logger.info("Listing and filtering HIP objects")

    # List all HIP objects in the Texas folder
    all_hip_objects = hip_objects.list(folder="Texas")
    logger.info(f"Found {len(all_hip_objects)} HIP objects in the Texas folder")

    # Filter by criteria types
    host_info_objects = hip_objects.list(folder="Texas", criteria_types=["host_info"])
    logger.info(f"Found {len(host_info_objects)} HIP objects with 'host_info' criteria")

    # Print details of HIP objects
    logger.info("\nDetails of HIP objects:")
    for hip_object in all_hip_objects[:5]:  # Print details of up to 5 objects
        logger.info(f"  - HIP Object: {hip_object.name}")
        logger.info(f"    ID: {hip_object.id}")
        logger.info(
            f"    Description: {hip_object.description if hip_object.description else 'None'}"
        )

        # Determine HIP object type
        hip_type = "Unknown"

        if hasattr(hip_object, "host_info") and hip_object.host_info:
            hip_type = "Host Information"
        elif hasattr(hip_object, "network_info") and hip_object.network_info:
            hip_type = "Network Information"
        elif hasattr(hip_object, "patch_management") and hip_object.patch_management:
            hip_type = "Patch Management"
        elif hasattr(hip_object, "disk_encryption") and hip_object.disk_encryption:
            hip_type = "Disk Encryption"
        elif hasattr(hip_object, "mobile_device") and hip_object.mobile_device:
            hip_type = "Mobile Device"
        elif hasattr(hip_object, "certificate") and hip_object.certificate:
            hip_type = "Certificate"

        logger.info(f"    Type: {hip_type}")
        logger.info("")

    return all_hip_objects


def cleanup_hip_objects(hip_objects, hip_object_ids):
    """Delete the HIP objects created in this example.

    Args:
        hip_objects: The HIPObject manager instance
        hip_object_ids: List of HIP object IDs to delete
    """
    logger.info("Cleaning up HIP objects")

    for hip_object_id in hip_object_ids:
        try:
            hip_objects.delete(hip_object_id)
            logger.info(f"Deleted HIP object with ID: {hip_object_id}")
        except NotFoundError as e:
            logger.error(f"HIP object not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting HIP object: {str(e)}")


def create_bulk_hip_objects(hip_objects, folder="Texas"):
    """Create multiple HIP objects in a batch.

    This function demonstrates creating multiple HIP objects in a batch,
    which is useful for setting up multiple security profiles at once.

    Args:
        hip_objects: The HIPObject manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")

    Returns:
        list: List of IDs of created HIP objects, or empty list if creation failed
    """
    logger.info("Creating a batch of HIP objects")

    # Define a list of HIP objects to create
    hip_configs = [
        {
            "name": f"bulk-win10-{uuid.uuid4().hex[:6]}",
            "description": "Bulk Windows 10 HIP profile",
            "folder": folder,
            "host_info": {"criteria": {"os": {"contains": {"Microsoft": "Windows 10"}}}},
        },
        {
            "name": f"bulk-macos-{uuid.uuid4().hex[:6]}",
            "description": "Bulk macOS HIP profile",
            "folder": folder,
            "host_info": {"criteria": {"os": {"contains": {"Apple": "macOS"}}}},
        },
        {
            "name": f"bulk-encrypted-{uuid.uuid4().hex[:6]}",
            "description": "Bulk disk encryption HIP profile",
            "folder": folder,
            "disk_encryption": {
                "criteria": {
                    "is_installed": True,
                    "encrypted_locations": [
                        {"name": "SystemDrive", "encryption_state": {"is": "encrypted"}}
                    ],
                }
            },
        },
    ]

    created_hip_objects = []

    # Create each HIP object
    for hip_config in hip_configs:
        try:
            new_hip_object = hip_objects.create(hip_config)
            logger.info(f"Created HIP object: {new_hip_object.name} with ID: {new_hip_object.id}")
            created_hip_objects.append(new_hip_object.id)
        except Exception as e:
            logger.error(f"Error creating HIP object {hip_config['name']}: {str(e)}")

    return created_hip_objects


def generate_hip_object_report(hip_objects, hip_object_ids, execution_time):
    """Generate a comprehensive CSV report of all HIP objects created by the script.

    This function fetches detailed information about each HIP object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    Args:
        hip_objects: The HIPObject manager instance used to fetch object details
        hip_object_ids: List of HIP object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"hip_objects_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Object ID",
        "Name",
        "Type",
        "Details",
        "Description",
        "Created On",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each HIP object
    hip_object_data = []
    for idx, hip_id in enumerate(hip_object_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(hip_object_ids) - 1:
            log_info(f"Processing HIP object {idx + 1} of {len(hip_object_ids)}")

        try:
            # Get the HIP object details
            hip = hip_objects.get(hip_id)

            # Determine HIP object type and details
            hip_type = "Unknown"
            hip_details = "N/A"

            if hasattr(hip, "host_info") and hip.host_info:
                hip_type = "Host Information"
                # Extract OS information if available
                if hasattr(hip.host_info.criteria, "os") and hip.host_info.criteria.os:
                    hip_details = "OS criteria specified"
                # Extract domain information if available
                if hasattr(hip.host_info.criteria, "domain") and hip.host_info.criteria.domain:
                    hip_details = f"{hip_details}, Domain criteria specified"
                # Extract managed state if available
                if (
                    hasattr(hip.host_info.criteria, "managed")
                    and hip.host_info.criteria.managed is not None
                ):
                    hip_details = f"{hip_details}, Managed: {hip.host_info.criteria.managed}"
            elif hasattr(hip, "network_info") and hip.network_info:
                hip_type = "Network Information"
                hip_details = "Network criteria specified"
            elif hasattr(hip, "patch_management") and hip.patch_management:
                hip_type = "Patch Management"
                # Check if vendor information is available
                if hasattr(hip.patch_management, "vendor") and hip.patch_management.vendor:
                    vendors = [v.name for v in hip.patch_management.vendor]
                    hip_details = f"Vendors: {', '.join(vendors)}"
            elif hasattr(hip, "disk_encryption") and hip.disk_encryption:
                hip_type = "Disk Encryption"
                # Check if encrypted locations are specified
                if (
                    hasattr(hip.disk_encryption.criteria, "encrypted_locations")
                    and hip.disk_encryption.criteria.encrypted_locations
                ):
                    locations = [
                        loc.name for loc in hip.disk_encryption.criteria.encrypted_locations
                    ]
                    hip_details = f"Encrypted Locations: {', '.join(locations)}"
            elif hasattr(hip, "mobile_device") and hip.mobile_device:
                hip_type = "Mobile Device"
                hip_details = "Mobile device criteria specified"
            elif hasattr(hip, "certificate") and hip.certificate:
                hip_type = "Certificate"
                if (
                    hasattr(hip.certificate.criteria, "certificate_profile")
                    and hip.certificate.criteria.certificate_profile
                ):
                    hip_details = f"Profile: {hip.certificate.criteria.certificate_profile}"

            # Add HIP object data
            hip_object_data.append(
                [
                    hip.id,
                    hip.name,
                    hip_type,
                    hip_details,
                    hip.description if hip.description else "None",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if hasattr(hip, "created_on") and hip.created_on
                    else "Unknown",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for HIP object ID {hip_id}", str(e))
            # Add minimal info for HIP objects that couldn't be retrieved
            hip_object_data.append(
                [
                    hip_id,
                    "ERROR",
                    "ERROR",
                    "ERROR",
                    f"Failed to retrieve HIP object details: {str(e)}",
                    "",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )
            failed_fetches += 1

    try:
        # Write to CSV file
        with open(report_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(hip_object_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(hip_object_ids)])
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
            fallback_file = f"hip_objects_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(hip_object_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """Parse command-line arguments for the HIP object example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which HIP object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager HIP Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created HIP objects (don't delete them)",
    )

    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--host-info", action="store_true", help="Create Host Info HIP examples"
    )
    object_group.add_argument(
        "--network-info", action="store_true", help="Create Network Info HIP examples"
    )
    object_group.add_argument(
        "--patch-management", action="store_true", help="Create Patch Management HIP examples"
    )
    object_group.add_argument(
        "--disk-encryption", action="store_true", help="Create Disk Encryption HIP examples"
    )
    object_group.add_argument(
        "--mobile-device", action="store_true", help="Create Mobile Device HIP examples"
    )
    object_group.add_argument(
        "--certificate", action="store_true", help="Create Certificate HIP examples"
    )
    object_group.add_argument("--bulk", action="store_true", help="Create bulk HIP examples")
    object_group.add_argument(
        "--all", action="store_true", help="Create all HIP object types (default behavior)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Folder
    parser.add_argument(
        "--folder", type=str, default="Texas", help="Folder name in SCM to create objects in"
    )

    return parser.parse_args()


def main():
    """Execute the comprehensive set of HIP object examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of HIP objects (Host Info, Network Info, etc.)
    4. Update an existing HIP object to demonstrate modification capabilities
    5. List and filter HIP objects to show search functionality
    6. Generate a detailed CSV report of all created HIP objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created HIP objects (don't delete them)
        --host-info: Create only Host Info HIP examples
        --network-info: Create only Network Info HIP examples
        --patch-management: Create only Patch Management HIP examples
        --disk-encryption: Create only Disk Encryption HIP examples
        --mobile-device: Create only Mobile Device HIP examples
        --certificate: Create only Certificate HIP examples
        --bulk: Create only bulk HIP examples
        --all: Create all HIP object types (default behavior)
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
        args.host_info
        or args.network_info
        or args.patch_management
        or args.disk_encryption
        or args.mobile_device
        or args.certificate
        or args.bulk
    )

    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize HIPObject object
        log_section("HIP OBJECT CONFIGURATION")
        log_operation_start("Initializing HIP object manager")
        hip_objects = HIPObject(client)
        log_operation_complete("HIP object manager initialization")

        # Create various HIP objects
        created_hip_objects = []

        # Host Info HIP objects
        if create_all or args.host_info:
            log_section("HOST INFO HIP OBJECTS")
            log_info("Creating host information based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a host info HIP object
            host_info_hip = create_host_info_hip_object(hip_objects, folder_name)
            if host_info_hip:
                created_hip_objects.append(host_info_hip.id)
                object_count += 1

            log_success("Created Host Info HIP objects")

        # Network Info HIP objects
        if create_all or args.network_info:
            log_section("NETWORK INFO HIP OBJECTS")
            log_info("Creating network information based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a network info HIP object
            network_info_hip = create_network_info_hip_object(hip_objects, folder_name)
            if network_info_hip:
                created_hip_objects.append(network_info_hip.id)
                object_count += 1

            log_success("Created Network Info HIP objects")

        # Patch Management HIP objects
        if create_all or args.patch_management:
            log_section("PATCH MANAGEMENT HIP OBJECTS")
            log_info("Creating patch management based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a patch management HIP object
            patch_management_hip = create_patch_management_hip_object(hip_objects, folder_name)
            if patch_management_hip:
                created_hip_objects.append(patch_management_hip.id)
                object_count += 1

            log_success("Created Patch Management HIP objects")

        # Disk Encryption HIP objects
        if create_all or args.disk_encryption:
            log_section("DISK ENCRYPTION HIP OBJECTS")
            log_info("Creating disk encryption based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a disk encryption HIP object
            disk_encryption_hip = create_disk_encryption_hip_object(hip_objects, folder_name)
            if disk_encryption_hip:
                created_hip_objects.append(disk_encryption_hip.id)
                object_count += 1

            log_success("Created Disk Encryption HIP objects")

        # Mobile Device HIP objects
        if create_all or args.mobile_device:
            log_section("MOBILE DEVICE HIP OBJECTS")
            log_info("Creating mobile device based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a mobile device HIP object
            mobile_device_hip = create_mobile_device_hip_object(hip_objects, folder_name)
            if mobile_device_hip:
                created_hip_objects.append(mobile_device_hip.id)
                object_count += 1

            log_success("Created Mobile Device HIP objects")

        # Certificate HIP objects
        if create_all or args.certificate:
            log_section("CERTIFICATE HIP OBJECTS")
            log_info("Creating certificate based HIP objects")
            log_info(f"Using folder: {folder_name}")

            # Create a certificate HIP object
            certificate_hip = create_certificate_hip_object(hip_objects, folder_name)
            if certificate_hip:
                created_hip_objects.append(certificate_hip.id)
                object_count += 1

            log_success("Created Certificate HIP objects")

        # Bulk HIP object creation
        if create_all or args.bulk:
            log_section("BULK HIP OBJECTS")
            log_info("Creating multiple HIP objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk HIP objects
            bulk_hip_ids = create_bulk_hip_objects(hip_objects, folder_name)
            if bulk_hip_ids:
                created_hip_objects.extend(bulk_hip_ids)
                object_count += len(bulk_hip_ids)
                log_success(f"Created {len(bulk_hip_ids)} bulk HIP objects")

        # Update one of the objects
        if created_hip_objects:
            log_section("UPDATING HIP OBJECTS")
            log_info("Demonstrating how to update existing HIP objects")
            fetch_and_update_hip_object(hip_objects, created_hip_objects[0])

        # List and filter HIP objects
        log_section("LISTING AND FILTERING HIP OBJECTS")
        log_info("Demonstrating how to search and filter HIP objects")
        list_and_filter_hip_objects(hip_objects)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_hip_objects and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating HIP objects CSV report")
            report_file = generate_hip_object_report(
                hip_objects, created_hip_objects, execution_time_so_far
            )
            if report_file:
                log_success(f"Generated HIP objects report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_hip_objects)} HIP objects created"
                )
            else:
                log_error("Failed to generate HIP objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No HIP objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_hip_objects)} HIP objects"
            )
            log_info(
                "To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            log_operation_start(f"Cleaning up {len(created_hip_objects)} created HIP objects")
            cleanup_hip_objects(hip_objects, created_hip_objects)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total HIP objects created: {object_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(f"Average time per object: {execution_time / max(object_count, 1):.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some HIP objects may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
