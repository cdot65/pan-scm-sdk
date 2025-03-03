#!/usr/bin/env python3
"""
Comprehensive examples of working with Log Forwarding Profile objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Log Forwarding Profile configurations and operations commonly 
used in enterprise networks, including:

1. Log Forwarding Profile Types:
   - Traffic log forwarding profiles
   - Threat log forwarding profiles
   - URL log forwarding profiles
   - Wildfire log forwarding profiles
   - Multi-type log forwarding profiles

2. Operational examples:
   - Creating log forwarding profiles
   - Searching and filtering log forwarding profiles
   - Updating log forwarding profile configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with log forwarding profile details
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
   - SKIP_CLEANUP=true: Set this to preserve created log forwarding profiles for manual inspection
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
from scm.config.objects import LogForwardingProfile
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
logger = logging.getLogger("log_forwarding_profile_example")


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


def create_traffic_log_profile(profiles, folder="Texas"):
    """
    Create a log forwarding profile for traffic logs.
    
    This function demonstrates creating a profile for forwarding traffic logs
    to an HTTP server and Panorama.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        LogForwardingProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating traffic log forwarding profile")

    # Generate a unique profile name with UUID to avoid conflicts
    profile_name = f"traffic-logs-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    traffic_profile_config = {
        "name": profile_name,
        "description": "Example traffic log forwarding profile",
        "folder": folder,  # Use the provided folder name
        "match_list": [
            {
                "name": "internal-traffic",
                "log_type": "traffic",
                "filter": "addr.src in 10.0.0.0/8",
                "send_syslog": ["test123"],  # Using existing syslog profile from the environment
                "send_to_panorama": True
            }
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Traffic Log Profile")
    log_info(f"  - Match: {traffic_profile_config['match_list'][0]['name']}")
    log_info(f"  - Filter: {traffic_profile_config['match_list'][0]['filter']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = profiles.create(traffic_profile_config)
        log_success(f"Created log forwarding profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_info(f"  - Description: {new_profile.description}")
        log_operation_complete(
            "Traffic log forwarding profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating log forwarding profile", str(e))

    return None


def create_threat_log_profile(profiles, folder="Texas"):
    """
    Create a log forwarding profile for threat logs.
    
    This function demonstrates creating a profile for forwarding threat logs
    to syslog servers.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        LogForwardingProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating threat log forwarding profile")

    # Generate a unique profile name with UUID to avoid conflicts
    profile_name = f"threat-logs-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    threat_profile_config = {
        "name": profile_name,
        "description": "Example threat log forwarding profile",
        "folder": folder,  # Use the provided folder name
        "match_list": [
            {
                "name": "critical-threats",
                "log_type": "threat",
                "filter": "severity eq critical",
                "send_syslog": ["test123"],  # Using existing syslog profile from the environment
                "send_to_panorama": True
            }
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Threat Log Profile")
    log_info(f"  - Match: {threat_profile_config['match_list'][0]['name']}")
    log_info(f"  - Filter: {threat_profile_config['match_list'][0]['filter']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = profiles.create(threat_profile_config)
        log_success(f"Created log forwarding profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_info(f"  - Description: {new_profile.description}")
        log_operation_complete(
            "Threat log forwarding profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating log forwarding profile", str(e))

    return None


def create_url_log_profile(profiles, folder="Texas"):
    """
    Create a log forwarding profile for URL filtering logs.
    
    This function demonstrates creating a profile for forwarding URL logs
    to HTTP servers.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        LogForwardingProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating URL log forwarding profile")

    # Generate a unique profile name with UUID to avoid conflicts
    profile_name = f"url-logs-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    url_profile_config = {
        "name": profile_name,
        "description": "Example URL log forwarding profile",
        "folder": folder,  # Use the provided folder name
        "match_list": [
            {
                "name": "blocked-urls",
                "log_type": "url",
                "filter": "action eq block",
                "send_syslog": ["test123"],  # Using existing syslog profile from the environment
                "send_to_panorama": False
            }
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: URL Log Profile")
    log_info(f"  - Match: {url_profile_config['match_list'][0]['name']}")
    log_info(f"  - Filter: {url_profile_config['match_list'][0]['filter']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = profiles.create(url_profile_config)
        log_success(f"Created log forwarding profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_info(f"  - Description: {new_profile.description}")
        log_operation_complete(
            "URL log forwarding profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating log forwarding profile", str(e))

    return None


def create_wildfire_log_profile(profiles, folder="Texas"):
    """
    Create a log forwarding profile for WildFire logs.
    
    This function demonstrates creating a profile for forwarding WildFire logs
    to both HTTP and syslog servers.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        LogForwardingProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating WildFire log forwarding profile")

    # Generate a unique profile name with UUID to avoid conflicts
    profile_name = f"wildfire-logs-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    wildfire_profile_config = {
        "name": profile_name,
        "description": "Example WildFire log forwarding profile",
        "folder": folder,  # Use the provided folder name
        "match_list": [
            {
                "name": "malware-verdicts",
                "log_type": "wildfire",
                "filter": "verdict eq malware",
                "send_syslog": ["test123"],  # Using existing syslog profile from the environment
                "send_to_panorama": True
            }
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: WildFire Log Profile")
    log_info(f"  - Match: {wildfire_profile_config['match_list'][0]['name']}")
    log_info(f"  - Filter: {wildfire_profile_config['match_list'][0]['filter']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = profiles.create(wildfire_profile_config)
        log_success(f"Created log forwarding profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_info(f"  - Description: {new_profile.description}")
        log_operation_complete(
            "WildFire log forwarding profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating log forwarding profile", str(e))

    return None


def create_multi_type_profile(profiles, folder="Texas"):
    """
    Create a log forwarding profile with multiple match lists for different log types.
    
    This function demonstrates creating a comprehensive profile for managing
    multiple log types in a single profile.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        LogForwardingProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating multi-type log forwarding profile")

    # Generate a unique profile name with UUID to avoid conflicts
    profile_name = f"multi-type-logs-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration with multiple match lists
    multi_type_profile_config = {
        "name": profile_name,
        "description": "Example multi-type log forwarding profile",
        "folder": folder,  # Use the provided folder name
        "match_list": [
            {
                "name": "critical-traffic",
                "log_type": "traffic",
                "filter": "flags.set eq emergency",
                "send_syslog": ["test123"]  # Using existing syslog profile from the environment
            },
            {
                "name": "high-severity-threats",
                "log_type": "threat",
                "filter": "severity eq high",
                "send_syslog": ["test123"]  # Using existing syslog profile from the environment
            },
            {
                "name": "malicious-urls",
                "log_type": "url",
                "filter": "category.member eq malware",
                "send_syslog": ["test123"]  # Using existing syslog profile from the environment
            }
        ],
        "enhanced_application_logging": True
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Multi-type Log Profile")
    log_info(f"  - Match Lists: {len(multi_type_profile_config['match_list'])}")
    for idx, match in enumerate(multi_type_profile_config['match_list']):
        log_info(f"  - Match {idx+1}: {match['name']} ({match['log_type']} logs)")
        log_info(f"    Filter: {match['filter']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = profiles.create(multi_type_profile_config)
        log_success(f"Created log forwarding profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_info(f"  - Description: {new_profile.description}")
        log_operation_complete(
            "Multi-type log forwarding profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating log forwarding profile", str(e))

    return None


def fetch_and_update_profile(profiles, profile_id):
    """
    Fetch a log forwarding profile by ID and update its description and match list.
    
    This function demonstrates how to:
    1. Retrieve an existing log forwarding profile using its ID
    2. Modify profile properties (description, match lists)
    3. Submit the updated profile back to the SCM API
    
    Args:
        profiles: The LogForwardingProfile manager instance
        profile_id: The UUID of the profile to update
        
    Returns:
        LogForwardingProfileResponseModel: The updated profile, or None if update failed
    """
    logger.info(f"Fetching and updating log forwarding profile with ID: {profile_id}")

    try:
        # Fetch the profile
        profile = profiles.get(profile_id)
        logger.info(f"Found log forwarding profile: {profile.name}")

        # Update description
        profile.description = f"Updated description for {profile.name}"
        
        # Update/add match lists
        if profile.match_list:
            # Modify existing match list
            for match in profile.match_list:
                match.action_desc = f"Updated match list for {match.name}"
                
                # Add send_to_panorama option if not already set
                if match.send_to_panorama is None:
                    match.send_to_panorama = True
        else:
            # Create a new match list if none exists
            profile.match_list = [
                {
                    "name": "updated-match",
                    "log_type": "traffic",
                    "filter": "addr.src in 192.168.0.0/16",
                    "send_http": ["HTTP-Profile"],
                    "action_desc": "Added during update operation"
                }
            ]

        # Perform the update
        updated_profile = profiles.update(profile)
        logger.info(
            f"Updated log forwarding profile: {updated_profile.name} with description: {updated_profile.description}"
        )
        return updated_profile

    except NotFoundError as e:
        logger.error(f"Log forwarding profile not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid profile update: {e.message}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_profiles(profiles):
    """
    List and filter log forwarding profiles.
    
    This function demonstrates how to:
    1. List all log forwarding profiles in a folder
    2. Filter profiles by various criteria
    3. Display detailed information about each profile
    
    Args:
        profiles: The LogForwardingProfile manager instance
        
    Returns:
        list: All retrieved log forwarding profiles
    """
    logger.info("Listing and filtering log forwarding profiles")

    # List all log forwarding profiles in the Texas folder
    all_profiles = profiles.list(folder="Texas")
    logger.info(f"Found {len(all_profiles)} log forwarding profiles in the Texas folder")

    # Filter by log type
    try:
        traffic_profiles = profiles.list(folder="Texas", log_type="traffic")
        logger.info(f"Found {len(traffic_profiles)} profiles with traffic log type")
    except Exception as e:
        logger.error(f"Filtering by log_type failed: {str(e)}")

    # Filter by multiple log types
    try:
        security_profiles = profiles.list(folder="Texas", log_types=["threat", "wildfire"])
        logger.info(f"Found {len(security_profiles)} profiles with threat or wildfire log types")
    except Exception as e:
        logger.error(f"Filtering by log_types failed: {str(e)}")

    # Print details of profiles
    logger.info("\nDetails of log forwarding profiles:")
    for profile in all_profiles[:5]:  # Print details of up to 5 profiles
        logger.info(f"  - Profile: {profile.name}")
        logger.info(f"    ID: {profile.id}")
        logger.info(f"    Description: {profile.description}")
        
        # Print match list details
        if profile.match_list:
            logger.info(f"    Match Lists: {len(profile.match_list)}")
            for match in profile.match_list:
                logger.info(f"      - {match.name} ({match.log_type})")
                logger.info(f"        Filter: {match.filter if match.filter else 'None'}")
                
                if match.send_http:
                    logger.info(f"        HTTP Servers: {', '.join(match.send_http)}")
                if match.send_syslog:
                    logger.info(f"        Syslog Servers: {', '.join(match.send_syslog)}")
                logger.info(f"        Send to Panorama: {match.send_to_panorama}")
        else:
            logger.info("    No match lists defined")
        
        logger.info("")

    return all_profiles


def cleanup_profiles(profiles, profile_ids):
    """
    Delete the log forwarding profiles created in this example.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        profile_ids: List of profile IDs to delete
    """
    logger.info("Cleaning up log forwarding profiles")

    for profile_id in profile_ids:
        try:
            profiles.delete(profile_id)
            logger.info(f"Deleted log forwarding profile with ID: {profile_id}")
        except NotFoundError as e:
            logger.error(f"Log forwarding profile not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting log forwarding profile: {str(e)}")


def create_bulk_profiles(profiles, folder="Texas"):
    """
    Create multiple log forwarding profiles in a batch.
    
    This function demonstrates creating multiple profiles in a batch,
    which is useful for setting up multiple log forwarding profiles at once.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: Folder name in SCM to create profiles in (default: "Texas")
        
    Returns:
        list: List of IDs of created profiles, or empty list if creation failed
    """
    logger.info("Creating a batch of log forwarding profiles")

    # Define a list of profiles to create
    profile_configs = [
        {
            "name": f"bulk-traffic-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created traffic profile",
            "folder": folder,
            "match_list": [
                {
                    "name": "bulk-traffic-match",
                    "log_type": "traffic",
                    "filter": "addr.dst in 172.16.0.0/12",
                    "send_syslog": ["test123"]  # Using existing syslog profile from the environment
                }
            ]
        },
        {
            "name": f"bulk-threat-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created threat profile",
            "folder": folder,
            "match_list": [
                {
                    "name": "bulk-threat-match",
                    "log_type": "threat",
                    "filter": "severity eq informational",
                    "send_syslog": ["test123"]  # Using existing syslog profile from the environment
                }
            ]
        },
        {
            "name": f"bulk-url-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created URL profile",
            "folder": folder,
            "match_list": [
                {
                    "name": "bulk-url-match",
                    "log_type": "url",
                    "filter": "category.member eq social-networking",
                    "send_syslog": ["test123"]  # Using existing syslog profile from the environment
                }
            ]
        }
    ]

    created_profiles = []

    # Create each profile
    for profile_config in profile_configs:
        try:
            new_profile = profiles.create(profile_config)
            logger.info(
                f"Created log forwarding profile: {new_profile.name} with ID: {new_profile.id}"
            )
            created_profiles.append(new_profile.id)
        except Exception as e:
            logger.error(f"Error creating profile {profile_config['name']}: {str(e)}")

    return created_profiles


def generate_profile_report(profiles, profile_ids, execution_time):
    """
    Generate a comprehensive CSV report of all log forwarding profiles created by the script.
    
    This function fetches detailed information about each profile and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        profiles: The LogForwardingProfile manager instance used to fetch profile details
        profile_ids: List of profile IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"log_forwarding_profiles_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Description", 
        "Match Lists Count",
        "Log Types", 
        "HTTP Servers",
        "Syslog Servers",
        "Send to Panorama",
        "Enhanced Application Logging",
        "Created On",
        "Report Generation Time"
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
            profile = profiles.get(profile_id)
            
            # Extract log types from match lists
            log_types = []
            http_servers = []
            syslog_servers = []
            send_to_panorama = "No"
            
            if profile.match_list:
                for match in profile.match_list:
                    # Add log type if not already in list
                    if match.log_type not in log_types:
                        log_types.append(match.log_type)
                        
                    # Add HTTP servers
                    if match.send_http:
                        for server in match.send_http:
                            if server not in http_servers:
                                http_servers.append(server)
                                
                    # Add Syslog servers
                    if match.send_syslog:
                        for server in match.send_syslog:
                            if server not in syslog_servers:
                                syslog_servers.append(server)
                                
                    # Check if any match sends to Panorama
                    if match.send_to_panorama:
                        send_to_panorama = "Yes"
            
            # Add profile data
            profile_data.append([
                profile.id,
                profile.name,
                profile.description if profile.description else "None",
                len(profile.match_list) if profile.match_list else 0,
                ", ".join(log_types) if log_types else "None",
                ", ".join(http_servers) if http_servers else "None",
                ", ".join(syslog_servers) if syslog_servers else "None",
                send_to_panorama,
                "Yes" if profile.enhanced_application_logging else "No",
                getattr(profile, "created_on", "Unknown"),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for profile ID {profile_id}", str(e))
            # Add minimal info for profiles that couldn't be retrieved
            profile_data.append([
                profile_id, 
                "ERROR", 
                "Failed to retrieve profile details", 
                "ERROR",
                "ERROR",
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
            writer.writerows(profile_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(profile_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"log_forwarding_profiles_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(profile_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the log forwarding profile example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created profiles
    - Which profile types to create
    - Whether to generate a CSV report
    - Folder name to use for profile creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Log Forwarding Profiles Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created log forwarding profiles (don't delete them)"
    )
    
    # Profile types to create
    profile_group = parser.add_argument_group("Profile Type Selection")
    profile_group.add_argument(
        "--traffic", 
        action="store_true",
        help="Create traffic log profile examples"
    )
    profile_group.add_argument(
        "--threat", 
        action="store_true", 
        help="Create threat log profile examples"
    )
    profile_group.add_argument(
        "--url", 
        action="store_true",
        help="Create URL log profile examples"
    )
    profile_group.add_argument(
        "--wildfire", 
        action="store_true",
        help="Create WildFire log profile examples"
    )
    profile_group.add_argument(
        "--multi", 
        action="store_true",
        help="Create multi-type log profile examples"
    )
    profile_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk log profile examples"
    )
    profile_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all log profile types (default behavior)"
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
        help="Folder name in SCM to create profiles in"
    )
    
    return parser.parse_args()


def check_syslog_profile_exists(profiles, folder, syslog_name="test123"):
    """
    Verify if the required syslog server profile exists in the environment.
    
    Args:
        profiles: The LogForwardingProfile manager instance
        folder: The folder to check in
        syslog_name: The name of the syslog server profile to look for
        
    Returns:
        bool: True if the syslog profile exists or verification was skipped, False otherwise
    """
    log_info(f"Checking if syslog server profile '{syslog_name}' exists...")
    
    try:
        # Get existing profiles to check if any of them use the syslog profile
        all_profiles = profiles.list(folder=folder)
        
        # Check if any of the profiles contain a reference to the syslog server
        for profile in all_profiles:
            if profile.match_list:
                for match in profile.match_list:
                    if match.send_syslog and syslog_name in match.send_syslog:
                        log_success(f"Found syslog server profile '{syslog_name}' in existing profiles")
                        return True
        
        log_warning(f"Syslog server profile '{syslog_name}' not found in any existing profiles")
        log_info("The script may fail if the syslog server profile doesn't exist")
        log_info("You may need to modify the script to use an existing syslog server profile")
        return False
    
    except Exception as e:
        log_warning(f"Error checking for syslog server profile: {str(e)}")
        log_info("Proceeding anyway, but the script may fail if required profiles don't exist")
        return True

def main():
    """
    Execute the comprehensive set of log forwarding profile examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Check if required syslog server profiles exist
    4. Create various types of log forwarding profiles (traffic, threat, URL, WildFire, multi-type)
    5. Update an existing profile to demonstrate modification capabilities
    6. List and filter profiles to show search functionality
    7. Generate a detailed CSV report of all created profiles
    8. Clean up created profiles (unless skip_cleanup is enabled)
    9. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created profiles (don't delete them)
        --traffic: Create only traffic log profile examples
        --threat: Create only threat log profile examples
        --url: Create only URL log profile examples
        --wildfire: Create only WildFire log profile examples
        --multi: Create only multi-type log profile examples
        --bulk: Create only bulk log profile examples
        --all: Create all profile types (default behavior)
        --no-report: Skip CSV report generation
        --folder: Folder name in SCM to create profiles in (default: "Texas")
    
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
    object_count = 0
    
    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"
    
    # Determine which profile types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.traffic or args.threat or args.url or args.wildfire or args.multi or args.bulk)
    
    # Get folder name for profile creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize LogForwardingProfile object
        log_section("LOG FORWARDING PROFILE CONFIGURATION")
        log_operation_start("Initializing LogForwardingProfile object manager")
        profiles = LogForwardingProfile(client)
        log_operation_complete("LogForwardingProfile object manager initialization")
        
        # Verify that required syslog server profile exists
        log_section("PREREQUISITE VERIFICATION")
        syslog_exists = check_syslog_profile_exists(profiles, folder_name)
        if not syslog_exists:
            log_warning("The script may encounter errors if the required syslog server profile doesn't exist")
            log_info("You can modify the script to use an existing syslog server profile in your environment")
        
        # Create various log forwarding profiles
        created_profiles = []

        # Traffic Log Profile
        if create_all or args.traffic:
            log_section("TRAFFIC LOG PROFILES")
            log_info("Creating traffic log forwarding profile patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a traffic log profile
            traffic_profile = create_traffic_log_profile(profiles, folder_name)
            if traffic_profile:
                created_profiles.append(traffic_profile.id)
                object_count += 1

            log_success(f"Created {len(created_profiles)} log forwarding profiles so far")

        # Threat Log Profile
        if create_all or args.threat:
            log_section("THREAT LOG PROFILES")
            log_info("Creating threat log forwarding profile patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a threat log profile
            threat_profile = create_threat_log_profile(profiles, folder_name)
            if threat_profile:
                created_profiles.append(threat_profile.id)
                object_count += 1

            log_success(f"Created threat log forwarding profiles")

        # URL Log Profile
        if create_all or args.url:
            log_section("URL LOG PROFILES")
            log_info("Creating URL log forwarding profile patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a URL log profile
            url_profile = create_url_log_profile(profiles, folder_name)
            if url_profile:
                created_profiles.append(url_profile.id)
                object_count += 1

            log_success(f"Created URL log forwarding profiles")

        # WildFire Log Profile
        if create_all or args.wildfire:
            log_section("WILDFIRE LOG PROFILES")
            log_info("Creating WildFire log forwarding profile patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a WildFire log profile
            wildfire_profile = create_wildfire_log_profile(profiles, folder_name)
            if wildfire_profile:
                created_profiles.append(wildfire_profile.id)
                object_count += 1

            log_success(f"Created WildFire log forwarding profiles")

        # Multi-type Log Profile
        if create_all or args.multi:
            log_section("MULTI-TYPE LOG PROFILES")
            log_info("Creating multi-type log forwarding profile patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a multi-type log profile
            multi_profile = create_multi_type_profile(profiles, folder_name)
            if multi_profile:
                created_profiles.append(multi_profile.id)
                object_count += 1

            log_success(f"Created multi-type log forwarding profiles")

        # Bulk Profile creation
        if create_all or args.bulk:
            log_section("BULK LOG PROFILES")
            log_info("Creating multiple log forwarding profiles in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk profiles
            bulk_profile_ids = create_bulk_profiles(profiles, folder_name)
            if bulk_profile_ids:
                created_profiles.extend(bulk_profile_ids)
                object_count += len(bulk_profile_ids)
                log_success(f"Created {len(bulk_profile_ids)} bulk log forwarding profiles")

        # Update one of the profiles
        if created_profiles:
            log_section("UPDATING LOG FORWARDING PROFILES")
            log_info("Demonstrating how to update existing log forwarding profiles")
            updated_profile = fetch_and_update_profile(profiles, created_profiles[0])

        # List and filter profiles
        log_section("LISTING AND FILTERING LOG FORWARDING PROFILES")
        log_info("Demonstrating how to search and filter log forwarding profiles")
        all_profiles = list_and_filter_profiles(profiles)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are profiles to report and report generation is not disabled
        if created_profiles and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating log forwarding profiles CSV report")
            report_file = generate_profile_report(profiles, created_profiles, execution_time_so_far)
            if report_file:
                log_success(f"Generated log forwarding profiles report: {report_file}")
                log_info(f"The report contains details of all {len(created_profiles)} profiles created")
            else:
                log_error("Failed to generate log forwarding profiles report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No log forwarding profiles were created, skipping report generation")

        # Clean up the created profiles, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_profiles)} log forwarding profiles")
            log_info("To clean up these profiles, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_profiles)} created log forwarding profiles")
            cleanup_profiles(profiles, created_profiles)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total log forwarding profiles created: {object_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(
            f"Average time per profile: {execution_time/max(object_count, 1):.2f} seconds"
        )

    except AuthenticationError as e:
        log_error(f"Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some log forwarding profiles may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()