#!/usr/bin/env python3
"""Comprehensive examples of working with HTTP Server Profiles in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a variety of operations for managing HTTP Server Profiles
which are used to define HTTP servers for sending system logs:

1. HTTP Server Profile Creation:
   - Basic HTTP server profile with HTTP protocol
   - Advanced HTTPS server profile with TLS and certificate configuration
   - Multiple server configurations within a single profile
   - HTTP server profiles in different containers (folder, snippet, device)

2. HTTP Server Profile Management:
   - Listing HTTP server profiles with various filtering options
   - Fetching specific HTTP server profiles by name
   - Updating existing HTTP server profiles
   - Deleting HTTP server profiles

3. Configuration Examples:
   - Protocol configuration (HTTP vs HTTPS)
   - TLS version configuration
   - Tag registration settings
   - Payload format configuration for various log types

4. Operational examples:
   - Error handling and validation
   - Container-based operations (folder, snippet, device)
   - Pagination for large result sets

5. Reporting and Documentation:
   - Detailed CSV report generation
   - Execution statistics tracking

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- Progress tracking and execution statistics
- Colorized output for improved readability
- CSV report generation with profile details

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
from scm.config.objects import HTTPServerProfile
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)
from scm.models.objects import (
    HTTPServerProfileUpdateModel,
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
logger = logging.getLogger("http_server_profile_example")


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


def create_basic_http_server_profile(http_profiles, folder="Texas"):
    """Create a basic HTTP server profile with HTTP protocol.

    This function demonstrates creating a simple HTTP server profile with a basic HTTP server
    configuration using a dictionary that gets converted to a HTTPServerProfileCreateModel.

    Args:
        http_profiles: The HTTP server profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The created HTTP server profile, or None if creation failed
    """
    log_operation_start("Creating basic HTTP server profile with HTTP protocol")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"basic-http-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Method 1: Using a dictionary and letting the SDK create models
    basic_profile_config = {
        "name": profile_name,
        "description": "Example basic HTTP server profile",
        "folder": folder,  # Use the provided folder name
        "tag_registration": True,
        "server": [
            {
                "name": "log-collector",
                "address": "192.168.1.100",
                "protocol": "HTTP",
                "port": 80,
                "http_method": "POST",
            }
        ],
        "format": {
            "traffic": {},
            "threat": {},
            "url": {},
        },
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(
        f"  - Server: {basic_profile_config['server'][0]['name']} ({basic_profile_config['server'][0]['address']})"
    )
    log_info(f"  - Protocol: {basic_profile_config['server'][0]['protocol']}")
    log_info(f"  - Port: {basic_profile_config['server'][0]['port']}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_http_profile = http_profiles.create(basic_profile_config)
        log_success(f"Created HTTP server profile: {new_http_profile.name}")
        log_info(f"  - Profile ID: {new_http_profile.id}")
        log_info(
            f"  - Server: {new_http_profile.server[0].name} ({new_http_profile.server[0].address})"
        )
        log_operation_complete(
            "Basic HTTP server profile creation", f"Profile: {new_http_profile.name}"
        )
        return new_http_profile
    except NameNotUniqueError as e:
        log_error("HTTP server profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_type = str(type(e).__name__)
        if "HTTPSConnectionPool" in str(e) and "500" in str(e):
            log_error(
                "API server error (500) when creating HTTP server profile - "
                "The server may be experiencing issues or the API endpoint may not be fully implemented yet",
                str(e),
            )
            log_info("This error is coming from the SCM API server, not your code")
        else:
            log_error(f"Unexpected error creating HTTP server profile ({error_type})", str(e))

    return None


def create_https_server_profile(http_profiles, folder="Texas"):
    """Create an HTTP server profile with HTTPS protocol and TLS configuration.

    This function demonstrates creating an HTTP server profile with HTTPS protocol,
    TLS version specification, and certificate configuration.

    Args:
        http_profiles: The HTTP server profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The created HTTP server profile, or None if creation failed
    """
    log_operation_start("Creating HTTP server profile with HTTPS protocol")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"https-server-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HTTP server profile configuration with HTTPS
    https_profile_config = {
        "name": profile_name,
        "description": "Example HTTPS server profile with TLS configuration",
        "folder": folder,
        "tag_registration": True,
        "server": [
            {
                "name": "secure-log-collector",
                "address": "secure.example.com",
                "protocol": "HTTPS",
                "port": 443,
                "tls_version": "1.2",
                "certificate_profile": "default",
                "http_method": "POST",
            }
        ],
        "format": {
            "traffic": {},
            "threat": {},
            "url": {},
            "wildfire": {},
            "data": {},
        },
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(
        f"  - Server: {https_profile_config['server'][0]['name']} ({https_profile_config['server'][0]['address']})"
    )
    log_info(f"  - Protocol: {https_profile_config['server'][0]['protocol']}")
    log_info(f"  - Port: {https_profile_config['server'][0]['port']}")
    log_info(f"  - TLS Version: {https_profile_config['server'][0]['tls_version']}")
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_https_profile = http_profiles.create(https_profile_config)
        log_success(f"Created HTTPS server profile: {new_https_profile.name}")
        log_info(f"  - Profile ID: {new_https_profile.id}")
        log_info(
            f"  - Server: {new_https_profile.server[0].name} ({new_https_profile.server[0].address})"
        )
        log_info(f"  - TLS Version: {new_https_profile.server[0].tls_version}")
        log_operation_complete(
            "HTTPS server profile creation", f"Profile: {new_https_profile.name}"
        )
        return new_https_profile
    except NameNotUniqueError as e:
        log_error("HTTP server profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HTTP server profile", str(e))

    return None


def create_multi_server_profile(http_profiles, folder="Texas"):
    """Create an HTTP server profile with multiple server configurations.

    This function demonstrates creating an HTTP server profile that includes
    multiple server configurations for redundancy or different log types.

    Args:
        http_profiles: The HTTP server profile manager instance
        folder: Folder name in SCM to create the profile in (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The created HTTP server profile, or None if creation failed
    """
    log_operation_start("Creating HTTP server profile with multiple servers")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"multi-server-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HTTP server profile configuration with multiple servers
    multi_server_config = {
        "name": profile_name,
        "description": "Example HTTP server profile with multiple server configurations",
        "folder": folder,
        "tag_registration": True,
        "server": [
            {
                "name": "primary-log-collector",
                "address": "192.168.1.100",
                "protocol": "HTTP",
                "port": 80,
                "http_method": "POST",
            },
            {
                "name": "backup-log-collector",
                "address": "192.168.1.101",
                "protocol": "HTTP",
                "port": 80,
                "http_method": "POST",
            },
            {
                "name": "secure-log-collector",
                "address": "secure.example.com",
                "protocol": "HTTPS",
                "port": 443,
                "tls_version": "1.2",
                "certificate_profile": "default",
                "http_method": "POST",
            },
        ],
        "format": {
            "traffic": {},
            "threat": {},
            "wildfire": {},
        },
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(f"  - Number of servers: {len(multi_server_config['server'])}")
    for idx, server in enumerate(multi_server_config["server"]):
        log_info(
            f"  - Server {idx + 1}: {server['name']} ({server['address']}) - {server['protocol']}:{server['port']}"
        )
    log_info(f"  - Container: folder '{folder}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_multi_profile = http_profiles.create(multi_server_config)
        log_success(f"Created multi-server HTTP profile: {new_multi_profile.name}")
        log_info(f"  - Profile ID: {new_multi_profile.id}")
        log_info(f"  - Number of servers: {len(new_multi_profile.server)}")
        log_operation_complete(
            "Multi-server HTTP profile creation", f"Profile: {new_multi_profile.name}"
        )
        return new_multi_profile
    except NameNotUniqueError as e:
        log_error("HTTP server profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating HTTP server profile", str(e))

    return None


def create_http_server_profile_with_snippet(http_profiles, folder="Texas"):
    """Create an HTTP server profile in a snippet container instead of a folder.

    This function demonstrates creating an HTTP server profile that is stored in a snippet
    container instead of the default folder container.

    Args:
        http_profiles: The HTTP server profile manager instance
        folder: Fallback folder name in SCM to create the profile in (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The created HTTP server profile, or None if creation failed
    """
    log_operation_start("Creating HTTP server profile in a snippet container")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"snippet-http-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HTTP server profile configuration in a snippet
    snippet_profile_config = {
        "name": profile_name,
        "description": "Example HTTP server profile in a snippet container",
        "snippet": "test123",  # Specify snippet instead of folder
        "tag_registration": True,
        "server": [
            {
                "name": "snippet-server",
                "address": "192.168.5.100",
                "protocol": "HTTP",
                "port": 80,
                "http_method": "POST",
            }
        ],
        "format": {
            "traffic": {},
            "threat": {},
        },
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(
        f"  - Server: {snippet_profile_config['server'][0]['name']} ({snippet_profile_config['server'][0]['address']})"
    )
    log_info(f"  - Protocol: {snippet_profile_config['server'][0]['protocol']}")
    log_info(f"  - Container: snippet '{snippet_profile_config['snippet']}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_http_profile = http_profiles.create(snippet_profile_config)
        log_success(f"Created HTTP server profile: {new_http_profile.name}")
        log_info(f"  - Profile ID: {new_http_profile.id}")
        log_info(f"  - Container: snippet '{new_http_profile.snippet}'")
        log_operation_complete(
            "Snippet HTTP server profile creation", f"Profile: {new_http_profile.name}"
        )
        return new_http_profile
    except NameNotUniqueError as e:
        log_error("HTTP server profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            # If snippet doesn't exist, fallback to folder
            if "snippet" in str(e.details).lower():
                log_warning(f"Snippet 'test123' may not exist. Falling back to folder '{folder}'")
                snippet_profile_config.pop("snippet")
                snippet_profile_config["folder"] = folder
                try:
                    fallback_profile = http_profiles.create(snippet_profile_config)
                    log_success(
                        f"Created HTTP server profile in folder instead: {fallback_profile.name}"
                    )
                    log_info(f"  - Profile ID: {fallback_profile.id}")
                    log_info(f"  - Container: folder '{fallback_profile.folder}'")
                    log_operation_complete(
                        "Fallback HTTP server profile creation",
                        f"Profile: {fallback_profile.name}",
                    )
                    return fallback_profile
                except Exception as fallback_error:
                    log_error("Fallback creation also failed", str(fallback_error))
    except Exception as e:
        log_error("Unexpected error creating HTTP server profile", str(e))

    return None


def create_http_server_profile_with_device(http_profiles, folder="Texas"):
    """Create an HTTP server profile in a device container.

    This function demonstrates creating an HTTP server profile that is stored in a device
    container instead of the default folder container.

    Args:
        http_profiles: The HTTP server profile manager instance
        folder: Fallback folder name in SCM to create the profile in (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The created HTTP server profile, or None if creation failed
    """
    log_operation_start("Creating HTTP server profile in a device container")

    # Generate a unique profile name with timestamp to avoid conflicts
    profile_name = f"device-http-profile-{uuid.uuid4().hex[:6]}"
    log_info(f"Profile name: {profile_name}")

    # Create the HTTP server profile configuration in a device
    device_profile_config = {
        "name": profile_name,
        "description": "Example HTTP server profile in a device container",
        "device": "austin1",  # Specify device instead of folder
        "server": [
            {
                "name": "device-server",
                "address": "10.0.0.100",
                "protocol": "HTTP",
                "port": 514,
                "http_method": "POST",
            }
        ],
        "format": {
            "traffic": {},
            "threat": {},
        },
    }

    log_info("Configuration details:")
    log_info(f"  - Name: {profile_name}")
    log_info(
        f"  - Server: {device_profile_config['server'][0]['name']} ({device_profile_config['server'][0]['address']})"
    )
    log_info(f"  - Protocol: {device_profile_config['server'][0]['protocol']}")
    log_info(f"  - Container: device '{device_profile_config['device']}'")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_http_profile = http_profiles.create(device_profile_config)
        log_success(f"Created HTTP server profile: {new_http_profile.name}")
        log_info(f"  - Profile ID: {new_http_profile.id}")
        log_info(f"  - Container: device '{new_http_profile.device}'")
        log_operation_complete(
            "Device HTTP server profile creation", f"Profile: {new_http_profile.name}"
        )
        return new_http_profile
    except NameNotUniqueError as e:
        log_error("HTTP server profile name conflict", e.message)
        log_info("Try using a different profile name or check existing profiles")
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            # If device doesn't exist, fallback to folder
            if "device" in str(e.details).lower():
                log_warning(f"Device 'austin1' may not exist. Falling back to folder '{folder}'")
                device_profile_config.pop("device")
                device_profile_config["folder"] = folder
                try:
                    fallback_profile = http_profiles.create(device_profile_config)
                    log_success(
                        f"Created HTTP server profile in folder instead: {fallback_profile.name}"
                    )
                    log_info(f"  - Profile ID: {fallback_profile.id}")
                    log_info(f"  - Container: folder '{fallback_profile.folder}'")
                    log_operation_complete(
                        "Fallback HTTP server profile creation",
                        f"Profile: {fallback_profile.name}",
                    )
                    return fallback_profile
                except Exception as fallback_error:
                    log_error("Fallback creation also failed", str(fallback_error))
    except Exception as e:
        log_error("Unexpected error creating HTTP server profile", str(e))

    return None


def fetch_and_update_http_server_profile(http_profiles, profile_id):
    """Fetch an HTTP server profile by ID and update its configuration.

    This function demonstrates how to:
    1. Retrieve an existing HTTP server profile using its ID
    2. Modify profile properties (server configuration, format settings)
    3. Submit the updated profile back to the SCM API

    Args:
        http_profiles: The HTTP server profile manager instance
        profile_id: The UUID of the HTTP server profile to update

    Returns:
        HTTPServerProfileResponseModel: The updated HTTP server profile object, or None if update failed
    """
    log_section("UPDATING HTTP SERVER PROFILES")
    log_operation_start(f"Fetching and updating HTTP server profile with ID: {profile_id}")

    try:
        # Fetch the profile
        http_profile = http_profiles.get(profile_id)
        log_success(f"Found HTTP server profile: {http_profile.name}")
        log_info(f"  - Current server count: {len(http_profile.server)}")

        for idx, server in enumerate(http_profile.server):
            log_info(
                f"  - Server {idx + 1}: {server.name} ({server.address}) - {server.protocol}:{server.port}"
            )

        # Create a modified server list - change port and add method if missing
        updated_servers = []
        for server in http_profile.server:
            # Create a copy of the server data (can't modify the original directly)
            server_data = {
                "name": server.name,
                "address": server.address,
                "protocol": server.protocol,
                "port": (8080 if server.port == 80 else server.port),  # Change HTTP port to 8080
            }

            # Add HTTP method if not present
            if not server.http_method:
                server_data["http_method"] = "POST"

            # Add TLS version for HTTPS servers if not present
            if server.protocol == "HTTPS" and not server.tls_version:
                server_data["tls_version"] = "1.2"

            updated_servers.append(server_data)

        # Add a new server to the list
        updated_servers.append(
            {
                "name": "additional-server",
                "address": "10.20.30.40",
                "protocol": "HTTP",
                "port": 8080,
                "http_method": "POST",
            }
        )

        # Create an update model with the modified server list
        update_data = {
            "id": http_profile.id,
            "name": http_profile.name,
            "description": f"Updated HTTP server profile - modified on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "server": updated_servers,
            "tag_registration": True,
        }

        # Add the appropriate container field (folder, snippet, or device)
        if http_profile.folder:
            update_data["folder"] = http_profile.folder
        elif http_profile.snippet:
            update_data["snippet"] = http_profile.snippet
        elif http_profile.device:
            update_data["device"] = http_profile.device

        # Create the update model
        update_model = HTTPServerProfileUpdateModel(**update_data)

        log_info("Updating HTTP server profile with:")
        log_info(f"  - New server count: {len(updated_servers)}")
        log_info(f"  - New description: {update_data['description']}")

        # Perform the update
        updated_profile = http_profiles.update(update_model)
        log_success(f"Updated HTTP server profile: {updated_profile.name}")
        log_info(f"  - Updated server count: {len(updated_profile.server)}")
        log_info(f"  - Updated description: {updated_profile.description}")

        for idx, server in enumerate(updated_profile.server):
            log_info(
                f"  - Server {idx + 1}: {server.name} ({server.address}) - {server.protocol}:{server.port}"
            )

        log_operation_complete("HTTP server profile update", f"Profile: {updated_profile.name}")
        return updated_profile

    except NotFoundError as e:
        log_error("HTTP server profile not found", e.message)
    except InvalidObjectError as e:
        log_error("Invalid HTTP server profile update", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error updating HTTP server profile", str(e))

    return None


def list_and_filter_http_server_profiles(http_profiles):
    """List and filter HTTP server profiles with various filtering options.

    This function demonstrates:
    1. Listing all HTTP server profiles in a specific folder
    2. Filtering by exact match on container
    3. Filtering by tag registration status
    4. Filtering by server protocol
    5. Excluding profiles from specific containers (folders/snippets/devices)

    Args:
        http_profiles: The HTTP server profile manager instance

    Returns:
        list: List of all HTTP server profiles found
    """
    log_section("LISTING AND FILTERING HTTP SERVER PROFILES")
    log_operation_start("Listing and filtering HTTP server profiles")

    try:
        # List all HTTP server profiles in the Texas folder
        all_profiles = http_profiles.list(folder="Texas")
        log_success(f"Found {len(all_profiles)} HTTP server profiles in the Texas folder")

        # Filter with exact_match=True to get profiles directly in the folder (not subfolder)
        direct_profiles = http_profiles.list(folder="Texas", exact_match=True)
        log_info(f"Found {len(direct_profiles)} HTTP server profiles directly in the Texas folder")

        # Filter by tag registration status
        tag_reg_profiles = http_profiles.list(folder="Texas", tag_registration=True)
        log_info(
            f"Found {len(tag_reg_profiles)} HTTP server profiles with tag registration enabled"
        )

        # Filter by server protocol - profiles with at least one HTTPS server
        https_profiles = http_profiles.list(folder="Texas", protocol=["HTTPS"])
        log_info(f"Found {len(https_profiles)} HTTP server profiles with at least one HTTPS server")

        # Filter out profiles from a specific subfolder
        filtered_profiles = http_profiles.list(folder="Texas", exclude_folders=["Austin"])
        log_info(f"Found {len(filtered_profiles)} HTTP server profiles excluding 'Austin'")

        # Print details of profiles
        log_info("\nDetails of HTTP server profiles:")
        for profile in all_profiles[:5]:  # Print details of up to 5 profiles
            log_info(f"  - Profile: {profile.name}")
            log_info(f"    ID: {profile.id}")
            log_info(f"    Servers: {len(profile.server)}")
            for idx, server in enumerate(profile.server):
                log_info(f"      Server {idx + 1}: {server.name} ({server.protocol}:{server.port})")
            if profile.description:
                log_info(f"    Description: {profile.description}")
            log_info("")

        return all_profiles

    except InvalidObjectError as e:
        log_error("Invalid request when listing HTTP server profiles", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error listing HTTP server profiles", str(e))

    return []


def fetch_http_server_profile_by_name(http_profiles, profile_name, folder="Texas"):
    """Fetch a specific HTTP server profile by name from a folder.

    This function demonstrates using the fetch method to retrieve an HTTP server profile
    by its name rather than its ID, which is useful when you know the name but
    not the ID of the profile.

    Args:
        http_profiles: The HTTP server profile manager instance
        profile_name: The name of the HTTP server profile to fetch
        folder: The folder containing the HTTP server profile (default: "Texas")

    Returns:
        HTTPServerProfileResponseModel: The fetched HTTP server profile, or None if fetch failed
    """
    log_section("FETCHING HTTP SERVER PROFILE BY NAME")
    log_operation_start(f"Fetching HTTP server profile '{profile_name}' from {folder}")

    try:
        # Fetch the profile by name
        profile = http_profiles.fetch(name=profile_name, folder=folder)
        log_success(f"Found HTTP server profile: {profile.name}")
        log_info(f"  - ID: {profile.id}")
        log_info(f"  - Servers: {len(profile.server)}")
        for idx, server in enumerate(profile.server):
            log_info(
                f"    Server {idx + 1}: {server.name} ({server.address}) - {server.protocol}:{server.port}"
            )
        if profile.description:
            log_info(f"  - Description: {profile.description}")

        log_operation_complete("HTTP server profile fetch by name", f"Profile: {profile.name}")
        return profile

    except NotFoundError as e:
        log_error("HTTP server profile not found", e.message)
    except InvalidObjectError as e:
        log_error("Invalid fetch request", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error fetching HTTP server profile", str(e))

    return None


def delete_http_server_profile(http_profiles, profile_id):
    """Delete an HTTP server profile.

    This function demonstrates deleting an HTTP server profile using its ID. It handles
    common error cases such as the profile not being found or already deleted.

    Args:
        http_profiles: The HTTP server profile manager instance
        profile_id: The UUID of the HTTP server profile to delete

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    log_section("DELETING HTTP SERVER PROFILE")
    log_operation_start(f"Deleting HTTP server profile with ID: {profile_id}")

    try:
        # Delete the profile
        http_profiles.delete(profile_id)
        log_success(f"Successfully deleted HTTP server profile with ID: {profile_id}")
        log_operation_complete("HTTP server profile deletion")
        return True

    except NotFoundError as e:
        log_error("HTTP server profile not found", e.message)
    except InvalidObjectError as e:
        log_error("Invalid delete request", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error deleting HTTP server profile", str(e))

    return False


def generate_http_server_profile_report(http_profiles, profile_ids, execution_time):
    """Generate a comprehensive CSV report of all HTTP server profiles created by the script.

    This function fetches detailed information about each HTTP server profile and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    The report includes:
    - Profile identifiers (ID, name)
    - Server configurations (protocol, port, TLS version)
    - Tag registration status
    - Format settings
    - Containers (folder, snippet, device)
    - Summary statistics (total profiles, success/failure counts, execution time)

    Args:
        http_profiles: The HTTP server profile manager instance
        profile_ids: List of HTTP server profile IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"http_server_profiles_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Profile ID",
        "Name",
        "Description",
        "Container Type",
        "Container Name",
        "Server Count",
        "Server Names",
        "Server Protocols",
        "Server Ports",
        "TLS Versions",
        "Tag Registration",
        "Format Types",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each profile
    profile_data = []
    for idx, profile_id in enumerate(profile_ids):
        # Show progress for large profile sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(profile_ids) - 1:
            log_info(f"Processing profile {idx + 1} of {len(profile_ids)}")

        try:
            # Get the profile details
            profile = http_profiles.get(profile_id)

            # Determine container type and name
            container_type = "None"
            container_name = "None"
            if profile.folder:
                container_type = "Folder"
                container_name = profile.folder
            elif profile.snippet:
                container_type = "Snippet"
                container_name = profile.snippet
            elif profile.device:
                container_type = "Device"
                container_name = profile.device

            # Collect server information
            server_count = len(profile.server)
            server_names = ", ".join([server.name for server in profile.server])
            server_protocols = ", ".join([server.protocol for server in profile.server])
            server_ports = ", ".join([str(server.port) for server in profile.server])

            # Collect TLS versions (if any)
            tls_versions = []
            for server in profile.server:
                if hasattr(server, "tls_version") and server.tls_version:
                    tls_versions.append(f"{server.name}: {server.tls_version}")
            tls_versions_str = ", ".join(tls_versions) if tls_versions else "None"

            # Collect format types
            format_types = []
            if profile.format:
                format_types = list(profile.format.keys())
            format_types_str = ", ".join(format_types) if format_types else "None"

            # Add profile data
            profile_data.append(
                [
                    profile.id,
                    profile.name,
                    profile.description if profile.description else "None",
                    container_type,
                    container_name,
                    server_count,
                    server_names,
                    server_protocols,
                    server_ports,
                    tls_versions_str,
                    "Enabled" if profile.tag_registration else "Disabled",
                    format_types_str,
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
                    f"Failed to retrieve profile details: {str(e)}",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
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
            writer.writerows(profile_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Profiles Processed", len(profile_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(
                [
                    "Report Generated On",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

        log_success(f"Report file created: {report_file}")
        return report_file

    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"http_profiles_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(profile_data)

            log_success(f"Fallback report file created: {fallback_file}")
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def cleanup_http_server_profiles(http_profiles, profile_ids):
    """Delete the HTTP server profiles created in this example.

    Args:
        http_profiles: The HTTP server profile manager instance
        profile_ids: List of UUIDs of HTTP server profiles to delete
    """
    log_section("CLEANUP")
    log_operation_start(f"Cleaning up {len(profile_ids)} HTTP server profiles")

    for profile_id in profile_ids:
        try:
            http_profiles.delete(profile_id)
            log_success(f"Deleted HTTP server profile with ID: {profile_id}")
        except NotFoundError:
            log_warning(
                f"HTTP server profile with ID {profile_id} not found - may have been already deleted"
            )
        except Exception as e:
            log_error(f"Error deleting HTTP server profile with ID {profile_id}", str(e))


def parse_arguments():
    """Parse command-line arguments for the HTTP server profile example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created profiles
    - Which HTTP server profile operations to demonstrate
    - Whether to generate a CSV report
    - Folder name to use for profile creation

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager HTTP Server Profiles Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created HTTP server profiles (don't delete them)",
    )

    # Report generation
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Operations to demonstrate
    op_group = parser.add_argument_group("Operations")
    op_group.add_argument("--create", action="store_true", help="Demonstrate creation operations")
    op_group.add_argument("--update", action="store_true", help="Demonstrate update operations")
    op_group.add_argument("--list", action="store_true", help="Demonstrate listing operations")
    op_group.add_argument("--delete", action="store_true", help="Demonstrate deletion operations")
    op_group.add_argument(
        "--all",
        action="store_true",
        help="Demonstrate all operations (default behavior)",
    )

    # Container name
    parser.add_argument(
        "--folder",
        type=str,
        default="Texas",
        help="Folder name in SCM to use for operations",
    )

    return parser.parse_args()


def main():
    """Execute the comprehensive set of HTTP server profile examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of HTTP server profiles (basic, HTTPS, multi-server)
    4. Update an existing HTTP server profile to demonstrate modification capabilities
    5. List and filter HTTP server profiles to show search functionality
    6. Generate a CSV report (if enabled)
    7. Clean up created profiles (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Track execution time for reporting
    start_time = __import__("time").time()
    profile_count = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine whether to generate a report
    # Command-line argument takes precedence over environment variable
    skip_report = args.no_report or os.environ.get("NO_REPORT", "").lower() == "true"

    # Determine which operations to demonstrate
    # If no specific operations are specified, demonstrate all (default behavior)
    demo_all = args.all or not (args.create or args.update or args.list or args.delete)

    # Get folder name for operations
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize HTTP server profiles object
        log_section("HTTP SERVER PROFILE CONFIGURATION")
        log_operation_start("Initializing HTTP server profile manager")
        http_profiles = HTTPServerProfile(client)
        log_operation_complete("HTTP server profile manager initialization")

        # Track created profiles for cleanup and reporting
        created_profiles = []

        # Demonstrate creation operations
        if demo_all or args.create:
            log_section("HTTP SERVER PROFILE CREATION")
            log_info("Demonstrating HTTP server profile creation with various configurations")
            log_info(f"Using folder: {folder_name}")

            # Create a basic HTTP server profile
            basic_profile = create_basic_http_server_profile(http_profiles, folder_name)
            if basic_profile:
                created_profiles.append(basic_profile.id)
                profile_count += 1

            # Create an HTTPS server profile
            https_profile = create_https_server_profile(http_profiles, folder_name)
            if https_profile:
                created_profiles.append(https_profile.id)
                profile_count += 1

            # Create a multi-server profile
            multi_profile = create_multi_server_profile(http_profiles, folder_name)
            if multi_profile:
                created_profiles.append(multi_profile.id)
                profile_count += 1

            # Create an HTTP server profile in a snippet container
            snippet_profile = create_http_server_profile_with_snippet(http_profiles, folder_name)
            if snippet_profile:
                created_profiles.append(snippet_profile.id)
                profile_count += 1

            # Create an HTTP server profile in a device container
            device_profile = create_http_server_profile_with_device(http_profiles, folder_name)
            if device_profile:
                created_profiles.append(device_profile.id)
                profile_count += 1

            log_success(f"Created {len(created_profiles)} HTTP server profiles")

        # Demonstrate update operations
        if demo_all or args.update:
            if created_profiles:
                # Update the first created profile
                updated_profile = fetch_and_update_http_server_profile(
                    http_profiles, created_profiles[0]
                )
                if updated_profile:
                    log_success("Successfully updated HTTP server profile")
            else:
                log_warning("No profiles were created to update")

        # Demonstrate list and fetch operations
        if demo_all or args.list:
            # List and filter profiles
            all_profiles = list_and_filter_http_server_profiles(http_profiles)

            # Fetch a profile by name if we have created any
            if created_profiles and all_profiles:
                # Use the name of the first profile in the list
                fetch_profile_by_name = fetch_http_server_profile_by_name(
                    http_profiles,
                    all_profiles[0].name,
                    all_profiles[0].folder if all_profiles[0].folder else folder_name,
                )
                if fetch_profile_by_name:
                    log_success("Successfully fetched HTTP server profile by name")

        # Demonstrate delete operations
        if demo_all or args.delete:
            if created_profiles:
                # Delete the last created profile to demonstrate the delete operation
                delete_success = delete_http_server_profile(http_profiles, created_profiles[-1])
                if delete_success:
                    # Remove it from the list of profiles to clean up later
                    deleted_id = created_profiles.pop()
                    log_success(
                        f"Successfully demonstrated deletion of HTTP server profile {deleted_id}"
                    )
            else:
                log_warning("No profiles were created to delete")

        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_profiles and not skip_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating HTTP server profiles CSV report")

            # Calculate execution time so far
            current_time = __import__("time").time()
            execution_time_so_far = current_time - start_time

            # Generate the report
            report_file = generate_http_server_profile_report(
                http_profiles, created_profiles, execution_time_so_far
            )

            if report_file:
                log_success(f"Generated HTTP server profiles report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_profiles)} HTTP server profiles created"
                )
            else:
                log_error("Failed to generate HTTP server profiles report")
        elif skip_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No HTTP server profiles were created, skipping report generation")

        # Clean up the created profiles, unless skip_cleanup is true
        if created_profiles:
            if skip_cleanup:
                log_info(
                    f"SKIP_CLEANUP is set to true - preserving {len(created_profiles)} HTTP server profiles"
                )
                log_info(
                    "To clean up these profiles, run the script again with SKIP_CLEANUP unset or set to false"
                )
            else:
                log_operation_start(
                    f"Cleaning up {len(created_profiles)} created HTTP server profiles"
                )
                cleanup_http_server_profiles(http_profiles, created_profiles)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total HTTP server profiles created: {profile_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if profile_count > 0:
            log_info(f"Average time per profile: {execution_time / profile_count:.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some HTTP server profiles may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
