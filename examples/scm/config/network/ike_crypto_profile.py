#!/usr/bin/env python3
"""
Comprehensive examples of working with IKE Crypto Profile objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of IKE Crypto Profile configurations and operations commonly
used in enterprise networks, including:

1. IKE Crypto Profile Types and Configurations:
   - Creating profiles with different hash algorithms
   - Creating profiles with different encryption algorithms
   - Creating profiles with different DH groups
   - Configuring various lifetime settings (seconds, minutes, hours, days)

2. Operational examples:
   - Creating IKE crypto profile objects
   - Fetching and listing IKE crypto profiles
   - Updating IKE crypto profile configurations
   - Filtering and searching for specific profiles

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with profile details
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
   - SKIP_CLEANUP=true: Set this to preserve created profiles for manual inspection
"""

import argparse
import csv
import datetime
import logging
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from scm.client import ScmClient
from scm.config.network import IKECryptoProfile
from scm.models.network import (
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
    IKECryptoProfileUpdateModel,
)
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
logger = logging.getLogger("ike_crypto_profile_example")


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
        ScmClient: An authenticated SCM client instance ready for API calls

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
    client = ScmClient(
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


def create_basic_ike_crypto_profile(ike_profile_manager, folder="Texas"):
    """
    Create a basic IKE crypto profile with standard settings.

    This function demonstrates creating a standard IKE crypto profile with
    commonly used settings for VPN tunnels.

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        IKECryptoProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating basic IKE crypto profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"ike-basic-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    basic_profile_config = {
        "name": profile_name,
        "description": "Basic IKE crypto profile for standard VPN tunnels",
        "folder": folder,
        "hash": [HashAlgorithm.SHA1, HashAlgorithm.SHA256],
        "encryption": [EncryptionAlgorithm.AES_128_CBC, EncryptionAlgorithm.AES_256_CBC],
        "dh_group": [DHGroup.GROUP2, DHGroup.GROUP14],
        "lifetime": {"hours": 8},  # 8 hours lifetime
        "authentication_multiple": 0,  # Disable reauthentication
    }

    log_info("Configuration details:")
    log_info("  - Hash Algorithms: SHA1, SHA256")
    log_info("  - Encryption: AES-128-CBC, AES-256-CBC")
    log_info("  - DH Groups: Group2, Group14")
    log_info("  - Lifetime: 8 hours")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = ike_profile_manager.create(basic_profile_config)
        log_success(f"Created IKE crypto profile: {new_profile.name}")
        log_info(f"  - Profile ID: {new_profile.id}")
        # No description field in response model
        log_operation_complete("Basic IKE crypto profile creation", f"Profile: {new_profile.name}")
        return new_profile
    except NameNotUniqueError as e:
        log_error("Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating IKE crypto profile", str(e))

    return None


def create_strong_security_ike_profile(ike_profile_manager, folder="Texas"):
    """
    Create an IKE crypto profile with stronger security settings.

    This function demonstrates creating an IKE profile with high security
    settings for sensitive VPN tunnels.

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        IKECryptoProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating high-security IKE crypto profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"ike-high-security-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration with stronger security settings
    strong_profile_config = {
        "name": profile_name,
        "description": "High-security IKE crypto profile for sensitive VPNs",
        "folder": folder,
        "hash": [HashAlgorithm.SHA256, HashAlgorithm.SHA384, HashAlgorithm.SHA512],  # Stronger hash
        "encryption": [
            EncryptionAlgorithm.AES_256_CBC,
            EncryptionAlgorithm.AES_256_GCM,
        ],  # Stronger encryption
        "dh_group": [DHGroup.GROUP14, DHGroup.GROUP19, DHGroup.GROUP20],  # Stronger DH groups
        "lifetime": {"hours": 4},  # Shorter lifetime for more frequent key rotation
        "authentication_multiple": 3,  # Enable reauthentication
    }

    log_info("Configuration details:")
    log_info("  - Hash Algorithms: SHA256, SHA384, SHA512")
    log_info("  - Encryption: AES-256-CBC, AES-256-GCM")
    log_info("  - DH Groups: Group14, Group19, Group20")
    log_info("  - Lifetime: 4 hours")
    log_info("  - Authentication Multiple: 3")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = ike_profile_manager.create(strong_profile_config)
        log_success(f"Created high-security IKE crypto profile: {new_profile.name}")
        log_info(f"  - Profile ID: {new_profile.id}")
        # No description field in response model
        log_operation_complete(
            "High-security IKE crypto profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error("Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating IKE crypto profile", str(e))

    return None


def create_legacy_compatibility_profile(ike_profile_manager, folder="Texas"):
    """
    Create an IKE crypto profile with legacy algorithm support.

    This function demonstrates creating an IKE profile with compatibility
    settings for legacy VPN endpoints.

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        IKECryptoProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating legacy compatibility IKE crypto profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"ike-legacy-compat-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration with legacy compatibility settings
    legacy_profile_config = {
        "name": profile_name,
        "description": "Legacy compatibility IKE crypto profile for older VPN devices",
        "folder": folder,
        "hash": [HashAlgorithm.MD5, HashAlgorithm.SHA1],  # Include legacy hash algorithms
        "encryption": [
            EncryptionAlgorithm.THREE_DES,  # Legacy encryption
            EncryptionAlgorithm.AES_128_CBC,
            EncryptionAlgorithm.AES_256_CBC,
        ],
        "dh_group": [DHGroup.GROUP1, DHGroup.GROUP2, DHGroup.GROUP5],  # Include legacy DH groups
        "lifetime": {"days": 1},  # Longer lifetime for compatibility
        "authentication_multiple": 0,
    }

    log_info("Configuration details:")
    log_info("  - Hash Algorithms: MD5, SHA1")
    log_info("  - Encryption: 3DES, AES-128-CBC, AES-256-CBC")
    log_info("  - DH Groups: Group1, Group2, Group5")
    log_info("  - Lifetime: 1 day")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = ike_profile_manager.create(legacy_profile_config)
        log_success(f"Created legacy compatibility IKE crypto profile: {new_profile.name}")
        log_info(f"  - Profile ID: {new_profile.id}")
        # No description field in response model
        log_operation_complete(
            "Legacy compatibility IKE crypto profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error("Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating IKE crypto profile", str(e))

    return None


def create_custom_lifetime_profile(ike_profile_manager, folder="Texas"):
    """
    Create IKE crypto profiles with different lifetime settings.

    This function demonstrates creating profiles with various lifetime
    configurations (seconds, minutes, hours, days).

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        list: List of created profiles, or empty list if creation failed
    """
    log_operation_start("Creating IKE crypto profiles with custom lifetimes")

    created_profiles = []

    # Define lifetime configurations to demonstrate
    lifetime_configs = [
        {
            "name": f"ike-seconds-{uuid.uuid4().hex[:6]}",
            "lifetime": {"seconds": 3600},
            "description": "IKE profile with seconds-based lifetime (3600 seconds)",
        },
        {
            "name": f"ike-minutes-{uuid.uuid4().hex[:6]}",
            "lifetime": {"minutes": 120},
            "description": "IKE profile with minutes-based lifetime (120 minutes)",
        },
        {
            "name": f"ike-hours-{uuid.uuid4().hex[:6]}",
            "lifetime": {"hours": 12},
            "description": "IKE profile with hours-based lifetime (12 hours)",
        },
        {
            "name": f"ike-days-{uuid.uuid4().hex[:6]}",
            "lifetime": {"days": 2},
            "description": "IKE profile with days-based lifetime (2 days)",
        },
    ]

    # Create each profile with a different lifetime configuration
    for config in lifetime_configs:
        log_info(f"Creating IKE profile: {config['name']}")
        log_info(f"  - Description: {config['description']}")
        log_info(f"  - Lifetime: {config['lifetime']}")

        # Build complete profile configuration
        profile_config = {
            "name": config["name"],
            "description": config["description"],
            "folder": folder,
            "hash": [HashAlgorithm.SHA1, HashAlgorithm.SHA256],
            "encryption": [EncryptionAlgorithm.AES_128_CBC, EncryptionAlgorithm.AES_256_CBC],
            "dh_group": [DHGroup.GROUP2, DHGroup.GROUP14],
            "lifetime": config["lifetime"],
            "authentication_multiple": 0,
        }

        try:
            new_profile = ike_profile_manager.create(profile_config)
            log_success(f"Created IKE profile: {new_profile.name}")
            log_info(f"  - Profile ID: {new_profile.id}")
            created_profiles.append(new_profile)
        except Exception as e:
            log_error(f"Failed to create profile {config['name']}", str(e))

    log_operation_complete(
        "Custom lifetime profile creation", f"Created {len(created_profiles)} profiles"
    )
    return created_profiles


def fetch_and_update_profile(ike_profile_manager, profile_id):
    """
    Fetch an IKE crypto profile by ID and update its settings.

    This function demonstrates how to:
    1. Retrieve an existing IKE crypto profile using its ID
    2. Modify profile properties (hash, encryption, DH groups)
    3. Submit the updated profile back to the SCM API

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        profile_id: The UUID of the profile to update

    Returns:
        IKECryptoProfileResponseModel: The updated profile, or None if update failed
    """
    logger.info(f"Fetching and updating IKE crypto profile with ID: {profile_id}")

    try:
        # Fetch the profile
        profile = ike_profile_manager.get(profile_id)
        logger.info(f"Found IKE crypto profile: {profile.name}")
        logger.info(f"  - Current hash algorithms: {[h.value for h in profile.hash]}")
        logger.info(f"  - Current encryption: {[e.value for e in profile.encryption]}")
        logger.info(f"  - Current DH groups: {[g.value for g in profile.dh_group]}")

        # Build updated profile object
        update_data = {
            "id": str(profile.id),
            "name": profile.name,
            # API doesn't return description, but we can include it in the update
            "description": "Updated IKE crypto profile",
            "folder": profile.folder,
            # Add SHA384 if not already present
            "hash": list(set(profile.hash + [HashAlgorithm.SHA384])),
            # Add AES-256-GCM if not already present
            "encryption": list(set(profile.encryption + [EncryptionAlgorithm.AES_256_GCM])),
            # Keep original DH groups
            "dh_group": profile.dh_group,
            # Update lifetime to 6 hours if it exists
            "lifetime": {"hours": 6} if hasattr(profile, "lifetime") else None,
            # Keep original authentication multiple
            "authentication_multiple": profile.authentication_multiple
            if hasattr(profile, "authentication_multiple")
            else 0,
        }

        # Create update model
        update_model = IKECryptoProfileUpdateModel(**update_data)

        # Perform the update
        updated_profile = ike_profile_manager.update(update_model)
        logger.info(f"Updated IKE crypto profile: {updated_profile.name}")
        logger.info(f"  - New hash algorithms: {[h.value for h in updated_profile.hash]}")
        logger.info(f"  - New encryption: {[e.value for e in updated_profile.encryption]}")

        return updated_profile

    except NotFoundError as e:
        logger.error(f"IKE crypto profile not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid IKE crypto profile update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")
    except Exception as e:
        logger.error(f"Unexpected error updating IKE crypto profile: {str(e)}")

    return None


def list_and_filter_profiles(ike_profile_manager, folder="Texas"):
    """
    List and filter IKE crypto profiles.

    This function demonstrates how to:
    1. List all IKE crypto profiles in a folder
    2. Filter profiles using built-in filtering mechanisms
    3. Display detailed information about each profile

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        folder: Folder to search in (default: "Texas")

    Returns:
        list: All retrieved IKE crypto profiles
    """
    logger.info("Listing and filtering IKE crypto profiles")

    # List all IKE crypto profiles in the folder
    all_profiles = ike_profile_manager.list(folder=folder)
    logger.info(f"Found {len(all_profiles)} IKE crypto profiles in the {folder} folder")

    # Print details of profiles
    logger.info("\nDetails of IKE crypto profiles:")
    for profile in all_profiles:
        logger.info(f"  - Profile: {profile.name}")
        logger.info(f"    ID: {profile.id}")
        # No description field in response model

        # Display hash algorithms
        if hasattr(profile, "hash") and profile.hash:
            logger.info(f"    Hash Algorithms: {', '.join([h.value for h in profile.hash])}")

        # Display encryption algorithms
        if hasattr(profile, "encryption") and profile.encryption:
            logger.info(f"    Encryption: {', '.join([e.value for e in profile.encryption])}")

        # Display DH groups
        if hasattr(profile, "dh_group") and profile.dh_group:
            logger.info(f"    DH Groups: {', '.join([g.value for g in profile.dh_group])}")

        # Display lifetime if it exists
        if hasattr(profile, "lifetime") and profile.lifetime:
            # Find which lifetime type is used
            if hasattr(profile.lifetime, "seconds"):
                logger.info(f"    Lifetime: {profile.lifetime.seconds} seconds")
            elif hasattr(profile.lifetime, "minutes"):
                logger.info(f"    Lifetime: {profile.lifetime.minutes} minutes")
            elif hasattr(profile.lifetime, "hours"):
                logger.info(f"    Lifetime: {profile.lifetime.hours} hours")
            elif hasattr(profile.lifetime, "days"):
                logger.info(f"    Lifetime: {profile.lifetime.days} days")

        # Display authentication multiple if it exists
        if hasattr(profile, "authentication_multiple"):
            logger.info(f"    Authentication Multiple: {profile.authentication_multiple}")

        logger.info("")

    return all_profiles


def cleanup_profiles(ike_profile_manager, profile_ids):
    """
    Delete the IKE crypto profiles created in this example.

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        profile_ids: List of profile IDs to delete
    """
    logger.info("Cleaning up IKE crypto profiles")

    deleted_count = 0
    for profile_id in profile_ids:
        try:
            ike_profile_manager.delete(profile_id)
            logger.info(f"Deleted IKE crypto profile with ID: {profile_id}")
            deleted_count += 1
        except NotFoundError as e:
            logger.error(f"IKE crypto profile not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting IKE crypto profile: {str(e)}")

    logger.info(
        f"Successfully deleted {deleted_count} out of {len(profile_ids)} IKE crypto profiles"
    )


def generate_profile_report(ike_profile_manager, profile_ids, execution_time):
    """
    Generate a comprehensive CSV report of all IKE crypto profiles created by the script.

    This function fetches detailed information about each profile and writes it to a
    CSV file with a timestamp in the filename.

    Args:
        ike_profile_manager: The IKECryptoProfile manager instance
        profile_ids: List of profile IDs to include in the report
        execution_time: Total execution time in seconds

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ike_crypto_profiles_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Profile ID",
        "Name",
        "Description",
        "Hash Algorithms",
        "Encryption Algorithms",
        "DH Groups",
        "Lifetime",
        "Authentication Multiple",
        "Folder",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each profile
    profile_data = []
    for idx, profile_id in enumerate(profile_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(profile_ids) - 1:
            log_info(f"Processing profile {idx + 1} of {len(profile_ids)}")

        try:
            # Get the profile details
            profile = ike_profile_manager.get(profile_id)

            # Determine lifetime value
            lifetime_value = "None"
            if hasattr(profile, "lifetime") and profile.lifetime:
                if hasattr(profile.lifetime, "seconds"):
                    lifetime_value = f"{profile.lifetime.seconds} seconds"
                elif hasattr(profile.lifetime, "minutes"):
                    lifetime_value = f"{profile.lifetime.minutes} minutes"
                elif hasattr(profile.lifetime, "hours"):
                    lifetime_value = f"{profile.lifetime.hours} hours"
                elif hasattr(profile.lifetime, "days"):
                    lifetime_value = f"{profile.lifetime.days} days"

            # Add profile data
            profile_data.append(
                [
                    profile.id,
                    profile.name,
                    "No description available",  # No description field in response model
                    ", ".join([h.value for h in profile.hash])
                    if hasattr(profile, "hash")
                    else "None",
                    ", ".join([e.value for e in profile.encryption])
                    if hasattr(profile, "encryption")
                    else "None",
                    ", ".join([g.value for g in profile.dh_group])
                    if hasattr(profile, "dh_group")
                    else "None",
                    lifetime_value,
                    profile.authentication_multiple
                    if hasattr(profile, "authentication_multiple")
                    else "None",
                    profile.folder if hasattr(profile, "folder") else "None",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for profile ID {profile_id}", str(e))
            # Add minimal info for profiles that couldn't be retrieved
            profile_data.append(
                [
                    profile_id,
                    "ERROR",
                    "ERROR",
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
            writer.writerows(profile_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Profiles Processed", len(profile_ids)])
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
            fallback_file = f"ike_profiles_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(profile_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the IKE crypto profile example script.

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager IKE Crypto Profile Examples",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created IKE crypto profiles (don't delete them)",
    )

    # Profile types to create
    profile_group = parser.add_argument_group("Profile Type Selection")
    profile_group.add_argument(
        "--basic", action="store_true", help="Create basic IKE crypto profile example"
    )
    profile_group.add_argument(
        "--high-security",
        action="store_true",
        help="Create high-security IKE crypto profile example",
    )
    profile_group.add_argument(
        "--legacy",
        action="store_true",
        help="Create legacy compatibility IKE crypto profile example",
    )
    profile_group.add_argument(
        "--lifetime", action="store_true", help="Create custom lifetime IKE crypto profile examples"
    )
    profile_group.add_argument(
        "--all", action="store_true", help="Create all IKE crypto profile types (default behavior)"
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
    Execute the comprehensive set of IKE crypto profile examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of IKE crypto profiles
    4. Update an existing profile to demonstrate modification capabilities
    5. List and filter profiles to show search functionality
    6. Generate a detailed CSV report of all created profiles
    7. Clean up created profiles (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created profiles (don't delete them)
        --basic: Create only basic IKE crypto profile examples
        --high-security: Create only high-security IKE crypto profile examples
        --legacy: Create only legacy compatibility IKE crypto profile examples
        --lifetime: Create only custom lifetime IKE crypto profile examples
        --all: Create all IKE crypto profile types (default behavior)
        --no-report: Skip CSV report generation
        --folder: Folder name in SCM to create objects in (default: "Texas")

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

    # Determine which profile types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.basic or args.high_security or args.legacy or args.lifetime)

    # Get folder name for object creation
    folder_name = args.folder

    # Keep track of created profiles for cleanup
    created_profiles = []

    try:
        # Initialize client
        client = initialize_client()

        # Initialize IKECryptoProfile object
        log_section("IKE CRYPTO PROFILE CONFIGURATION")
        log_operation_start("Initializing IKE Crypto Profile manager")
        ike_profile_manager = IKECryptoProfile(client)
        log_operation_complete("IKE Crypto Profile manager initialization")

        # Basic IKE crypto profile
        if create_all or args.basic:
            log_section("BASIC IKE CRYPTO PROFILE")
            log_info("Creating basic IKE crypto profile with standard settings")
            log_info(f"Using folder: {folder_name}")

            basic_profile = create_basic_ike_crypto_profile(ike_profile_manager, folder_name)
            if basic_profile:
                created_profiles.append(basic_profile)
                profile_count += 1

        # High security IKE crypto profile
        if create_all or args.high_security:
            log_section("HIGH SECURITY IKE CRYPTO PROFILE")
            log_info("Creating high-security IKE crypto profile")
            log_info(f"Using folder: {folder_name}")

            high_security_profile = create_strong_security_ike_profile(
                ike_profile_manager, folder_name
            )
            if high_security_profile:
                created_profiles.append(high_security_profile)
                profile_count += 1

        # Legacy compatibility IKE crypto profile
        if create_all or args.legacy:
            log_section("LEGACY COMPATIBILITY IKE CRYPTO PROFILE")
            log_info("Creating legacy compatibility IKE crypto profile")
            log_info(f"Using folder: {folder_name}")

            legacy_profile = create_legacy_compatibility_profile(ike_profile_manager, folder_name)
            if legacy_profile:
                created_profiles.append(legacy_profile)
                profile_count += 1

        # Custom lifetime IKE crypto profiles
        if create_all or args.lifetime:
            log_section("CUSTOM LIFETIME IKE CRYPTO PROFILES")
            log_info("Creating IKE crypto profiles with different lifetime settings")
            log_info(f"Using folder: {folder_name}")

            lifetime_profiles = create_custom_lifetime_profile(ike_profile_manager, folder_name)
            if lifetime_profiles:
                created_profiles.extend(lifetime_profiles)
                profile_count += len(lifetime_profiles)

        # Update one of the profiles (if any were created)
        if created_profiles:
            log_section("UPDATING IKE CRYPTO PROFILE")
            log_info("Demonstrating how to update an existing IKE crypto profile")

            fetch_and_update_profile(ike_profile_manager, created_profiles[0].id)

        # List and filter profiles
        log_section("LISTING AND FILTERING IKE CRYPTO PROFILES")
        log_info("Demonstrating how to search and filter IKE crypto profiles")
        list_and_filter_profiles(ike_profile_manager, folder_name)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are profiles to report and report generation is not disabled
        if created_profiles and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating IKE crypto profiles CSV report")
            profile_ids = [profile.id for profile in created_profiles]
            report_file = generate_profile_report(
                ike_profile_manager, profile_ids, execution_time_so_far
            )
            if report_file:
                log_success(f"Generated IKE crypto profiles report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_profiles)} IKE crypto profiles created"
                )
            else:
                log_error("Failed to generate IKE crypto profiles report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No IKE crypto profiles were created, skipping report generation")

        # Clean up the created profiles, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_profiles)} IKE crypto profiles"
            )
            log_info(
                "To clean up these profiles, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            log_operation_start(f"Cleaning up {len(created_profiles)} created IKE crypto profiles")
            profile_ids = [profile.id for profile in created_profiles]
            cleanup_profiles(ike_profile_manager, profile_ids)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total IKE crypto profiles created: {profile_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(f"Average time per profile: {execution_time / max(profile_count, 1):.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some IKE crypto profiles may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
