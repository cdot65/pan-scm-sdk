#!/usr/bin/env python3
"""
Comprehensive examples of working with Region objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Region object configurations and operations commonly 
used in enterprise networks, including:

1. Region Object Types:
   - Regions with geographic coordinates (latitude/longitude)
   - Regions with associated network addresses
   - Regions with both coordinates and network addresses
   
2. Operational examples:
   - Creating region objects
   - Searching and filtering region objects
   - Updating region object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with region object details
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
   - SKIP_CLEANUP=true: Set this to preserve created region objects for manual inspection
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
from scm.config.objects import Region
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
logger = logging.getLogger("region_example")


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


def create_region_with_coordinates(regions, folder="Texas"):
    """
    Create a region object with geographic coordinates.
    
    This function demonstrates creating a region with latitude and longitude 
    coordinates for a geographic location.
    
    Args:
        regions: The Region manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        RegionResponseModel: The created region object, or None if creation failed
    """
    log_operation_start("Creating region with geographic coordinates")

    # Generate a unique region name with UUID to avoid conflicts
    region_name = f"us-west-{uuid.uuid4().hex[:6]}"
    log_info(f"Region name: {region_name}")

    # Create the region configuration
    # San Francisco coordinates as an example
    region_config = {
        "name": region_name,
        "description": "Example region for San Francisco metropolitan area",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "West-Coast"],
        "geo_location": {
            "latitude": 37.7749,
            "longitude": -122.4194
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Geographic Coordinates Region")
    log_info(f"  - Location: San Francisco")
    log_info(f"  - Description: {region_config['description']}")
    log_info(f"  - Tags: {', '.join(region_config['tag'])}")
    log_info(f"  - Latitude: {region_config['geo_location']['latitude']}")
    log_info(f"  - Longitude: {region_config['geo_location']['longitude']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_region = regions.create(region_config)
        log_success(f"Created region object: {new_region.name}")
        log_info(f"  - Object ID: {new_region.id}")
        description = getattr(new_region, "description", None)
        log_info(f"  - Description: {description}")
        if hasattr(new_region, 'tag') and new_region.tag:
            log_info(f"  - Tags: {', '.join(new_region.tag)}")
        if new_region.geo_location:
            log_info(f"  - Latitude: {new_region.geo_location.latitude}")
            log_info(f"  - Longitude: {new_region.geo_location.longitude}")
        log_operation_complete(
            "Region with coordinates creation", f"Region: {new_region.name}"
        )
        return new_region
    except NameNotUniqueError as e:
        log_error(f"Region name conflict", e.message)
        log_info("Try using a different region name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid region data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating region object", str(e))

    return None


def create_region_with_addresses(regions, folder="Texas"):
    """
    Create a region object with network addresses.
    
    This function demonstrates creating a region with a list of network 
    addresses without specific geographic coordinates.
    
    Args:
        regions: The Region manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        RegionResponseModel: The created region object, or None if creation failed
    """
    log_operation_start("Creating region with network addresses")

    # Generate a unique region name with UUID to avoid conflicts
    region_name = f"corp-net-{uuid.uuid4().hex[:6]}"
    log_info(f"Region name: {region_name}")

    # Create the region configuration
    region_config = {
        "name": region_name,
        "description": "Example region for corporate network addresses",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Corporate", "Internal"],
        "address": [
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16"
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Network Addresses Region")
    log_info(f"  - Description: {region_config['description']}")
    log_info(f"  - Tags: {', '.join(region_config['tag'])}")
    log_info(f"  - Addresses: {', '.join(region_config['address'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_region = regions.create(region_config)
        log_success(f"Created region object: {new_region.name}")
        log_info(f"  - Object ID: {new_region.id}")
        # Safely access description field
        description = getattr(new_region, "description", None)
        log_info(f"  - Description: {description}")
        if hasattr(new_region, 'tag') and new_region.tag:
            log_info(f"  - Tags: {', '.join(new_region.tag)}")
        if new_region.address:
            log_info(f"  - Addresses: {', '.join(new_region.address)}")
        log_operation_complete(
            "Region with addresses creation", f"Region: {new_region.name}"
        )
        return new_region
    except NameNotUniqueError as e:
        log_error(f"Region name conflict", e.message)
        log_info("Try using a different region name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid region data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating region object", str(e))

    return None


def create_comprehensive_region(regions, folder="Texas"):
    """
    Create a comprehensive region object with both coordinates and addresses.
    
    This function demonstrates creating a region with both geographic coordinates
    and a list of network addresses for a complete definition.
    
    Args:
        regions: The Region manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        RegionResponseModel: The created region object, or None if creation failed
    """
    log_operation_start("Creating comprehensive region with coordinates and addresses")

    # Generate a unique region name with UUID to avoid conflicts
    region_name = f"nyc-region-{uuid.uuid4().hex[:6]}"
    log_info(f"Region name: {region_name}")

    # Create the region configuration
    # New York City coordinates as an example
    region_config = {
        "name": region_name,
        "description": "Example comprehensive region for NYC area",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "East-Coast", "Office"],
        "geo_location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "address": [
            "198.51.100.0/24",
            "203.0.113.0/24"
        ]
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Comprehensive Region")
    log_info(f"  - Location: New York City")
    log_info(f"  - Description: {region_config['description']}")
    log_info(f"  - Tags: {', '.join(region_config['tag'])}")
    log_info(f"  - Latitude: {region_config['geo_location']['latitude']}")
    log_info(f"  - Longitude: {region_config['geo_location']['longitude']}")
    log_info(f"  - Addresses: {', '.join(region_config['address'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_region = regions.create(region_config)
        log_success(f"Created region object: {new_region.name}")
        log_info(f"  - Object ID: {new_region.id}")
        # Safely access description field
        description = getattr(new_region, "description", None)
        log_info(f"  - Description: {description}")
        if hasattr(new_region, 'tag') and new_region.tag:
            log_info(f"  - Tags: {', '.join(new_region.tag)}")
        if new_region.geo_location:
            log_info(f"  - Latitude: {new_region.geo_location.latitude}")
            log_info(f"  - Longitude: {new_region.geo_location.longitude}")
        if new_region.address:
            log_info(f"  - Addresses: {', '.join(new_region.address)}")
        log_operation_complete(
            "Comprehensive region creation", f"Region: {new_region.name}"
        )
        return new_region
    except NameNotUniqueError as e:
        log_error(f"Region name conflict", e.message)
        log_info("Try using a different region name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid region data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating region object", str(e))

    return None


def fetch_and_update_region(regions, region_id):
    """
    Fetch a region object by ID and update its coordinates and addresses.
    
    This function demonstrates how to:
    1. Retrieve an existing region object using its ID
    2. Modify object properties (coordinates, addresses)
    3. Submit the updated object back to the SCM API
    
    Args:
        regions: The Region manager instance
        region_id: The UUID of the region object to update
        
    Returns:
        RegionResponseModel: The updated region object, or None if update failed
    """
    logger.info(f"Fetching and updating region object with ID: {region_id}")

    try:
        # Fetch the region
        region = regions.get(region_id)
        logger.info(f"Found region object: {region.name}")

        # Update description
        region.description = f"Updated description for {region.name}"
        logger.info(f"Updated description: {region.description}")
        
        # Add or update tags
        if hasattr(region, 'tag') and region.tag:
            # Add a new tag if not already present
            if "Updated" not in region.tag:
                region.tag.append("Updated")
                logger.info(f"Added new tag: Updated")
        else:
            # Create tag list if none exists
            region.tag = ["Updated", "Modified"]
            logger.info(f"Added new tags: Updated, Modified")
                
        # Update geo_location if exists, create new geo_location if none exists
        if region.geo_location:
            # Slightly adjust coordinates
            new_lat = region.geo_location.latitude + 0.01
            new_long = region.geo_location.longitude + 0.01
            region.geo_location.latitude = new_lat
            region.geo_location.longitude = new_long
            logger.info(f"Updated coordinates to: {new_lat}, {new_long}")
        else:
            # Add geo_location if it doesn't exist
            region.geo_location = {
                "latitude": 51.5074,  # London coordinates
                "longitude": -0.1278
            }
            logger.info(f"Added new coordinates: 51.5074, -0.1278")
        
        # Add or update addresses
        if region.address:
            # Add a new address if not already present
            new_address = "198.18.0.0/15"
            if new_address not in region.address:
                region.address.append(new_address)
                logger.info(f"Added new address: {new_address}")
        else:
            # Create address list if none exists
            region.address = ["198.18.0.0/15", "203.0.113.0/24"]
            logger.info(f"Added new addresses: 198.18.0.0/15, 203.0.113.0/24")

        # Perform the update
        updated_region = regions.update(region)
        logger.info(
            f"Updated region object: {updated_region.name}"
        )
        return updated_region

    except NotFoundError as e:
        logger.error(f"Region object not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid region object update: {e.message}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_regions(regions, folder="Texas"):
    """
    List and filter region objects.
    
    This function demonstrates how to:
    1. List all region objects in a folder
    2. Filter region objects by various criteria
    3. Display detailed information about each object
    
    Args:
        regions: The Region manager instance
        folder: Folder name to list regions from (default: "Texas")
        
    Returns:
        list: All retrieved region objects
    """
    logger.info("Listing and filtering region objects")

    # List all region objects in the folder
    all_regions = regions.list(folder=folder)
    logger.info(f"Found {len(all_regions)} region objects in the {folder} folder")

    # Filter by tag
    try:
        automation_tagged = regions.list(folder=folder, tag=["Automation"])
        logger.info(f"Found {len(automation_tagged)} region objects with 'Automation' tag")
    except Exception as e:
        logger.error(f"Filtering by tag failed: {str(e)}")
    
    # Filter by name pattern (where supported)
    try:
        west_regions = regions.list(folder=folder, name="west")
        logger.info(f"Found {len(west_regions)} region objects with 'west' in the name")
    except Exception as e:
        logger.error(f"Filtering by name failed: {str(e)}")

    # Filter by geographic coordinates
    try:
        # Filter for western hemisphere (longitude < 0)
        western_regions = regions.list(
            folder=folder,
            geo_location={
                "longitude": {"min": -180, "max": 0}
            }
        )
        logger.info(f"Found {len(western_regions)} region objects in the western hemisphere")
    except Exception as e:
        logger.error(f"Filtering by geo_location failed: {str(e)}")

    # Filter by network address
    try:
        # Filter for regions with specific address ranges
        filtered_regions = regions.list(
            folder=folder,
            addresses=["10.0.0.0/8"]
        )
        logger.info(f"Found {len(filtered_regions)} region objects with 10.0.0.0/8 address")
    except Exception as e:
        logger.error(f"Filtering by addresses failed: {str(e)}")

    # Print details of regions
    logger.info("\nDetails of region objects:")
    for region in all_regions[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Region: {region.name}")
        logger.info(f"    ID: {region.id}")
        
        # Print description if available
        description = getattr(region, "description", "None")
        logger.info(f"    Description: {description}")
        
        # Print tags if available
        if hasattr(region, "tag") and region.tag:
            logger.info(f"    Tags: {', '.join(region.tag)}")
        else:
            logger.info(f"    Tags: None")
            
        # Print geographic location if available
        if hasattr(region, "geo_location") and region.geo_location:
            logger.info(f"    Geographic Location: {region.geo_location.latitude}, {region.geo_location.longitude}")
        else:
            logger.info(f"    Geographic Location: None")
            
        # Print addresses if available
        if hasattr(region, "address") and region.address:
            logger.info(f"    Addresses: {', '.join(region.address)}")
        else:
            logger.info(f"    Addresses: None")
            
        logger.info("")

    return all_regions


def cleanup_region_objects(regions, region_ids):
    """
    Delete the region objects created in this example.
    
    Args:
        regions: The Region manager instance
        region_ids: List of region object IDs to delete
    """
    logger.info("Cleaning up region objects")

    for region_id in region_ids:
        try:
            regions.delete(region_id)
            logger.info(f"Deleted region object with ID: {region_id}")
        except NotFoundError as e:
            logger.error(f"Region object not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting region object: {str(e)}")


def create_bulk_region_objects(regions, folder="Texas"):
    """
    Create multiple region objects in a batch.
    
    This function demonstrates creating multiple region objects in a batch,
    which is useful for setting up multiple regions at once.
    
    Args:
        regions: The Region manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created region objects, or empty list if creation failed
    """
    logger.info("Creating a batch of region objects")

    # Define a list of region objects to create
    region_configs = [
        {
            "name": f"eu-west-{uuid.uuid4().hex[:6]}",
            "description": "London region with primary datacenters",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Europe", "DC"],
            "geo_location": {
                "latitude": 51.5074,
                "longitude": -0.1278
            },
            "address": ["198.51.100.0/24"]
        },
        {
            "name": f"eu-central-{uuid.uuid4().hex[:6]}",
            "description": "Berlin region for continental operations",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Europe"],
            "geo_location": {
                "latitude": 52.5200,
                "longitude": 13.4050
            },
            "address": ["203.0.113.0/24"]
        },
        {
            "name": f"asia-east-{uuid.uuid4().hex[:6]}",
            "description": "Tokyo region for APAC operations",
            "folder": folder,
            "tag": ["Automation", "Bulk", "APAC"],
            "geo_location": {
                "latitude": 35.6762,
                "longitude": 139.6503
            },
            "address": ["192.0.2.0/24"]
        }
    ]

    created_regions = []

    # Create each region object
    for region_config in region_configs:
        try:
            new_region = regions.create(region_config)
            logger.info(
                f"Created region object: {new_region.name} with ID: {new_region.id}"
            )
            # Safely access description field
            description = getattr(new_region, "description", None)
            logger.info(f"  - Description: {description}")
            if hasattr(new_region, 'tag') and new_region.tag:
                logger.info(f"  - Tags: {', '.join(new_region.tag)}")
            created_regions.append(new_region.id)
        except Exception as e:
            logger.error(f"Error creating region {region_config['name']}: {str(e)}")

    return created_regions


def generate_region_report(regions, region_ids, execution_time):
    """
    Generate a comprehensive CSV report of all region objects created by the script.
    
    This function fetches detailed information about each region object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        regions: The Region manager instance used to fetch object details
        region_ids: List of region object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"region_objects_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Description",
        "Tags",
        "Latitude", 
        "Longitude",
        "Addresses",
        "Folder",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each region object
    region_data = []
    for idx, region_id in enumerate(region_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(region_ids) - 1:
            log_info(f"Processing region {idx + 1} of {len(region_ids)}")
            
        try:
            # Get the region details
            region = regions.get(region_id)
            
            # Get description if available
            description = region.description if hasattr(region, "description") and region.description else "None"
            
            # Get tags if available
            tags = "None"
            if hasattr(region, "tag") and region.tag:
                tags = ", ".join(region.tag)
            
            # Get latitude and longitude if available
            latitude = "N/A"
            longitude = "N/A"
            if region.geo_location:
                latitude = region.geo_location.latitude
                longitude = region.geo_location.longitude
                
            # Get addresses if available
            addresses = "N/A"
            if region.address:
                addresses = ", ".join(region.address)
            
            # Get created_on timestamp if available
            created_on = "Unknown"
            if hasattr(region, "created_on") and region.created_on:
                created_on = region.created_on.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add region data
            region_data.append([
                region.id,
                region.name,
                description,
                tags,
                latitude,
                longitude,
                addresses,
                region.folder if hasattr(region, "folder") and region.folder else "N/A",
                created_on,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for region ID {region_id}", str(e))
            # Add minimal info for regions that couldn't be retrieved
            region_data.append([
                region_id, 
                "ERROR", 
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
            writer.writerows(region_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(region_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"region_objects_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(region_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the region example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which region object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Region Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created region objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--coordinates", 
        action="store_true",
        help="Create regions with geographic coordinates"
    )
    object_group.add_argument(
        "--addresses", 
        action="store_true", 
        help="Create regions with network addresses"
    )
    object_group.add_argument(
        "--comprehensive", 
        action="store_true",
        help="Create comprehensive regions with both coordinates and addresses"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk region examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all region object types (default behavior)"
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
    Execute the comprehensive set of region object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of region objects (coordinates, addresses, comprehensive)
    4. Update an existing region object to demonstrate modification capabilities
    5. List and filter region objects to show search functionality
    6. Generate a detailed CSV report of all created region objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created region objects (don't delete them)
        --coordinates: Create only regions with geographic coordinates
        --addresses: Create only regions with network addresses
        --comprehensive: Create only comprehensive regions with both coordinates and addresses
        --bulk: Create only bulk region examples
        --all: Create all region object types (default behavior)
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
    create_all = args.all or not (args.coordinates or args.addresses or args.comprehensive or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Region object
        log_section("REGION OBJECT CONFIGURATION")
        log_operation_start("Initializing Region object manager")
        regions = Region(client)
        log_operation_complete("Region object manager initialization")

        # Create various region objects
        created_regions = []

        # Regions with Geographic Coordinates
        if create_all or args.coordinates:
            log_section("GEOGRAPHIC COORDINATES REGIONS")
            log_info("Creating region objects with geographic coordinates")
            log_info(f"Using folder: {folder_name}")

            # Create a region with coordinates
            coord_region = create_region_with_coordinates(regions, folder_name)
            if coord_region:
                created_regions.append(coord_region.id)
                object_count += 1

            log_success(f"Created {len(created_regions)} region objects so far")

        # Regions with Network Addresses
        if create_all or args.addresses:
            log_section("NETWORK ADDRESS REGIONS")
            log_info("Creating region objects with network addresses")
            log_info(f"Using folder: {folder_name}")

            # Create a region with network addresses
            addr_region = create_region_with_addresses(regions, folder_name)
            if addr_region:
                created_regions.append(addr_region.id)
                object_count += 1

            log_success(f"Created region objects with network addresses")

        # Comprehensive Regions
        if create_all or args.comprehensive:
            log_section("COMPREHENSIVE REGIONS")
            log_info("Creating comprehensive region objects")
            log_info(f"Using folder: {folder_name}")

            # Create a comprehensive region
            comp_region = create_comprehensive_region(regions, folder_name)
            if comp_region:
                created_regions.append(comp_region.id)
                object_count += 1

            log_success(f"Created comprehensive region objects")

        # Bulk Region creation
        if create_all or args.bulk:
            log_section("BULK REGION OBJECTS")
            log_info("Creating multiple region objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk region objects
            bulk_region_ids = create_bulk_region_objects(regions, folder_name)
            if bulk_region_ids:
                created_regions.extend(bulk_region_ids)
                object_count += len(bulk_region_ids)
                log_success(f"Created {len(bulk_region_ids)} bulk region objects")

        # Update one of the objects
        if created_regions:
            log_section("UPDATING REGION OBJECTS")
            log_info("Demonstrating how to update existing region objects")
            updated_region = fetch_and_update_region(regions, created_regions[0])

        # List and filter region objects
        log_section("LISTING AND FILTERING REGION OBJECTS")
        log_info("Demonstrating how to search and filter region objects")
        all_regions = list_and_filter_regions(regions, folder_name)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_regions and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating region objects CSV report")
            report_file = generate_region_report(regions, created_regions, execution_time_so_far)
            if report_file:
                log_success(f"Generated region objects report: {report_file}")
                log_info(f"The report contains details of all {len(created_regions)} region objects created")
            else:
                log_error("Failed to generate region objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No region objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_regions)} region objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_regions)} created region objects")
            cleanup_region_objects(regions, created_regions)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total region objects created: {object_count}")
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
        log_info("Note: Some region objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()