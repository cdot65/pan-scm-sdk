#!/usr/bin/env python3
"""
Comprehensive examples of working with Service objects in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of Service object configurations and operations commonly 
used in enterprise networks, including:

1. Service Object Types:
   - TCP services with single and multiple ports
   - UDP services with single and multiple ports
   - Services with protocol overrides (timeout, halfclose_timeout, timewait_timeout)

2. Operational examples:
   - Creating service objects
   - Searching and filtering service objects
   - Updating service object configurations
   - Bulk operations and error handling

3. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with service object details
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
   - SKIP_CLEANUP=true: Set this to preserve created service objects for manual inspection
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
from scm.config.objects import Service
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
logger = logging.getLogger("service_example")


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


def create_tcp_single_port_service(services, folder="Texas"):
    """
    Create a service object for a single TCP port.
    
    This function demonstrates creating a standard TCP service with a single port,
    commonly used for web servers and other applications.
    
    Args:
        services: The Service manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceResponseModel: The created service object, or None if creation failed
    """
    log_operation_start("Creating TCP single port service object")

    # Generate a unique service name with timestamp to avoid conflicts
    service_name = f"tcp-http-{uuid.uuid4().hex[:6]}"
    log_info(f"Service name: {service_name}")

    # Create the service configuration
    tcp_single_port_config = {
        "name": service_name,
        "description": "HTTP web server service on port 80",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Web"],
        "protocol": {
            "tcp": {
                "port": "80",
                "override": {
                    "timeout": 60,
                    "halfclose_timeout": 30
                }
            }
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Protocol: TCP")
    log_info(f"  - Port: {tcp_single_port_config['protocol']['tcp']['port']}")
    log_info(f"  - Tags: {', '.join(tcp_single_port_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_service = services.create(tcp_single_port_config)
        log_success(f"Created service object: {new_service.name}")
        log_info(f"  - Object ID: {new_service.id}")
        log_info(f"  - Description: {new_service.description}")
        log_operation_complete(
            "TCP single port service creation", f"Service: {new_service.name}"
        )
        return new_service
    except NameNotUniqueError as e:
        log_error(f"Service name conflict", e.message)
        log_info("Try using a different service name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating service object", str(e))

    return None


def create_tcp_multi_port_service(services, folder="Texas"):
    """
    Create a service object for multiple TCP ports.
    
    This function demonstrates creating a TCP service with multiple ports,
    useful for applications that use several ports (e.g., web services with HTTP and HTTPS).
    
    Args:
        services: The Service manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceResponseModel: The created service object, or None if creation failed
    """
    log_operation_start("Creating TCP multi-port service object")

    # Generate a unique service name with timestamp to avoid conflicts
    service_name = f"tcp-web-{uuid.uuid4().hex[:6]}"
    log_info(f"Service name: {service_name}")

    # Create the service configuration
    tcp_multi_port_config = {
        "name": service_name,
        "description": "Combined HTTP and HTTPS web service",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Web"],
        "protocol": {
            "tcp": {
                "port": "80,443",
                "override": {
                    "timeout": 120,
                    "halfclose_timeout": 60,
                    "timewait_timeout": 15
                }
            }
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Protocol: TCP")
    log_info(f"  - Ports: {tcp_multi_port_config['protocol']['tcp']['port']}")
    log_info(f"  - Tags: {', '.join(tcp_multi_port_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_service = services.create(tcp_multi_port_config)
        log_success(f"Created service object: {new_service.name}")
        log_info(f"  - Object ID: {new_service.id}")
        log_info(f"  - Description: {new_service.description}")
        log_operation_complete(
            "TCP multi-port service creation", f"Service: {new_service.name}"
        )
        return new_service
    except NameNotUniqueError as e:
        log_error(f"Service name conflict", e.message)
        log_info("Try using a different service name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating service object", str(e))

    return None


def create_udp_single_port_service(services, folder="Texas"):
    """
    Create a service object for a single UDP port.
    
    This function demonstrates creating a standard UDP service with a single port,
    typically used for DNS, DHCP, or other UDP-based services.
    
    Args:
        services: The Service manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceResponseModel: The created service object, or None if creation failed
    """
    log_operation_start("Creating UDP single port service object")

    # Generate a unique service name with timestamp to avoid conflicts
    service_name = f"udp-dns-{uuid.uuid4().hex[:6]}"
    log_info(f"Service name: {service_name}")

    # Create the service configuration
    udp_single_port_config = {
        "name": service_name,
        "description": "DNS service on port 53",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "DNS"],
        "protocol": {
            "udp": {
                "port": "53",
                "override": {
                    "timeout": 30
                }
            }
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Protocol: UDP")
    log_info(f"  - Port: {udp_single_port_config['protocol']['udp']['port']}")
    log_info(f"  - Tags: {', '.join(udp_single_port_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_service = services.create(udp_single_port_config)
        log_success(f"Created service object: {new_service.name}")
        log_info(f"  - Object ID: {new_service.id}")
        log_info(f"  - Description: {new_service.description}")
        log_operation_complete(
            "UDP single port service creation", f"Service: {new_service.name}"
        )
        return new_service
    except NameNotUniqueError as e:
        log_error(f"Service name conflict", e.message)
        log_info("Try using a different service name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating service object", str(e))

    return None


def create_udp_multi_port_service(services, folder="Texas"):
    """
    Create a service object for multiple UDP ports.
    
    This function demonstrates creating a UDP service with multiple ports,
    useful for applications that use several UDP ports (e.g., DHCP client and server).
    
    Args:
        services: The Service manager instance
        folder: Folder name in SCM to create the object in (default: "Texas")
        
    Returns:
        ServiceResponseModel: The created service object, or None if creation failed
    """
    log_operation_start("Creating UDP multi-port service object")

    # Generate a unique service name with timestamp to avoid conflicts
    service_name = f"udp-dhcp-{uuid.uuid4().hex[:6]}"
    log_info(f"Service name: {service_name}")

    # Create the service configuration
    udp_multi_port_config = {
        "name": service_name,
        "description": "DHCP client and server ports (67,68)",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "DHCP"],
        "protocol": {
            "udp": {
                "port": "67,68",
                "override": {
                    "timeout": 45
                }
            }
        }
    }

    log_info("Configuration details:")
    log_info(f"  - Protocol: UDP")
    log_info(f"  - Ports: {udp_multi_port_config['protocol']['udp']['port']}")
    log_info(f"  - Tags: {', '.join(udp_multi_port_config['tag'])}")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_service = services.create(udp_multi_port_config)
        log_success(f"Created service object: {new_service.name}")
        log_info(f"  - Object ID: {new_service.id}")
        log_info(f"  - Description: {new_service.description}")
        log_operation_complete(
            "UDP multi-port service creation", f"Service: {new_service.name}"
        )
        return new_service
    except NameNotUniqueError as e:
        log_error(f"Service name conflict", e.message)
        log_info("Try using a different service name or check existing objects")
    except InvalidObjectError as e:
        log_error(f"Invalid service data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error(f"Unexpected error creating service object", str(e))

    return None


def fetch_and_update_service(services, service_id):
    """
    Fetch a service object by ID and update its description, port and tags.
    
    This function demonstrates how to:
    1. Retrieve an existing service object using its ID
    2. Modify object properties (description, ports, tags)
    3. Submit the updated object back to the SCM API
    
    Args:
        services: The Service manager instance
        service_id: The UUID of the service object to update
        
    Returns:
        ServiceResponseModel: The updated service object, or None if update failed
    """
    logger.info(f"Fetching and updating service object with ID: {service_id}")

    try:
        # Fetch the service
        service = services.get(service_id)
        logger.info(f"Found service object: {service.name}")

        # Update description and tags
        service.description = f"Updated description for {service.name}"
        
        # Add additional tags if they don't exist
        if "Updated" not in service.tag:
            service.tag = service.tag + ["Updated"]
        
        # Update port configuration (assuming it's a TCP service for example)
        if hasattr(service.protocol, "tcp") and service.protocol.tcp:
            # If it already has a port range, we'll add a new port
            current_ports = service.protocol.tcp.port
            if "8080" not in current_ports:
                # Add the new port to existing ports
                service.protocol.tcp.port = f"{current_ports},8080"
                logger.info(f"Updated ports to: {service.protocol.tcp.port}")

        # Perform the update
        updated_service = services.update(service)
        logger.info(
            f"Updated service object: {updated_service.name} with description: {updated_service.description}"
        )
        return updated_service

    except NotFoundError as e:
        logger.error(f"Service object not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid service object update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_services(services):
    """
    List and filter service objects.
    
    This function demonstrates how to:
    1. List all service objects in a folder
    2. Filter service objects by various criteria
    3. Display detailed information about each object
    
    Args:
        services: The Service manager instance
        
    Returns:
        list: All retrieved service objects
    """
    logger.info("Listing and filtering service objects")

    # List all service objects in the Texas folder
    all_services = services.list(folder="Texas")
    logger.info(f"Found {len(all_services)} service objects in the Texas folder")

    # Filter by tag
    automation_tagged = services.list(folder="Texas", tags=["Automation"])
    logger.info(f"Found {len(automation_tagged)} service objects with 'Automation' tag")

    # Filter by protocol
    try:
        tcp_services = services.list(folder="Texas", protocols=["tcp"])
        logger.info(f"Found {len(tcp_services)} TCP service objects")
        
        udp_services = services.list(folder="Texas", protocols=["udp"])
        logger.info(f"Found {len(udp_services)} UDP service objects")
    except Exception as e:
        logger.error(f"Filtering by protocol failed: {str(e)}")

    # Print details of services
    logger.info("\nDetails of service objects:")
    for service in all_services[:5]:  # Print details of up to 5 objects
        logger.info(f"  - Service: {service.name}")
        logger.info(f"    ID: {service.id}")
        logger.info(f"    Description: {service.description}")
        logger.info(f"    Tags: {service.tag}")
        
        # Determine service type and ports
        service_type = "Unknown"
        service_ports = "Unknown"
        
        if hasattr(service.protocol, "tcp") and service.protocol.tcp:
            service_type = "TCP"
            service_ports = service.protocol.tcp.port
        elif hasattr(service.protocol, "udp") and service.protocol.udp:
            service_type = "UDP"
            service_ports = service.protocol.udp.port
            
        logger.info(f"    Protocol: {service_type}")
        logger.info(f"    Ports: {service_ports}")
        logger.info("")

    return all_services


def cleanup_service_objects(services, service_ids):
    """
    Delete the service objects created in this example.
    
    Args:
        services: The Service manager instance
        service_ids: List of service object IDs to delete
    """
    logger.info("Cleaning up service objects")

    for service_id in service_ids:
        try:
            services.delete(service_id)
            logger.info(f"Deleted service object with ID: {service_id}")
        except NotFoundError as e:
            logger.error(f"Service object not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting service object: {str(e)}")


def create_bulk_service_objects(services, folder="Texas"):
    """
    Create multiple service objects in a batch.
    
    This function demonstrates creating multiple service objects in a batch,
    which is useful for setting up multiple services at once.
    
    Args:
        services: The Service manager instance
        folder: Folder name in SCM to create objects in (default: "Texas")
        
    Returns:
        list: List of IDs of created service objects, or empty list if creation failed
    """
    logger.info("Creating a batch of service objects")

    # Define a list of service objects to create
    service_configs = [
        {
            "name": f"bulk-ssh-{uuid.uuid4().hex[:6]}",
            "description": "SSH service on port 22",
            "folder": folder,
            "tag": ["Automation", "Bulk", "SSH"],
            "protocol": {
                "tcp": {
                    "port": "22",
                    "override": {
                        "timeout": 60
                    }
                }
            }
        },
        {
            "name": f"bulk-rdp-{uuid.uuid4().hex[:6]}",
            "description": "RDP service on port 3389",
            "folder": folder,
            "tag": ["Automation", "Bulk", "Windows"],
            "protocol": {
                "tcp": {
                    "port": "3389",
                    "override": {
                        "timeout": 120
                    }
                }
            }
        },
        {
            "name": f"bulk-ntp-{uuid.uuid4().hex[:6]}",
            "description": "NTP service on port 123",
            "folder": folder,
            "tag": ["Automation", "Bulk", "NTP"],
            "protocol": {
                "udp": {
                    "port": "123",
                    "override": {
                        "timeout": 30
                    }
                }
            }
        },
        {
            "name": f"bulk-snmp-{uuid.uuid4().hex[:6]}",
            "description": "SNMP service on ports 161,162",
            "folder": folder,
            "tag": ["Automation", "Bulk", "SNMP"],
            "protocol": {
                "udp": {
                    "port": "161,162",
                    "override": {
                        "timeout": 30
                    }
                }
            }
        }
    ]

    created_services = []

    # Create each service object
    for service_config in service_configs:
        try:
            new_service = services.create(service_config)
            logger.info(
                f"Created service object: {new_service.name} with ID: {new_service.id}"
            )
            created_services.append(new_service.id)
        except Exception as e:
            logger.error(f"Error creating service {service_config['name']}: {str(e)}")

    return created_services


def generate_service_report(services, service_ids, execution_time):
    """
    Generate a comprehensive CSV report of all service objects created by the script.
    
    This function fetches detailed information about each service object and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.
    
    Args:
        services: The Service manager instance used to fetch object details
        service_ids: List of service object IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)
    
    Returns:
        str: Path to the generated CSV report file, or None if generation failed
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"service_objects_report_{timestamp}.csv"
    
    # Define CSV headers
    headers = [
        "Object ID", 
        "Name",
        "Protocol", 
        "Ports", 
        "Description", 
        "Tags",
        "Created On",
        "Report Generation Time"
    ]
    
    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0
    
    # Collect data for each service object
    service_data = []
    for idx, service_id in enumerate(service_ids):
        # Show progress for large sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(service_ids) - 1:
            log_info(f"Processing service {idx + 1} of {len(service_ids)}")
            
        try:
            # Get the service details
            service = services.get(service_id)
            
            # Determine service protocol and ports
            protocol = "Unknown"
            ports = "Unknown"
            
            if hasattr(service.protocol, "tcp") and service.protocol.tcp:
                protocol = "TCP"
                ports = service.protocol.tcp.port
            elif hasattr(service.protocol, "udp") and service.protocol.udp:
                protocol = "UDP"
                ports = service.protocol.udp.port
            
            # Add service data
            service_data.append([
                service.id,
                service.name,
                protocol,
                ports,
                service.description if service.description else "None",
                ", ".join(service.tag) if service.tag else "None",
                service.created_on.strftime("%Y-%m-%d %H:%M:%S") if hasattr(service, "created_on") and service.created_on else "Unknown",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            
            successful_fetches += 1
            
        except Exception as e:
            log_error(f"Error getting details for service ID {service_id}", str(e))
            # Add minimal info for services that couldn't be retrieved
            service_data.append([
                service_id, 
                "ERROR", 
                "ERROR", 
                "ERROR",
                f"Failed to retrieve service details: {str(e)}", 
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
            writer.writerows(service_data)
            
            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Objects Processed", len(service_ids)])
            writer.writerow(["Successfully Retrieved", successful_fetches])
            writer.writerow(["Failed to Retrieve", failed_fetches])
            writer.writerow(["Execution Time (so far)", f"{execution_time:.2f} seconds"])
            writer.writerow(["Report Generated On", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return report_file
        
    except Exception as e:
        log_error("Failed to write CSV report file", str(e))
        # Try to write to a different location as fallback
        try:
            fallback_file = f"service_objects_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")
            
            with open(fallback_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(service_data)
            
            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """
    Parse command-line arguments for the service example script.
    
    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created objects
    - Which service object types to create
    - Whether to generate a CSV report
    - Folder name to use for object creation
    
    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager Service Objects Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="Preserve created service objects (don't delete them)"
    )
    
    # Object types to create
    object_group = parser.add_argument_group("Object Type Selection")
    object_group.add_argument(
        "--tcp", 
        action="store_true",
        help="Create TCP service examples"
    )
    object_group.add_argument(
        "--udp", 
        action="store_true", 
        help="Create UDP service examples"
    )
    object_group.add_argument(
        "--bulk", 
        action="store_true",
        help="Create bulk service examples"
    )
    object_group.add_argument(
        "--all", 
        action="store_true",
        help="Create all service object types (default behavior)"
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
    Execute the comprehensive set of service object examples for Strata Cloud Manager.
    
    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of service objects (TCP, UDP)
    4. Update an existing service object to demonstrate modification capabilities
    5. List and filter service objects to show search functionality
    6. Generate a detailed CSV report of all created service objects
    7. Clean up created objects (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information
    
    Command-line Arguments:
        --skip-cleanup: Preserve created service objects (don't delete them)
        --tcp: Create only TCP service examples
        --udp: Create only UDP service examples
        --bulk: Create only bulk service examples
        --all: Create all service object types (default behavior)
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
    create_all = args.all or not (args.tcp or args.udp or args.bulk)
    
    # Get folder name for object creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize Service object
        log_section("SERVICE OBJECT CONFIGURATION")
        log_operation_start("Initializing Service object manager")
        services = Service(client)
        log_operation_complete("Service object manager initialization")

        # Create various service objects
        created_services = []

        # TCP Service objects
        if create_all or args.tcp:
            log_section("TCP SERVICE OBJECTS")
            log_info("Creating common TCP service object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a TCP single port service
            tcp_single_port = create_tcp_single_port_service(services, folder_name)
            if tcp_single_port:
                created_services.append(tcp_single_port.id)
                object_count += 1

            # Create a TCP multi-port service
            tcp_multi_port = create_tcp_multi_port_service(services, folder_name)
            if tcp_multi_port:
                created_services.append(tcp_multi_port.id)
                object_count += 1

            log_success(f"Created {len(created_services)} TCP service objects so far")

        # UDP Service objects
        if create_all or args.udp:
            log_section("UDP SERVICE OBJECTS")
            log_info("Creating common UDP service object patterns")
            log_info(f"Using folder: {folder_name}")

            # Create a UDP single port service
            udp_single_port = create_udp_single_port_service(services, folder_name)
            if udp_single_port:
                created_services.append(udp_single_port.id)
                object_count += 1

            # Create a UDP multi-port service
            udp_multi_port = create_udp_multi_port_service(services, folder_name)
            if udp_multi_port:
                created_services.append(udp_multi_port.id)
                object_count += 1

            log_success(f"Created UDP service objects")

        # Bulk Service object creation
        if create_all or args.bulk:
            log_section("BULK SERVICE OBJECTS")
            log_info("Creating multiple service objects in bulk")
            log_info(f"Using folder: {folder_name}")

            # Create bulk service objects
            bulk_service_ids = create_bulk_service_objects(services, folder_name)
            if bulk_service_ids:
                created_services.extend(bulk_service_ids)
                object_count += len(bulk_service_ids)
                log_success(f"Created {len(bulk_service_ids)} bulk service objects")

        # Update one of the objects
        if created_services:
            log_section("UPDATING SERVICE OBJECTS")
            log_info("Demonstrating how to update existing service objects")
            updated_service = fetch_and_update_service(services, created_services[0])

        # List and filter service objects
        log_section("LISTING AND FILTERING SERVICE OBJECTS")
        log_info("Demonstrating how to search and filter service objects")
        all_services = list_and_filter_services(services)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time
        
        # Generate CSV report before cleanup if there are objects to report and report generation is not disabled
        if created_services and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating service objects CSV report")
            report_file = generate_service_report(services, created_services, execution_time_so_far)
            if report_file:
                log_success(f"Generated service objects report: {report_file}")
                log_info(f"The report contains details of all {len(created_services)} service objects created")
            else:
                log_error("Failed to generate service objects report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No service objects were created, skipping report generation")

        # Clean up the created objects, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_services)} service objects")
            log_info("To clean up these objects, run the script again with SKIP_CLEANUP unset or set to false")
        else:
            log_operation_start(f"Cleaning up {len(created_services)} created service objects")
            cleanup_service_objects(services, created_services)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success(f"Example script completed successfully")
        log_info(f"Total service objects created: {object_count}")
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
        log_info("Note: Some service objects may not have been cleaned up")
    except Exception as e:
        log_error(f"Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()