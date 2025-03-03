#!/usr/bin/env python3
"""
Comprehensive examples of working with Address objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Address object configurations and operations commonly 
used in enterprise networks, including:

1. Address Object Types:
   - IPv4 network addresses (CIDR notation)
   - IPv4 host addresses
   - IPv4 address ranges
   - IPv6 addresses
   - FQDN (Fully Qualified Domain Names)

2. Operational examples:
   - Creating address objects
   - Searching and filtering address objects
   - Updating address object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with address object details
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
   - SKIP_CLEANUP=true: Set this to preserve created address objects for manual inspection
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
from scm.config.objects import Address
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
logger = logging.getLogger("address_example")


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


def create_ipv4_network_address(addresses, folder="Texas"):
    """
    Create an address object for an IPv4 network.
    
    This function demonstrates creating a standard IPv4 network address object
    with CIDR notation, commonly used for subnets and network segments.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        AddressResponseModel: The created address object, or None if creation failed
    """
    log_operation_start("Creating IPv4 network address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"network-segment-{uuid.uuid4().hex[:6]}"
    log_info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_network_config = {
        "name": address_name,
        "description": "Example IPv4 network segment for corporate LAN",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Corporate"],
        "ip_netmask": "10.10.10.0/24",
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IPv4 Network")
    log_info(f"  - Network: {ipv4_network_config['ip_netmask']}")
    log_info(f"  - Tags: {', '.join(ipv4_network_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_network_config)
        log_success(f"Created address object: {new_address.name}")
        log_info(f"  - Object ID: {new_address.id}")
        log_info(f"  - Description: {new_address.description}")
        log_operation_complete(
            "IPv4 network address creation", f"Address: {new_address.name}"
        )
        return new_address
    except NameNotUniqueError as e:
        log_error(f"Address name conflict", e.message)
        log_info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid address data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address object", str(e))

    return None


def create_ipv4_host_address(addresses, folder="Texas"):
    """
    Create an address object for a single IPv4 host.
    
    This function demonstrates creating an IPv4 host address object,
    commonly used for servers, endpoints, or other individual hosts.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        AddressResponseModel: The created address object, or None if creation failed
    """
    log_operation_start("Creating IPv4 host address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"server-host-{uuid.uuid4().hex[:6]}"
    log_info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_host_config = {
        "name": address_name,
        "description": "Example server host address",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Servers"],
        "ip_netmask": "192.168.1.100/32",  # /32 for a single host
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IPv4 Host")
    log_info(f"  - Host IP: {ipv4_host_config['ip_netmask'].split('/')[0]}")
    log_info(f"  - Tags: {', '.join(ipv4_host_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_host_config)
        log_success(f"Created address object: {new_address.name}")
        log_info(f"  - Object ID: {new_address.id}")
        log_info(f"  - Description: {new_address.description}")
        log_operation_complete(
            "IPv4 host address creation", f"Address: {new_address.name}"
        )
        return new_address
    except NameNotUniqueError as e:
        log_error(f"Address name conflict", e.message)
        log_info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid address data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address object", str(e))

    return None


def create_ipv4_range_address(addresses, folder="Texas"):
    """
    Create an address object for an IPv4 address range.
    
    This function demonstrates creating an IPv4 range address object,
    commonly used for DHCP pools, IP blocks, or other address ranges.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        AddressResponseModel: The created address object, or None if creation failed
    """
    log_operation_start("Creating IPv4 range address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"dhcp-range-{uuid.uuid4().hex[:6]}"
    log_info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_range_config = {
        "name": address_name,
        "description": "Example DHCP address range",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "DHCP"],
        "ip_range": "10.20.30.100-10.20.30.200",
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IPv4 Range")
    log_info(f"  - Range: {ipv4_range_config['ip_range']}")
    log_info(f"  - Tags: {', '.join(ipv4_range_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_range_config)
        log_success(f"Created address object: {new_address.name}")
        log_info(f"  - Object ID: {new_address.id}")
        log_info(f"  - Description: {new_address.description}")
        log_operation_complete(
            "IPv4 range address creation", f"Address: {new_address.name}"
        )
        return new_address
    except NameNotUniqueError as e:
        log_error(f"Address name conflict", e.message)
        log_info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid address data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address object", str(e))

    return None


def create_ipv6_address(addresses, folder="Texas"):
    """
    Create an address object for an IPv6 network.
    
    This function demonstrates creating an IPv6 network address object,
    useful for IPv6 subnets and segments.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        AddressResponseModel: The created address object, or None if creation failed
    """
    log_operation_start("Creating IPv6 network address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"ipv6-segment-{uuid.uuid4().hex[:6]}"
    log_info(f"Address name: {address_name}")

    # Create the address configuration - using ip_netmask for IPv6 as well
    ipv6_network_config = {
        "name": address_name,
        "description": "Example IPv6 network segment",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "IPv6"],
        "ip_netmask": "2001:db8:1234::/64",  # IPv6 uses the same field as IPv4
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IPv6 Network")
    log_info(f"  - Network: {ipv6_network_config['ip_netmask']}")
    log_info(f"  - Tags: {', '.join(ipv6_network_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv6_network_config)
        log_success(f"Created address object: {new_address.name}")
        log_info(f"  - Object ID: {new_address.id}")
        log_info(f"  - Description: {new_address.description}")
        log_operation_complete(
            "IPv6 network address creation", f"Address: {new_address.name}"
        )
        return new_address
    except NameNotUniqueError as e:
        log_error(f"Address name conflict", e.message)
        log_info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid address data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address object", str(e))

    return None


def create_fqdn_address(addresses, folder="Texas"):
    """
    Create an address object for a fully qualified domain name (FQDN).
    
    This function demonstrates creating an FQDN address object,
    commonly used for websites, cloud services, or dynamic hosts.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        AddressResponseModel: The created address object, or None if creation failed
    """
    log_operation_start("Creating FQDN address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"website-fqdn-{uuid.uuid4().hex[:6]}"
    log_info(f"Address name: {address_name}")

    # Create the address configuration
    fqdn_config = {
        "name": address_name,
        "description": "Example website FQDN address",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Web"],
        "fqdn": "www.example.com",
    }

    log_info("Configuration details:")
    log_info(f"  - Type: FQDN")
    log_info(f"  - Domain: {fqdn_config['fqdn']}")
    log_info(f"  - Tags: {', '.join(fqdn_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(fqdn_config)
        log_success(f"Created address object: {new_address.name}")
        log_info(f"  - Object ID: {new_address.id}")
        log_info(f"  - Description: {new_address.description}")
        log_operation_complete(
            "FQDN address creation", f"Address: {new_address.name}"
        )
        return new_address
    except NameNotUniqueError as e:
        log_error(f"Address name conflict", e.message)
        log_info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid address data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating address object", str(e))

    return None


def fetch_and_update_address(addresses, address_id):
    """
    Fetch an address object by ID and update its description and tags.
    
    This function demonstrates how to:
    1. Retrieve an existing address object using its ID
    2. Modify object properties (description, tags)
    3. Submit the updated object back to the SCM API
    
    Args:
        addresses: The Address manager instance
        address_id: The UUID of the address object to update
        
    Returns:
        AddressResponseModel: The updated address object, or None if update failed
    """
    logger.info(f"Fetching and updating address object with ID: {address_id}")

    try:
        # Fetch the address
        address = addresses.get(address_id)
        logger.info(f"Found address object: {address.name}")

        # Update description and tags
        address.description = f"Updated description for {address.name}"
        
        # Add additional tags if they don't exist
        if "Updated" not in address.tag:
            address.tag = address.tag + ["Updated"]

        # Perform the update
        updated_address = addresses.update(address)
        logger.info(
            f"Updated address object: {updated_address.name} with description: {updated_address.description}"
        )
        return updated_address

    except NotFoundError as e:
        logger.error(f"Address object not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid address object update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_addresses(addresses):
    """
    List and filter address objects.
    
    This function demonstrates how to:
    1. List all address objects in a folder
    2. Filter address objects by various criteria
    3. Display detailed information about each object
    
    Args:
        addresses: The Address manager instance
        
    Returns:
        list: All retrieved address objects
    """
    logger.info("Listing and filtering address objects")

    # List all address objects in the Texas folder
    all_addresses = addresses.list(folder="Texas")
    logger.info(f"Found {len(all_addresses)} address objects in the Texas folder")

    # Filter by tag
    automation_tagged = addresses.list(folder="Texas", tag=["Automation"])
    logger.info(f"Found {len(automation_tagged)} address objects with 'Automation' tag")

    # Filter by name pattern (where supported)
    try:
        network_addresses = addresses.list(folder="Texas", name="network")
        logger.info(f"Found {len(network_addresses)} address objects with 'network' in the name")
    except Exception as e:
        logger.error(f"Filtering by name is not supported: {str(e)}")

    # Print details of addresses
    logger.info("\nDetails of address objects:")
    for address in all_addresses[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Address: {address.name}")
        logger.info(f"    ID: {address.id}")
        logger.info(f"    Description: {address.description}")
        logger.info(f"    Tags: {address.tag}")
        
        # Determine address type and value
        address_type = "Unknown"
        address_value = "Unknown"
        
        if hasattr(address, "ip_netmask") and address.ip_netmask:
            # Check if this is IPv6 (contains colons)
            if ":" in address.ip_netmask:
                address_type = "IPv6 Network/Host"
            else:
                address_type = "IPv4 Network/Host"
            address_value = address.ip_netmask
        elif hasattr(address, "ip_range") and address.ip_range:
            address_type = "IPv4 Range"
            address_value = address.ip_range
        elif hasattr(address, "fqdn") and address.fqdn:
            address_type = "FQDN"
            address_value = address.fqdn
            
        logger.info(f"    Type: {address_type}")
        logger.info(f"    Value: {address_value}")
        logger.info("")

    return all_addresses


def cleanup_address_objects(addresses, address_ids):
    """
    Delete the address objects created in this example.
    
    Args:
        addresses: The Address manager instance
        address_ids: List of address object IDs to delete
    """
    logger.info("Cleaning up address objects")

    for address_id in address_ids:
        try:
            addresses.delete(address_id)
            logger.info(f"Deleted address object with ID: {address_id}")
        except NotFoundError as e:
            logger.error(f"Address object not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting address object: {str(e)}")


def create_bulk_address_objects(addresses, folder="Texas"):
    """
    Create multiple address objects in a batch.
    
    This function demonstrates creating multiple address objects in a batch,
    which is useful for setting up multiple addresses at once.
    
    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created address objects, or empty list if creation failed
    """
    logger.info("Creating a batch of address objects")

    # Define a list of address objects to create
    address_configs = [
        {
            "name": f"bulk-host-1-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created host 1",
            "folder": folder,
            "tag": ["Automation", "Bulk"],
            "ip_netmask": "10.100.1.1/32",
        },
        {
            "name": f"bulk-host-2-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created host 2",
            "folder": folder,
            "tag": ["Automation", "Bulk"],
            "ip_netmask": "10.100.1.2/32",
        },
        {
            "name": f"bulk-network-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created network",
            "folder": folder,
            "tag": ["Automation", "Bulk"],
            "ip_netmask": "10.100.2.0/24",
        },
        {
            "name": f"bulk-fqdn-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created FQDN",
            "folder": folder,
            "tag": ["Automation", "Bulk"],
            "fqdn": "api.example.com",
        }
    ]

    created_addresses = []

    # Create each address object
    for address_config in address_configs:
        try:
            new_address = addresses.create(address_config)
            logger.info(
                f"Created address object: {new_address.name} with ID: {new_address.id}"
            )
            created_addresses.append(new_address.id)
        except Exception as e:
            logger.error(f"Error creating address {address_config['name']}: {str(e)}")

    return created_addresses


def generate_address_report(addresses, address_ids, execution_time):
    """
    Generate a comprehensive CSV report of all address objects created by the script.
    
    This function fetches detailed information about each address object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        addresses: The Address manager instance used to fetch object details
        address_ids: List of address object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"address_objects_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Type",
        "Value", 
        "Description", 
        "Tags",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each address object
    address_data = []
    for idx, address_id in enumerate(address_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(address_ids) - 1:
            log_info(f"Processing address {idx + 1} of {len(address_ids)}")
            
        try:
            # Get the address details
            address = addresses.get(address_id)
            
            # Determine address type and value
            address_type = "Unknown"
            address_value = "Unknown"
            
            if hasattr(address, "ip_netmask") and address.ip_netmask:
                # Check if this is IPv6 (contains colons)
                if ":" in address.ip_netmask:
                    if "/128" in address.ip_netmask:
                        address_type = "IPv6 Host"
                    else:
                        address_type = "IPv6 Network"
                else:
                    if "/32" in address.ip_netmask:
                        address_type = "IPv4 Host"
                    else:
                        address_type = "IPv4 Network"
                address_value = address.ip_netmask
            elif hasattr(address, "ip_range") and address.ip_range:
                address_type = "IPv4 Range"
                address_value = address.ip_range
            elif hasattr(address, "fqdn") and address.fqdn:
                address_type = "FQDN"
                address_value = address.fqdn
            
            # Add address data
            address_data.append([
                address.id,
                address.name,
                address_type,
                address_value,
                address.description if address.description else "None",
                ", ".join(address.tag) if address.tag else "None",
                address.created_on.strftime("%Y-%m-%d %H:%M:%S") if hasattr(address, "created_on") and address.created_on else "Unknown",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for address ID {address_id}", str(e))
            # Add minimal info for addresses that couldn't be retrieved
            address_data.append([
                address_id, 
                "ERROR", 
                "ERROR", 
                "ERROR",
                f"Failed to retrieve address details: {str(e)}", 
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
            writer.writerows(address_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(address_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"address_objects_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(address_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the address example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which address object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Address Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created address objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--ipv4", 
        action="store_true",
        help="Create IPv4 address examples"
    )
    object_group.add_argument(
        "--ipv6", 
        action="store_true", 
        help="Create IPv6 address examples"
    )
    object_group.add_argument(
        "--fqdn", 
        action="store_true",
        help="Create FQDN address examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk address examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all address object types (default behavior)"
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
    Execute the comprehensive set of address object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of address objects (IPv4, IPv6, FQDN)
    4. Update an existing address object to demonstrate modification capabilities
    5. List and filter address objects to show search functionality
    6. Generate a detailed CSV report of all created address objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created address objects (don't delete them)
        --ipv4: Create only IPv4 address examples
        --ipv6: Create only IPv6 address examples
        --fqdn: Create only FQDN address examples
        --bulk: Create only bulk address examples
        --all: Create all address object types (default behavior)
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
    create_all = args.all or not (args.ipv4 or args.ipv6 or args.fqdn or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Address object
        log_section("ADDRESS OBJECT CONFIGURATION")
        log_operation_start("Initializing Address object manager")
        addresses = Address(client)
        log_operation_complete("Address object manager initialization")

        # Create various address objects
        created_addresses = []

        # IPv4 Address objects
        if create_all or args.ipv4:
            log_section("IPv4 ADDRESS OBJECTS")
            log_info("Creating common IPv4 address object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create an IPv4 network address
            ipv4_network = create_ipv4_network_address(addresses, folder_name)
            if ipv4_network:
                created_addresses.append(ipv4_network.id)
                object_count += 1

            # Create an IPv4 host address
            ipv4_host = create_ipv4_host_address(addresses, folder_name)
            if ipv4_host:
                created_addresses.append(ipv4_host.id)
                object_count += 1

            # Create an IPv4 range address
            ipv4_range = create_ipv4_range_address(addresses, folder_name)
            if ipv4_range:
                created_addresses.append(ipv4_range.id)
                object_count += 1

            log_success(f"Created {len(created_addresses)} IPv4 address objects so far")

        # IPv6 Address objects
        if create_all or args.ipv6:
            log_section("IPv6 ADDRESS OBJECTS")
            log_info("Creating IPv6 address object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create an IPv6 network address
            ipv6_network = create_ipv6_address(addresses, folder_name)
            if ipv6_network:
                created_addresses.append(ipv6_network.id)
                object_count += 1

            log_success(f"Created IPv6 address objects")

        # FQDN Address objects
        if create_all or args.fqdn:
            log_section("FQDN ADDRESS OBJECTS")
            log_info("Creating FQDN address object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create an FQDN address
            fqdn_address = create_fqdn_address(addresses, folder_name)
            if fqdn_address:
                created_addresses.append(fqdn_address.id)
                object_count += 1

            log_success(f"Created FQDN address objects")

        # Bulk Address object creation
        if create_all or args.bulk:
            log_section("BULK ADDRESS OBJECTS")
            log_info("Creating multiple address objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk address objects
            bulk_address_ids = create_bulk_address_objects(addresses, folder_name)
            if bulk_address_ids:
                created_addresses.extend(bulk_address_ids)
                object_count += len(bulk_address_ids)
                log_success(f"Created {len(bulk_address_ids)} bulk address objects")

        # Update one of the objects
        if created_addresses:
            log_section("UPDATING ADDRESS OBJECTS")
            log_info("Demonstrating how to update existing address objects")
            updated_address = fetch_and_update_address(addresses, created_addresses[0])

        # List and filter address objects
        log_section("LISTING AND FILTERING ADDRESS OBJECTS")
        log_info("Demonstrating how to search and filter address objects")
        all_addresses = list_and_filter_addresses(addresses)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_addresses and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating address objects CSV report")
            report_file = generate_address_report(addresses, created_addresses, execution_time_so_far)
            if report_file:
                log_success(f"Generated address objects report: {report_file}")
                log_info(f"The report contains details of all {len(created_addresses)} address objects created")
            else:
                log_error("Failed to generate address objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No address objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_addresses)} address objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_addresses)} created address objects")
            cleanup_address_objects(addresses, created_addresses)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total address objects created: {object_count}")
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
        log_info("Note: Some address objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
