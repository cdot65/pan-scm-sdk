#!/usr/bin/env python3
"""Standardized example of working with Address objects in Palo Alto Networks' Strata Cloud Manager.

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
   - Detailed CSV and PDF report generation
   - Formatted output with Rich console formatting
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV and PDF report generation with address object details
- Optional cleanup skipping with SKIP_CLEANUP=true environment variable
- Progress tracking for long operations

Before running this example:
1. Replace the authentication credentials with your own or use a .env file:
   ```
   SCM_CLIENT_ID=your_client_id
   SCM_CLIENT_SECRET=your_client_secret
   SCM_TSG_ID=your_tsg_id
   SCM_LOG_LEVEL=DEBUG  # Optional
   ```

2. Make sure you have a folder named "Texas" in your SCM environment or change the
   folder name with the --folder argument.

3. Optional environment variables:
   - SKIP_CLEANUP=true: Set this to preserve created address objects for manual inspection
"""

import argparse
import datetime
import os
import uuid
import time
from typing import List, Dict, Any, Optional, Tuple, TypeVar

# Import shared utilities
from examples.utils.logging import SDKLogger
from examples.utils.client import ClientInitializer
from examples.utils.report import ReportGenerator

# Import SDK modules
from scm.client import Scm
from scm.config.objects import Address
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)

# Define types for stronger typing
AddressManager = Address
AddressObject = TypeVar("AddressObject")  # The address object returned from API calls
AddressConfig = Dict[str, Any]  # Configuration dictionary for creating addresses
AddressID = str  # UUID string for address objects

# Initialize logger
logger = SDKLogger("address_example")


def create_ipv4_network_address(
    addresses: AddressManager, folder: str = "Texas"
) -> Optional[AddressObject]:
    """Create an address object for an IPv4 network.

    This function demonstrates creating a standard IPv4 network address object
    with CIDR notation, commonly used for subnets and network segments.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        AddressObject: The created address object, or None if creation failed
    """
    logger.operation_start("Creating IPv4 network address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"network-segment-{uuid.uuid4().hex[:6]}"
    logger.info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_network_config = {
        "name": address_name,
        "description": "Example IPv4 network segment for corporate LAN",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Corporate"],
        "ip_netmask": "10.10.10.0/24",
    }

    logger.info("Configuration details:")
    logger.info("  - Type: IPv4 Network")
    logger.info(f"  - Network: {ipv4_network_config['ip_netmask']}")
    logger.info(f"  - Tags: {', '.join(ipv4_network_config['tag'])}")

    try:
        logger.info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_network_config)
        logger.success(f"Created address object: {new_address.name}")
        logger.info(f"  - Object ID: {new_address.id}")
        logger.info(f"  - Description: {new_address.description}")
        logger.operation_complete("IPv4 network address creation", f"Address: {new_address.name}")
        return new_address
    except NameNotUniqueError as e:
        logger.error("Address name conflict", e.message)
        logger.info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        logger.error("Invalid address data", e.message)
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")
            logger.info("Check your configuration values and try again")
    except Exception as e:
        logger.error("Unexpected error creating address object", str(e))

    return None


def create_ipv4_host_address(
    addresses: AddressManager, folder: str = "Texas"
) -> Optional[AddressObject]:
    """Create an address object for a single IPv4 host.

    This function demonstrates creating an IPv4 host address object,
    commonly used for servers, endpoints, or other individual hosts.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        AddressObject: The created address object, or None if creation failed
    """
    logger.operation_start("Creating IPv4 host address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"server-host-{uuid.uuid4().hex[:6]}"
    logger.info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_host_config = {
        "name": address_name,
        "description": "Example server host address",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Servers"],
        "ip_netmask": "192.168.1.100/32",  # /32 for a single host
    }

    logger.info("Configuration details:")
    logger.info("  - Type: IPv4 Host")
    logger.info(f"  - Host IP: {ipv4_host_config['ip_netmask'].split('/')[0]}")
    logger.info(f"  - Tags: {', '.join(ipv4_host_config['tag'])}")

    try:
        logger.info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_host_config)
        logger.success(f"Created address object: {new_address.name}")
        logger.info(f"  - Object ID: {new_address.id}")
        logger.info(f"  - Description: {new_address.description}")
        logger.operation_complete("IPv4 host address creation", f"Address: {new_address.name}")
        return new_address
    except NameNotUniqueError as e:
        logger.error("Address name conflict", e.message)
        logger.info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        logger.error("Invalid address data", e.message)
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")
            logger.info("Check your configuration values and try again")
    except Exception as e:
        logger.error("Unexpected error creating address object", str(e))

    return None


