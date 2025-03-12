#!/usr/bin/env python3
"""
Comprehensive examples of working with Service Connection objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Service Connection configurations and operations commonly
used in enterprise networks, including:

1. Service Connection Types:
   - Basic service connections
   - Service connections with BGP configuration
   - Service connections with QoS settings
   - Service connections with different subnet configurations

2. Operational examples:
   - Creating service connection objects
   - Searching and filtering service connections
   - Updating service connection configurations
   - Listing all service connections with pagination support

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with service connection details
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

2. Make sure there are IPsec tunnels available in your environment or modify the example to use
   tunnel names that exist in your environment.

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
from scm.config.deployment import ServiceConnection
from scm.models.deployment import ServiceConnectionUpdateModel
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError,
    MissingQueryParameterError,
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
logger = logging.getLogger("service_connection_example")


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


def create_basic_service_connection(sc_manager, ipsec_tunnel=None):
    """
    Create a basic service connection without complex configurations.

    This function demonstrates creating a simple service connection with
    minimal configuration options.

    Args:
        sc_manager: The ServiceConnection manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)

    Returns:
        ServiceConnectionResponseModel: The created service connection, or None if creation failed
    """
    log_operation_start("Creating basic service connection")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        return None

    # Generate a unique connection name to avoid conflicts
    connection_name = f"basic-sc-{uuid.uuid4().hex[:6]}"
    log_info(f"Connection name: {connection_name}")

    # Create the connection configuration
    basic_connection_config = {
        "name": connection_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "us-east-1",
        "onboarding_type": "classic",
        "subnets": ["10.1.0.0/24", "192.168.1.0/24"],
        "source_nat": True,
    }

    log_info("Configuration details:")
    log_info(f"  - IPsec Tunnel: {basic_connection_config['ipsec_tunnel']}")
    log_info(f"  - Region: {basic_connection_config['region']}")
    log_info(f"  - Subnets: {', '.join(basic_connection_config['subnets'])}")
    log_info(f"  - Source NAT: {basic_connection_config['source_nat']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_connection = sc_manager.create(basic_connection_config)
        log_success(f"Created basic service connection: {new_connection.name}")
        log_info(f"  - Connection ID: {new_connection.id}")
        log_info(f"  - IPsec Tunnel: {new_connection.ipsec_tunnel}")
        log_operation_complete(
            "Basic service connection creation", f"Connection: {new_connection.name}"
        )
        return new_connection
    except NameNotUniqueError as e:
        log_error("Connection name conflict", e.message)
        log_info("Try using a different connection name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid connection data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating service connection", error_str)

    return None


def create_bgp_service_connection(sc_manager, ipsec_tunnel=None):
    """
    Create a service connection with BGP configuration.

    This function demonstrates creating a service connection with
    BGP peering configuration.

    Args:
        sc_manager: The ServiceConnection manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)

    Returns:
        ServiceConnectionResponseModel: The created service connection, or None if creation failed
    """
    log_operation_start("Creating service connection with BGP configuration")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        return None

    # Generate a unique connection name to avoid conflicts
    connection_name = f"bgp-sc-{uuid.uuid4().hex[:6]}"
    log_info(f"Connection name: {connection_name}")

    # Create the connection configuration with BGP details
    bgp_connection_config = {
        "name": connection_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "us-east-1",
        "onboarding_type": "classic",
        "subnets": ["10.2.0.0/24", "192.168.2.0/24"],
        "source_nat": True,
        "bgp_peer": {
            "local_ip_address": "192.168.2.1",
            "peer_ip_address": "192.168.2.2",
        },
        "protocol": {
            "bgp": {
                "enable": True,
                "peer_as": "65000",
                "originate_default_route": True,
                "fast_failover": True,
            }
        },
    }

    log_info("Configuration details:")
    log_info(f"  - IPsec Tunnel: {bgp_connection_config['ipsec_tunnel']}")
    log_info(f"  - Region: {bgp_connection_config['region']}")
    log_info(f"  - Subnets: {', '.join(bgp_connection_config['subnets'])}")
    log_info(f"  - Local BGP IP: {bgp_connection_config['bgp_peer']['local_ip_address']}")
    log_info(f"  - Peer BGP IP: {bgp_connection_config['bgp_peer']['peer_ip_address']}")
    log_info(f"  - Peer AS: {bgp_connection_config['protocol']['bgp']['peer_as']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_connection = sc_manager.create(bgp_connection_config)
        log_success(f"Created BGP service connection: {new_connection.name}")
        log_info(f"  - Connection ID: {new_connection.id}")
        log_info(f"  - IPsec Tunnel: {new_connection.ipsec_tunnel}")
        log_operation_complete(
            "BGP service connection creation", f"Connection: {new_connection.name}"
        )
        return new_connection
    except NameNotUniqueError as e:
        log_error("Connection name conflict", e.message)
        log_info("Try using a different connection name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid connection data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating service connection", error_str)

    return None


def create_qos_service_connection(sc_manager, ipsec_tunnel=None):
    """
    Create a service connection with QoS configuration.

    This function demonstrates creating a service connection with
    Quality of Service settings.

    Args:
        sc_manager: The ServiceConnection manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)

    Returns:
        ServiceConnectionResponseModel: The created service connection, or None if creation failed
    """
    log_operation_start("Creating service connection with QoS configuration")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        return None

    # Generate a unique connection name to avoid conflicts
    connection_name = f"qos-sc-{uuid.uuid4().hex[:6]}"
    log_info(f"Connection name: {connection_name}")

    # Create the connection configuration with QoS settings
    qos_connection_config = {
        "name": connection_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "us-west-1",
        "onboarding_type": "classic",
        "subnets": ["10.3.0.0/24", "192.168.3.0/24"],
        "source_nat": True,
        "qos": {"enable": True, "qos_profile": "default-qos-profile"},
    }

    log_info("Configuration details:")
    log_info(f"  - IPsec Tunnel: {qos_connection_config['ipsec_tunnel']}")
    log_info(f"  - Region: {qos_connection_config['region']}")
    log_info(f"  - Subnets: {', '.join(qos_connection_config['subnets'])}")
    log_info(f"  - QoS Enabled: {qos_connection_config['qos']['enable']}")
    log_info(f"  - QoS Profile: {qos_connection_config['qos']['qos_profile']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_connection = sc_manager.create(qos_connection_config)
        log_success(f"Created QoS service connection: {new_connection.name}")
        log_info(f"  - Connection ID: {new_connection.id}")
        log_info(f"  - IPsec Tunnel: {new_connection.ipsec_tunnel}")
        log_operation_complete(
            "QoS service connection creation", f"Connection: {new_connection.name}"
        )
        return new_connection
    except NameNotUniqueError as e:
        log_error("Connection name conflict", e.message)
        log_info("Try using a different connection name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid connection data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating service connection", error_str)

    return None


def create_advanced_service_connection(sc_manager, ipsec_tunnel=None, secondary_tunnel=None):
    """
    Create a service connection with advanced configuration options.

    This function demonstrates creating a service connection with
    multiple advanced settings enabled.

    Args:
        sc_manager: The ServiceConnection manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)
        secondary_tunnel: Name of existing secondary IPsec tunnel to use (optional)

    Returns:
        ServiceConnectionResponseModel: The created service connection, or None if creation failed
    """
    log_operation_start("Creating service connection with advanced configuration")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        return None

    # Generate a unique connection name to avoid conflicts
    connection_name = f"advanced-sc-{uuid.uuid4().hex[:6]}"
    log_info(f"Connection name: {connection_name}")

    # Create the connection configuration with advanced settings
    advanced_connection_config = {
        "name": connection_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "eu-west-1",
        "onboarding_type": "classic",
        "subnets": ["10.4.0.0/24", "172.16.0.0/24", "192.168.4.0/24"],
        "source_nat": True,
        "backup_SC": f"backup-sc-{uuid.uuid4().hex[:6]}",
        "bgp_peer": {
            "local_ip_address": "192.168.4.1",
            "peer_ip_address": "192.168.4.2",
            "secret": "bgp-auth-key",
        },
        "protocol": {
            "bgp": {
                "enable": True,
                "peer_as": "65001",
                "originate_default_route": True,
                "fast_failover": True,
                "summarize_mobile_user_routes": True,
                "do_not_export_routes": False,
            }
        },
        "no_export_community": "Enabled-Both",
        "qos": {"enable": True, "qos_profile": "high-priority-profile"},
    }

    # Add secondary tunnel if provided
    if secondary_tunnel:
        advanced_connection_config["secondary_ipsec_tunnel"] = secondary_tunnel
        log_info(f"Using provided secondary IPsec tunnel: {secondary_tunnel}")
    else:
        log_info(
            "No secondary IPsec tunnel provided, advanced connection will use only primary tunnel"
        )

    log_info("Configuration details:")
    log_info(f"  - Primary IPsec Tunnel: {advanced_connection_config['ipsec_tunnel']}")
    if "secondary_ipsec_tunnel" in advanced_connection_config:
        log_info(
            f"  - Secondary IPsec Tunnel: {advanced_connection_config['secondary_ipsec_tunnel']}"
        )
    log_info(f"  - Backup Service Connection: {advanced_connection_config['backup_SC']}")
    log_info(f"  - Region: {advanced_connection_config['region']}")
    log_info(f"  - Subnets: {', '.join(advanced_connection_config['subnets'])}")
    log_info(
        f"  - BGP Configuration: Enabled with AS {advanced_connection_config['protocol']['bgp']['peer_as']}"
    )
    log_info(f"  - No Export Community: {advanced_connection_config['no_export_community']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_connection = sc_manager.create(advanced_connection_config)
        log_success(f"Created advanced service connection: {new_connection.name}")
        log_info(f"  - Connection ID: {new_connection.id}")
        log_info(f"  - IPsec Tunnel: {new_connection.ipsec_tunnel}")
        log_operation_complete(
            "Advanced service connection creation", f"Connection: {new_connection.name}"
        )
        return new_connection
    except NameNotUniqueError as e:
        log_error("Connection name conflict", e.message)
        log_info("Try using a different connection name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid connection data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating service connection", error_str)

    return None


def fetch_and_update_service_connection(sc_manager, connection_id):
    """
    Fetch a service connection by ID and update its configuration.

    This function demonstrates how to:
    1. Retrieve an existing service connection using its ID
    2. Modify connection properties (subnets, BGP configuration)
    3. Submit the updated connection back to the SCM API

    Args:
        sc_manager: The ServiceConnection manager instance
        connection_id: The UUID of the service connection to update

    Returns:
        ServiceConnectionResponseModel: The updated connection, or None if update failed
    """
    log_operation_start(f"Fetching and updating service connection with ID: {connection_id}")

    try:
        # Fetch the service connection
        connection = sc_manager.get(connection_id)
        log_success(f"Found service connection: {connection.name}")
        log_info(f"  - Current region: {connection.region}")
        log_info(f"  - Current subnets: {connection.subnets}")

        # Create an update model from the retrieved connection
        update_model = ServiceConnectionUpdateModel(**connection.model_dump())

        # Make changes to the connection
        # Add a new subnet if there are existing subnets
        if update_model.subnets:
            log_info("Adding new subnet to connection")
            original_subnets = update_model.subnets.copy()
            new_subnet = "172.16.1.0/24"
            if new_subnet not in original_subnets:
                update_model.subnets.append(new_subnet)
            log_info(f"  - Updated subnets: {update_model.subnets}")

        # Update BGP configuration if it exists
        if update_model.protocol and update_model.protocol.bgp:
            log_info("Updating BGP configuration")
            # Toggle fast failover setting
            original_fast_failover = update_model.protocol.bgp.fast_failover
            update_model.protocol.bgp.fast_failover = not original_fast_failover
            log_info(
                f"  - Fast failover changed from {original_fast_failover} to {update_model.protocol.bgp.fast_failover}"
            )

        # Perform the update
        log_info("Sending update request to Strata Cloud Manager API...")
        updated_connection = sc_manager.update(update_model)
        log_success(f"Updated service connection: {updated_connection.name}")

        # Verify changes
        if updated_connection.subnets and "172.16.1.0/24" in updated_connection.subnets:
            log_info("  ✓ Subnet update verified")

        if updated_connection.protocol and updated_connection.protocol.bgp:
            log_info(
                f"  ✓ BGP fast_failover update verified: {updated_connection.protocol.bgp.fast_failover}"
            )

        log_operation_complete(
            "Service connection update", f"Connection: {updated_connection.name}"
        )
        return updated_connection

    except NotFoundError as e:
        log_error("Service connection not found", e.message)
    except InvalidObjectError as e:
        log_error("Invalid service connection update", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error updating service connection", str(e))

    return None


def list_and_filter_service_connections(sc_manager):
    """
    List and filter service connections.

    This function demonstrates how to:
    1. List all service connections
    2. Filter service connections by region
    3. Display detailed information about each connection

    Args:
        sc_manager: The ServiceConnection manager instance

    Returns:
        list: All retrieved service connections
    """
    log_section("LISTING AND FILTERING SERVICE CONNECTIONS")
    log_operation_start("Retrieving all service connections")

    try:
        # List all service connections
        all_connections = sc_manager.list()
        log_success(f"Found {len(all_connections)} service connections")

        # Group connections by region for reporting
        connections_by_region = {}
        for conn in all_connections:
            region = conn.region
            if region not in connections_by_region:
                connections_by_region[region] = []
            connections_by_region[region].append(conn)

        # Report connections by region
        log_info("\nService connections by region:")
        for region, connections in connections_by_region.items():
            log_info(f"  - Region: {region} - {len(connections)} connections")

        # Filter connections by name (if we have any connections)
        if all_connections:
            name_pattern = "basic"
            log_operation_start(
                f"Filtering service connections by name containing '{name_pattern}'"
            )
            basic_connections = [
                conn for conn in all_connections if name_pattern in conn.name.lower()
            ]
            log_success(
                f"Found {len(basic_connections)} service connections with '{name_pattern}' in the name"
            )

            # Filter connections by region
            if "us-east-1" in connections_by_region:
                log_operation_start("Retrieving service connections in us-east-1 region")
                east_connections = connections_by_region["us-east-1"]
                log_success(
                    f"Found {len(east_connections)} service connections in us-east-1 region"
                )

        # Print details of up to 5 connections
        log_info("\nDetails of service connections:")
        display_limit = min(5, len(all_connections))
        for i, conn in enumerate(all_connections[:display_limit]):
            log_info(f"  - Connection {i + 1}: {conn.name}")
            log_info(f"    ID: {conn.id}")
            log_info(f"    Region: {conn.region}")
            log_info(f"    IPsec Tunnel: {conn.ipsec_tunnel}")

            # Show subnets if available
            if conn.subnets:
                log_info(f"    Subnets: {', '.join(conn.subnets)}")

            # Show BGP configuration if available
            if conn.protocol and conn.protocol.bgp and conn.protocol.bgp.enable:
                log_info(f"    BGP: Enabled with peer AS {conn.protocol.bgp.peer_as}")
            else:
                log_info("    BGP: Not configured")

            # Show QoS configuration if available
            if conn.qos and conn.qos.enable:
                log_info(f"    QoS: Enabled with profile {conn.qos.qos_profile}")
            else:
                log_info("    QoS: Not configured")

            log_info("")

        log_operation_complete("Service connection listing and filtering")
        return all_connections

    except InvalidObjectError as e:
        log_error("Error listing service connections", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error listing service connections", str(e))

    return []


def fetch_service_connection_by_name(sc_manager, connection_name):
    """
    Fetch a service connection by name.

    This function demonstrates how to:
    1. Retrieve a service connection using its name instead of ID
    2. Handle not found scenarios

    Args:
        sc_manager: The ServiceConnection manager instance
        connection_name: The name of the service connection to fetch

    Returns:
        ServiceConnectionResponseModel: The fetched connection, or None if not found
    """
    log_operation_start(f"Fetching service connection by name: {connection_name}")

    try:
        # Fetch the service connection by name
        connection = sc_manager.fetch(name=connection_name)
        log_success(f"Found service connection: {connection.name}")
        log_info(f"  - Connection ID: {connection.id}")
        log_info(f"  - Region: {connection.region}")
        log_info(f"  - IPsec Tunnel: {connection.ipsec_tunnel}")

        log_operation_complete("Service connection fetch by name", f"Connection: {connection.name}")
        return connection

    except MissingQueryParameterError as e:
        log_error("Missing query parameter", e.message)
    except InvalidObjectError as e:
        log_error("Service connection not found", e.message)
    except Exception as e:
        log_error("Unexpected error fetching service connection", str(e))

    return None


def cleanup_service_connections(sc_manager, connection_ids):
    """
    Delete the service connections created in this example.

    This function will try to delete all the created service connections.

    Args:
        sc_manager: The ServiceConnection manager instance
        connection_ids: List of service connection IDs to delete
    """
    log_section("CLEANUP")
    log_operation_start(f"Cleaning up {len(connection_ids)} service connections")

    # Keep track of successful deletions
    deleted_ids = set()

    # Try to delete each service connection
    for connection_id in connection_ids:
        try:
            sc_manager.delete(connection_id)
            log_success(f"Deleted service connection with ID: {connection_id}")
            deleted_ids.add(connection_id)
        except NotFoundError as e:
            log_error("Service connection not found", e.message)
            deleted_ids.add(connection_id)  # Consider it deleted if not found
        except ReferenceNotZeroError as e:
            log_error("Service connection still in use", e.message)
            log_info("This usually means the connection is referenced by another object")
        except Exception as e:
            log_error("Error deleting service connection", str(e))

    # Report results
    if len(deleted_ids) == len(connection_ids):
        log_success(f"Successfully deleted all {len(deleted_ids)} service connections")
    else:
        log_warning(f"Deleted {len(deleted_ids)} out of {len(connection_ids)} service connections")
        log_info("Some connections could not be deleted due to dependencies")


def generate_service_connection_report(sc_manager, connection_ids, execution_time):
    """
    Generate a comprehensive CSV report of all service connections created by the script.

    This function fetches detailed information about each service connection and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    Args:
        sc_manager: The ServiceConnection manager instance
        connection_ids: List of service connection IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"service_connections_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Connection ID",
        "Name",
        "Region",
        "IPsec Tunnel",
        "Secondary Tunnel",
        "Subnets",
        "BGP Enabled",
        "Peer AS",
        "QoS Enabled",
        "Source NAT",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each service connection
    connection_data = []
    for idx, connection_id in enumerate(connection_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(connection_ids) - 1:
            log_info(f"Processing connection {idx + 1} of {len(connection_ids)}")

        try:
            # Get the connection details
            connection = sc_manager.get(connection_id)

            # Extract BGP information
            bgp_enabled = "No"
            peer_as = "N/A"
            if connection.protocol and connection.protocol.bgp and connection.protocol.bgp.enable:
                bgp_enabled = "Yes"
                peer_as = (
                    connection.protocol.bgp.peer_as
                    if connection.protocol.bgp.peer_as
                    else "Default"
                )

            # Extract QoS information
            qos_enabled = "No"
            if connection.qos and connection.qos.enable:
                qos_enabled = "Yes"

            # Add connection data
            connection_data.append(
                [
                    connection.id,
                    connection.name,
                    connection.region,
                    connection.ipsec_tunnel,
                    connection.secondary_ipsec_tunnel
                    if connection.secondary_ipsec_tunnel
                    else "None",
                    ", ".join(connection.subnets) if connection.subnets else "None",
                    bgp_enabled,
                    peer_as,
                    qos_enabled,
                    "Yes" if connection.source_nat else "No",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for connection ID {connection_id}", str(e))
            # Add minimal info for connections that couldn't be retrieved
            connection_data.append(
                [
                    connection_id,
                    "ERROR",
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
            writer.writerows(connection_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Connections Processed", len(connection_ids)])
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
            fallback_file = f"service_connections_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(connection_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the service connection example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which service connection types to create
    - Whether to generate a CSV report
    - IPsec tunnel configuration

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Service Connection Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created service connections (don't delete them)",
    )

    # Connection types to create
    conn_type = parser.add_argument_group("Connection Type Selection")
    conn_type.add_argument(
        "--basic", action="store_true", help="Create basic service connection examples"
    )
    conn_type.add_argument(
        "--bgp", action="store_true", help="Create BGP service connection examples"
    )
    conn_type.add_argument(
        "--qos", action="store_true", help="Create QoS service connection examples"
    )
    conn_type.add_argument(
        "--advanced", action="store_true", help="Create advanced service connection examples"
    )
    conn_type.add_argument(
        "--all", action="store_true", help="Create all service connection types (default behavior)"
    )

    # IPsec Tunnel Configuration - REQUIRED for successful creation
    tunnel_config = parser.add_argument_group("IPsec Tunnel Configuration")
    tunnel_config.add_argument(
        "--ipsec-tunnel",
        type=str,
        help="Name of existing IPsec tunnel to use (required for all connection types)",
    )
    tunnel_config.add_argument(
        "--secondary-tunnel",
        type=str,
        help="Name of existing secondary IPsec tunnel to use for advanced connections",
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Max limit for list operations
    parser.add_argument(
        "--max-limit",
        type=int,
        default=200,
        help="Maximum number of objects to return in a single API request (1-1000)",
    )

    return parser.parse_args()


def main():
    """
    Execute the comprehensive set of service connection examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of service connections (basic, BGP, QoS, advanced)
    4. Update an existing service connection to demonstrate modification capabilities
    5. List and filter service connections to show search functionality
    6. Fetch a specific service connection by name
    7. Generate a detailed CSV report of all created service connections
    8. Clean up created objects (unless skip_cleanup is enabled)
    9. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created objects (don't delete them)
        --basic: Create only basic service connection examples
        --bgp: Create only BGP service connection examples
        --qos: Create only QoS service connection examples
        --advanced: Create only advanced service connection examples
        --all: Create all service connection types (default behavior)
        --ipsec-tunnel: Name of existing IPsec tunnel to use (REQUIRED for all connections)
        --secondary-tunnel: Name of existing secondary IPsec tunnel (optional, for advanced connections)
        --no-report: Skip CSV report generation
        --max-limit: Maximum number of objects to return in a single API request (1-1000)

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
    connection_count = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine which connection types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.basic or args.bgp or args.qos or args.advanced)

    # Keep track of created connections for cleanup
    created_connections = []
    created_connection_ids = []

    try:
        # Initialize client
        client = initialize_client()

        # Initialize ServiceConnection object
        log_section("SERVICE CONNECTION CONFIGURATION")
        log_operation_start("Initializing ServiceConnection manager")
        service_connections = ServiceConnection(client, max_limit=args.max_limit)
        log_operation_complete(
            "ServiceConnection manager initialization",
            f"Max limit: {service_connections.max_limit}",
        )

        # Check if we have required IPsec tunnel parameter
        if not args.ipsec_tunnel and (
            create_all or args.basic or args.bgp or args.qos or args.advanced
        ):
            log_error("Missing required IPsec tunnel parameter")
            log_info("An existing IPsec tunnel name is required to create service connections")
            log_info("Example: python service_connections.py --ipsec-tunnel your-tunnel-name")
            log_info("Run with --help for more information")
            return

        # Create basic service connection
        if create_all or args.basic:
            log_section("BASIC SERVICE CONNECTION")
            log_info("Creating basic service connection with minimal configuration")

            basic_connection = create_basic_service_connection(
                service_connections, ipsec_tunnel=args.ipsec_tunnel
            )
            if basic_connection:
                created_connections.append(basic_connection)
                created_connection_ids.append(basic_connection.id)
                connection_count += 1

        # Create BGP service connection
        if create_all or args.bgp:
            log_section("BGP SERVICE CONNECTION")
            log_info("Creating service connection with BGP configuration")

            bgp_connection = create_bgp_service_connection(
                service_connections, ipsec_tunnel=args.ipsec_tunnel
            )
            if bgp_connection:
                created_connections.append(bgp_connection)
                created_connection_ids.append(bgp_connection.id)
                connection_count += 1

        # Create QoS service connection
        if create_all or args.qos:
            log_section("QOS SERVICE CONNECTION")
            log_info("Creating service connection with QoS configuration")

            qos_connection = create_qos_service_connection(
                service_connections, ipsec_tunnel=args.ipsec_tunnel
            )
            if qos_connection:
                created_connections.append(qos_connection)
                created_connection_ids.append(qos_connection.id)
                connection_count += 1

        # Create advanced service connection
        if create_all or args.advanced:
            log_section("ADVANCED SERVICE CONNECTION")
            log_info("Creating service connection with advanced configuration")

            advanced_connection = create_advanced_service_connection(
                service_connections,
                ipsec_tunnel=args.ipsec_tunnel,
                secondary_tunnel=args.secondary_tunnel,
            )
            if advanced_connection:
                created_connections.append(advanced_connection)
                created_connection_ids.append(advanced_connection.id)
                connection_count += 1

        # Update one of the connections if we created any
        if created_connections:
            log_section("UPDATING SERVICE CONNECTION")
            log_info("Demonstrating how to update an existing service connection")

            fetch_and_update_service_connection(service_connections, created_connections[0].id)

        # List and filter service connections
        list_and_filter_service_connections(service_connections)

        # Fetch a specific connection by name
        if created_connections:
            log_section("FETCHING SERVICE CONNECTION BY NAME")
            log_info("Demonstrating how to fetch a service connection by name")

            # Use the first created connection's name
            fetch_service_connection_by_name(service_connections, created_connections[0].name)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are connections to report and report generation is not disabled
        if created_connection_ids and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating service connections CSV report")

            report_file = generate_service_connection_report(
                service_connections, created_connection_ids, execution_time_so_far
            )

            if report_file:
                log_success(f"Generated service connections report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_connection_ids)} service connections created"
                )
            else:
                log_error("Failed to generate service connections report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No service connections were created, skipping report generation")

        # Clean up the created connections, unless skip_cleanup is true
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_connection_ids)} service connections"
            )
            log_info(
                "To clean up these connections, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            cleanup_service_connections(service_connections, created_connection_ids)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total service connections created: {connection_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if connection_count > 0:
            log_info(
                f"Average time per connection: {execution_time / connection_count:.2f} seconds"
            )

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some service connections may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
