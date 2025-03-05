#!/usr/bin/env python3
"""
Comprehensive examples of working with Application objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Application object configurations and operations commonly 
used in enterprise networks, including:

1. Application Object Types:
   - Standard business applications
   - Secure applications with custom security attributes
   - High-risk applications
   - Network protocol applications

2. Operational examples:
   - Creating application objects
   - Searching and filtering application objects
   - Updating application object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with application object details
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
   - SKIP_CLEANUP=true: Set this to preserve created application objects for manual inspection
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
from scm.config.objects import Application
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
logger = logging.getLogger("application_example")


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


def create_business_application(applications, folder="Texas"):
    """
    Create a standard business application.
    
    This function demonstrates creating a standard business application,
    commonly used for corporate systems.
    
    Args:
        applications: The Application manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationResponseModel: The created application object, or None if creation failed
    """
    log_operation_start("Creating business application object")

    # Generate a unique application name with timestamp to avoid conflicts
    app_name = f"custom-db-{uuid.uuid4().hex[:6]}"
    log_info(f"Application name: {app_name}")

    # Create the application configuration 
    # Note: ApplicationResponseModel does not include a 'tag' field, so we don't include it here
    business_app_config = {
        "name": app_name,
        "description": "Example custom database application",
        "folder": folder,  # Use the provided folder name
        "category": "business-systems",
        "subcategory": "database",
        "technology": "client-server",
        "risk": 3,
        "ports": ["tcp/1521", "tcp/1525"],
    }

    log_info("Configuration details:")
    log_info(f"  - Category: {business_app_config['category']}")
    log_info(f"  - Subcategory: {business_app_config['subcategory']}")
    log_info(f"  - Technology: {business_app_config['technology']}")
    log_info(f"  - Risk: {business_app_config['risk']}")
    log_info(f"  - Ports: {', '.join(business_app_config['ports'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_app = applications.create(business_app_config)
        log_success(f"Created application object: {new_app.name}")
        log_info(f"  - Object ID: {new_app.id}")
        log_info(f"  - Description: {new_app.description}")
        log_operation_complete(
            "Business application creation", f"Application: {new_app.name}"
        )
        return new_app
    except NameNotUniqueError as e:
        log_error(f"Application name conflict", e.message)
        log_info("Try using a different application name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid application data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application object", str(e))

    return None


def create_secure_application(applications, folder="Texas"):
    """
    Create a secure application with special security attributes.
    
    This function demonstrates creating a secure application with specific security attributes,
    commonly used for secure messaging, VPN, or other trusted applications.
    
    Args:
        applications: The Application manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationResponseModel: The created application object, or None if creation failed
    """
    log_operation_start("Creating secure application object")

    # Generate a unique application name with timestamp to avoid conflicts
    app_name = f"secure-app-{uuid.uuid4().hex[:6]}"
    log_info(f"Application name: {app_name}")

    # Create the application configuration
    # Note: ApplicationResponseModel does not include a 'tag' field, so we don't include it here
    secure_app_config = {
        "name": app_name,
        "description": "Example secure messaging application",
        "folder": folder,  # Use the provided folder name
        "category": "collaboration",
        "subcategory": "instant-messaging",
        "technology": "peer-to-peer",
        "risk": 1,
        "ports": ["tcp/8443"],
        "transfers_files": True,
        "has_known_vulnerabilities": False,
        "evasive": False,
        "pervasive": True,
    }

    log_info("Configuration details:")
    log_info(f"  - Category: {secure_app_config['category']}")
    log_info(f"  - Subcategory: {secure_app_config['subcategory']}")
    log_info(f"  - Technology: {secure_app_config['technology']}")
    log_info(f"  - Risk: {secure_app_config['risk']}")
    log_info(f"  - Ports: {', '.join(secure_app_config['ports'])}")
    log_info(f"  - Transfers files: {secure_app_config['transfers_files']}")
    log_info(f"  - Has known vulnerabilities: {secure_app_config['has_known_vulnerabilities']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_app = applications.create(secure_app_config)
        log_success(f"Created application object: {new_app.name}")
        log_info(f"  - Object ID: {new_app.id}")
        log_info(f"  - Description: {new_app.description}")
        log_operation_complete(
            "Secure application creation", f"Application: {new_app.name}"
        )
        return new_app
    except NameNotUniqueError as e:
        log_error(f"Application name conflict", e.message)
        log_info("Try using a different application name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid application data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application object", str(e))

    return None


def create_high_risk_application(applications, folder="Texas"):
    """
    Create a high-risk application.
    
    This function demonstrates creating a high-risk application,
    which might represent a potentially dangerous or suspicious application.
    
    Args:
        applications: The Application manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationResponseModel: The created application object, or None if creation failed
    """
    log_operation_start("Creating high-risk application object")

    # Generate a unique application name with timestamp to avoid conflicts
    app_name = f"high-risk-app-{uuid.uuid4().hex[:6]}"
    log_info(f"Application name: {app_name}")

    # Create the application configuration
    # Note: ApplicationResponseModel does not include a 'tag' field, so we don't include it here
    risk_app_config = {
        "name": app_name,
        "description": "Example high-risk file sharing application",
        "folder": folder,  # Use the provided folder name
        "category": "general-internet",
        "subcategory": "file-sharing",
        "technology": "peer-to-peer",
        "risk": 5,
        "ports": ["tcp/6881-6889"],
        "transfers_files": True,
        "has_known_vulnerabilities": True,
        "evasive": True,
        "used_by_malware": True,
        "prone_to_misuse": True,
        "no_certifications": True,
    }

    log_info("Configuration details:")
    log_info(f"  - Category: {risk_app_config['category']}")
    log_info(f"  - Subcategory: {risk_app_config['subcategory']}")
    log_info(f"  - Technology: {risk_app_config['technology']}")
    log_info(f"  - Risk: {risk_app_config['risk']} (High)")
    log_info(f"  - Ports: {', '.join(risk_app_config['ports'])}")
    log_info(f"  - Evasive: {risk_app_config['evasive']}")
    log_info(f"  - Used by malware: {risk_app_config['used_by_malware']}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_app = applications.create(risk_app_config)
        log_success(f"Created application object: {new_app.name}")
        log_info(f"  - Object ID: {new_app.id}")
        log_info(f"  - Description: {new_app.description}")
        log_operation_complete(
            "High-risk application creation", f"Application: {new_app.name}"
        )
        return new_app
    except NameNotUniqueError as e:
        log_error(f"Application name conflict", e.message)
        log_info("Try using a different application name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid application data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application object", str(e))

    return None


def create_protocol_application(applications, folder="Texas"):
    """
    Create a network protocol application.
    
    This function demonstrates creating a network protocol application,
    commonly used for specific network protocols not covered by predefined applications.
    
    Args:
        applications: The Application manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ApplicationResponseModel: The created application object, or None if creation failed
    """
    log_operation_start("Creating protocol application object")

    # Generate a unique application name with timestamp to avoid conflicts
    app_name = f"custom-protocol-{uuid.uuid4().hex[:6]}"
    log_info(f"Application name: {app_name}")

    # Create the application configuration
    # Note: ApplicationResponseModel does not include a 'tag' field, so we don't include it here
    protocol_app_config = {
        "name": app_name,
        "description": "Example custom network protocol",
        "folder": folder,  # Use the provided folder name
        "category": "networking",
        "subcategory": "ip-protocol",
        "technology": "client-server",
        "risk": 2,
        "ports": ["tcp/9000", "udp/9000"],
    }

    log_info("Configuration details:")
    log_info(f"  - Category: {protocol_app_config['category']}")
    log_info(f"  - Subcategory: {protocol_app_config['subcategory']}")
    log_info(f"  - Technology: {protocol_app_config['technology']}")
    log_info(f"  - Risk: {protocol_app_config['risk']}")
    log_info(f"  - Ports: {', '.join(protocol_app_config['ports'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_app = applications.create(protocol_app_config)
        log_success(f"Created application object: {new_app.name}")
        log_info(f"  - Object ID: {new_app.id}")
        log_info(f"  - Description: {new_app.description}")
        log_operation_complete(
            "Protocol application creation", f"Application: {new_app.name}"
        )
        return new_app
    except NameNotUniqueError as e:
        log_error(f"Application name conflict", e.message)
        log_info("Try using a different application name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid application data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating application object", str(e))

    return None


def fetch_and_update_application(applications, application_id):
    """
    Fetch an application object by ID and update its description and risk level.
    
    This function demonstrates how to:
    1. Retrieve an existing application object using its ID
    2. Modify object properties (description, risk level)
    3. Submit the updated object back to the SCM API
    
    Args:
        applications: The Application manager instance
        application_id: The UUID of the application object to update
        
    Returns:
        ApplicationResponseModel: The updated application object, or None if update failed
    """
    logger.info(f"Fetching and updating application object with ID: {application_id}")

    try:
        # Fetch the application
        application = applications.get(application_id)
        logger.info(f"Found application object: {application.name}")

        # Update description
        application.description = f"Updated description for {application.name}"
        
        # Update risk level (if applicable)
        if hasattr(application, "risk") and application.risk < 5:
            application.risk += 1
            logger.info(f"Increasing risk level to: {application.risk}")

        # Perform the update
        updated_application = applications.update(application)
        logger.info(
            f"Updated application object: {updated_application.name} with description: {updated_application.description}"
        )
        return updated_application

    except NotFoundError as e:
        logger.error(f"Application object not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid application object update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_applications(applications):
    """
    List and filter application objects.
    
    This function demonstrates how to:
    1. List the applications we just created (by ID)
    2. Filter application objects by various criteria
    3. Display detailed information about each object
    
    Args:
        applications: The Application manager instance
        
    Returns:
        list: Our created application objects
    """
    logger.info("Listing and filtering application objects")

    # Instead of trying to list all applications in the folder,
    # we'll just use the applications we've created and demonstrate filtering in code
    
    # Create a small list of application objects to analyze
    created_apps = []
    
    # For demonstration, pretend we're filtering from a larger set
    logger.info("Demonstrating application filtering (using our created applications)")
    
    try:
        # Create a custom Application instance with small max_limit to avoid timeouts
        applications_limited = Application(applications.api_client, max_limit=5000)
        
        app_ids = []
        # Get applications with small limit to avoid timeouts
        recent_apps = applications_limited.list(folder="Texas", exact_match=True)
        
        # Get the IDs
        for app in recent_apps[:5]:  # Just use the first few
            if hasattr(app, "id"):
                app_ids.append(app.id)
        
        # Show how many we found
        logger.info(f"Found {len(app_ids)} recent applications in folder for analysis")
        
        # Get details for a few applications (up to 3)
        for app_id in app_ids[:3]:
            logger.info(f"Getting details of application with ID: {app_id}")
            try:
                app = applications.get(app_id)
                if app:
                    created_apps.append(app)
                    logger.info(f"Retrieved application: {app.name} ({app.category})")
            except Exception as app_error:
                logger.warning(f"Could not retrieve application {app_id}: {str(app_error)}")
        
    except Exception as e:
        logger.error(f"Error retrieving application details: {str(e)}")
        # If we couldn't get our created apps, we'll just report that and continue
        logger.info("Using only our newly created applications instead")
    
    logger.info(f"Retrieved {len(created_apps)} applications for analysis")
    
    # Demonstrate filtering in code (as if we had retrieved from the API)
    logger.info("\nDemonstrating filtering capabilities:")
    
    # Filter by category
    business_category = [app for app in created_apps if hasattr(app, "category") and app.category == "business-systems"]
    logger.info(f"Found {len(business_category)} business applications")
    
    # Filter by risk level
    high_risk = [app for app in created_apps if hasattr(app, "risk") and app.risk >= 4]
    logger.info(f"Found {len(high_risk)} high-risk applications (risk ≥ 4)")
    
    # Print details of applications
    logger.info("\nDetails of application objects:")
    for app in created_apps[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Application: {app.name}")
        logger.info(f"    ID: {app.id}")
        logger.info(f"    Description: {app.description}")
        logger.info(f"    Category: {app.category}")
        logger.info(f"    Subcategory: {app.subcategory}")
        logger.info(f"    Technology: {app.technology}")
        logger.info(f"    Risk: {app.risk}")
        
        # Show ports if they exist
        if hasattr(app, "ports") and app.ports:
            logger.info(f"    Ports: {', '.join(app.ports)}")
            
        # Show security characteristics
        security_attrs = []
        if hasattr(app, "evasive") and app.evasive:
            security_attrs.append("Evasive")
        if hasattr(app, "pervasive") and app.pervasive:
            security_attrs.append("Pervasive")
        if hasattr(app, "used_by_malware") and app.used_by_malware:
            security_attrs.append("Used by Malware")
        if hasattr(app, "has_known_vulnerabilities") and app.has_known_vulnerabilities:
            security_attrs.append("Has Known Vulnerabilities")
        if hasattr(app, "transfers_files") and app.transfers_files:
            security_attrs.append("Transfers Files")
            
        if security_attrs:
            logger.info(f"    Security Attributes: {', '.join(security_attrs)}")
            
        logger.info("")

    return created_apps


def cleanup_application_objects(applications, application_ids):
    """
    Delete the application objects created in this example.
    
    Args:
        applications: The Application manager instance
        application_ids: List of application object IDs to delete
    """
    logger.info("Cleaning up application objects")

    for application_id in application_ids:
        try:
            applications.delete(application_id)
            logger.info(f"Deleted application object with ID: {application_id}")
        except NotFoundError as e:
            logger.error(f"Application object not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting application object: {str(e)}")


def create_bulk_application_objects(applications, folder="Texas"):
    """
    Create multiple application objects in a batch.
    
    This function demonstrates creating multiple application objects in a batch,
    which is useful for setting up multiple applications at once.
    
    Args:
        applications: The Application manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created application objects, or empty list if creation failed
    """
    logger.info("Creating a batch of application objects")

    # Define a list of application objects to create
    # Note: ApplicationResponseModel does not include a 'tag' field, so we don't include it here
    application_configs = [
        {
            "name": f"bulk-app-1-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created application 1",
            "folder": folder,
            "category": "business-systems",
            "subcategory": "database",
            "technology": "client-server",
            "risk": 2,
            "ports": ["tcp/8080"],
        },
        {
            "name": f"bulk-app-2-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created application 2",
            "folder": folder,
            "category": "collaboration",
            "subcategory": "instant-messaging",
            "technology": "client-server",
            "risk": 3,
            "ports": ["tcp/1935"],
        },
        {
            "name": f"bulk-protocol-{uuid.uuid4().hex[:6]}",
            "description": "Bulk created protocol",
            "folder": folder,
            "category": "networking",
            "subcategory": "ip-protocol",
            "technology": "client-server",
            "risk": 1,
            "ports": ["tcp/12345"],
        }
    ]

    created_applications = []

    # Create each application object
    for app_config in application_configs:
        try:
            new_app = applications.create(app_config)
            logger.info(
                f"Created application object: {new_app.name} with ID: {new_app.id}"
            )
            created_applications.append(new_app.id)
        except Exception as e:
            logger.error(f"Error creating application {app_config['name']}: {str(e)}")

    return created_applications


def generate_application_report(applications, application_ids, execution_time):
    """
    Generate a comprehensive CSV report of all application objects created by the script.
    
    This function fetches detailed information about each application object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        applications: The Application manager instance used to fetch object details
        application_ids: List of application object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"application_objects_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Category",
        "Subcategory", 
        "Technology",
        "Risk",
        "Ports",
        "Description", 
        "Tags",  # Note: Tag field not available in ApplicationResponseModel
        "Security Attributes",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each application object
    application_data = []
    for idx, application_id in enumerate(application_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(application_ids) - 1:
            log_info(f"Processing application {idx + 1} of {len(application_ids)}")
            
        try:
            # Get the application details
            application = applications.get(application_id)
            
            # Determine security attributes
            security_attrs = []
            if hasattr(application, "evasive") and application.evasive:
                security_attrs.append("Evasive")
            if hasattr(application, "pervasive") and application.pervasive:
                security_attrs.append("Pervasive")
            if hasattr(application, "used_by_malware") and application.used_by_malware:
                security_attrs.append("Used by Malware")
            if hasattr(application, "has_known_vulnerabilities") and application.has_known_vulnerabilities:
                security_attrs.append("Has Known Vulnerabilities")
            if hasattr(application, "transfers_files") and application.transfers_files:
                security_attrs.append("Transfers Files")
            if hasattr(application, "tunnels_other_apps") and application.tunnels_other_apps:
                security_attrs.append("Tunnels Other Apps")
            if hasattr(application, "prone_to_misuse") and application.prone_to_misuse:
                security_attrs.append("Prone to Misuse")
            if hasattr(application, "excessive_bandwidth_use") and application.excessive_bandwidth_use:
                security_attrs.append("Excessive Bandwidth Use")
            if hasattr(application, "no_certifications") and application.no_certifications:
                security_attrs.append("No Certifications")
            
            # Add application data
            application_data.append([
                application.id,
                application.name,
                application.category,
                application.subcategory,
                application.technology,
                application.risk,
                ", ".join(application.ports) if hasattr(application, "ports") and application.ports else "None",
                application.description if application.description else "None",
                "None",  # No tag field in ApplicationResponseModel
                ", ".join(security_attrs) if security_attrs else "None",
                application.created_on.strftime("%Y-%m-%d %H:%M:%S") if hasattr(application, "created_on") and application.created_on else "Unknown",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for application ID {application_id}", str(e))
            # Add minimal info for applications that couldn't be retrieved
            application_data.append([
                application_id, 
                "ERROR", 
                "ERROR", 
                "ERROR",
                "ERROR",
                "ERROR",
                "ERROR",
                f"Failed to retrieve application details: {str(e)}", 
                "",
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
            writer.writerows(application_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(application_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"application_objects_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(application_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the application example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which application object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Application Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created application objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--business", 
        action="store_true",
        help="Create business application examples"
    )
    object_group.add_argument(
        "--secure", 
        action="store_true", 
        help="Create secure application examples"
    )
    object_group.add_argument(
        "--high-risk", 
        action="store_true",
        help="Create high-risk application examples"
    )
    object_group.add_argument(
        "--protocol", 
        action="store_true",
        help="Create protocol application examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk application examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all application object types (default behavior)"
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
    Execute the comprehensive set of application object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of application objects (business, secure, high-risk, protocol)
    4. Update an existing application object to demonstrate modification capabilities
    5. List and filter application objects to show search functionality
    6. Generate a detailed CSV report of all created application objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created application objects (don't delete them)
        --business: Create only business application examples
        --secure: Create only secure application examples
        --high-risk: Create only high-risk application examples
        --protocol: Create only protocol application examples
        --bulk: Create only bulk application examples
        --all: Create all application object types (default behavior)
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
    create_all = args.all or not (args.business or args.secure or args.high_risk or args.protocol or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Application object
        log_section("APPLICATION OBJECT CONFIGURATION")
        log_operation_start("Initializing Application object manager")
        applications = Application(client)
        log_operation_complete("Application object manager initialization")

        # Create various application objects
        created_applications = []

        # Business Application objects
        if create_all or args.business:
            log_section("BUSINESS APPLICATION OBJECTS")
            log_info("Creating business application patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a business application
            business_app = create_business_application(applications, folder_name)
            if business_app:
                created_applications.append(business_app.id)
                object_count += 1

            log_success(f"Created business application objects")

        # Secure Application objects
        if create_all or args.secure:
            log_section("SECURE APPLICATION OBJECTS")
            log_info("Creating secure application patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a secure application
            secure_app = create_secure_application(applications, folder_name)
            if secure_app:
                created_applications.append(secure_app.id)
                object_count += 1

            log_success(f"Created secure application objects")

        # High-risk Application objects
        if create_all or args.high_risk:
            log_section("HIGH-RISK APPLICATION OBJECTS")
            log_info("Creating high-risk application patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a high-risk application
            risk_app = create_high_risk_application(applications, folder_name)
            if risk_app:
                created_applications.append(risk_app.id)
                object_count += 1

            log_success(f"Created high-risk application objects")

        # Protocol Application objects
        if create_all or args.protocol:
            log_section("PROTOCOL APPLICATION OBJECTS")
            log_info("Creating protocol application patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a protocol application
            protocol_app = create_protocol_application(applications, folder_name)
            if protocol_app:
                created_applications.append(protocol_app.id)
                object_count += 1

            log_success(f"Created protocol application objects")

        # Bulk Application object creation
        if create_all or args.bulk:
            log_section("BULK APPLICATION OBJECTS")
            log_info("Creating multiple application objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk application objects
            bulk_application_ids = create_bulk_application_objects(applications, folder_name)
            if bulk_application_ids:
                created_applications.extend(bulk_application_ids)
                object_count += len(bulk_application_ids)
                log_success(f"Created {len(bulk_application_ids)} bulk application objects")

        # Update one of the objects
        if created_applications:
            log_section("UPDATING APPLICATION OBJECTS")
            log_info("Demonstrating how to update existing application objects")
            updated_application = fetch_and_update_application(applications, created_applications[0])

        # List and filter application objects
        log_section("LISTING AND FILTERING APPLICATION OBJECTS")
        log_info("Demonstrating how to search and filter application objects")
        all_applications = list_and_filter_applications(applications)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_applications and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating application objects CSV report")
            report_file = generate_application_report(applications, created_applications, execution_time_so_far)
            if report_file:
                log_success(f"Generated application objects report: {report_file}")
                log_info(f"The report contains details of all {len(created_applications)} application objects created")
            else:
                log_error("Failed to generate application objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No application objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_applications)} application objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_applications)} created application objects")
            cleanup_application_objects(applications, created_applications)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total application objects created: {object_count}")
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
        log_info("Note: Some application objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()