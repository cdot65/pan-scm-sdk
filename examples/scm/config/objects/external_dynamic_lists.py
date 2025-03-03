#!/usr/bin/env python3
"""
Comprehensive examples of working with External Dynamic Lists (EDL) in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of External Dynamic List configurations and operations commonly 
used in enterprise networks, including:

1. External Dynamic List Types:
   - IP-based EDLs for IP address lists
   - Domain-based EDLs for domain name lists
   - URL-based EDLs for URL/URI lists
   - Predefined IP/URL EDLs for Palo Alto Networks predefined lists
   - IMSI and IMEI EDLs for mobile network identifiers

2. Update Schedules:
   - Five-minute interval updates for critical lists
   - Hourly updates for standard threat intelligence
   - Daily updates for less frequently changing lists
   - Weekly and monthly updates for slowly changing datasets

3. Authentication Methods:
   - HTTP basic authentication for protected sources
   - Certificate-based authentication

4. Operational examples:
   - Creating various EDL types
   - Searching and filtering EDLs
   - Updating EDL configurations
   - Bulk operations and error handling

5. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with EDL details
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
   - SKIP_CLEANUP=true: Set this to preserve created EDL objects for manual inspection
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
from scm.config.objects import ExternalDynamicLists
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)
from scm.models.objects.external_dynamic_lists import (
    FiveMinuteRecurringModel,
    HourlyRecurringModel,
    DailyRecurringModel,
    WeeklyRecurringModel,
    MonthlyRecurringModel,
    AuthModel,
    IpModel,
    DomainModel,
    UrlTypeModel,  # Changed from UrlModel to UrlTypeModel
    ImsiModel,
    ImeiModel,
    PredefinedIpModel,
    PredefinedUrlModel,
    IpType,
    DomainType,
    UrlType,
    ImsiType,
    ImeiType,
    PredefinedIpType,
    PredefinedUrlType,
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
logger = logging.getLogger("edl_example")


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


def create_ip_edl_hourly(edl_manager, folder="Texas"):
    """
    Create an IP-based External Dynamic List with hourly updates.
    
    This function demonstrates creating an EDL for IP addresses with
    hourly updates, commonly used for moderate-risk threat intelligence
    feeds that change relatively frequently.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating IP-based EDL with hourly updates")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"ip-threat-feed-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the hourly recurring schedule
    hourly_schedule = HourlyRecurringModel(
        hourly={}  # The model expects a dict object for hourly field
    )

    # Create the IP list model
    ip_list = IpModel(
        url="https://www.example.com/threat-feeds/ip-blocklist.txt",
        description="Hourly updated IP threat intelligence feed",
        recurring=hourly_schedule
    )

    # Create the EDL configuration
    ip_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": IpType(ip=ip_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IP External Dynamic List")
    log_info(f"  - Source URL: {ip_list.url}")
    log_info(f"  - Update Schedule: Hourly")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(ip_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: IP list")
        log_operation_complete(
            "IP-based EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def create_domain_edl_daily(edl_manager, folder="Texas"):
    """
    Create a domain-based External Dynamic List with daily updates.
    
    This function demonstrates creating an EDL for domain names with
    daily updates, commonly used for standard threat intelligence
    feeds that change on a daily basis.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating domain-based EDL with daily updates")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"domain-blocklist-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the daily recurring schedule
    daily_schedule = DailyRecurringModel(
        daily={"at": "01"}  # The model expects a nested dict with 'at' field for hour (00-23)
    )

    # Create the domain list model
    domain_list = DomainModel(
        url="https://www.example.com/threat-feeds/domain-blocklist.txt",
        description="Daily updated domain blocklist",
        recurring=daily_schedule,
        expand_domain=True  # Automatically expand subdomains
    )

    # Create the EDL configuration
    domain_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": DomainType(domain=domain_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Domain External Dynamic List")
    log_info(f"  - Source URL: {domain_list.url}")
    log_info(f"  - Update Schedule: Daily at {daily_schedule.daily.at}:00")
    log_info(f"  - Expand Domain: {domain_list.expand_domain}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(domain_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: Domain list")
        log_operation_complete(
            "Domain-based EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def create_url_edl_five_minute(edl_manager, folder="Texas"):
    """
    Create a URL-based External Dynamic List with five-minute updates.
    
    This function demonstrates creating an EDL for URLs with
    five-minute updates, commonly used for high-priority threat
    intelligence feeds that change frequently.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating URL-based EDL with five-minute updates")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"url-malware-feed-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the five-minute recurring schedule
    five_minute_schedule = FiveMinuteRecurringModel(
        five_minute={}  # The model expects a dict object for five_minute field
    )

    # Create the authentication model for protected feed
    auth = AuthModel(
        username="feed_reader",
        password="example_password"
    )

    # Create the URL list model
    url_list = UrlTypeModel(  # Changed from UrlModel to UrlTypeModel
        url="https://www.example.com/threat-feeds/malware-urls.txt",
        description="High-frequency malware URL blocklist",
        recurring=five_minute_schedule,
        certificate_profile="default",  # Required when using auth
        auth=auth  # Use basic authentication
    )

    # Create the EDL configuration
    url_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": UrlType(url=url_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: URL External Dynamic List")
    log_info(f"  - Source URL: {url_list.url}")
    log_info(f"  - Update Schedule: Every five minutes")
    log_info(f"  - Authentication: Basic (username/password) with certificate profile: {url_list.certificate_profile}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(url_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: URL list")
        log_operation_complete(
            "URL-based EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def create_predefined_ip_edl(edl_manager, folder="Texas"):
    """
    Create a predefined IP External Dynamic List.
    
    This function demonstrates creating an EDL using Palo Alto Networks
    predefined IP lists, which are maintained by Palo Alto Networks
    and updated automatically.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating predefined IP EDL")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"panw-ip-blocklist-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the predefined IP list model
    predefined_ip_list = PredefinedIpModel(
        url="panw-bulletproof-ip-list",  # The predefined list name must be provided as url
        description="Palo Alto Networks maintained bulletproof IP blocklist"
    )

    # Create the EDL configuration
    predefined_ip_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": PredefinedIpType(predefined_ip=predefined_ip_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Predefined IP External Dynamic List")
    log_info(f"  - Predefined List: {predefined_ip_list.url}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(predefined_ip_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: Predefined IP list")
        log_operation_complete(
            "Predefined IP EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def create_imsi_edl_weekly(edl_manager, folder="Texas"):
    """
    Create an IMSI-based External Dynamic List with weekly updates.
    
    This function demonstrates creating an EDL for IMSI (International Mobile
    Subscriber Identity) numbers with weekly updates, commonly used for
    mobile network security applications.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating IMSI-based EDL with weekly updates")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"blocked-imsi-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the weekly recurring schedule
    weekly_schedule = WeeklyRecurringModel(
        weekly={
            "day_of_week": "monday",
            "at": "02"  # Update at 2:00 AM each Monday, format is hour only (00-23)
        }
    )

    # Create the IMSI list model
    imsi_list = ImsiModel(
        url="https://www.example.com/mobile/blocked-imsi.txt",
        description="Weekly updated IMSI blocklist",
        recurring=weekly_schedule
    )

    # Create the EDL configuration
    imsi_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": ImsiType(imsi=imsi_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IMSI External Dynamic List")
    log_info(f"  - Source URL: {imsi_list.url}")
    log_info(f"  - Update Schedule: Weekly on {weekly_schedule.weekly.day_of_week} at {weekly_schedule.weekly.at}:00")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(imsi_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: IMSI list")
        log_operation_complete(
            "IMSI-based EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def create_imei_edl_monthly(edl_manager, folder="Texas"):
    """
    Create an IMEI-based External Dynamic List with monthly updates.
    
    This function demonstrates creating an EDL for IMEI (International Mobile
    Equipment Identity) numbers with monthly updates, commonly used for 
    tracking stolen or compromised mobile devices.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ExternalDynamicListsResponseModel: The created EDL object, or None if creation failed
    """
    log_operation_start("Creating IMEI-based EDL with monthly updates")

    # Generate a unique EDL name with UUID to avoid conflicts
    edl_name = f"stolen-imei-{uuid.uuid4().hex[:6]}"
    log_info(f"EDL name: {edl_name}")

    # Create the monthly recurring schedule
    monthly_schedule = MonthlyRecurringModel(
        monthly={
            "day_of_month": 1,
            "at": "03"  # Update at 3:00 AM on the 1st of each month, format is hour only (00-23)
        }
    )

    # Create the IMEI list model
    imei_list = ImeiModel(
        url="https://www.example.com/mobile/stolen-imei.txt",
        description="Monthly updated stolen device IMEI blocklist",
        recurring=monthly_schedule
    )

    # Create the EDL configuration
    imei_edl_config = {
        "name": edl_name,
        "folder": folder,  # Use the provided folder name
        "type": ImeiType(imei=imei_list)
    }

    log_info("Configuration details:")
    log_info(f"  - Type: IMEI External Dynamic List")
    log_info(f"  - Source URL: {imei_list.url}")
    log_info(f"  - Update Schedule: Monthly on day {monthly_schedule.monthly.day_of_month} at {monthly_schedule.monthly.at}:00")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_edl = edl_manager.create(imei_edl_config)
        log_success(f"Created EDL: {new_edl.name}")
        log_info(f"  - Object ID: {new_edl.id}")
        log_info(f"  - Type: IMEI list")
        log_operation_complete(
            "IMEI-based EDL creation", f"EDL: {new_edl.name}"
        )
        return new_edl
    except NameNotUniqueError as e:
        log_error(f"EDL name conflict", e.message)
        log_info("Try using a different EDL name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid EDL data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating EDL", str(e))

    return None


def fetch_and_update_edl(edl_manager, edl_id):
    """
    Fetch an External Dynamic List by ID and update its configuration.
    
    This function demonstrates how to:
    1. Retrieve an existing EDL using its ID
    2. Modify the EDL configuration (description, update frequency, etc.)
    3. Submit the updated EDL back to the SCM API
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        edl_id: The UUID of the EDL to update
        
    Returns:
        ExternalDynamicListsResponseModel: The updated EDL object, or None if update failed
    """
    logger.info(f"Fetching and updating External Dynamic List with ID: {edl_id}")

    try:
        # Fetch the EDL
        edl = edl_manager.get(edl_id)
        logger.info(f"Found EDL: {edl.name}")

        # Determine EDL type and update its configuration
        if hasattr(edl.type, "ip"):
            logger.info("Updating IP-type EDL...")
            # Update the description
            edl.type.ip.description = f"Updated: {edl.type.ip.description}"
            
            # Change to daily updates at 02:00
            edl.type.ip.recurring = DailyRecurringModel(
                daily={"at": "02"}  # Format is hour only (00-23)
            )
            
            update_details = "Changed to daily updates at 02:00"
            
        elif hasattr(edl.type, "domain"):
            logger.info("Updating Domain-type EDL...")
            # Update the description
            edl.type.domain.description = f"Updated: {edl.type.domain.description}"
            
            # Toggle the expand_domain setting
            edl.type.domain.expand_domain = not edl.type.domain.expand_domain
            
            update_details = f"Toggled expand_domain to {edl.type.domain.expand_domain}"
            
        elif hasattr(edl.type, "url"):
            logger.info("Updating URL-type EDL...")
            # Update the description
            edl.type.url.description = f"Updated: {edl.type.url.description}"
            
            # Change to hourly updates
            edl.type.url.recurring = HourlyRecurringModel(
                hourly={}  # The model doesn't support specific minute settings
            )
            
            update_details = "Changed to hourly updates"
            
        else:
            logger.info("This EDL type doesn't require updating in this example")
            update_details = "No updates made for this EDL type"

        # Perform the update
        updated_edl = edl_manager.update(edl)
        logger.info(f"Updated EDL: {updated_edl.name}")
        logger.info(f"Update details: {update_details}")
        return updated_edl

    except NotFoundError as e:
        logger.error(f"EDL not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid EDL update: {e.message}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_edls(edl_manager):
    """
    List and filter External Dynamic List objects.
    
    This function demonstrates how to:
    1. List all EDLs in a folder
    2. Filter EDLs by name pattern
    3. Display detailed information about each EDL
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        
    Returns:
        list: All retrieved EDL objects
    """
    logger.info("Listing and filtering External Dynamic List objects")

    # List all EDLs in the Texas folder
    all_edls = edl_manager.list(folder="Texas")
    logger.info(f"Found {len(all_edls)} EDLs in the Texas folder")

    # Filter by name pattern (if supported)
    try:
        ip_edls = edl_manager.list(folder="Texas", name="ip")
        logger.info(f"Found {len(ip_edls)} EDLs with 'ip' in the name")
    except Exception as e:
        logger.warning(f"Filtering by name is not supported: {str(e)}")

    # Print details of EDLs
    logger.info("\nDetails of External Dynamic List objects:")
    for edl in all_edls[:5]:  # Print details of up to 5 objects
        logger.info(f"  - EDL: {edl.name}")
        logger.info(f"    ID: {edl.id}")
        
        # Determine EDL type and details
        edl_type = "Unknown"
        edl_url = "N/A"
        edl_schedule = "N/A"
        
        if hasattr(edl.type, "ip"):
            edl_type = "IP List"
            edl_url = edl.type.ip.url if hasattr(edl.type.ip, "url") else "N/A"
            # Determine update schedule type
            if hasattr(edl.type.ip, "recurring"):
                if hasattr(edl.type.ip.recurring, "five_minute") and edl.type.ip.recurring.five_minute:
                    edl_schedule = "Every 5 minutes"
                elif hasattr(edl.type.ip.recurring, "hourly") and edl.type.ip.recurring.hourly:
                    edl_schedule = f"Hourly at minute {edl.type.ip.recurring.at}"
                elif hasattr(edl.type.ip.recurring, "daily") and edl.type.ip.recurring.daily:
                    edl_schedule = f"Daily at {edl.type.ip.recurring.at}"
                elif hasattr(edl.type.ip.recurring, "weekly") and edl.type.ip.recurring.weekly:
                    edl_schedule = f"Weekly on {edl.type.ip.recurring.day_of_week} at {edl.type.ip.recurring.at}"
                elif hasattr(edl.type.ip.recurring, "monthly") and edl.type.ip.recurring.monthly:
                    edl_schedule = f"Monthly on day {edl.type.ip.recurring.day_of_month} at {edl.type.ip.recurring.at}"
        
        elif hasattr(edl.type, "domain"):
            edl_type = "Domain List"
            edl_url = edl.type.domain.url if hasattr(edl.type.domain, "url") else "N/A"
            # Extract schedule similar to above
            if hasattr(edl.type.domain, "recurring"):
                if hasattr(edl.type.domain.recurring, "daily") and edl.type.domain.recurring.daily:
                    edl_schedule = f"Daily at {edl.type.domain.recurring.at}"
            # Retrieve expand_domain setting
            expand_domain = edl.type.domain.expand_domain if hasattr(edl.type.domain, "expand_domain") else False
            logger.info(f"    Expand Domain: {expand_domain}")
            
        elif hasattr(edl.type, "url"):
            edl_type = "URL List"
            edl_url = edl.type.url.url if hasattr(edl.type.url, "url") else "N/A"
            # Extract schedule similar to above
            if hasattr(edl.type.url, "recurring") and hasattr(edl.type.url.recurring, "five_minute"):
                edl_schedule = "Every 5 minutes"
                
        elif hasattr(edl.type, "predefined_ip"):
            edl_type = "Predefined IP List"
            predefined_name = edl.type.predefined_ip.name if hasattr(edl.type.predefined_ip, "name") else "Unknown"
            logger.info(f"    Predefined List: {predefined_name}")
            
        elif hasattr(edl.type, "predefined_url"):
            edl_type = "Predefined URL List"
            predefined_name = edl.type.predefined_url.name if hasattr(edl.type.predefined_url, "name") else "Unknown"
            logger.info(f"    Predefined List: {predefined_name}")
            
        elif hasattr(edl.type, "imsi"):
            edl_type = "IMSI List"
            edl_url = edl.type.imsi.url if hasattr(edl.type.imsi, "url") else "N/A"
            # Extract schedule similar to above
            if hasattr(edl.type.imsi, "recurring") and hasattr(edl.type.imsi.recurring, "weekly"):
                edl_schedule = f"Weekly on {edl.type.imsi.recurring.day_of_week} at {edl.type.imsi.recurring.at}"
                
        elif hasattr(edl.type, "imei"):
            edl_type = "IMEI List"
            edl_url = edl.type.imei.url if hasattr(edl.type.imei, "url") else "N/A"
            # Extract schedule similar to above
            if hasattr(edl.type.imei, "recurring") and hasattr(edl.type.imei.recurring, "monthly"):
                edl_schedule = f"Monthly on day {edl.type.imei.recurring.day_of_month} at {edl.type.imei.recurring.at}"
            
        logger.info(f"    Type: {edl_type}")
        logger.info(f"    URL: {edl_url}")
        logger.info(f"    Update Schedule: {edl_schedule}")
        
        # Print folder/container info if available
        if hasattr(edl, "folder") and edl.folder:
            logger.info(f"    Folder: {edl.folder}")
        elif hasattr(edl, "snippet") and edl.snippet:
            logger.info(f"    Snippet: {edl.snippet}")
        elif hasattr(edl, "device") and edl.device:
            logger.info(f"    Device: {edl.device}")
            
        logger.info("")

    return all_edls


def cleanup_edl_objects(edl_manager, edl_ids):
    """
    Delete the External Dynamic List objects created in this example.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        edl_ids: List of EDL object IDs to delete
    """
    logger.info("Cleaning up External Dynamic List objects")

    for edl_id in edl_ids:
        try:
            edl_manager.delete(edl_id)
            logger.info(f"Deleted EDL with ID: {edl_id}")
        except NotFoundError as e:
            logger.error(f"EDL not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting EDL: {str(e)}")


def create_bulk_edl_objects(edl_manager, folder="Texas"):
    """
    Create multiple External Dynamic List objects in a batch.
    
    This function demonstrates creating multiple EDL objects in a batch,
    which is useful for setting up multiple threat intelligence feeds at once.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created EDL objects, or empty list if creation failed
    """
    logger.info("Creating a batch of External Dynamic List objects")

    # Define the daily update schedule used by all EDLs
    daily_schedule = DailyRecurringModel(
        daily={"at": "03"}  # Update at 3:00 AM each day, format is hour only (00-23)
    )

    # Define a list of EDL objects to create
    edl_configs = [
        {
            "name": f"bulk-ip-feed-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "type": IpType(
                ip=IpModel(
                    url="https://www.example.com/bulk/ip-feed1.txt",
                    description="Bulk created IP blocklist 1",
                    recurring=daily_schedule
                )
            )
        },
        {
            "name": f"bulk-ip-feed-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "type": IpType(
                ip=IpModel(
                    url="https://www.example.com/bulk/ip-feed2.txt",
                    description="Bulk created IP blocklist 2",
                    recurring=daily_schedule
                )
            )
        },
        {
            "name": f"bulk-domain-feed-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "type": DomainType(
                domain=DomainModel(
                    url="https://www.example.com/bulk/domain-feed.txt",
                    description="Bulk created domain blocklist",
                    recurring=daily_schedule,
                    expand_domain=True
                )
            )
        },
        {
            "name": f"bulk-url-feed-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "type": UrlType(
                url=UrlTypeModel(  # Changed from UrlModel to UrlTypeModel
                    url="https://www.example.com/bulk/url-feed.txt",
                    description="Bulk created URL blocklist",
                    recurring=daily_schedule,
                    # No auth used here so certificate_profile is not required
                )
            )
        }
    ]

    created_edls = []

    # Create each EDL object
    for edl_config in edl_configs:
        try:
            new_edl = edl_manager.create(edl_config)
            logger.info(
                f"Created EDL: {new_edl.name} with ID: {new_edl.id}"
            )
            created_edls.append(new_edl.id)
        except Exception as e:
            logger.error(f"Error creating EDL {edl_config['name']}: {str(e)}")

    return created_edls


