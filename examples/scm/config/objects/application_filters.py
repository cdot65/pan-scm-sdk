#!/usr/bin/env python3
"""
Comprehensive examples of working with Application Filters in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Application Filter configurations and operations commonly 
used in enterprise networks, including:

1. Application Filter Types:
   - Category-based filters
   - Technology-based filters
   - Risk-based filters
   - Behavioral-based filters (evasive, used by malware, etc.)
   - SaaS-based filters

2. Operational examples:
   - Creating application filter objects
   - Searching and filtering application filters
   - Updating application filter configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with application filter details
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
   - SKIP_CLEANUP=true: Set this to preserve created application filter objects for manual inspection
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
from scm.config.objects import ApplicationFilters
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
logger = logging.getLogger("application_filters_example")


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


def create_category_filter(app_filters, folder="Texas"):
    """
    Create an application filter based on application categories.
    
    This function demonstrates creating a category-based application filter,
    commonly used to group applications by their primary function.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating category-based application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"category-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration
    category_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "category": ["business-systems", "collaboration"],
        "sub_category": ["management", "video-conferencing"],
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Category Filter")
    log_info(f"  - Categories: {', '.join(category_filter_config['category'])}")
    log_info(f"  - Sub-categories: {', '.join(category_filter_config['sub_category'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(category_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "Category-based application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def create_technology_filter(app_filters, folder="Texas"):
    """
    Create an application filter based on technology characteristics.
    
    This function demonstrates creating a technology-based application filter,
    commonly used to group applications by their underlying technology.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating technology-based application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"tech-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration
    tech_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "technology": ["browser-based", "client-server"],
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Technology Filter")
    log_info(f"  - Technologies: {', '.join(tech_filter_config['technology'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(tech_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "Technology-based application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def create_risk_filter(app_filters, folder="Texas"):
    """
    Create an application filter based on risk levels.
    
    This function demonstrates creating a risk-based application filter,
    commonly used to identify high-risk applications.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating risk-based application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"risk-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration
    risk_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "risk": [4, 5],  # High risk (4) and Critical risk (5) applications
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Risk Filter")
    log_info(f"  - Risk Levels: {', '.join(map(str, risk_filter_config['risk']))}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(risk_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "Risk-based application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def create_behavioral_filter(app_filters, folder="Texas"):
    """
    Create an application filter based on behavioral characteristics.
    
    This function demonstrates creating a behavior-based application filter,
    commonly used to identify applications with specific security concerns.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating behavior-based application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"behavior-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration
    behavior_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "evasive": True,
        "used_by_malware": True,
        "transfers_files": True,
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Behavioral Filter")
    log_info(f"  - Evasive: {behavior_filter_config['evasive']}")
    log_info(f"  - Used by Malware: {behavior_filter_config['used_by_malware']}")
    log_info(f"  - Transfers Files: {behavior_filter_config['transfers_files']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(behavior_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "Behavioral application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def create_saas_filter(app_filters, folder="Texas"):
    """
    Create an application filter for SaaS applications.
    
    This function demonstrates creating a SaaS-based application filter,
    commonly used to identify and manage cloud-based applications.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating SaaS application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"saas-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration
    # Note: Removed invalid saas_certifications field based on error logs
    saas_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "is_saas": True,
        "saas_risk": ["high", "medium"],
        # saas_certifications field removed due to validation errors with the provided values
    }

    log_info("Configuration details:")
    log_info(f"  - Type: SaaS Filter")
    log_info(f"  - Is SaaS: {saas_filter_config['is_saas']}")
    log_info(f"  - SaaS Risk Levels: {', '.join(saas_filter_config['saas_risk'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(saas_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "SaaS application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def create_comprehensive_filter(app_filters, folder="Texas"):
    """
    Create a comprehensive application filter combining multiple criteria.
    
    This function demonstrates creating a complex application filter with 
    multiple criteria types combined, useful for targeted application control.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationFiltersResponseModel: The created filter object, or None if creation failed
    """
    log_operation_start("Creating comprehensive application filter")

    # Generate a unique filter name with UUID to avoid conflicts
    filter_name = f"comprehensive-filter-{uuid.uuid4().hex[:6]}"
    log_info(f"Filter name: {filter_name}")

    # Create the filter configuration with multiple criteria
    comprehensive_filter_config = {
        "name": filter_name,
        "folder": folder,  # Use the provided folder name
        "category": ["collaboration"],
        "technology": ["browser-based"],
        "risk": [3, 4, 5],  # Medium to critical risk
        "is_saas": True,
        "pervasive": True,
    }

    log_info("Configuration details:")
    log_info(f"  - Type: Comprehensive Filter")
    log_info(f"  - Categories: {', '.join(comprehensive_filter_config['category'])}")
    log_info(f"  - Technologies: {', '.join(comprehensive_filter_config['technology'])}")
    log_info(f"  - Risk Levels: {', '.join(map(str, comprehensive_filter_config['risk']))}")
    log_info(f"  - Is SaaS: {comprehensive_filter_config['is_saas']}")
    log_info(f"  - Is Pervasive: {comprehensive_filter_config['pervasive']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_filter = app_filters.create(comprehensive_filter_config)
        log_success(f"Created application filter: {new_filter.name}")
        log_info(f"  - Object ID: {new_filter.id}")
        log_operation_complete(
            "Comprehensive application filter creation", f"Filter: {new_filter.name}"
        )
        return new_filter
    except NameNotUniqueError as e:
        log_error(f"Filter name conflict", e.message)
        log_info("Try using a different filter name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid filter data", e.message)
        if hasattr(e, 'details') and e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application filter", str(e))

    return None


def fetch_and_update_filter(app_filters, filter_id):
    """
    Fetch an application filter by ID and update its properties.
    
    This function demonstrates how to:
    1. Retrieve an existing application filter using its ID
    2. Modify filter properties (e.g., add new category or risk level)
    3. Submit the updated filter back to the SCM API
    
    Args:
        app_filters: The ApplicationFilters manager instance
        filter_id: The UUID of the filter object to update
        
    Returns:
        ApplicationFiltersResponseModel: The updated filter object, or None if update failed
    """
    logger.info(f"Fetching and updating application filter with ID: {filter_id}")

    try:
        # Fetch the filter
        app_filter = app_filters.get(filter_id)
        logger.info(f"Found application filter: {app_filter.name}")

        # Update filter criteria - for example, add an additional category
        if hasattr(app_filter, "category") and app_filter.category:
            if "media" not in app_filter.category:
                app_filter.category = app_filter.category + ["media"]
        else:
            app_filter.category = ["media"]

        # Add an additional risk level if it exists
        if hasattr(app_filter, "risk") and app_filter.risk:
            if 3 not in app_filter.risk:
                app_filter.risk = app_filter.risk + [3]

        # Perform the update
        updated_filter = app_filters.update(app_filter)
        logger.info(f"Updated application filter: {updated_filter.name}")
        if hasattr(updated_filter, "category") and updated_filter.category:
            logger.info(f"Updated categories: {', '.join(updated_filter.category)}")
        if hasattr(updated_filter, "risk") and updated_filter.risk:
            logger.info(f"Updated risk levels: {', '.join(map(str, updated_filter.risk))}")
            
        return updated_filter

    except NotFoundError as e:
        logger.error(f"Application filter not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid application filter update: {e.message}")
        if hasattr(e, 'details') and e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_app_filters(app_filters):
    """
    List and filter application filter objects.
    
    This function demonstrates how to:
    1. List all application filters in a folder
    2. Filter application filters by name pattern
    3. Display detailed information about each filter
    
    Args:
        app_filters: The ApplicationFilters manager instance
        
    Returns:
        list: All retrieved application filter objects
    """
    logger.info("Listing and filtering application filter objects")

    # List all application filters in the Texas folder
    all_filters = app_filters.list(folder="Texas")
    logger.info(f"Found {len(all_filters)} application filters in the Texas folder")

    # Filter by name pattern (if supported)
    try:
        category_filters = app_filters.list(folder="Texas", name="category")
        logger.info(f"Found {len(category_filters)} application filters with 'category' in the name")
    except Exception as e:
        logger.warning(f"Filtering by name is not supported: {str(e)}")

    # Print details of filters
    logger.info("\nDetails of application filter objects:")
    for app_filter in all_filters[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Filter: {app_filter.name}")
        logger.info(f"    ID: {app_filter.id}")
        
        # Print categories if available
        if hasattr(app_filter, "category") and app_filter.category:
            logger.info(f"    Categories: {', '.join(app_filter.category)}")
            
        # Print sub-categories if available
        if hasattr(app_filter, "sub_category") and app_filter.sub_category:
            logger.info(f"    Sub-categories: {', '.join(app_filter.sub_category)}")
            
        # Print technologies if available
        if hasattr(app_filter, "technology") and app_filter.technology:
            logger.info(f"    Technologies: {', '.join(app_filter.technology)}")
            
        # Print risk levels if available
        if hasattr(app_filter, "risk") and app_filter.risk:
            logger.info(f"    Risk Levels: {', '.join(map(str, app_filter.risk))}")
            
        # Print behavioral flags
        for behavior in ["evasive", "used_by_malware", "transfers_files", "has_known_vulnerabilities",
                         "tunnels_other_apps", "prone_to_misuse", "pervasive", "is_saas", "new_appid"]:
            if hasattr(app_filter, behavior) and getattr(app_filter, behavior):
                logger.info(f"    {behavior.replace('_', ' ').title()}: True")
                
        # Print SaaS-specific properties
        if hasattr(app_filter, "saas_risk") and app_filter.saas_risk:
            logger.info(f"    SaaS Risk: {', '.join(app_filter.saas_risk)}")
            
        if hasattr(app_filter, "saas_certifications") and app_filter.saas_certifications:
            logger.info(f"    SaaS Certifications: {', '.join(app_filter.saas_certifications)}")
            
        logger.info("")

    return all_filters


def cleanup_app_filter_objects(app_filters, filter_ids):
    """
    Delete the application filter objects created in this example.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        filter_ids: List of application filter object IDs to delete
    """
    logger.info("Cleaning up application filter objects")

    for filter_id in filter_ids:
        try:
            app_filters.delete(filter_id)
            logger.info(f"Deleted application filter with ID: {filter_id}")
        except NotFoundError as e:
            logger.error(f"Application filter not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting application filter: {str(e)}")


def create_bulk_app_filter_objects(app_filters, folder="Texas"):
    """
    Create multiple application filter objects in a batch.
    
    This function demonstrates creating multiple application filter objects in a batch,
    which is useful for setting up multiple filters at once.
    
    Args:
        app_filters: The ApplicationFilters manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created application filter objects, or empty list if creation failed
    """
    logger.info("Creating a batch of application filter objects")

    # Define a list of application filter objects to create
    filter_configs = [
        {
            "name": f"bulk-category-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "category": ["networking"],
        },
        {
            "name": f"bulk-tech-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "technology": ["client-server"],  # Changed from 'p2p' which was invalid
        },
        {
            "name": f"bulk-risk-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "risk": [5],  # Critical risk only
        },
        {
            "name": f"bulk-behavior-{uuid.uuid4().hex[:6]}",
            "folder": folder,
            "tunnels_other_apps": True,
            "has_known_vulnerabilities": True,
        }
    ]

    created_filters = []

    # Create each application filter object
    for filter_config in filter_configs:
        try:
            new_filter = app_filters.create(filter_config)
            logger.info(
                f"Created application filter: {new_filter.name} with ID: {new_filter.id}"
            )
            created_filters.append(new_filter.id)
        except Exception as e:
            logger.error(f"Error creating filter {filter_config['name']}: {str(e)}")

    return created_filters


def generate_app_filter_report(app_filters, filter_ids, execution_time):
    """
    Generate a comprehensive CSV report of all application filter objects created by the script.
    
    This function fetches detailed information about each application filter object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        app_filters: The ApplicationFilters manager instance used to fetch object details
        filter_ids: List of application filter object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"application_filters_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Categories",
        "Sub-Categories",
        "Technologies",
        "Risk Levels",
        "Behavioral Flags",
        "SaaS Properties",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each application filter object
    filter_data = []
    for idx, filter_id in enumerate(filter_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(filter_ids) - 1:
            log_info(f"Processing application filter {idx + 1} of {len(filter_ids)}")
            
        try:
            # Get the application filter details
            app_filter = app_filters.get(filter_id)
            
            # Collect filter metadata
            categories = ", ".join(app_filter.category) if hasattr(app_filter, "category") and app_filter.category else "None"
            sub_categories = ", ".join(app_filter.sub_category) if hasattr(app_filter, "sub_category") and app_filter.sub_category else "None"
            technologies = ", ".join(app_filter.technology) if hasattr(app_filter, "technology") and app_filter.technology else "None"
            risk_levels = ", ".join(map(str, app_filter.risk)) if hasattr(app_filter, "risk") and app_filter.risk else "None"
            
            # Collect behavioral flags
            behavioral_flags = []
            for behavior in ["evasive", "used_by_malware", "transfers_files", "has_known_vulnerabilities",
                             "tunnels_other_apps", "prone_to_misuse", "pervasive", "is_saas", "new_appid"]:
                if hasattr(app_filter, behavior) and getattr(app_filter, behavior):
                    behavioral_flags.append(behavior.replace('_', ' ').title())
            
            behavioral_flags_str = ", ".join(behavioral_flags) if behavioral_flags else "None"
            
            # Collect SaaS properties
            saas_properties = []
            
            if hasattr(app_filter, "is_saas") and app_filter.is_saas:
                saas_properties.append("Is SaaS")
                
            if hasattr(app_filter, "saas_risk") and app_filter.saas_risk:
                saas_properties.append(f"Risk: {', '.join(app_filter.saas_risk)}")
                
            # Note: saas_certifications field removed as it was causing validation errors
            # Kept for reference in case it becomes supported in the future
            # if hasattr(app_filter, "saas_certifications") and app_filter.saas_certifications:
            #    saas_properties.append(f"Certs: {', '.join(app_filter.saas_certifications)}")
                
            saas_properties_str = "; ".join(saas_properties) if saas_properties else "None"
            
            # Add filter data
            filter_data.append([
                app_filter.id,
                app_filter.name,
                categories,
                sub_categories,
                technologies,
                risk_levels,
                behavioral_flags_str,
                saas_properties_str,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for application filter ID {filter_id}", str(e))
            # Add minimal info for filters that couldn't be retrieved
            filter_data.append([
                filter_id, 
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
            writer.writerows(filter_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(filter_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"app_filters_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(filter_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the application filter example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which application filter types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Application Filters Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created application filter objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Filter Type Selection")
    object_group.add_argument(
        "--category", 
        action="store_true",
        help="Create category-based filter examples"
    )
    object_group.add_argument(
        "--technology", 
        action="store_true", 
        help="Create technology-based filter examples"
    )
    object_group.add_argument(
        "--risk", 
        action="store_true",
        help="Create risk-based filter examples"
    )
    object_group.add_argument(
        "--behavioral", 
        action="store_true",
        help="Create behavioral filter examples"
    )
    object_group.add_argument(
        "--saas", 
        action="store_true",
        help="Create SaaS filter examples"
    )
    object_group.add_argument(
        "--comprehensive", 
        action="store_true",
        help="Create comprehensive filter examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk filter examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all application filter types (default behavior)"
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
    Execute the comprehensive set of application filter examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of application filters (category, technology, risk, behavioral, SaaS)
    4. Update an existing application filter to demonstrate modification capabilities
    5. List and filter application filters to show search functionality
    6. Generate a detailed CSV report of all created application filter objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created application filter objects (don't delete them)
        --category: Create only category-based filter examples
        --technology: Create only technology-based filter examples
        --risk: Create only risk-based filter examples
        --behavioral: Create only behavioral filter examples
        --saas: Create only SaaS filter examples
        --comprehensive: Create only comprehensive filter examples
        --bulk: Create only bulk filter examples
        --all: Create all application filter types (default behavior)
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
    create_all = args.all or not (args.category or args.technology or args.risk or 
                                 args.behavioral or args.saas or args.comprehensive or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize ApplicationFilters object
        log_section("APPLICATION FILTERS CONFIGURATION")
        log_operation_start("Initializing ApplicationFilters object manager")
        app_filters = ApplicationFilters(client)
        log_operation_complete("ApplicationFilters object manager initialization")

        # Create various application filter objects
        created_filters = []

        # Category-based filters
        if create_all or args.category:
            log_section("CATEGORY-BASED FILTERS")
            log_info("Creating category-based application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a category-based filter
            category_filter = create_category_filter(app_filters, folder_name)
            if category_filter:
                created_filters.append(category_filter.id)
                object_count += 1

            log_success(f"Created category-based application filter")

        # Technology-based filters
        if create_all or args.technology:
            log_section("TECHNOLOGY-BASED FILTERS")
            log_info("Creating technology-based application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a technology-based filter
            tech_filter = create_technology_filter(app_filters, folder_name)
            if tech_filter:
                created_filters.append(tech_filter.id)
                object_count += 1

            log_success(f"Created technology-based application filter")

        # Risk-based filters
        if create_all or args.risk:
            log_section("RISK-BASED FILTERS")
            log_info("Creating risk-based application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a risk-based filter
            risk_filter = create_risk_filter(app_filters, folder_name)
            if risk_filter:
                created_filters.append(risk_filter.id)
                object_count += 1

            log_success(f"Created risk-based application filter")

        # Behavioral filters
        if create_all or args.behavioral:
            log_section("BEHAVIORAL FILTERS")
            log_info("Creating behavior-based application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a behavioral filter
            behavior_filter = create_behavioral_filter(app_filters, folder_name)
            if behavior_filter:
                created_filters.append(behavior_filter.id)
                object_count += 1

            log_success(f"Created behavior-based application filter")

        # SaaS filters
        if create_all or args.saas:
            log_section("SAAS FILTERS")
            log_info("Creating SaaS application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a SaaS filter
            saas_filter = create_saas_filter(app_filters, folder_name)
            if saas_filter:
                created_filters.append(saas_filter.id)
                object_count += 1

            log_success(f"Created SaaS application filter")

        # Comprehensive filters
        if create_all or args.comprehensive:
            log_section("COMPREHENSIVE FILTERS")
            log_info("Creating comprehensive application filter patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a comprehensive filter
            comprehensive_filter = create_comprehensive_filter(app_filters, folder_name)
            if comprehensive_filter:
                created_filters.append(comprehensive_filter.id)
                object_count += 1

            log_success(f"Created comprehensive application filter")

        # Bulk filter creation
        if create_all or args.bulk:
            log_section("BULK APPLICATION FILTERS")
            log_info("Creating multiple application filter objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk filter objects
            bulk_filter_ids = create_bulk_app_filter_objects(app_filters, folder_name)
            if bulk_filter_ids:
                created_filters.extend(bulk_filter_ids)
                object_count += len(bulk_filter_ids)
                log_success(f"Created {len(bulk_filter_ids)} bulk application filter objects")

        # Update one of the objects
        if created_filters:
            log_section("UPDATING APPLICATION FILTERS")
            log_info("Demonstrating how to update existing application filter objects")
            updated_filter = fetch_and_update_filter(app_filters, created_filters[0])

        # List and filter application filter objects
        log_section("LISTING AND FILTERING APPLICATION FILTERS")
        log_info("Demonstrating how to search and filter application filter objects")
        all_filters = list_and_filter_app_filters(app_filters)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_filters and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating application filters CSV report")
            report_file = generate_app_filter_report(app_filters, created_filters, execution_time_so_far)
            if report_file:
                log_success(f"Generated application filters report: {report_file}")
                log_info(f"The report contains details of all {len(created_filters)} application filter objects created")
            else:
                log_error("Failed to generate application filters report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No application filter objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_filters)} application filter objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_filters)} created application filter objects")
            cleanup_app_filter_objects(app_filters, created_filters)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total application filter objects created: {object_count}")
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
        log_info("Note: Some application filter objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()