def create_ipv4_range_address(
    addresses: AddressManager, folder: str = "Texas"
) -> Optional[AddressObject]:
    """Create an address object for an IPv4 address range.

    This function demonstrates creating an IPv4 range address object,
    commonly used for DHCP pools, IP blocks, or other address ranges.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        AddressObject: The created address object, or None if creation failed
    """
    logger.operation_start("Creating IPv4 range address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"dhcp-range-{uuid.uuid4().hex[:6]}"
    logger.info(f"Address name: {address_name}")

    # Create the address configuration
    ipv4_range_config = {
        "name": address_name,
        "description": "Example DHCP address range",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "DHCP"],
        "ip_range": "10.20.30.100-10.20.30.200",
    }

    logger.info("Configuration details:")
    logger.info("  - Type: IPv4 Range")
    logger.info(f"  - Range: {ipv4_range_config['ip_range']}")
    logger.info(f"  - Tags: {', '.join(ipv4_range_config['tag'])}")

    try:
        logger.info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv4_range_config)
        logger.success(f"Created address object: {new_address.name}")
        logger.info(f"  - Object ID: {new_address.id}")
        logger.info(f"  - Description: {new_address.description}")
        logger.operation_complete("IPv4 range address creation", f"Address: {new_address.name}")
        return new_address
    except NameNotUniqueError as e:
        logger.error("Address name conflict", e.message)
        logger.info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        logger.error("Invalid address data", e.message)
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")
            logger.info("Check your configuration values and try again")
    except Exception as e:
        logger.error("Unexpected error creating address object", str(e))

    return None


def create_ipv6_address(
    addresses: AddressManager, folder: str = "Texas"
) -> Optional[AddressObject]:
    """Create an address object for an IPv6 network.

    This function demonstrates creating an IPv6 network address object,
    useful for IPv6 subnets and segments.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        AddressObject: The created address object, or None if creation failed
    """
    logger.operation_start("Creating IPv6 network address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"ipv6-segment-{uuid.uuid4().hex[:6]}"
    logger.info(f"Address name: {address_name}")

    # Create the address configuration - using ip_netmask for IPv6 as well
    ipv6_network_config = {
        "name": address_name,
        "description": "Example IPv6 network segment",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "IPv6"],
        "ip_netmask": "2001:db8:1234::/64",  # IPv6 uses the same field as IPv4
    }

    logger.info("Configuration details:")
    logger.info("  - Type: IPv6 Network")
    logger.info(f"  - Network: {ipv6_network_config['ip_netmask']}")
    logger.info(f"  - Tags: {', '.join(ipv6_network_config['tag'])}")

    try:
        logger.info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(ipv6_network_config)
        logger.success(f"Created address object: {new_address.name}")
        logger.info(f"  - Object ID: {new_address.id}")
        logger.info(f"  - Description: {new_address.description}")
        logger.operation_complete("IPv6 network address creation", f"Address: {new_address.name}")
        return new_address
    except NameNotUniqueError as e:
        logger.error("Address name conflict", e.message)
        logger.info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        logger.error("Invalid address data", e.message)
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")
            logger.info("Check your configuration values and try again")
    except Exception as e:
        logger.error("Unexpected error creating address object", str(e))

    return None