def generate_edl_report(edl_manager, edl_ids, execution_time):
    """
    Generate a comprehensive CSV report of all External Dynamic List objects created by the script.
    
    This function fetches detailed information about each EDL object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        edl_manager: The ExternalDynamicLists manager instance used to fetch object details
        edl_ids: List of EDL object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"external_dynamic_lists_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Type",
        "Source URL",
        "Update Schedule", 
        "Container Type",
        "Container Name",
        "Additional Features",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each EDL object
    edl_data = []
    for idx, edl_id in enumerate(edl_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(edl_ids) - 1:
            log_info(f"Processing External Dynamic List {idx + 1} of {len(edl_ids)}")
            
        try:
            # Get the EDL details
            edl = edl_manager.get(edl_id)
            
            # Determine EDL type, URL, and schedule
            edl_type = "Unknown"
            edl_url = "N/A"
            edl_schedule = "N/A"
            additional_features = "None"
            
            if hasattr(edl.type, "ip"):
                edl_type = "IP List"
                edl_url = edl.type.ip.url if hasattr(edl.type.ip, "url") else "N/A"
                # Extract schedule
                if hasattr(edl.type.ip, "recurring"):
                    if hasattr(edl.type.ip.recurring, "five_minute") and edl.type.ip.recurring.five_minute:
                        edl_schedule = "Every 5 minutes"
                    elif hasattr(edl.type.ip.recurring, "hourly") and edl.type.ip.recurring.hourly:
                        edl_schedule = "Hourly"
                    elif hasattr(edl.type.ip.recurring, "daily") and edl.type.ip.recurring.daily:
                        # Direct attribute access for models rather than dict access
                        at_time = edl.type.ip.recurring.daily.at if hasattr(edl.type.ip.recurring.daily, "at") else "00"
                        edl_schedule = f"Daily at {at_time}:00"
                    elif hasattr(edl.type.ip.recurring, "weekly") and edl.type.ip.recurring.weekly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.ip.recurring.weekly.day_of_week if hasattr(edl.type.ip.recurring.weekly, "day_of_week") else "monday"
                        at_time = edl.type.ip.recurring.weekly.at if hasattr(edl.type.ip.recurring.weekly, "at") else "00"
                        edl_schedule = f"Weekly on {day} at {at_time}:00"
                    elif hasattr(edl.type.ip.recurring, "monthly") and edl.type.ip.recurring.monthly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.ip.recurring.monthly.day_of_month if hasattr(edl.type.ip.recurring.monthly, "day_of_month") else 1
                        at_time = edl.type.ip.recurring.monthly.at if hasattr(edl.type.ip.recurring.monthly, "at") else "00"
                        edl_schedule = f"Monthly on day {day} at {at_time}:00"
            
            elif hasattr(edl.type, "domain"):
                edl_type = "Domain List"
                edl_url = edl.type.domain.url if hasattr(edl.type.domain, "url") else "N/A"
                # Extract schedule
                if hasattr(edl.type.domain, "recurring"):
                    if hasattr(edl.type.domain.recurring, "five_minute") and edl.type.domain.recurring.five_minute:
                        edl_schedule = "Every 5 minutes"
                    elif hasattr(edl.type.domain.recurring, "hourly") and edl.type.domain.recurring.hourly:
                        edl_schedule = "Hourly"
                    elif hasattr(edl.type.domain.recurring, "daily") and edl.type.domain.recurring.daily:
                        # Direct attribute access for models rather than dict access
                        at_time = edl.type.domain.recurring.daily.at if hasattr(edl.type.domain.recurring.daily, "at") else "00"
                        edl_schedule = f"Daily at {at_time}:00"
                    elif hasattr(edl.type.domain.recurring, "weekly") and edl.type.domain.recurring.weekly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.domain.recurring.weekly.day_of_week if hasattr(edl.type.domain.recurring.weekly, "day_of_week") else "monday"
                        at_time = edl.type.domain.recurring.weekly.at if hasattr(edl.type.domain.recurring.weekly, "at") else "00"
                        edl_schedule = f"Weekly on {day} at {at_time}:00"
                    elif hasattr(edl.type.domain.recurring, "monthly") and edl.type.domain.recurring.monthly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.domain.recurring.monthly.day_of_month if hasattr(edl.type.domain.recurring.monthly, "day_of_month") else 1
                        at_time = edl.type.domain.recurring.monthly.at if hasattr(edl.type.domain.recurring.monthly, "at") else "00"
                        edl_schedule = f"Monthly on day {day} at {at_time}:00"
                # Check for expand_domain
                if hasattr(edl.type.domain, "expand_domain") and edl.type.domain.expand_domain:
                    additional_features = "Expand Domain"
                
            elif hasattr(edl.type, "url"):
                edl_type = "URL List"
                edl_url = edl.type.url.url if hasattr(edl.type.url, "url") else "N/A"
                # Extract schedule
                if hasattr(edl.type.url, "recurring"):
                    if hasattr(edl.type.url.recurring, "five_minute") and edl.type.url.recurring.five_minute:
                        edl_schedule = "Every 5 minutes"
                    elif hasattr(edl.type.url.recurring, "hourly") and edl.type.url.recurring.hourly:
                        edl_schedule = "Hourly"
                    elif hasattr(edl.type.url.recurring, "daily") and edl.type.url.recurring.daily:
                        # Direct attribute access for models rather than dict access
                        at_time = edl.type.url.recurring.daily.at if hasattr(edl.type.url.recurring.daily, "at") else "00"
                        edl_schedule = f"Daily at {at_time}:00"
                    elif hasattr(edl.type.url.recurring, "weekly") and edl.type.url.recurring.weekly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.url.recurring.weekly.day_of_week if hasattr(edl.type.url.recurring.weekly, "day_of_week") else "monday"
                        at_time = edl.type.url.recurring.weekly.at if hasattr(edl.type.url.recurring.weekly, "at") else "00"
                        edl_schedule = f"Weekly on {day} at {at_time}:00"
                    elif hasattr(edl.type.url.recurring, "monthly") and edl.type.url.recurring.monthly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.url.recurring.monthly.day_of_month if hasattr(edl.type.url.recurring.monthly, "day_of_month") else 1
                        at_time = edl.type.url.recurring.monthly.at if hasattr(edl.type.url.recurring.monthly, "at") else "00"
                        edl_schedule = f"Monthly on day {day} at {at_time}:00"
                # Check for authentication
                if hasattr(edl.type.url, "auth") and edl.type.url.auth:
                    additional_features = "Basic Authentication"
                    
            elif hasattr(edl.type, "predefined_ip"):
                edl_type = "Predefined IP List"
                edl_url = "Palo Alto Networks maintained"
                predefined_name = edl.type.predefined_ip.url if hasattr(edl.type.predefined_ip, "url") else "Unknown"
                additional_features = f"Predefined: {predefined_name}"
                
            elif hasattr(edl.type, "predefined_url"):
                edl_type = "Predefined URL List"
                edl_url = "Palo Alto Networks maintained"
                predefined_name = edl.type.predefined_url.url if hasattr(edl.type.predefined_url, "url") else "Unknown"
                additional_features = f"Predefined: {predefined_name}"
                
            elif hasattr(edl.type, "imsi"):
                edl_type = "IMSI List"
                edl_url = edl.type.imsi.url if hasattr(edl.type.imsi, "url") else "N/A"
                # Extract schedule
                if hasattr(edl.type.imsi, "recurring"):
                    if hasattr(edl.type.imsi.recurring, "five_minute") and edl.type.imsi.recurring.five_minute:
                        edl_schedule = "Every 5 minutes"
                    elif hasattr(edl.type.imsi.recurring, "hourly") and edl.type.imsi.recurring.hourly:
                        edl_schedule = "Hourly"
                    elif hasattr(edl.type.imsi.recurring, "daily") and edl.type.imsi.recurring.daily:
                        # Direct attribute access for models rather than dict access
                        at_time = edl.type.imsi.recurring.daily.at if hasattr(edl.type.imsi.recurring.daily, "at") else "00"
                        edl_schedule = f"Daily at {at_time}:00"
                    elif hasattr(edl.type.imsi.recurring, "weekly") and edl.type.imsi.recurring.weekly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.imsi.recurring.weekly.day_of_week if hasattr(edl.type.imsi.recurring.weekly, "day_of_week") else "monday"
                        at_time = edl.type.imsi.recurring.weekly.at if hasattr(edl.type.imsi.recurring.weekly, "at") else "00"
                        edl_schedule = f"Weekly on {day} at {at_time}:00"
                    elif hasattr(edl.type.imsi.recurring, "monthly") and edl.type.imsi.recurring.monthly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.imsi.recurring.monthly.day_of_month if hasattr(edl.type.imsi.recurring.monthly, "day_of_month") else 1
                        at_time = edl.type.imsi.recurring.monthly.at if hasattr(edl.type.imsi.recurring.monthly, "at") else "00"
                        edl_schedule = f"Monthly on day {day} at {at_time}:00"
                    
            elif hasattr(edl.type, "imei"):
                edl_type = "IMEI List"
                edl_url = edl.type.imei.url if hasattr(edl.type.imei, "url") else "N/A"
                # Extract schedule
                if hasattr(edl.type.imei, "recurring"):
                    if hasattr(edl.type.imei.recurring, "five_minute") and edl.type.imei.recurring.five_minute:
                        edl_schedule = "Every 5 minutes"
                    elif hasattr(edl.type.imei.recurring, "hourly") and edl.type.imei.recurring.hourly:
                        edl_schedule = "Hourly"
                    elif hasattr(edl.type.imei.recurring, "daily") and edl.type.imei.recurring.daily:
                        # Direct attribute access for models rather than dict access
                        at_time = edl.type.imei.recurring.daily.at if hasattr(edl.type.imei.recurring.daily, "at") else "00"
                        edl_schedule = f"Daily at {at_time}:00"
                    elif hasattr(edl.type.imei.recurring, "weekly") and edl.type.imei.recurring.weekly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.imei.recurring.weekly.day_of_week if hasattr(edl.type.imei.recurring.weekly, "day_of_week") else "monday"
                        at_time = edl.type.imei.recurring.weekly.at if hasattr(edl.type.imei.recurring.weekly, "at") else "00"
                        edl_schedule = f"Weekly on {day} at {at_time}:00"
                    elif hasattr(edl.type.imei.recurring, "monthly") and edl.type.imei.recurring.monthly:
                        # Direct attribute access for models rather than dict access
                        day = edl.type.imei.recurring.monthly.day_of_month if hasattr(edl.type.imei.recurring.monthly, "day_of_month") else 1
                        at_time = edl.type.imei.recurring.monthly.at if hasattr(edl.type.imei.recurring.monthly, "at") else "00"
                        edl_schedule = f"Monthly on day {day} at {at_time}:00"
            
            # Determine container type and name
            container_type = "Unknown"
            container_name = "Unknown"
            
            if hasattr(edl, "folder") and edl.folder:
                container_type = "Folder"
                container_name = edl.folder
            elif hasattr(edl, "snippet") and edl.snippet:
                container_type = "Snippet"
                container_name = edl.snippet
            elif hasattr(edl, "device") and edl.device:
                container_type = "Device"
                container_name = edl.device
                
            # Add EDL data
            edl_data.append([
                edl.id,
                edl.name,
                edl_type,
                edl_url,
                edl_schedule,
                container_type,
                container_name,
                additional_features,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for EDL ID {edl_id}", str(e))
            # Add minimal info for EDLs that couldn't be retrieved
            edl_data.append([
                edl_id, 
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
            writer.writerows(edl_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(edl_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"edl_report_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(edl_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the External Dynamic Lists example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which EDL types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager External Dynamic Lists Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created External Dynamic List objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("EDL Type Selection")
    object_group.add_argument(
        "--ip", 
        action="store_true",
        help="Create IP-based EDL examples"
    )
    object_group.add_argument(
        "--domain", 
        action="store_true", 
        help="Create domain-based EDL examples"
    )
    object_group.add_argument(
        "--url", 
        action="store_true",
        help="Create URL-based EDL examples"
    )
    object_group.add_argument(
        "--predefined", 
        action="store_true",
        help="Create predefined EDL examples"
    )
    object_group.add_argument(
        "--mobile", 
        action="store_true",
        help="Create IMSI and IMEI EDL examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk EDL examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all EDL types (default behavior)"
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
    Execute the comprehensive set of External Dynamic Lists examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of EDLs (IP, domain, URL, predefined, IMSI, IMEI)
    4. Update an existing EDL to demonstrate modification capabilities
    5. List and filter EDLs to show search functionality
    6. Generate a detailed CSV report of all created EDL objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created EDL objects (don't delete them)
        --ip: Create only IP-based EDL examples
        --domain: Create only domain-based EDL examples
        --url: Create only URL-based EDL examples
        --predefined: Create only predefined EDL examples
        --mobile: Create only IMSI and IMEI EDL examples
        --bulk: Create only bulk EDL examples
        --all: Create all EDL types (default behavior)
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
    create_all = args.all or not (args.ip or args.domain or args.url or 
                                args.predefined or args.mobile or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize ExternalDynamicLists object
        log_section("EXTERNAL DYNAMIC LISTS CONFIGURATION")
        log_operation_start("Initializing ExternalDynamicLists object manager")
        edl_manager = ExternalDynamicLists(client)
        log_operation_complete("ExternalDynamicLists object manager initialization")

        # Create various External Dynamic List objects
        created_edls = []

        # IP-based EDLs
        if create_all or args.ip:
            log_section("IP-BASED EXTERNAL DYNAMIC LISTS")
            log_info("Creating IP-based EDL examples")
            log_info(f"Using folder: {folder_name}")

            # Create an IP-based EDL with hourly updates
            ip_edl = create_ip_edl_hourly(edl_manager, folder_name)
            if ip_edl:
                created_edls.append(ip_edl.id)
                object_count += 1

            log_success(f"Created IP-based EDL")

        # Domain-based EDLs
        if create_all or args.domain:
            log_section("DOMAIN-BASED EXTERNAL DYNAMIC LISTS")
            log_info("Creating domain-based EDL examples")
            log_info(f"Using folder: {folder_name}")

            # Create a domain-based EDL with daily updates
            domain_edl = create_domain_edl_daily(edl_manager, folder_name)
            if domain_edl:
                created_edls.append(domain_edl.id)
                object_count += 1

            log_success(f"Created domain-based EDL")

        # URL-based EDLs
        if create_all or args.url:
            log_section("URL-BASED EXTERNAL DYNAMIC LISTS")
            log_info("Creating URL-based EDL examples")
            log_info(f"Using folder: {folder_name}")

            # Create a URL-based EDL with five-minute updates
            url_edl = create_url_edl_five_minute(edl_manager, folder_name)
            if url_edl:
                created_edls.append(url_edl.id)
                object_count += 1

            log_success(f"Created URL-based EDL")

        # Predefined EDLs
        if create_all or args.predefined:
            log_section("PREDEFINED EXTERNAL DYNAMIC LISTS")
            log_info("Creating predefined EDL examples")
            log_info(f"Using folder: {folder_name}")

            # Create a predefined IP EDL
            predefined_edl = create_predefined_ip_edl(edl_manager, folder_name)
            if predefined_edl:
                created_edls.append(predefined_edl.id)
                object_count += 1

            log_success(f"Created predefined EDL")

        # Mobile (IMSI/IMEI) EDLs
        if create_all or args.mobile:
            log_section("MOBILE IDENTIFIER EXTERNAL DYNAMIC LISTS")
            log_info("Creating IMSI and IMEI EDL examples")
            log_info(f"Using folder: {folder_name}")

            # Create an IMSI-based EDL with weekly updates
            imsi_edl = create_imsi_edl_weekly(edl_manager, folder_name)
            if imsi_edl:
                created_edls.append(imsi_edl.id)
                object_count += 1

            # Create an IMEI-based EDL with monthly updates
            imei_edl = create_imei_edl_monthly(edl_manager, folder_name)
            if imei_edl:
                created_edls.append(imei_edl.id)
                object_count += 1

            log_success(f"Created IMSI and IMEI EDLs")

        # Bulk EDL creation
        if create_all or args.bulk:
            log_section("BULK EXTERNAL DYNAMIC LISTS")
            log_info("Creating multiple EDL objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk EDL objects
            bulk_edl_ids = create_bulk_edl_objects(edl_manager, folder_name)
            if bulk_edl_ids:
                created_edls.extend(bulk_edl_ids)
                object_count += len(bulk_edl_ids)
                log_success(f"Created {len(bulk_edl_ids)} bulk EDL objects")

        # Update one of the objects
        if created_edls:
            log_section("UPDATING EXTERNAL DYNAMIC LISTS")
            log_info("Demonstrating how to update existing EDL objects")
            updated_edl = fetch_and_update_edl(edl_manager, created_edls[0])

        # List and filter EDL objects
        log_section("LISTING AND FILTERING EXTERNAL DYNAMIC LISTS")
        log_info("Demonstrating how to search and filter EDL objects")
        all_edls = list_and_filter_edls(edl_manager)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_edls and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating External Dynamic Lists CSV report")
            report_file = generate_edl_report(edl_manager, created_edls, execution_time_so_far)
            if report_file:
                log_success(f"Generated External Dynamic Lists report: {report_file}")
                log_info(f"The report contains details of all {len(created_edls)} EDL objects created")
            else:
                log_error("Failed to generate External Dynamic Lists report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No EDL objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_edls)} EDL objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_edls)} created EDL objects")
            cleanup_edl_objects(edl_manager, created_edls)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total External Dynamic List objects created: {object_count}")
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
        log_info("Note: Some EDL objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()