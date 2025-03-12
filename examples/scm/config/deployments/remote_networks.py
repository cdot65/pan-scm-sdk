#!/usr/bin/env python3
"""
Comprehensive examples of working with Remote Network objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Remote Network configurations and operations commonly
used in enterprise networks, including:

1. Remote Network Types:
   - Basic remote networks
   - Remote networks with BGP configuration
   - Remote networks with ECMP load balancing
   - Remote networks with different subnet configurations

2. Operational examples:
   - Creating remote network objects
   - Searching and filtering remote networks
   - Updating remote network configurations
   - Listing all remote networks with pagination support

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with remote network details
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
from scm.config.deployment import RemoteNetworks
from scm.models.deployment import RemoteNetworkUpdateModel, EcmpLoadBalancingEnum
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
logger = logging.getLogger("remote_network_example")


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


def create_basic_remote_network(rn_manager, ipsec_tunnel=None, folder=None):
    """
    Create a basic remote network without complex configurations.

    This function demonstrates creating a simple remote network with
    minimal configuration options.

    Args:
        rn_manager: The RemoteNetworks manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)
        folder: Folder name where the remote network will be created

    Returns:
        RemoteNetworkResponseModel: The created remote network, or None if creation failed
    """
    log_operation_start("Creating basic remote network")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        return None

    # Check if folder was provided
    if not folder:
        log_error("No folder name provided")
        log_info("Please provide a folder name with --folder parameter")
        log_info(
            "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
        )
        return None

    # Generate a unique network name to avoid conflicts
    network_name = f"basic-rn-{uuid.uuid4().hex[:6]}"
    log_info(f"Network name: {network_name}")

    # Create the network configuration
    basic_network_config = {
        "name": network_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "us-east-1",
        "license_type": "FWAAS-AGGREGATE",
        "spn_name": "service-provider-network",
        "subnets": ["10.1.0.0/24", "192.168.1.0/24"],
        "folder": folder,
    }

    log_info("Configuration details:")
    log_info(f"  - IPsec Tunnel: {basic_network_config['ipsec_tunnel']}")
    log_info(f"  - Region: {basic_network_config['region']}")
    log_info(f"  - License Type: {basic_network_config['license_type']}")
    log_info(f"  - SPN Name: {basic_network_config['spn_name']}")
    log_info(f"  - Subnets: {', '.join(basic_network_config['subnets'])}")
    log_info(f"  - Folder: {basic_network_config['folder']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_network = rn_manager.create(basic_network_config)
        log_success(f"Created basic remote network: {new_network.name}")
        log_info(f"  - Network ID: {new_network.id}")
        log_info(f"  - IPsec Tunnel: {new_network.ipsec_tunnel}")
        log_operation_complete("Basic remote network creation", f"Network: {new_network.name}")
        return new_network
    except NameNotUniqueError as e:
        log_error("Network name conflict", e.message)
        log_info("Try using a different network name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid network data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating remote network", error_str)

    return None


def create_bgp_remote_network(rn_manager, ipsec_tunnel=None, folder=None):
    """
    Create a remote network with BGP configuration.

    This function demonstrates creating a remote network with
    BGP peering configuration.

    Args:
        rn_manager: The RemoteNetworks manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)
        folder: Folder name where the remote network will be created

    Returns:
        RemoteNetworkResponseModel: The created remote network, or None if creation failed
    """
    log_operation_start("Creating remote network with BGP configuration")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        return None

    # Check if folder was provided
    if not folder:
        log_error("No folder name provided")
        log_info("Please provide a folder name with --folder parameter")
        log_info(
            "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
        )
        return None

    # Generate a unique network name to avoid conflicts
    network_name = f"bgp-rn-{uuid.uuid4().hex[:6]}"
    log_info(f"Network name: {network_name}")

    # Create the network configuration with BGP details
    bgp_network_config = {
        "name": network_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "us-east-1",
        "license_type": "FWAAS-AGGREGATE",
        "spn_name": "service-provider-network",
        "subnets": ["10.2.0.0/24", "192.168.2.0/24"],
        "folder": folder,
        "bgp_peer": {
            "local_ip_address": "192.168.2.1",
            "peer_ip_address": "192.168.2.2",
        },
        "protocol": {
            "bgp": {
                "enable": True,
                "peer_as": "65000",
                "originate_default_route": True,
                "summarize_mobile_user_routes": True,
            }
        },
    }

    log_info("Configuration details:")
    log_info(f"  - IPsec Tunnel: {bgp_network_config['ipsec_tunnel']}")
    log_info(f"  - Region: {bgp_network_config['region']}")
    log_info(f"  - License Type: {bgp_network_config['license_type']}")
    log_info(f"  - SPN Name: {bgp_network_config['spn_name']}")
    log_info(f"  - Subnets: {', '.join(bgp_network_config['subnets'])}")
    log_info(f"  - Local BGP IP: {bgp_network_config['bgp_peer']['local_ip_address']}")
    log_info(f"  - Peer BGP IP: {bgp_network_config['bgp_peer']['peer_ip_address']}")
    log_info(f"  - Peer AS: {bgp_network_config['protocol']['bgp']['peer_as']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_network = rn_manager.create(bgp_network_config)
        log_success(f"Created BGP remote network: {new_network.name}")
        log_info(f"  - Network ID: {new_network.id}")
        log_info(f"  - IPsec Tunnel: {new_network.ipsec_tunnel}")
        log_operation_complete("BGP remote network creation", f"Network: {new_network.name}")
        return new_network
    except NameNotUniqueError as e:
        log_error("Network name conflict", e.message)
        log_info("Try using a different network name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid network data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating remote network", error_str)

    return None


def create_ecmp_remote_network(rn_manager, ipsec_tunnels=None, folder=None):
    """
    Create a remote network with ECMP load balancing.

    This function demonstrates creating a remote network with
    ECMP (Equal-Cost Multi-Path) load balancing across multiple tunnels.

    Args:
        rn_manager: The RemoteNetworks manager instance
        ipsec_tunnels: List of existing IPsec tunnel names to use (at least 2 required)
        folder: Folder name where the remote network will be created

    Returns:
        RemoteNetworkResponseModel: The created remote network, or None if creation failed
    """
    log_operation_start("Creating remote network with ECMP configuration")

    # Check if valid IPsec tunnel names were provided
    if not ipsec_tunnels or len(ipsec_tunnels) < 2:
        log_error("At least 2 valid IPsec tunnel names are required for ECMP configuration")
        log_info("Please provide existing IPsec tunnel names with --ipsec-tunnels parameter")
        log_info(
            "Example: python remote_networks.py --ipsec-tunnels tunnel1 tunnel2 --folder your-folder"
        )
        return None

    # Check if folder was provided
    if not folder:
        log_error("No folder name provided")
        log_info("Please provide a folder name with --folder parameter")
        log_info(
            "Example: python remote_networks.py --ipsec-tunnels tunnel1 tunnel2 --folder your-folder"
        )
        return None

    # Generate a unique network name to avoid conflicts
    network_name = f"ecmp-rn-{uuid.uuid4().hex[:6]}"
    log_info(f"Network name: {network_name}")

    # Create ECMP tunnel configurations
    ecmp_tunnels = []
    for i, tunnel_name in enumerate(ipsec_tunnels[:4]):  # Limit to max 4 tunnels
        # Create a tunnel with BGP settings
        tunnel_config = {
            "name": f"ecmp-tunnel-{i + 1}",
            "ipsec_tunnel": tunnel_name,
            "local_ip_address": f"192.168.3.{i * 2 + 1}",
            "peer_ip_address": f"192.168.3.{i * 2 + 2}",
            "peer_as": "65001",
            "originate_default_route": True,
            "summarize_mobile_user_routes": True,
        }
        ecmp_tunnels.append(tunnel_config)

    # Create the network configuration with ECMP settings
    ecmp_network_config = {
        "name": network_name,
        "region": "us-west-1",
        "license_type": "FWAAS-AGGREGATE",
        "spn_name": "service-provider-network",
        "subnets": ["10.3.0.0/24", "192.168.3.0/24"],
        "folder": folder,
        "ecmp_load_balancing": "enable",
        "ecmp_tunnels": ecmp_tunnels,
    }

    log_info("Configuration details:")
    log_info(f"  - Region: {ecmp_network_config['region']}")
    log_info(f"  - License Type: {ecmp_network_config['license_type']}")
    log_info(f"  - SPN Name: {ecmp_network_config['spn_name']}")
    log_info(f"  - Subnets: {', '.join(ecmp_network_config['subnets'])}")
    log_info(f"  - ECMP Load Balancing: {ecmp_network_config['ecmp_load_balancing']}")
    log_info(f"  - ECMP Tunnels: {len(ecmp_tunnels)}")
    for i, tunnel in enumerate(ecmp_tunnels):
        log_info(
            f"    - Tunnel {i + 1}: {tunnel['name']} using IPsec tunnel {tunnel['ipsec_tunnel']}"
        )
        log_info(
            f"      Local IP: {tunnel['local_ip_address']}, Peer IP: {tunnel['peer_ip_address']}"
        )

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_network = rn_manager.create(ecmp_network_config)
        log_success(f"Created ECMP remote network: {new_network.name}")
        log_info(f"  - Network ID: {new_network.id}")
        log_info(f"  - ECMP Enabled: {new_network.ecmp_load_balancing}")
        log_operation_complete("ECMP remote network creation", f"Network: {new_network.name}")
        return new_network
    except NameNotUniqueError as e:
        log_error("Network name conflict", e.message)
        log_info("Try using a different network name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid network data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide existing IPsec tunnel names with --ipsec-tunnels parameter")
        else:
            log_error("Unexpected error creating remote network", error_str)

    return None


def create_advanced_remote_network(
    rn_manager, ipsec_tunnel=None, secondary_tunnel=None, folder=None
):
    """
    Create a remote network with advanced configuration options.

    This function demonstrates creating a remote network with
    multiple advanced settings enabled.

    Args:
        rn_manager: The RemoteNetworks manager instance
        ipsec_tunnel: Name of existing IPsec tunnel to use (required)
        secondary_tunnel: Name of existing secondary IPsec tunnel to use (optional)
        folder: Folder name where the remote network will be created

    Returns:
        RemoteNetworkResponseModel: The created remote network, or None if creation failed
    """
    log_operation_start("Creating remote network with advanced configuration")

    # Check if a valid IPsec tunnel name was provided
    if not ipsec_tunnel:
        log_error("No valid IPsec tunnel name provided")
        log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
        log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        return None

    # Check if folder was provided
    if not folder:
        log_error("No folder name provided")
        log_info("Please provide a folder name with --folder parameter")
        log_info(
            "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
        )
        return None

    # Generate a unique network name to avoid conflicts
    network_name = f"advanced-rn-{uuid.uuid4().hex[:6]}"
    log_info(f"Network name: {network_name}")

    # Create the network configuration with advanced settings
    advanced_network_config = {
        "name": network_name,
        "ipsec_tunnel": ipsec_tunnel,  # Use the provided tunnel name
        "region": "eu-west-1",
        "license_type": "FWAAS-AGGREGATE",
        "spn_name": "service-provider-network",
        "subnets": ["10.4.0.0/24", "172.16.0.0/24", "192.168.4.0/24"],
        "folder": folder,
        "description": "Advanced remote network with comprehensive configuration",
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
                "summarize_mobile_user_routes": True,
                "do_not_export_routes": False,
                "peering_type": "exchange-v4-over-v4",
            }
        },
    }

    # Add secondary tunnel if provided
    if secondary_tunnel:
        advanced_network_config["secondary_ipsec_tunnel"] = secondary_tunnel
        log_info(f"Using provided secondary IPsec tunnel: {secondary_tunnel}")
    else:
        log_info(
            "No secondary IPsec tunnel provided, advanced network will use only primary tunnel"
        )

    log_info("Configuration details:")
    log_info(f"  - Primary IPsec Tunnel: {advanced_network_config['ipsec_tunnel']}")
    if "secondary_ipsec_tunnel" in advanced_network_config:
        log_info(f"  - Secondary IPsec Tunnel: {advanced_network_config['secondary_ipsec_tunnel']}")
    log_info(f"  - Region: {advanced_network_config['region']}")
    log_info(f"  - License Type: {advanced_network_config['license_type']}")
    log_info(f"  - SPN Name: {advanced_network_config['spn_name']}")
    log_info(f"  - Subnets: {', '.join(advanced_network_config['subnets'])}")
    log_info(
        f"  - BGP Configuration: Enabled with AS {advanced_network_config['protocol']['bgp']['peer_as']}"
    )
    log_info(f"  - Peering Type: {advanced_network_config['protocol']['bgp']['peering_type']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_network = rn_manager.create(advanced_network_config)
        log_success(f"Created advanced remote network: {new_network.name}")
        log_info(f"  - Network ID: {new_network.id}")
        log_info(f"  - IPsec Tunnel: {new_network.ipsec_tunnel}")
        log_operation_complete("Advanced remote network creation", f"Network: {new_network.name}")
        return new_network
    except NameNotUniqueError as e:
        log_error("Network name conflict", e.message)
        log_info("Try using a different network name or check existing objects")
    except InvalidObjectError as e:
        log_error("Invalid network data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        error_str = str(e)
        if "is not a valid reference" in error_str and "ipsec-tunnel" in error_str:
            log_error("Invalid IPsec tunnel reference", "The specified IPsec tunnel does not exist")
            log_info("Please provide an existing IPsec tunnel name with --ipsec-tunnel parameter")
            log_info("Example: python remote_networks.py --ipsec-tunnel your-tunnel-name")
        else:
            log_error("Unexpected error creating remote network", error_str)

    return None


def fetch_and_update_remote_network(rn_manager, network_id):
    """
    Fetch a remote network by ID and update its configuration.

    This function demonstrates how to:
    1. Retrieve an existing remote network using its ID
    2. Modify network properties (subnets, BGP configuration)
    3. Submit the updated network back to the SCM API

    Args:
        rn_manager: The RemoteNetworks manager instance
        network_id: The UUID of the remote network to update

    Returns:
        RemoteNetworkResponseModel: The updated network, or None if update failed
    """
    log_operation_start(f"Fetching and updating remote network with ID: {network_id}")

    try:
        # Fetch the remote network
        network = rn_manager.get(network_id)
        log_success(f"Found remote network: {network.name}")
        log_info(f"  - Current region: {network.region}")
        log_info(f"  - Current subnets: {network.subnets}")

        # Create an update model from the retrieved network
        update_model = RemoteNetworkUpdateModel(**network.model_dump())

        # Make changes to the network
        # Add a new subnet if there are existing subnets
        if update_model.subnets:
            log_info("Adding new subnet to network")
            original_subnets = update_model.subnets.copy()
            new_subnet = "172.16.1.0/24"
            if new_subnet not in original_subnets:
                update_model.subnets.append(new_subnet)
            log_info(f"  - Updated subnets: {update_model.subnets}")

        # Update BGP configuration if it exists
        if update_model.protocol and update_model.protocol.bgp:
            log_info("Updating BGP configuration")
            # Toggle summarize_mobile_user_routes setting
            original_route_summarization = update_model.protocol.bgp.summarize_mobile_user_routes
            update_model.protocol.bgp.summarize_mobile_user_routes = (
                not original_route_summarization
            )
            log_info(
                f"  - Route summarization changed from {original_route_summarization} to {update_model.protocol.bgp.summarize_mobile_user_routes}"
            )

        # Perform the update
        log_info("Sending update request to Strata Cloud Manager API...")
        updated_network = rn_manager.update(update_model)
        log_success(f"Updated remote network: {updated_network.name}")

        # Verify changes
        if updated_network.subnets and "172.16.1.0/24" in updated_network.subnets:
            log_info("  ✓ Subnet update verified")

        if updated_network.protocol and updated_network.protocol.bgp:
            log_info(
                f"  ✓ BGP summarize_mobile_user_routes update verified: {updated_network.protocol.bgp.summarize_mobile_user_routes}"
            )

        log_operation_complete("Remote network update", f"Network: {updated_network.name}")
        return updated_network

    except NotFoundError as e:
        log_error("Remote network not found", e.message)
    except InvalidObjectError as e:
        log_error("Invalid remote network update", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error updating remote network", str(e))

    return None


def list_and_filter_remote_networks(rn_manager, folder):
    """
    List and filter remote networks.

    This function demonstrates how to:
    1. List all remote networks in a folder
    2. Filter remote networks by region
    3. Display detailed information about each network

    Args:
        rn_manager: The RemoteNetworks manager instance
        folder: Folder name to search for remote networks

    Returns:
        list: All retrieved remote networks
    """
    log_section("LISTING AND FILTERING REMOTE NETWORKS")
    log_operation_start(f"Retrieving all remote networks in folder '{folder}'")

    try:
        # List all remote networks in the specified folder
        all_networks = rn_manager.list(folder=folder)
        log_success(f"Found {len(all_networks)} remote networks")

        # Group networks by region for reporting
        networks_by_region = {}
        for network in all_networks:
            region = network.region
            if region not in networks_by_region:
                networks_by_region[region] = []
            networks_by_region[region].append(network)

        # Report networks by region
        log_info("\nRemote networks by region:")
        for region, networks in networks_by_region.items():
            log_info(f"  - Region: {region} - {len(networks)} networks")

        # Filter networks by name (if we have any networks)
        if all_networks:
            name_pattern = "basic"
            log_operation_start(f"Filtering remote networks by name containing '{name_pattern}'")
            basic_networks = [
                network for network in all_networks if name_pattern in network.name.lower()
            ]
            log_success(
                f"Found {len(basic_networks)} remote networks with '{name_pattern}' in the name"
            )

            # Filter networks by region
            if "us-east-1" in networks_by_region:
                log_operation_start("Retrieving remote networks in us-east-1 region")
                east_networks = networks_by_region["us-east-1"]
                log_success(f"Found {len(east_networks)} remote networks in us-east-1 region")

        # Print details of up to 5 networks
        log_info("\nDetails of remote networks:")
        display_limit = min(5, len(all_networks))
        for i, network in enumerate(all_networks[:display_limit]):
            log_info(f"  - Network {i + 1}: {network.name}")
            log_info(f"    ID: {network.id}")
            log_info(f"    Region: {network.region}")
            log_info(f"    License Type: {network.license_type}")
            log_info(f"    SPN Name: {network.spn_name}")

            # Show ECMP configuration if enabled
            if network.ecmp_load_balancing == EcmpLoadBalancingEnum.enable:
                log_info("    ECMP Load Balancing: Enabled")
                if network.ecmp_tunnels:
                    log_info(f"    ECMP Tunnels: {len(network.ecmp_tunnels)}")
                    for j, tunnel in enumerate(network.ecmp_tunnels):
                        log_info(f"      - Tunnel {j + 1}: {tunnel.name} ({tunnel.ipsec_tunnel})")
            else:
                log_info(f"    IPsec Tunnel: {network.ipsec_tunnel}")
                if network.secondary_ipsec_tunnel:
                    log_info(f"    Secondary IPsec Tunnel: {network.secondary_ipsec_tunnel}")

            # Show subnets if available
            if network.subnets:
                log_info(f"    Subnets: {', '.join(network.subnets)}")

            # Show BGP configuration if available
            if network.protocol and network.protocol.bgp and network.protocol.bgp.enable:
                log_info(f"    BGP: Enabled with peer AS {network.protocol.bgp.peer_as}")
            else:
                log_info("    BGP: Not configured")

            log_info("")

        log_operation_complete("Remote network listing and filtering")
        return all_networks

    except InvalidObjectError as e:
        log_error("Error listing remote networks", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
    except Exception as e:
        log_error("Unexpected error listing remote networks", str(e))

    return []


def fetch_remote_network_by_name(rn_manager, network_name, folder):
    """
    Fetch a remote network by name.

    This function demonstrates how to:
    1. Retrieve a remote network using its name instead of ID
    2. Handle not found scenarios

    Args:
        rn_manager: The RemoteNetworks manager instance
        network_name: The name of the remote network to fetch
        folder: Folder name where the remote network is located

    Returns:
        RemoteNetworkResponseModel: The fetched network, or None if not found
    """
    log_operation_start(f"Fetching remote network by name: {network_name}")

    try:
        # Fetch the remote network by name
        network = rn_manager.fetch(name=network_name, folder=folder)
        log_success(f"Found remote network: {network.name}")
        log_info(f"  - Network ID: {network.id}")
        log_info(f"  - Region: {network.region}")
        log_info(f"  - License Type: {network.license_type}")

        log_operation_complete("Remote network fetch by name", f"Network: {network.name}")
        return network

    except MissingQueryParameterError as e:
        log_error("Missing query parameter", e.message)
    except InvalidObjectError as e:
        log_error("Remote network not found", e.message)
    except Exception as e:
        log_error("Unexpected error fetching remote network", str(e))

    return None


def cleanup_remote_networks(rn_manager, network_ids):
    """
    Delete the remote networks created in this example.

    This function will try to delete all the created remote networks.

    Args:
        rn_manager: The RemoteNetworks manager instance
        network_ids: List of remote network IDs to delete
    """
    log_section("CLEANUP")
    log_operation_start(f"Cleaning up {len(network_ids)} remote networks")

    # Keep track of successful deletions
    deleted_ids = set()

    # Try to delete each remote network
    for network_id in network_ids:
        try:
            rn_manager.delete(network_id)
            log_success(f"Deleted remote network with ID: {network_id}")
            deleted_ids.add(network_id)
        except NotFoundError as e:
            log_error("Remote network not found", e.message)
            deleted_ids.add(network_id)  # Consider it deleted if not found
        except ReferenceNotZeroError as e:
            log_error("Remote network still in use", e.message)
            log_info("This usually means the network is referenced by another object")
        except Exception as e:
            log_error("Error deleting remote network", str(e))

    # Report results
    if len(deleted_ids) == len(network_ids):
        log_success(f"Successfully deleted all {len(deleted_ids)} remote networks")
    else:
        log_warning(f"Deleted {len(deleted_ids)} out of {len(network_ids)} remote networks")
        log_info("Some networks could not be deleted due to dependencies")


def generate_remote_network_report(rn_manager, network_ids, execution_time):
    """
    Generate a comprehensive CSV report of all remote networks created by the script.

    This function fetches detailed information about each remote network and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    Args:
        rn_manager: The RemoteNetworks manager instance
        network_ids: List of remote network IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"remote_networks_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Network ID",
        "Name",
        "Region",
        "License Type",
        "SPN Name",
        "IPsec Tunnel",
        "Secondary Tunnel",
        "Subnets",
        "BGP Enabled",
        "Peer AS",
        "ECMP Enabled",
        "ECMP Tunnels",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each remote network
    network_data = []
    for idx, network_id in enumerate(network_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(network_ids) - 1:
            log_info(f"Processing network {idx + 1} of {len(network_ids)}")

        try:
            # Get the network details
            network = rn_manager.get(network_id)

            # Extract BGP information
            bgp_enabled = "No"
            peer_as = "N/A"
            if network.protocol and network.protocol.bgp and network.protocol.bgp.enable:
                bgp_enabled = "Yes"
                peer_as = (
                    network.protocol.bgp.peer_as if network.protocol.bgp.peer_as else "Default"
                )

            # Extract ECMP information
            ecmp_enabled = "No"
            ecmp_tunnels = "N/A"
            if network.ecmp_load_balancing == EcmpLoadBalancingEnum.enable:
                ecmp_enabled = "Yes"
                if network.ecmp_tunnels:
                    ecmp_tunnels = ", ".join([tunnel.name for tunnel in network.ecmp_tunnels])

            # Add network data
            network_data.append(
                [
                    network.id,
                    network.name,
                    network.region,
                    network.license_type,
                    network.spn_name,
                    network.ipsec_tunnel if network.ipsec_tunnel else "N/A (ECMP)",
                    network.secondary_ipsec_tunnel if network.secondary_ipsec_tunnel else "None",
                    ", ".join(network.subnets) if network.subnets else "None",
                    bgp_enabled,
                    peer_as,
                    ecmp_enabled,
                    ecmp_tunnels,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for network ID {network_id}", str(e))
            # Add minimal info for networks that couldn't be retrieved
            network_data.append(
                [
                    network_id,
                    "ERROR",
                    "ERROR",
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
            writer.writerows(network_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Networks Processed", len(network_ids)])
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
            fallback_file = f"remote_networks_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(network_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the remote network example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which remote network types to create
    - Whether to generate a CSV report
    - IPsec tunnel configuration

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Remote Network Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created remote networks (don't delete them)",
    )

    # Connection types to create
    conn_type = parser.add_argument_group("Network Type Selection")
    conn_type.add_argument(
        "--basic", action="store_true", help="Create basic remote network examples"
    )
    conn_type.add_argument("--bgp", action="store_true", help="Create BGP remote network examples")
    conn_type.add_argument(
        "--ecmp", action="store_true", help="Create ECMP remote network examples"
    )
    conn_type.add_argument(
        "--advanced", action="store_true", help="Create advanced remote network examples"
    )
    conn_type.add_argument(
        "--all", action="store_true", help="Create all remote network types (default behavior)"
    )

    # IPsec Tunnel Configuration - REQUIRED for successful creation
    tunnel_config = parser.add_argument_group("IPsec Tunnel Configuration")
    tunnel_config.add_argument(
        "--ipsec-tunnel",
        type=str,
        help="Name of existing IPsec tunnel to use (required for non-ECMP networks)",
    )
    tunnel_config.add_argument(
        "--secondary-tunnel",
        type=str,
        help="Name of existing secondary IPsec tunnel to use for advanced networks",
    )
    tunnel_config.add_argument(
        "--ipsec-tunnels",
        nargs="+",
        help="List of existing IPsec tunnel names to use for ECMP networks (at least 2 required)",
    )

    # Folder Configuration - REQUIRED for all operations
    parser.add_argument(
        "--folder", type=str, help="Folder name where remote networks will be created (required)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Max limit for list operations
    parser.add_argument(
        "--max-limit",
        type=int,
        default=200,
        help="Maximum number of objects to return in a single API request (1-5000)",
    )

    return parser.parse_args()


def main():
    """
    Execute the comprehensive set of remote network examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of remote networks (basic, BGP, ECMP, advanced)
    4. Update an existing remote network to demonstrate modification capabilities
    5. List and filter remote networks to show search functionality
    6. Fetch a specific remote network by name
    7. Generate a detailed CSV report of all created remote networks
    8. Clean up created objects (unless skip_cleanup is enabled)
    9. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created objects (don't delete them)
        --basic: Create only basic remote network examples
        --bgp: Create only BGP remote network examples
        --ecmp: Create only ECMP remote network examples
        --advanced: Create only advanced remote network examples
        --all: Create all remote network types (default behavior)
        --ipsec-tunnel: Name of existing IPsec tunnel to use (required for non-ECMP networks)
        --secondary-tunnel: Name of existing secondary IPsec tunnel (optional, for advanced networks)
        --ipsec-tunnels: List of existing IPsec tunnel names for ECMP networks (at least 2 required)
        --folder: Folder name where remote networks will be created (required)
        --no-report: Skip CSV report generation
        --max-limit: Maximum number of objects to return in a single API request (1-5000)

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
    network_count = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine which network types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (args.basic or args.bgp or args.ecmp or args.advanced)

    # Keep track of created networks for cleanup
    created_networks = []
    created_network_ids = []

    try:
        # Initialize client
        client = initialize_client()

        # Initialize RemoteNetworks object
        log_section("REMOTE NETWORK CONFIGURATION")
        log_operation_start("Initializing RemoteNetworks manager")
        remote_networks = RemoteNetworks(client, max_limit=args.max_limit)
        log_operation_complete(
            "RemoteNetworks manager initialization", f"Max limit: {remote_networks.max_limit}"
        )

        # Check if folder parameter is provided
        if not args.folder:
            log_error("Missing required folder parameter")
            log_info("A folder name is required to create remote networks")
            log_info(
                "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
            )
            log_info("Run with --help for more information")
            return

        # Create basic remote network
        if create_all or args.basic:
            log_section("BASIC REMOTE NETWORK")
            log_info("Creating basic remote network with minimal configuration")

            # Check if we have required IPsec tunnel parameter
            if not args.ipsec_tunnel:
                log_error("Missing required IPsec tunnel parameter for basic network")
                log_info(
                    "An existing IPsec tunnel name is required to create basic remote networks"
                )
                log_info(
                    "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
                )
                log_info("Skipping basic remote network creation")
            else:
                basic_network = create_basic_remote_network(
                    remote_networks, ipsec_tunnel=args.ipsec_tunnel, folder=args.folder
                )
                if basic_network:
                    created_networks.append(basic_network)
                    created_network_ids.append(basic_network.id)
                    network_count += 1

        # Create BGP remote network
        if create_all or args.bgp:
            log_section("BGP REMOTE NETWORK")
            log_info("Creating remote network with BGP configuration")

            # Check if we have required IPsec tunnel parameter
            if not args.ipsec_tunnel:
                log_error("Missing required IPsec tunnel parameter for BGP network")
                log_info("An existing IPsec tunnel name is required to create BGP remote networks")
                log_info(
                    "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
                )
                log_info("Skipping BGP remote network creation")
            else:
                bgp_network = create_bgp_remote_network(
                    remote_networks, ipsec_tunnel=args.ipsec_tunnel, folder=args.folder
                )
                if bgp_network:
                    created_networks.append(bgp_network)
                    created_network_ids.append(bgp_network.id)
                    network_count += 1

        # Create ECMP remote network
        if create_all or args.ecmp:
            log_section("ECMP REMOTE NETWORK")
            log_info("Creating remote network with ECMP configuration")

            # Check if we have required IPsec tunnels parameter
            if not args.ipsec_tunnels or len(args.ipsec_tunnels) < 2:
                log_error("Missing required IPsec tunnels parameter for ECMP network")
                log_info(
                    "At least 2 existing IPsec tunnel names are required to create ECMP remote networks"
                )
                log_info(
                    "Example: python remote_networks.py --ipsec-tunnels tunnel1 tunnel2 --folder your-folder"
                )
                log_info("Skipping ECMP remote network creation")
            else:
                ecmp_network = create_ecmp_remote_network(
                    remote_networks, ipsec_tunnels=args.ipsec_tunnels, folder=args.folder
                )
                if ecmp_network:
                    created_networks.append(ecmp_network)
                    created_network_ids.append(ecmp_network.id)
                    network_count += 1

        # Create advanced remote network
        if create_all or args.advanced:
            log_section("ADVANCED REMOTE NETWORK")
            log_info("Creating remote network with advanced configuration")

            # Check if we have required IPsec tunnel parameter
            if not args.ipsec_tunnel:
                log_error("Missing required IPsec tunnel parameter for advanced network")
                log_info(
                    "An existing IPsec tunnel name is required to create advanced remote networks"
                )
                log_info(
                    "Example: python remote_networks.py --ipsec-tunnel your-tunnel-name --folder your-folder"
                )
                log_info("Skipping advanced remote network creation")
            else:
                advanced_network = create_advanced_remote_network(
                    remote_networks,
                    ipsec_tunnel=args.ipsec_tunnel,
                    secondary_tunnel=args.secondary_tunnel,
                    folder=args.folder,
                )
                if advanced_network:
                    created_networks.append(advanced_network)
                    created_network_ids.append(advanced_network.id)
                    network_count += 1

        # Update one of the networks if we created any
        if created_networks:
            log_section("UPDATING REMOTE NETWORK")
            log_info("Demonstrating how to update an existing remote network")

            fetch_and_update_remote_network(remote_networks, created_networks[0].id)

        # List and filter remote networks
        list_and_filter_remote_networks(remote_networks, args.folder)

        # Fetch a specific network by name
        if created_networks:
            log_section("FETCHING REMOTE NETWORK BY NAME")
            log_info("Demonstrating how to fetch a remote network by name")

            # Use the first created network's name
            fetch_remote_network_by_name(remote_networks, created_networks[0].name, args.folder)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are networks to report and report generation is not disabled
        if created_network_ids and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating remote networks CSV report")

            report_file = generate_remote_network_report(
                remote_networks, created_network_ids, execution_time_so_far
            )

            if report_file:
                log_success(f"Generated remote networks report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_network_ids)} remote networks created"
                )
            else:
                log_error("Failed to generate remote networks report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No remote networks were created, skipping report generation")

        # Clean up the created networks, unless skip_cleanup is true
        if skip_cleanup:
            log_info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_network_ids)} remote networks"
            )
            log_info(
                "To clean up these networks, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            cleanup_remote_networks(remote_networks, created_network_ids)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total remote networks created: {network_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if network_count > 0:
            log_info(f"Average time per network: {execution_time / network_count:.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some remote networks may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
