#!/usr/bin/env python3
"""
Comprehensive examples of working with Syslog Server Profile objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Syslog Server Profile configurations and operations commonly 
used in enterprise networks, including:

1. Syslog Server Profile Types:
   - UDP syslog servers
   - TCP syslog servers
   - Mixed transport configurations
   - Multiple servers in a single profile

2. Format configurations:
   - BSD format
   - IETF format
   - Custom log formats for different log types

3. Operational examples:
   - Creating syslog server profiles
   - Searching and filtering profiles
   - Updating profile configurations
   - Bulk operations and error handling

4. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with syslog server profile details
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
   - SKIP_CLEANUP=true: Set this to preserve created syslog server profiles for manual inspection
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
from scm.config.objects import SyslogServerProfile
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
logger = logging.getLogger("syslog_server_profile_example")


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


def create_udp_syslog_profile(syslog_profiles, folder="Texas"):
    """
    Create a syslog server profile with a UDP server.
    
    This function demonstrates creating a standard UDP syslog server profile
    commonly used for basic system and traffic logging.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        SyslogServerProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating UDP syslog server profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"udp-syslog-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    udp_syslog_config = {
        "name": profile_name,
        "folder": folder,  # Use the provided folder name
        "servers": {
            "primary-udp": {
                "name": "primary-udp",
                "server": "192.168.1.100",
                "transport": "UDP",
                "port": 514,
                "format": "BSD",
                "facility": "LOG_USER"
            }
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Primary server: {udp_syslog_config['servers']['primary-udp']['server']}")
    log_info(f"  - Transport: {udp_syslog_config['servers']['primary-udp']['transport']}")
    log_info(f"  - Port: {udp_syslog_config['servers']['primary-udp']['port']}")
    log_info(f"  - Format: {udp_syslog_config['servers']['primary-udp']['format']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = syslog_profiles.create(udp_syslog_config)
        log_success(f"Created syslog server profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_operation_complete(
            "UDP syslog server profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating syslog server profile", str(e))

    return None


def create_tcp_syslog_profile(syslog_profiles, folder="Texas"):
    """
    Create a syslog server profile with a TCP server.
    
    This function demonstrates creating a TCP syslog server profile,
    commonly used for more reliable log delivery and critical system events.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        SyslogServerProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating TCP syslog server profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"tcp-syslog-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration
    tcp_syslog_config = {
        "name": profile_name,
        "folder": folder,  # Use the provided folder name
        "servers": {
            "primary-tcp": {
                "name": "primary-tcp",
                "server": "logs.example.com",
                "transport": "TCP",
                "port": 1514,
                "format": "IETF",
                "facility": "LOG_LOCAL0"
            }
        },
        "format": {
            "traffic": "${time} ${src} ${dst} ${proto} ${action}",
            "threat": "${time} ${threatid} ${src} ${dst} ${severity}",
            "system": "${time} ${severity} ${actiontext}"
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Primary server: {tcp_syslog_config['servers']['primary-tcp']['server']}")
    log_info(f"  - Transport: {tcp_syslog_config['servers']['primary-tcp']['transport']}")
    log_info(f"  - Port: {tcp_syslog_config['servers']['primary-tcp']['port']}")
    log_info(f"  - Format: {tcp_syslog_config['servers']['primary-tcp']['format']}")
    log_info(f"  - Custom formats defined for: traffic, threat, system")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = syslog_profiles.create(tcp_syslog_config)
        log_success(f"Created syslog server profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_operation_complete(
            "TCP syslog server profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating syslog server profile", str(e))

    return None


def create_multi_server_profile(syslog_profiles, folder="Texas"):
    """
    Create a syslog server profile with multiple servers of different types.
    
    This function demonstrates creating a profile with multiple syslog servers,
    commonly used for redundant logging or separating different types of logs.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        SyslogServerProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating multi-server syslog profile")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"multi-syslog-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration with multiple servers
    multi_server_config = {
        "name": profile_name,
        "folder": folder,  # Use the provided folder name
        "servers": {
            "primary": {
                "name": "primary",
                "server": "logs-primary.example.com",
                "transport": "TCP",
                "port": 1514,
                "format": "IETF",
                "facility": "LOG_LOCAL0"
            },
            "secondary": {
                "name": "secondary",
                "server": "logs-backup.example.com",
                "transport": "TCP",
                "port": 1514,
                "format": "IETF",
                "facility": "LOG_LOCAL1"
            },
            "local": {
                "name": "local",
                "server": "192.168.10.50",
                "transport": "UDP",
                "port": 514,
                "format": "BSD",
                "facility": "LOG_USER"
            }
        },
        "format": {
            "traffic": "${time} ${src} ${dst} ${proto} ${action}",
            "threat": "${time} ${threatid} ${src} ${dst} ${severity}",
            "system": "${time} ${severity} ${actiontext}",
            "url": "${time} ${src} ${dst} ${url} ${category}",
            "wildfire": "${time} ${src} ${dst} ${filetype} ${severity}",
            "decryption": "${time} ${src} ${dst} ${cert-serial} ${error}"
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Number of servers: {len(multi_server_config['servers'])}")
    for server_name, server_data in multi_server_config['servers'].items():
        log_info(f"  - Server: {server_name}")
        log_info(f"    - Address: {server_data['server']}")
        log_info(f"    - Transport: {server_data['transport']}")
        log_info(f"    - Port: {server_data['port']}")
    log_info(f"  - Custom formats defined for: {', '.join(multi_server_config['format'].keys())}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = syslog_profiles.create(multi_server_config)
        log_success(f"Created syslog server profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_operation_complete(
            "Multi-server syslog profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating syslog server profile", str(e))

    return None


def create_escaping_profile(syslog_profiles, folder="Texas"):
    """
    Create a syslog server profile with character escaping configuration.
    
    This function demonstrates creating a syslog profile with character escaping,
    used to handle special characters in log messages.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        SyslogServerProfileResponseModel: The created profile, or None if creation failed
    """
    log_operation_start("Creating syslog profile with character escaping")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"escape-syslog-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the profile configuration with escaping
    escaping_config = {
        "name": profile_name,
        "folder": folder,  # Use the provided folder name
        "servers": {
            "main": {
                "name": "main",
                "server": "syslog.example.com",
                "transport": "TCP",
                "port": 6514,
                "format": "IETF",
                "facility": "LOG_LOCAL3"
            }
        },
        "format": {
            "escaping": {
                "escape_character": "\\",
                "escaped_characters": "%\"\\[]"
            },
            "traffic": "${time} ${src} ${dst} ${proto} ${action}",
            "threat": "${time} ${threatid} ${src} ${dst} ${severity}",
            "system": "${time} ${severity} ${actiontext}"
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Server: {escaping_config['servers']['main']['server']}")
    log_info(f"  - Transport: {escaping_config['servers']['main']['transport']}")
    log_info(f"  - Character escaping enabled:")
    log_info(f"    - Escape character: {escaping_config['format']['escaping']['escape_character']}")
    log_info(f"    - Escaped characters: {escaping_config['format']['escaping']['escaped_characters']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_profile = syslog_profiles.create(escaping_config)
        log_success(f"Created syslog server profile: {new_profile.name}")
        log_info(f"  - Object ID: {new_profile.id}")
        log_operation_complete(
            "Escaping syslog profile creation", f"Profile: {new_profile.name}"
        )
        return new_profile
    except NameNotUniqueError as e:
        log_error(f"Profile name conflict", e.message)
        log_info("Try using a different profile name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating syslog server profile", str(e))

    return None


def fetch_and_update_profile(syslog_profiles, profile_id):
    """
    Fetch a syslog server profile by ID and update its servers and format.
    
    This function demonstrates how to:
    1. Retrieve an existing syslog server profile using its ID
    2. Modify profile properties (servers, format)
    3. Submit the updated profile back to the SCM API
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        profile_id: The UUID of the profile to update
        
    Returns:
        SyslogServerProfileResponseModel: The updated profile, or None if update failed
    """
    logger.info(f"Fetching and updating syslog server profile with ID: {profile_id}")

    try:
        # Fetch the profile
        profile = syslog_profiles.get(profile_id)
        logger.info(f"Found syslog server profile: {profile.name}")

        # Create an update model with the current data
        update_data = {
            "id": profile.id,
            "name": profile.name,
            "folder": profile.folder if hasattr(profile, "folder") and profile.folder else None,
            "snippet": profile.snippet if hasattr(profile, "snippet") and profile.snippet else None,
            "device": profile.device if hasattr(profile, "device") and profile.device else None,
            "servers": profile.servers,
        }

        # Add a new server to the profile
        server_name = f"added-server-{uuid.uuid4().hex[:4]}"
        update_data["servers"][server_name] = {
            "name": server_name,
            "server": "192.168.100.200",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_LOCAL7"
        }

        # Modify or add format specifications
        if hasattr(profile, "format") and profile.format:
            update_data["format"] = profile.format.model_dump(exclude_unset=True)
            # Update existing format or add new ones
            update_data["format"]["system"] = "${time} ${host} UPDATED ${severity} ${module} ${actiontext}"
            update_data["format"]["auth"] = "${time} ${host} ${severity} ${user} ${event}"
        else:
            # Create new format if none exists
            update_data["format"] = {
                "system": "${time} ${host} NEW ${severity} ${module} ${actiontext}",
                "auth": "${time} ${host} ${severity} ${user} ${event}"
            }

        # Perform the update
        updated_profile = syslog_profiles.update(update_data)
        logger.info(
            f"Updated syslog server profile: {updated_profile.name} with {len(updated_profile.servers)} servers"
        )
        logger.info(f"Added new server: {server_name}")
        return updated_profile

    except NotFoundError as e:
        logger.error(f"Syslog server profile not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid syslog server profile update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_profiles(syslog_profiles, folder="Texas"):
    """
    List and filter syslog server profiles.
    
    This function demonstrates how to:
    1. List all syslog server profiles in a folder
    2. Filter profiles by various criteria
    3. Display detailed information about each profile
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to search in (default: "Texas")
        
    Returns:
        list: All retrieved syslog server profiles
    """
    logger.info("Listing and filtering syslog server profiles")

    # List all syslog server profiles in the folder
    all_profiles = syslog_profiles.list(folder=folder)
    logger.info(f"Found {len(all_profiles)} syslog server profiles in the {folder} folder")

    # Filter by transport protocol
    try:
        udp_profiles = syslog_profiles.list(folder=folder, transport=["UDP"])
        logger.info(f"Found {len(udp_profiles)} profiles with UDP transport")
        
        tcp_profiles = syslog_profiles.list(folder=folder, transport=["TCP"])
        logger.info(f"Found {len(tcp_profiles)} profiles with TCP transport")
    except Exception as e:
        logger.error(f"Error filtering by transport: {str(e)}")

    # Filter by format type
    try:
        bsd_profiles = syslog_profiles.list(folder=folder, format=["BSD"])
        logger.info(f"Found {len(bsd_profiles)} profiles with BSD format")
        
        ietf_profiles = syslog_profiles.list(folder=folder, format=["IETF"])
        logger.info(f"Found {len(ietf_profiles)} profiles with IETF format")
    except Exception as e:
        logger.error(f"Error filtering by format: {str(e)}")

    # Print details of profiles
    logger.info("\nDetails of syslog server profiles:")
    for profile in all_profiles[:5]:  # Print details of up to 5 profiles
        logger.info(f"  - Profile: {profile.name}")
        logger.info(f"    ID: {profile.id}")
        logger.info(f"    Folder: {profile.folder if hasattr(profile, 'folder') else 'None'}")
        logger.info(f"    Number of servers: {len(profile.servers)}")
        
        # Server details
        for server_name, server_data in profile.servers.items():
            logger.info(f"    - Server: {server_name}")
            logger.info(f"      Address: {server_data.get('server', 'Unknown')}")
            logger.info(f"      Transport: {server_data.get('transport', 'Unknown')}")
            logger.info(f"      Port: {server_data.get('port', 'Unknown')}")
            logger.info(f"      Format: {server_data.get('format', 'Unknown')}")
        
        # Format details if available
        if hasattr(profile, "format") and profile.format:
            format_fields = [field for field in dir(profile.format) 
                             if not field.startswith('_') and not callable(getattr(profile.format, field))]
            logger.info(f"    Custom formats defined for: {', '.join(format_fields)}")
        logger.info("")

    return all_profiles


def cleanup_syslog_profiles(syslog_profiles, profile_ids):
    """
    Delete the syslog server profiles created in this example.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        profile_ids: List of syslog server profile IDs to delete
    """
    logger.info("Cleaning up syslog server profiles")

    for profile_id in profile_ids:
        try:
            syslog_profiles.delete(profile_id)
            logger.info(f"Deleted syslog server profile with ID: {profile_id}")
        except NotFoundError as e:
            logger.error(f"Syslog server profile not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting syslog server profile: {str(e)}")


def create_bulk_syslog_profiles(syslog_profiles, folder="Texas"):
    """
    Create multiple syslog server profiles in a batch.
    
    This function demonstrates creating multiple syslog server profiles in a batch,
    which is useful for setting up multiple logging configurations at once.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created syslog server profiles, or empty list if creation failed
    """
    logger.info("Creating a batch of syslog server profiles")

    # Define a list of syslog server profile configurations to create
    profile_configs = [
        {
            "name": f"bulk-udp-1-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "servers": {
                "server1": {
                    "name": "server1",
                    "server": "10.1.1.1",
                    "transport": "UDP",
                    "port": 514,
                    "format": "BSD",
                    "facility": "LOG_USER"
                }
            }
        },
        {
            "name": f"bulk-tcp-1-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "servers": {
                "server1": {
                    "name": "server1",
                    "server": "10.1.1.2",
                    "transport": "TCP",
                    "port": 1514,
                    "format": "IETF",
                    "facility": "LOG_LOCAL0"
                }
            }
        },
        {
            "name": f"bulk-mixed-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "servers": {
                "tcp-server": {
                    "name": "tcp-server",
                    "server": "10.1.1.3",
                    "transport": "TCP",
                    "port": 1514,
                    "format": "IETF",
                    "facility": "LOG_LOCAL1"
                },
                "udp-server": {
                    "name": "udp-server",
                    "server": "10.1.1.4",
                    "transport": "UDP",
                    "port": 514,
                    "format": "BSD",
                    "facility": "LOG_LOCAL2"
                }
            }
        }
    ]

    created_profiles = []

    # Create each syslog server profile
    for profile_config in profile_configs:
        try:
            new_profile = syslog_profiles.create(profile_config)
            logger.info(
                f"Created syslog server profile: {new_profile.name} with ID: {new_profile.id}"
            )
            created_profiles.append(new_profile.id)
        except Exception as e:
            logger.error(f"Error creating profile {profile_config['name']}: {str(e)}")

    return created_profiles


def generate_syslog_profile_report(syslog_profiles, profile_ids, execution_time):
    """
    Generate a comprehensive CSV report of all syslog server profiles created by the script.
    
    This function fetches detailed information about each syslog server profile and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        syslog_profiles: The SyslogServerProfile manager instance used to fetch profile details
        profile_ids: List of syslog server profile IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"syslog_server_profiles_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Folder",
        "Number of Servers", 
        "Server Names",
        "Transport Protocols",
        "Format Types",
        "Custom Format Fields",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each syslog server profile
    profile_data = []
    for idx, profile_id in enumerate(profile_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(profile_ids) - 1:
            log_info(f"Processing profile {idx + 1} of {len(profile_ids)}")
            
        try:
            # Get the profile details
            profile = syslog_profiles.get(profile_id)
            
            # Server information
            server_names = ", ".join(profile.servers.keys())
            
            # Transport protocols
            transport_protocols = set()
            for server_data in profile.servers.values():
                if "transport" in server_data:
                    transport_protocols.add(server_data["transport"])
            transport_str = ", ".join(transport_protocols)
            
            # Format types
            format_types = set()
            for server_data in profile.servers.values():
                if "format" in server_data:
                    format_types.add(server_data["format"])
            format_str = ", ".join(format_types)
            
            # Custom format fields
            custom_format_fields = []
            if hasattr(profile, "format") and profile.format:
                format_dict = profile.format.model_dump(exclude_unset=True)
                # Filter out the 'escaping' key if present
                if "escaping" in format_dict:
                    format_dict.pop("escaping")
                custom_format_fields = list(format_dict.keys())
            custom_format_str = ", ".join(custom_format_fields) if custom_format_fields else "None"
            
            # Add profile data
            profile_data.append([
                profile.id,
                profile.name,
                profile.folder if hasattr(profile, "folder") and profile.folder else "None",
                len(profile.servers),
                server_names,
                transport_str,
                format_str,
                custom_format_str,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for profile ID {profile_id}", str(e))
            # Add minimal info for profiles that couldn't be retrieved
            profile_data.append([
                profile_id, 
                "ERROR", 
                "ERROR",
                "ERROR",
                "ERROR",
                "ERROR",
                "ERROR",
                f"Failed to retrieve profile details: {str(e)}",
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
            fallback_file = f"syslog_profiles_{timestamp}.csv"
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
    Parse command-line arguments for the syslog server profile example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which profile types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Syslog Server Profiles Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created syslog server profiles (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Profile Type Selection")
    object_group.add_argument(
        "--udp", 
        action="store_true",
        help="Create UDP syslog server profile examples"
    )
    object_group.add_argument(
        "--tcp", 
        action="store_true", 
        help="Create TCP syslog server profile examples"
    )
    object_group.add_argument(
        "--multi", 
        action="store_true",
        help="Create multi-server syslog profile examples"
    )
    object_group.add_argument(
        "--escaping", 
        action="store_true",
        help="Create syslog profile with character escaping"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk syslog profile examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all syslog server profile types (default behavior)"
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
    Execute the comprehensive set of syslog server profile examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of syslog server profiles (UDP, TCP, multi-server, etc.)
    4. Update an existing syslog server profile to demonstrate modification capabilities
    5. List and filter syslog server profiles to show search functionality
    6. Generate a detailed CSV report of all created syslog server profiles
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created syslog server profiles (don't delete them)
        --udp: Create only UDP syslog server profile examples
        --tcp: Create only TCP syslog server profile examples
        --multi: Create only multi-server syslog profile examples
        --escaping: Create only syslog profile with character escaping
        --bulk: Create only bulk syslog profile examples
        --all: Create all syslog server profile types (default behavior)
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
    create_all = args.all or not (args.udp or args.tcp or args.multi or args.escaping or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize SyslogServerProfile object
        log_section("SYSLOG SERVER PROFILE CONFIGURATION")
        log_operation_start("Initializing SyslogServerProfile manager")
        syslog_profiles = SyslogServerProfile(client)
        log_operation_complete("SyslogServerProfile manager initialization")

        # Create various syslog server profiles
        created_profiles = []

        # UDP Syslog Server Profile
        if create_all or args.udp:
            log_section("UDP SYSLOG SERVER PROFILES")
            log_info("Creating UDP syslog server profile examples")
            log_info(f"Using folder: {folder_name}")

            # Create a UDP syslog server profile
            udp_profile = create_udp_syslog_profile(syslog_profiles, folder_name)
            if udp_profile:
                created_profiles.append(udp_profile.id)
                object_count += 1

            log_success(f"Created UDP syslog server profiles")

        # TCP Syslog Server Profile
        if create_all or args.tcp:
            log_section("TCP SYSLOG SERVER PROFILES")
            log_info("Creating TCP syslog server profile examples")
            log_info(f"Using folder: {folder_name}")

            # Create a TCP syslog server profile
            tcp_profile = create_tcp_syslog_profile(syslog_profiles, folder_name)
            if tcp_profile:
                created_profiles.append(tcp_profile.id)
                object_count += 1

            log_success(f"Created TCP syslog server profiles")

        # Multi-server Syslog Profile
        if create_all or args.multi:
            log_section("MULTI-SERVER SYSLOG PROFILES")
            log_info("Creating multi-server syslog profile examples")
            log_info(f"Using folder: {folder_name}")

            # Create a multi-server syslog profile
            multi_profile = create_multi_server_profile(syslog_profiles, folder_name)
            if multi_profile:
                created_profiles.append(multi_profile.id)
                object_count += 1

            log_success(f"Created multi-server syslog profiles")

        # Syslog Profile with Character Escaping
        if create_all or args.escaping:
            log_section("SYSLOG PROFILES WITH CHARACTER ESCAPING")
            log_info("Creating syslog profile with character escaping examples")
            log_info(f"Using folder: {folder_name}")

            # Create a syslog profile with character escaping
            escaping_profile = create_escaping_profile(syslog_profiles, folder_name)
            if escaping_profile:
                created_profiles.append(escaping_profile.id)
                object_count += 1

            log_success(f"Created syslog profiles with character escaping")

        # Bulk Syslog Server Profile creation
        if create_all or args.bulk:
            log_section("BULK SYSLOG SERVER PROFILES")
            log_info("Creating multiple syslog server profiles in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk syslog server profiles
            bulk_profile_ids = create_bulk_syslog_profiles(syslog_profiles, folder_name)
            if bulk_profile_ids:
                created_profiles.extend(bulk_profile_ids)
                object_count += len(bulk_profile_ids)
                log_success(f"Created {len(bulk_profile_ids)} bulk syslog server profiles")

        # Update one of the objects
        if created_profiles:
            log_section("UPDATING SYSLOG SERVER PROFILES")
            log_info("Demonstrating how to update existing syslog server profiles")
            updated_profile = fetch_and_update_profile(syslog_profiles, created_profiles[0])

        # List and filter syslog server profiles
        log_section("LISTING AND FILTERING SYSLOG SERVER PROFILES")
        log_info("Demonstrating how to search and filter syslog server profiles")
        all_profiles = list_and_filter_profiles(syslog_profiles, folder_name)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_profiles and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating syslog server profiles CSV report")
            report_file = generate_syslog_profile_report(syslog_profiles, created_profiles, execution_time_so_far)
            if report_file:
                log_success(f"Generated syslog server profiles report: {report_file}")
                log_info(f"The report contains details of all {len(created_profiles)} syslog server profiles created")
            else:
                log_error("Failed to generate syslog server profiles report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No syslog server profiles were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_profiles)} syslog server profiles")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_profiles)} created syslog server profiles")
            cleanup_syslog_profiles(syslog_profiles, created_profiles)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total syslog server profiles created: {object_count}")
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
        log_info("Note: Some syslog server profiles may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()