def create_fqdn_address(
    addresses: AddressManager, folder: str = "Texas"
) -> Optional[AddressObject]:
    """Create an address object for a fully qualified domain name (FQDN).

    This function demonstrates creating an FQDN address object,
    commonly used for websites, cloud services, or dynamic hosts.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")

    Returns:
        AddressObject: The created address object, or None if creation failed
    """
    logger.operation_start("Creating FQDN address object")

    # Generate a unique address name with timestamp to avoid conflicts
    address_name = f"website-fqdn-{uuid.uuid4().hex[:6]}"
    logger.info(f"Address name: {address_name}")

    # Create the address configuration
    fqdn_config = {
        "name": address_name,
        "description": "Example website FQDN address",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Web"],
        "fqdn": "www.example.com",
    }

    logger.info("Configuration details:")
    logger.info("  - Type: FQDN")
    logger.info(f"  - Domain: {fqdn_config['fqdn']}")
    logger.info(f"  - Tags: {', '.join(fqdn_config['tag'])}")

    try:
        logger.info("Sending request to Strata Cloud Manager API...")
        new_address = addresses.create(fqdn_config)
        logger.success(f"Created address object: {new_address.name}")
        logger.info(f"  - Object ID: {new_address.id}")
        logger.info(f"  - Description: {new_address.description}")
        logger.operation_complete("FQDN address creation", f"Address: {new_address.name}")
        return new_address
    except NameNotUniqueError as e:
        logger.error("Address name conflict", e.message)
        logger.info("Try using a different address name or check existing objects")
    except InvalidObjectError as e:
        logger.error("Invalid address data", e.message)
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")
            logger.info("Check your configuration values and try again")
    except Exception as e:
        logger.error("Unexpected error creating address object", str(e))

    return None


def fetch_and_update_address(
    addresses: AddressManager, address_id: AddressID
) -> Optional[AddressObject]:
    """Fetch an address object by ID and update its description and tags.

    This function demonstrates how to:
    1. Retrieve an existing address object using its ID
    2. Modify object properties (description, tags)
    3. Submit the updated object back to the SCM API

    Args:
        addresses: The Address manager instance
        address_id: The UUID of the address object to update

    Returns:
        AddressObject: The updated address object, or None if update failed
    """
    logger.operation_start(f"Updating address object with ID: {address_id}")

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
        logger.info("Sending update request to Strata Cloud Manager API...")
        updated_address = addresses.update(address)
        logger.success(
            f"Updated address object: {updated_address.name} with description: {updated_address.description}"
        )
        logger.operation_complete("Address object update")
        return updated_address

    except NotFoundError as e:
        logger.error("Address object not found", e.message if hasattr(e, "message") else str(e))
    except InvalidObjectError as e:
        logger.error(
            "Invalid address object update", e.message if hasattr(e, "message") else str(e)
        )
        if hasattr(e, "details") and e.details:
            logger.info(f"Error details: {e.details}")

    return None


def list_and_filter_addresses(
    addresses: AddressManager, folder: str = "Texas"
) -> List[AddressObject]:
    """List and filter address objects.

    This function demonstrates how to:
    1. List all address objects in a folder
    2. Filter address objects by various criteria
    3. Display detailed information about each object

    Args:
        addresses: The Address manager instance
        folder: Folder name to filter objects by

    Returns:
        List[AddressObject]: All retrieved address objects
    """
    logger.operation_start("Listing and filtering address objects")

    # Use the progress bar for the listing operation
    with logger.create_progress() as progress:
        # Add a task for listing
        task = progress.add_task("Fetching address objects...", total=1)

        # List all address objects in the specified folder
        all_addresses = addresses.list(folder=folder)
        progress.update(task, advance=1)

    logger.success(f"Found {len(all_addresses)} address objects in the {folder} folder")

    # Filter by tag
    try:
        with logger.create_progress() as progress:
            task = progress.add_task("Filtering by tag...", total=1)
            automation_tagged = addresses.list(folder=folder, tag=["Automation"])
            progress.update(task, advance=1)

        logger.info(f"Found {len(automation_tagged)} address objects with 'Automation' tag")
    except Exception as e:
        logger.error("Error filtering by tag", str(e))

    # Filter by name pattern (where supported)
    try:
        with logger.create_progress() as progress:
            task = progress.add_task("Filtering by name...", total=1)
            network_addresses = addresses.list(folder=folder, name="network")
            progress.update(task, advance=1)

        logger.info(f"Found {len(network_addresses)} address objects with 'network' in the name")
    except Exception as e:
        logger.error("Filtering by name is not supported", str(e))

    # Display address objects in a table
    if all_addresses:
        # Create a table to display address details
        table = logger.create_table(
            "Address Objects", ["Name", "Type", "Value", "Description", "Tags"]
        )

        # Display up to 5 objects to avoid cluttering the output
        for address in all_addresses[:5]:
            # Determine address type and value
            address_type, address_value = get_address_type_and_value(address)

            # Add a row to the table
            table.add_row(
                address.name,
                address_type,
                address_value,
                (address.description or "")[:30],  # Truncate long descriptions
                ", ".join(address.tag) if address.tag else "",
            )

        # Display the table
        logger.console.print(table)

        if len(all_addresses) > 5:
            logger.info(f"Showing 5 of {len(all_addresses)} address objects")

    logger.operation_complete("Address listing and filtering")
    return all_addresses


def create_bulk_address_objects(
    addresses: AddressManager, folder: str = "Texas"
) -> List[AddressID]:
    """Create multiple address objects in a batch.

    This function demonstrates creating multiple address objects in a batch,
    which is useful for setting up multiple addresses at once.

    Args:
        addresses: The Address manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")

    Returns:
        List[AddressID]: List of IDs of created address objects, or empty list if creation failed
    """
    logger.operation_start("Creating a batch of address objects")

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
        },
    ]

    created_addresses = []

    # Create each address object with progress tracking
    with logger.create_progress() as progress:
        task = progress.add_task(
            f"Creating {len(address_configs)} address objects...", total=len(address_configs)
        )

        for address_config in address_configs:
            try:
                new_address = addresses.create(address_config)
                logger.success(
                    f"Created address object: {new_address.name} with ID: {new_address.id}"
                )
                created_addresses.append(new_address.id)
            except Exception as e:
                logger.error(f"Error creating address {address_config['name']}", str(e))

            progress.update(task, advance=1)

    logger.operation_complete(
        "Bulk address creation",
        f"Created {len(created_addresses)} of {len(address_configs)} objects",
    )
    return created_addresses


def cleanup_address_objects(addresses: AddressManager, address_ids: List[AddressID]) -> None:
    """Delete the address objects created in this example.

    Args:
        addresses: The Address manager instance
        address_ids: List of address object IDs to delete
    """
    logger.operation_start(f"Cleaning up {len(address_ids)} address objects")

    with logger.create_progress() as progress:
        task = progress.add_task(f"Deleting {len(address_ids)} objects...", total=len(address_ids))

        successful_deletions = 0
        failed_deletions = 0

        for address_id in address_ids:
            try:
                addresses.delete(address_id)
                successful_deletions += 1
            except NotFoundError as e:
                logger.error(
                    "Address object not found", e.message if hasattr(e, "message") else str(e)
                )
                failed_deletions += 1
            except Exception as e:
                logger.error("Error deleting address object", str(e))
                failed_deletions += 1

            progress.update(task, advance=1)

    if successful_deletions == len(address_ids):
        logger.success(f"All {len(address_ids)} address objects deleted successfully")
    else:
        logger.warning(
            f"Deleted {successful_deletions} of {len(address_ids)} address objects. {failed_deletions} failed."
        )

    logger.operation_complete("Address cleanup")


def get_address_type_and_value(address: AddressObject) -> Tuple[str, str]:
    """Helper function to determine address type and value.

    Args:
        address: The address object to analyze

    Returns:
        Tuple[str, str]: A tuple containing (address_type, address_value)
    """
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

    return address_type, address_value


def prepare_report_data(
    addresses: AddressManager, address_ids: List[AddressID]
) -> Tuple[List[str], List[List[str]], Dict[str, Any]]:
    """Prepare data for CSV and PDF reports.

    Args:
        addresses: The Address manager instance
        address_ids: List of address object IDs to include in the report

    Returns:
        Tuple[List[str], List[List[str]], Dict[str, Any]]: A tuple containing:
            - headers: List of column headers
            - data: List of rows (each row is a list of values)
            - summary_data: Dictionary of summary information
    """
    logger.operation_start("Preparing report data")

    # Define report headers
    headers = ["Name", "Type", "Value", "Description", "Tags"]

    # Collect data with progress tracking
    with logger.create_progress() as progress:
        task = progress.add_task(
            f"Processing {len(address_ids)} objects for report...", total=len(address_ids)
        )

        address_data = []
        successful_fetches = 0
        failed_fetches = 0

        for address_id in address_ids:
            try:
                # Get the address details
                address = addresses.get(address_id)

                # Determine address type and value
                address_type, address_value = get_address_type_and_value(address)

                # Add address data
                address_data.append(
                    [
                        address.name,
                        address_type,
                        address_value,
                        address.description if address.description else "None",
                        ", ".join(address.tag) if address.tag else "None",
                    ]
                )

                successful_fetches += 1

            except Exception as e:
                logger.error(f"Error getting details for address ID {address_id}", str(e))
                # Add minimal info for addresses that couldn't be retrieved
                address_data.append(
                    [
                        f"ERROR-{address_id[:8]}",
                        "ERROR",
                        "ERROR",
                        f"Failed to retrieve address details: {str(e)}",
                        "",
                    ]
                )
                failed_fetches += 1

            progress.update(task, advance=1)

    # Prepare summary data for the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_data = {
        "Total Objects Processed": len(address_ids),
        "Successfully Retrieved": successful_fetches,
        "Failed to Retrieve": failed_fetches,
        "Report Generated On": timestamp,
    }

    logger.operation_complete("Report data preparation", f"Processed {len(address_ids)} objects")
    return headers, address_data, summary_data


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for the address example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which address object types to create
    - Whether to generate reports
    - Folder name to use for object creation

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Address Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Preserve created address objects (don't delete them)",
    )

    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument("--ipv4", action="store_true", help="Create IPv4 address examples")
    object_group.add_argument("--ipv6", action="store_true", help="Create IPv6 address examples")
    object_group.add_argument("--fqdn", action="store_true", help="Create FQDN address examples")
    object_group.add_argument("--bulk", action="store_true", help="Create bulk address examples")
    object_group.add_argument(
        "--all", action="store_true", help="Create all address object types (default behavior)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip report generation")

    # Folder
    parser.add_argument(
        "--folder", type=str, default="Texas", help="Folder name in SCM to create objects in"
    )

    return parser.parse_args()


def main() -> None:
    """Execute the comprehensive set of address object examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of address objects (IPv4, IPv6, FQDN)
    4. Update an existing address object to demonstrate modification capabilities
    5. List and filter address objects to show search functionality
    6. Generate detailed CSV and PDF reports of all created address objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Track execution time for reporting
    start_time: float = time.time()
    object_count: int = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup: bool = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine which object types to create
    # If no specific types are specified, create all (default behavior)
    create_all: bool = args.all or not (args.ipv4 or args.ipv6 or args.fqdn or args.bulk)

    # Get folder name for object creation
    folder_name: str = args.folder

    try:
        # Initialize client using shared initializer
        client_init = ClientInitializer(logger)
        client = client_init.initialize_client(Scm)
        if not client:
            return

        # Initialize Address object
        logger.section("ADDRESS OBJECT CONFIGURATION")
        logger.operation_start("Initializing Address object manager")
        addresses = Address(client)
        logger.operation_complete("Address object manager initialization")

        # Create various address objects
        created_addresses: List[AddressID] = []

        # IPv4 Address objects
        if create_all or args.ipv4:
            logger.section("IPv4 ADDRESS OBJECTS")
            logger.info("Creating common IPv4 address object patterns")
            logger.info(f"Using folder: {folder_name}")

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

            logger.success(f"Created {len(created_addresses)} IPv4 address objects so far")

        # IPv6 Address objects
        if create_all or args.ipv6:
            logger.section("IPv6 ADDRESS OBJECTS")
            logger.info("Creating IPv6 address object patterns")
            logger.info(f"Using folder: {folder_name}")

            # Create an IPv6 network address
            ipv6_network = create_ipv6_address(addresses, folder_name)
            if ipv6_network:
                created_addresses.append(ipv6_network.id)
                object_count += 1

            logger.success("Created IPv6 address objects")

        # FQDN Address objects
        if create_all or args.fqdn:
            logger.section("FQDN ADDRESS OBJECTS")
            logger.info("Creating FQDN address object patterns")
            logger.info(f"Using folder: {folder_name}")

            # Create an FQDN address
            fqdn_address = create_fqdn_address(addresses, folder_name)
            if fqdn_address:
                created_addresses.append(fqdn_address.id)
                object_count += 1

            logger.success("Created FQDN address objects")

        # Bulk Address object creation
        if create_all or args.bulk:
            logger.section("BULK ADDRESS OBJECTS")
            logger.info("Creating multiple address objects in bulk")
            logger.info(f"Using folder: {folder_name}")

            # Create bulk address objects
            bulk_address_ids = create_bulk_address_objects(addresses, folder_name)
            if bulk_address_ids:
                created_addresses.extend(bulk_address_ids)
                object_count += len(bulk_address_ids)
                logger.success(f"Created {len(bulk_address_ids)} bulk address objects")

        # Update one of the objects
        if created_addresses:
            logger.section("UPDATING ADDRESS OBJECTS")
            logger.info("Demonstrating how to update existing address objects")
            fetch_and_update_address(addresses, created_addresses[0])

        # List and filter address objects
        logger.section("LISTING AND FILTERING ADDRESS OBJECTS")
        logger.info("Demonstrating how to search and filter address objects")
        list_and_filter_addresses(addresses, folder_name)

        # Generate reports before cleanup if there are objects to report and report generation is not disabled
        if created_addresses and not args.no_report:
            logger.section("REPORT GENERATION")

            # Prepare report data
            headers, data, summary = prepare_report_data(addresses, created_addresses)

            # Add execution time so far to summary
            current_time = time.time()
            execution_time_so_far = current_time - start_time
            summary["Execution Time (so far)"] = f"{execution_time_so_far:.2f} seconds"

            # Create report generator and generate reports
            report_gen = ReportGenerator("address_objects", logger)

            # Generate CSV report
            logger.operation_start("Generating CSV report")
            csv_file = report_gen.generate_csv(headers, data, summary)
            if csv_file:
                logger.success(f"Generated CSV report: {csv_file}")

            # Generate PDF report
            logger.operation_start("Generating PDF report")
            pdf_file = report_gen.generate_pdf("Address Objects Report", headers, data, summary)
            if pdf_file:
                logger.success(f"Generated PDF report: {pdf_file}")

            logger.info(
                f"The reports contain details of all {len(created_addresses)} address objects created"
            )

        elif args.no_report:
            logger.info("Report generation disabled by --no-report flag")
        else:
            logger.info("No address objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        logger.section("CLEANUP")
        if skip_cleanup:
            logger.info(
                f"SKIP_CLEANUP is set to true - preserving {len(created_addresses)} address objects"
            )
            logger.info(
                "To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            cleanup_address_objects(addresses, created_addresses)

        # Calculate and display final execution statistics
        end_time = time.time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        logger.section("EXECUTION SUMMARY")
        logger.success("Example script completed successfully")
        logger.info(f"Total address objects created: {object_count}")
        logger.info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        if object_count > 0:
            logger.info(f"Average time per object: {execution_time / object_count:.2f} seconds")

    except AuthenticationError as e:
        logger.error("Authentication failed", e.message if hasattr(e, "message") else str(e))
        if hasattr(e, "http_status_code"):
            logger.info(f"Status code: {e.http_status_code}")
        logger.info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        logger.warning("Script execution interrupted by user")
        logger.info("Note: Some address objects may not have been cleaned up")
    except Exception as e:
        logger.error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        logger.info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
