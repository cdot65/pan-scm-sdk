#!/usr/bin/env python3
"""Comprehensive examples of working with NAT rules in Palo Alto Networks' Strata Cloud Manager.

This script demonstrates a wide range of NAT rule configurations and operations commonly
used in enterprise networks, including:

1. Source NAT (SNAT) Configurations:
   - Dynamic IP and Port (PAT/Overloading)
   - Dynamic IP with address pool
   - Dynamic IP with fallback options
   - Static IP translation (1:1 mapping)
   - Interface-based translation

2. Destination NAT (DNAT) Configurations:
   - Port forwarding for web services
   - Multiple-port service publishing
   - Load balancing with different distribution methods
   - Bi-directional NAT (static NAT) and port forwarding (as separate rules)

3. Special NAT Types:
   - DNS64 NAT for DNS64 synthesis
   - NPTv6 for IPv6 prefix translation
   - NAT64 for IPv6-to-IPv4 communication

4. Operational examples:
   - Creating NAT rules with different positions (pre/post)
   - Searching and filtering NAT rules
   - Updating NAT rule configurations
   - Bulk operations and error handling

5. Reporting and Documentation:
   - Detailed CSV report generation
   - Formatted output with color-coded logging
   - Execution statistics and performance metrics

Features:
- Environment-based configuration (.env file support)
- Robust error handling with informative messages
- CSV report generation with rule details
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

3. The examples use security zones "local" and "internet".

4. Any network interface will be a value of either "$eth-local" (owned by the "local" zone)
   or "$eth-internet" (owned by the "internet" zone).

5. All rules use the tags "Automation", "Decrypted", or a combination of both. These are
   the only supported tags in the SCM environment.

6. Optional environment variables:
   - SKIP_CLEANUP=true: Set this to preserve created NAT rules for manual inspection
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
from scm.config.network import NatRule
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)
from scm.models.network import (
    DynamicIpAndPort,
    StaticIp,
    InterfaceAddress,
    DestinationTranslation,
    SourceTranslation,
)
from scm.models.network.nat_rules import BiDirectional

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
logger = logging.getLogger("nat_rule_example")


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


def create_source_nat_rule(nat_rules, folder="Texas"):
    """Create a source NAT rule using dynamic IP and port translation (PAT/overloading).

    This function demonstrates creating the most common type of NAT rule used for outbound
    internet access, where multiple internal IP addresses share a pool of public IPs.
    It shows how to:
    1. Structure the NAT rule configuration using a dictionary
    2. Define the basic properties (name, description, folder, tags)
    3. Configure zones, source, and destination
    4. Set up dynamic IP and port source translation
    5. Handle potential errors during rule creation

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    log_operation_start("Creating source NAT rule with dynamic IP and port (PAT)")

    # Generate a unique rule name with timestamp to avoid conflicts
    rule_name = f"source-nat-example-{uuid.uuid4().hex[:6]}"
    log_info(f"Rule name: {rule_name}")

    # Method 1: Using a dictionary and letting the SDK create models
    source_nat_config = {
        "name": rule_name,
        "description": "Example source NAT rule with dynamic IP and port",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "disabled": False,
        "nat_type": "ipv4",
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["10.0.0.0/24"],
        "destination": ["any"],
        "service": "any",
        "source_translation": {
            "dynamic_ip_and_port": {
                "type": "dynamic_ip_and_port",
                "translated_address": ["192.168.1.100", "192.168.1.101"],
            }
        },
    }

    log_info("Configuration details:")
    log_info("  - Type: Source NAT with dynamic IP and port")
    log_info("  - Source: 10.0.0.0/24 (internal network)")
    log_info("  - Translated addresses: 192.168.1.100, 192.168.1.101 (public IPs)")

    try:
        log_info("Sending request to Strata Cloud Manager API...")
        new_source_nat = nat_rules.create(source_nat_config)
        log_success(f"Created source NAT rule: {new_source_nat.name}")
        log_info(f"  - Rule ID: {new_source_nat.id}")
        log_info("  - Translation: Internal → Public with PAT")
        log_operation_complete("Source NAT rule creation", f"Rule: {new_source_nat.name}")
        return new_source_nat
    except NameNotUniqueError as e:
        log_error("NAT rule name conflict", e.message)
        log_info("Try using a different rule name or check existing rules")
    except InvalidObjectError as e:
        log_error("Invalid NAT rule data", e.message)
        if e.details:
            log_info(f"Error details: {e.details}")
            log_info("Check your configuration values and try again")
    except Exception as e:
        log_error("Unexpected error creating NAT rule", str(e))

    return None


def create_source_nat_rule_with_interface(nat_rules, folder="Texas"):
    """Create a source NAT rule using interface address for translation.

    This function demonstrates creating a NAT rule that uses the interface's IP address
    for translation, which is common for ISP connections with a single public IP.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a source NAT rule with interface address")

    # Method 2: Building the models explicitly
    interface_addr = InterfaceAddress(interface="$eth-internet", ip="192.168.1.1", floating_ip=None)

    dynamic_ip_port = DynamicIpAndPort(
        type="dynamic_ip_and_port", interface_address=interface_addr, translated_address=None
    )

    source_trans = SourceTranslation(
        dynamic_ip_and_port=dynamic_ip_port, dynamic_ip=None, static_ip=None
    )

    source_nat_config = {
        "name": f"source-nat-interface-{uuid.uuid4().hex[:6]}",
        "description": "Example source NAT rule with interface address",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation"],
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["10.0.0.0/24"],
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
    }

    try:
        new_source_nat = nat_rules.create(source_nat_config)
        logger.info(
            f"Created source NAT with interface: {new_source_nat.name} with ID: {new_source_nat.id}"
        )
        return new_source_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_static_nat_rule(nat_rules, folder="Texas"):
    """Create a rule with static IP source translation (1:1 mapping).

    This function demonstrates creating a static NAT rule where a specific internal IP
    is mapped to a specific external IP, often used for servers that need consistent
    external addressing.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a static NAT rule")

    static_ip = StaticIp(
        translated_address="192.168.1.5",
        bi_directional=BiDirectional.YES,  # Must be string "yes" or "no", not boolean
    )

    source_trans = SourceTranslation(static_ip=static_ip, dynamic_ip=None, dynamic_ip_and_port=None)

    static_nat_config = {
        "name": f"static-nat-{uuid.uuid4().hex[:6]}",
        "description": "Example static NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["10.0.0.5/32"],
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
    }

    try:
        new_static_nat = nat_rules.create(static_nat_config)
        logger.info(f"Created static NAT rule: {new_static_nat.name} with ID: {new_static_nat.id}")
        return new_static_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_dynamic_ip_with_fallback(nat_rules, folder="Texas"):
    """Create a NAT rule with dynamic IP source translation and fallback configuration.

    This function demonstrates creating a dynamic IP source NAT rule with fallback options,
    which is useful for ensuring connectivity when the primary IP pool is exhausted.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a dynamic IP NAT rule with fallback")

    # Example using dictionary directly
    dynamic_ip_config = {
        "name": f"dynamic-ip-fallback-{uuid.uuid4().hex[:6]}",
        "description": "Example dynamic IP NAT rule with fallback",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation"],
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["10.0.1.0/24"],
        "destination": ["any"],
        "service": "any",
        "source_translation": {
            "dynamic_ip": {
                "translated_address": [
                    "192.168.2.100",
                    "192.168.2.101",
                    "192.168.2.102",
                ],
                "fallback_type": "translated_address",
                "fallback_address": ["192.168.2.200"],
            }
        },
    }

    try:
        new_dynamic_ip = nat_rules.create(dynamic_ip_config)
        logger.info(
            f"Created dynamic IP NAT rule: {new_dynamic_ip.name} with ID: {new_dynamic_ip.id}"
        )
        return new_dynamic_ip
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_destination_nat_rule(nat_rules, folder="Texas"):
    """Create a destination NAT rule for port forwarding.

    This function demonstrates creating a basic destination NAT rule for port forwarding,
    commonly used for publishing internal services to external networks.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a destination NAT rule")

    # Create destination translation
    dest_trans = DestinationTranslation(
        translated_address="10.0.0.100", translated_port=80, dns_rewrite=None
    )

    dest_nat_config = {
        "name": f"dest-nat-{uuid.uuid4().hex[:6]}",
        "description": "Example destination NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "from_": ["internet"],
        "to_": ["local"],
        "source": ["any"],
        "destination": ["203.0.113.10/32"],  # Public IP
        "service": "any",  # Changed from 'service-http' to 'any' to avoid service reference errors
        "destination_translation": dest_trans.model_dump(exclude_none=True),
    }

    try:
        new_dest_nat = nat_rules.create(dest_nat_config)
        logger.info(f"Created destination NAT rule: {new_dest_nat.name} with ID: {new_dest_nat.id}")
        return new_dest_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_dns64_nat_rule(nat_rules, folder="Texas"):
    """Create a DNS64 NAT rule for IPv6-only clients to access IPv4 resources.

    This function demonstrates creating a DNS64 NAT rule which is used in IPv6 transition
    scenarios to allow IPv6-only clients to access IPv4 resources.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a DNS64 NAT rule")

    # For NAT64 rules, DNS rewrite is not allowed as per API constraints
    dest_trans = DestinationTranslation(
        translated_address="2001:db8::1",
        dns_rewrite=None,
        translated_port=None,
        # Do not include dns_rewrite for NAT64 rules
    )

    dns64_config = {
        "name": f"dns64-nat-{uuid.uuid4().hex[:6]}",
        "description": "Example DNS64 NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "nat_type": "nat64",
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["any"],
        "destination": ["any"],
        "service": "any",
        "destination_translation": dest_trans.model_dump(exclude_none=True),
    }

    try:
        new_dns64_nat = nat_rules.create(dns64_config)
        logger.info(f"Created DNS64 NAT rule: {new_dns64_nat.name} with ID: {new_dns64_nat.id}")
        return new_dns64_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_dynamic_dest_nat_rule(nat_rules, folder="Texas"):
    """Create a dynamic destination NAT rule for load balancing.

    This function demonstrates creating a destination NAT rule that could be used
    for load balancing traffic to multiple internal servers.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a dynamic destination NAT rule for load balancing")

    # Create destination translation for load balancing
    # Note: Distribution is not part of the destination_translation object in the API
    dest_trans = DestinationTranslation(
        translated_address="10.0.0.200", translated_port=8080, dns_rewrite=None
    )

    dynamic_dest_config = {
        "name": f"lb-nat-{uuid.uuid4().hex[:6]}",
        "description": "Example load balancing NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation"],
        "from_": ["internet"],
        "to_": ["local"],
        "source": ["any"],
        "destination": ["203.0.113.20/32"],  # Public IP
        "service": "any",  # Changed from 'service-http' to 'any' to avoid service reference errors
        "destination_translation": dest_trans.model_dump(exclude_none=True),
        # For load balancing, we would typically need to use a different API or parameter
        # Loading balancing configuration would be separate from the NAT rule itself
    }

    try:
        new_dynamic_dest = nat_rules.create(dynamic_dest_config)
        logger.info(
            f"Created dynamic destination NAT rule: {new_dynamic_dest.name} with ID: {new_dynamic_dest.id}"
        )
        return new_dynamic_dest
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def fetch_and_update_nat_rule(nat_rules, rule_id):
    """Fetch a NAT rule by ID and update its description, tags, and translated addresses.

    This function demonstrates how to:
    1. Retrieve an existing NAT rule using its ID
    2. Modify rule properties (description, tags)
    3. Update a specific attribute of the source translation if applicable
    4. Submit the updated rule back to the SCM API

    Args:
        nat_rules: The NAT rule manager instance
        rule_id: The UUID of the NAT rule to update

    Returns:
        NatRuleResponseModel: The updated NAT rule object, or None if update failed

    Note:
        - Only allowed tags ("Automation" and "Decrypted") can be used
        - This example focuses on updating dynamic IP and port translations
    """
    logger.info(f"Fetching and updating NAT rule with ID: {rule_id}")

    try:
        # Fetch the rule
        nat_rule = nat_rules.get(rule_id)
        logger.info(f"Found NAT rule: {nat_rule.name}")

        # Update description and tags
        nat_rule.description = f"Updated description for {nat_rule.name}"
        # Only use the allowed tags: "Automation" or "Decrypted"
        if "Automation" not in nat_rule.tag:
            nat_rule.tag = nat_rule.tag + ["Automation"]

        # For source NAT rules with dynamic IP and port, update the translated addresses
        if nat_rule.source_translation and hasattr(
            nat_rule.source_translation, "dynamic_ip_and_port"
        ):
            if nat_rule.source_translation.dynamic_ip_and_port.translated_address:
                # Add a new address to the translation pool
                original_addresses = (
                    nat_rule.source_translation.dynamic_ip_and_port.translated_address
                )
                nat_rule.source_translation.dynamic_ip_and_port.translated_address = (
                    original_addresses + ["192.168.1.200"]
                )
                logger.info(
                    f"Updating translated addresses to: {nat_rule.source_translation.dynamic_ip_and_port.translated_address}"
                )

        # Perform the update
        updated_rule = nat_rules.update(nat_rule)
        logger.info(
            f"Updated NAT rule: {updated_rule.name} with description: {updated_rule.description}"
        )
        return updated_rule

    except NotFoundError as e:
        logger.error(f"NAT rule not found: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule update: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def list_and_filter_nat_rules(nat_rules):
    """List and filter NAT rules."""
    logger.info("Listing and filtering NAT rules")

    # List all NAT rules in the Texas folder
    all_rules = nat_rules.list(folder="Texas")
    logger.info(f"Found {len(all_rules)} NAT rules in the Texas folder")

    # Filter by tag
    api_tagged_rules = nat_rules.list(folder="Texas", tag=["API"])
    logger.info(f"Found {len(api_tagged_rules)} NAT rules with 'API' tag")

    # Filter by NAT type
    ipv4_rules = nat_rules.list(folder="Texas", nat_type=["ipv4"])
    logger.info(f"Found {len(ipv4_rules)} IPv4 NAT rules")

    # Filter by source zone
    trust_rules = nat_rules.list(folder="Texas", source=["trust"])
    logger.info(f"Found {len(trust_rules)} NAT rules with 'trust' source zone")

    # Filter by destination zone
    untrust_rules = nat_rules.list(folder="Texas", destination=["untrust"])
    logger.info(f"Found {len(untrust_rules)} NAT rules with 'untrust' destination zone")

    # Print details of rules
    logger.info("\nDetails of NAT rules:")
    for rule in all_rules[:5]:  # Print details of up to 5 rules
        logger.info(f"  - Rule: {rule.name}")
        logger.info(f"    ID: {rule.id}")
        logger.info(f"    Description: {rule.description}")
        logger.info(f"    Tags: {rule.tag}")
        logger.info(f"    From: {rule.from_}, To: {rule.to_}")
        logger.info(f"    Source: {rule.source}, Destination: {rule.destination}")
        logger.info("")

    return all_rules


def cleanup_nat_rules(nat_rules, rule_ids):
    """Delete the NAT rules created in this example."""
    logger.info("Cleaning up NAT rules")

    for rule_id in rule_ids:
        try:
            nat_rules.delete(rule_id)
            logger.info(f"Deleted NAT rule with ID: {rule_id}")
        except NotFoundError as e:
            logger.error(f"NAT rule not found: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting NAT rule: {str(e)}")


def create_bidirectional_nat_rule(nat_rules, folder="Texas"):
    """Create a bi-directional NAT rule with static IP translation.

    This function demonstrates creating a bi-directional static NAT rule, which allows
    connections to be initiated from both sides of the NAT (inside to outside and outside to inside).

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a bi-directional NAT rule")

    # Create a static IP translation with bi-directional set to "yes"
    # API doesn't allow both bi-directional source NAT and destination translation in the same rule
    static_ip = StaticIp(translated_address="192.168.10.100", bi_directional=BiDirectional.YES)

    source_trans = SourceTranslation(static_ip=static_ip, dynamic_ip=None, dynamic_ip_and_port=None)

    bidirectional_nat_config = {
        "name": f"bidir-nat-{uuid.uuid4().hex[:6]}",
        "description": "Bi-directional NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["203.0.113.50/32"],  # Public IP for static mapping
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
        # No destination_translation for bi-directional static NAT rules
    }

    try:
        new_bidir_nat = nat_rules.create(bidirectional_nat_config)
        logger.info(
            f"Created bi-directional NAT rule: {new_bidir_nat.name} with ID: {new_bidir_nat.id}"
        )
        return new_bidir_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_multi_port_forwarding_rule(nat_rules, folder="Texas"):
    """Create a destination NAT rule for multiple services (ports).

    This function demonstrates creating a destination NAT rule that could be used
    for forwarding multiple ports to an internal server.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a multi-port forwarding NAT rule")

    # To avoid service reference errors, we use "any" for the service
    # In production, you would need to create the appropriate service objects first
    # and then reference them here

    dest_trans = DestinationTranslation(
        translated_address="10.10.20.150",
        dns_rewrite=None,
        translated_port=None,
        # No port translation here, will use the same ports internally
    )

    multi_port_config = {
        "name": f"multi-port-nat-{uuid.uuid4().hex[:6]}",
        "description": "Multi-port forwarding NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation"],
        "from_": ["internet"],
        "to_": ["local"],
        "source": ["any"],
        "destination": ["203.0.113.100/32"],  # Public IP for service publishing
        "service": "any",  # Using "any" to avoid service reference errors
        "destination_translation": dest_trans.model_dump(exclude_none=True),
    }

    try:
        new_multi_port_nat = nat_rules.create(multi_port_config)
        logger.info(
            f"Created multi-port forwarding NAT rule: {new_multi_port_nat.name} with ID: {new_multi_port_nat.id}"
        )
        return new_multi_port_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_port_forwarding_rule(nat_rules, folder="Texas"):
    """Create a port forwarding NAT rule (destination NAT with port translation).

    This function demonstrates creating a simple port forwarding rule, which is
    a common use case for exposing internal services to external networks.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a port forwarding NAT rule")

    # Only use destination translation for port forwarding, not bidirectional static NAT
    dest_trans = DestinationTranslation(
        translated_address="10.10.10.100", translated_port=8443, dns_rewrite=None
    )

    port_forwarding_config = {
        "name": f"port-forward-{uuid.uuid4().hex[:6]}",
        "description": "Port forwarding NAT rule",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "from_": ["internet"],  # From external zone
        "to_": ["local"],  # To internal zone
        "source": ["any"],
        "destination": ["203.0.113.50/32"],  # Public IP
        "service": "any",
        "destination_translation": dest_trans.model_dump(exclude_none=True),
        # No source_translation for simple port forwarding
    }

    try:
        new_port_forwarding = nat_rules.create(port_forwarding_config)
        logger.info(
            f"Created port forwarding NAT rule: {new_port_forwarding.name} with ID: {new_port_forwarding.id}"
        )
        return new_port_forwarding
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_nptv6_rule(nat_rules, folder="Texas"):
    """Create an NPTv6 NAT rule for IPv6 prefix translation.

    This function demonstrates creating an NPTv6 (Network Prefix Translation for IPv6) rule
    which allows translating IPv6 addresses by changing only the network prefix while
    preserving the interface identifier part of the address.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating an NPTv6 NAT rule")

    # NPTv6 is a 1:1 mapping between IPv6 networks, changing only the network prefix
    static_ip = StaticIp(
        translated_address="2001:db8:2::/64",  # Translated prefix
        bi_directional=BiDirectional.NO,  # String "yes" or "no" is required, not a boolean
    )

    source_trans = SourceTranslation(static_ip=static_ip, dynamic_ip=None, dynamic_ip_and_port=None)

    nptv6_config = {
        "name": f"nptv6-{uuid.uuid4().hex[:6]}",
        "description": "NPTv6 prefix translation",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "nat_type": "nptv6",
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["2001:db8:1::/64"],  # Internal IPv6 prefix
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
    }

    try:
        new_nptv6_nat = nat_rules.create(nptv6_config)
        logger.info(f"Created NPTv6 NAT rule: {new_nptv6_nat.name} with ID: {new_nptv6_nat.id}")
        return new_nptv6_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_outbound_nat_different_interfaces(nat_rules, folder="Texas"):
    """Create a NAT rule that uses different egress interfaces based on traffic.

    This function demonstrates creating an outbound NAT rule that specifies a particular
    egress interface, which is useful for multi-WAN or SD-WAN scenarios.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating an outbound NAT rule with interface selection")

    # Create dynamic IP and port with interface translation
    interface_addr = InterfaceAddress(
        interface="$eth-internet",
        ip="203.0.113.50",  # Primary internet connection
        floating_ip=None,
    )

    dynamic_ip_port = DynamicIpAndPort(
        type="dynamic_ip_and_port", interface_address=interface_addr, translated_address=None
    )

    source_trans = SourceTranslation(
        dynamic_ip_and_port=dynamic_ip_port, dynamic_ip=None, static_ip=None
    )

    outbound_config = {
        "name": f"outbound-primary-{uuid.uuid4().hex[:6]}",
        "description": "Outbound NAT using primary internet connection",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation", "Decrypted"],
        "from_": ["local"],
        "to_": ["internet"],
        "to_interface": "$eth-internet",  # Specify egress interface
        "source": ["10.1.0.0/16"],  # Internal subnet
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
    }

    try:
        new_outbound_nat = nat_rules.create(outbound_config)
        logger.info(
            f"Created outbound NAT rule with interface selection: {new_outbound_nat.name} with ID: {new_outbound_nat.id}"
        )
        return new_outbound_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_post_nat_rule(nat_rules, folder="Texas"):
    """Create a post-rulebase NAT rule.

    This function demonstrates creating a NAT rule in the post-rulebase, which is
    processed after security policy rules (unlike pre-rulebase NAT rules that are
    processed before security policy rules).

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        NatRuleResponseModel: The created NAT rule, or None if creation failed
    """
    logger.info("Creating a post-rulebase NAT rule")

    # Create a dynamic IP and port translation
    dynamic_ip_port = DynamicIpAndPort(
        type="dynamic_ip_and_port", translated_address=["192.168.5.100"], interface_address=None
    )

    source_trans = SourceTranslation(
        dynamic_ip_and_port=dynamic_ip_port, dynamic_ip=None, static_ip=None
    )

    post_nat_config = {
        "name": f"post-nat-{uuid.uuid4().hex[:6]}",
        "description": "Post-rulebase NAT rule example",
        "folder": folder,  # Use the provided folder name
        "tag": ["Automation"],
        "from_": ["local"],
        "to_": ["internet"],
        "source": ["10.5.0.0/24"],
        "destination": ["any"],
        "service": "any",
        "source_translation": source_trans.model_dump(exclude_none=True),
    }

    try:
        # Note the position="post" parameter for post-rulebase rules
        new_post_nat = nat_rules.create(post_nat_config, position="post")
        logger.info(
            f"Created post-rulebase NAT rule: {new_post_nat.name} with ID: {new_post_nat.id}"
        )
        return new_post_nat
    except NameNotUniqueError as e:
        logger.error(f"NAT rule name conflict: {e.message}")
    except InvalidObjectError as e:
        logger.error(f"Invalid NAT rule data: {e.message}")
        if e.details:
            logger.error(f"Details: {e.details}")

    return None


def create_bulk_nat_rules(nat_rules, folder="Texas"):
    """Create multiple NAT rules in a batch for similar services.

    This function demonstrates creating multiple similar NAT rules in a batch,
    which is useful for setting up port forwarding for multiple services.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        list: List of IDs of created NAT rules, or empty list if creation failed
    """
    logger.info("Creating a batch of NAT rules for different services")

    # Web server ports to forward
    services = [
        {"name": "HTTP", "service": "any", "port": 80},
        {"name": "HTTPS", "service": "any", "port": 443},
        {"name": "SSH", "service": "any", "port": 22},
        {"name": "FTP", "service": "any", "port": 21},
    ]

    created_rules = []

    # Create a destination NAT rule for each service
    for service_info in services:
        dest_trans = DestinationTranslation(
            translated_address="10.50.10.100",
            translated_port=service_info["port"],
            dns_rewrite=None,
        )

        nat_config = {
            "name": f"dnat-{service_info['name'].lower()}-{uuid.uuid4().hex[:6]}",
            "description": f"Port forwarding for {service_info['name']} service",
            "folder": folder,  # Use the provided folder name
            "tag": ["Automation", "Decrypted"],
            "from_": ["internet"],
            "to_": ["local"],
            "source": ["any"],
            "destination": ["203.0.113.200/32"],  # Public IP for service publishing
            "service": service_info["service"],
            "destination_translation": dest_trans.model_dump(exclude_none=True),
        }

        try:
            new_nat = nat_rules.create(nat_config)
            logger.info(
                f"Created {service_info['name']} forwarding NAT rule: {new_nat.name} with ID: {new_nat.id}"
            )
            created_rules.append(new_nat.id)
        except Exception as e:
            logger.error(f"Error creating {service_info['name']} NAT rule: {str(e)}")

    return created_rules


def create_nat_rules_for_multiple_sites(nat_rules, folder="Texas"):
    """Create NAT rules for multiple branch sites.

    This function demonstrates creating NAT rules for multiple branch sites,
    which is a common use case in enterprise networks with multiple locations.

    Args:
        nat_rules: The NAT rule manager instance
        folder: Folder name in SCM to create the rule in (default: "Texas")

    Returns:
        list: List of IDs of created NAT rules, or empty list if creation failed
    """
    logger.info("Creating NAT rules for multiple branch sites")

    # Branch site definitions
    branch_sites = [
        {
            "name": "New York",
            "internal_subnet": "10.100.1.0/24",
            "external_ip": "203.0.113.10",
        },
        {
            "name": "Chicago",
            "internal_subnet": "10.100.2.0/24",
            "external_ip": "203.0.113.11",
        },
        {
            "name": "Los Angeles",
            "internal_subnet": "10.100.3.0/24",
            "external_ip": "203.0.113.12",
        },
    ]

    created_rules = []

    # Create an outbound NAT rule for each branch site
    for site in branch_sites:
        # Dynamic IP and port translation for outbound traffic
        dynamic_ip_port = DynamicIpAndPort(
            type="dynamic_ip_and_port",
            translated_address=[site["external_ip"]],
            interface_address=None,
        )

        source_trans = SourceTranslation(
            dynamic_ip_and_port=dynamic_ip_port, dynamic_ip=None, static_ip=None
        )

        site_nat_config = {
            "name": f"outbound-{site['name'].lower().replace(' ', '-')}-{uuid.uuid4().hex[:6]}",
            "description": f"Outbound NAT for {site['name']} branch",
            "folder": folder,  # Use the provided folder name
            "tag": ["Automation"],
            "from_": ["local"],
            "to_": ["internet"],
            "source": [site["internal_subnet"]],
            "destination": ["any"],
            "service": "any",
            "source_translation": source_trans.model_dump(exclude_none=True),
        }

        try:
            new_site_nat = nat_rules.create(site_nat_config)
            logger.info(
                f"Created outbound NAT for {site['name']}: {new_site_nat.name} with ID: {new_site_nat.id}"
            )
            created_rules.append(new_site_nat.id)
        except Exception as e:
            logger.error(f"Error creating NAT rule for {site['name']}: {str(e)}")

    return created_rules


def generate_nat_rule_report(nat_rules, rule_ids, execution_time):
    """Generate a comprehensive CSV report of all NAT rules created by the script.

    This function fetches detailed information about each NAT rule and writes it to a
    CSV file with a timestamp in the filename. It provides progress updates during
    processing and includes a summary section with execution statistics.

    The report includes:
    - Rule identifiers (ID, name, type)
    - Configuration details (zones, source, destination)
    - Translation information (source and destination translations)
    - Tags and timestamps
    - Summary statistics (total rules, success/failure counts, execution time)

    Args:
        nat_rules: The NAT rule manager instance used to fetch rule details
        rule_ids: List of NAT rule IDs to include in the report
        execution_time: Total execution time in seconds (up to the point of report generation)

    Returns:
        str: Path to the generated CSV report file, or None if generation failed

    Raises:
        No exceptions are raised directly; errors are logged and handled internally
    """
    # Create a timestamp for the filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"nat_rules_report_{timestamp}.csv"

    # Define CSV headers
    headers = [
        "Rule ID",
        "Name",
        "Type",
        "Description",
        "Source Zone",
        "Destination Zone",
        "Source",
        "Destination",
        "Source Translation",
        "Destination Translation",
        "Tags",
        "Report Generation Time",
    ]

    # Stats for report summary
    successful_fetches = 0
    failed_fetches = 0

    # Collect data for each rule
    rule_data = []
    for idx, rule_id in enumerate(rule_ids):
        # Show progress for large rule sets
        if (idx + 1) % 5 == 0 or idx == 0 or idx == len(rule_ids) - 1:
            log_info(f"Processing rule {idx + 1} of {len(rule_ids)}")

        try:
            # Get the rule details
            rule = nat_rules.get(rule_id)

            # Determine source translation type
            source_trans_type = "None"
            if rule.source_translation:
                if (
                    hasattr(rule.source_translation, "dynamic_ip_and_port")
                    and rule.source_translation.dynamic_ip_and_port
                ):
                    source_trans_type = "Dynamic IP and Port"
                    if (
                        hasattr(rule.source_translation.dynamic_ip_and_port, "translated_address")
                        and rule.source_translation.dynamic_ip_and_port.translated_address
                    ):
                        translated_addresses = ", ".join(
                            rule.source_translation.dynamic_ip_and_port.translated_address
                        )
                        source_trans_type += f" ({translated_addresses})"
                    elif (
                        hasattr(rule.source_translation.dynamic_ip_and_port, "interface_address")
                        and rule.source_translation.dynamic_ip_and_port.interface_address
                    ):
                        interface = (
                            rule.source_translation.dynamic_ip_and_port.interface_address.interface
                        )
                        source_trans_type += f" (Interface: {interface})"
                elif (
                    hasattr(rule.source_translation, "dynamic_ip")
                    and rule.source_translation.dynamic_ip
                ):
                    source_trans_type = "Dynamic IP"
                    if (
                        hasattr(rule.source_translation.dynamic_ip, "translated_address")
                        and rule.source_translation.dynamic_ip.translated_address
                    ):
                        translated_addresses = ", ".join(
                            rule.source_translation.dynamic_ip.translated_address
                        )
                        source_trans_type += f" ({translated_addresses})"
                elif (
                    hasattr(rule.source_translation, "static_ip")
                    and rule.source_translation.static_ip
                ):
                    bi_dir = ""
                    if (
                        hasattr(rule.source_translation.static_ip, "bi_directional")
                        and rule.source_translation.static_ip.bi_directional == "yes"
                    ):
                        bi_dir = ", Bi-directional"
                    trans_addr = rule.source_translation.static_ip.translated_address
                    source_trans_type = f"Static IP ({trans_addr}{bi_dir})"

            # Determine destination translation type
            dest_trans_type = "None"
            if rule.destination_translation:
                if rule.destination_translation.translated_address:
                    if rule.destination_translation.translated_port:
                        dest_trans_type = f"Address ({rule.destination_translation.translated_address}) and Port ({rule.destination_translation.translated_port})"
                    else:
                        dest_trans_type = (
                            f"Address ({rule.destination_translation.translated_address})"
                        )

            # Add rule data
            rule_data.append(
                [
                    rule.id,
                    rule.name,
                    rule.nat_type,
                    rule.description if rule.description else "None",
                    ", ".join(rule.from_),
                    ", ".join(rule.to_),
                    ", ".join(rule.source),
                    ", ".join(rule.destination),
                    source_trans_type,
                    dest_trans_type,
                    ", ".join(rule.tag) if rule.tag else "None",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
            )

            successful_fetches += 1

        except Exception as e:
            log_error(f"Error getting details for rule ID {rule_id}", str(e))
            # Add minimal info for rules that couldn't be retrieved
            rule_data.append(
                [
                    rule_id,
                    "ERROR",
                    "ERROR",
                    f"Failed to retrieve rule details: {str(e)}",
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
            writer.writerows(rule_data)

            # Add summary section
            writer.writerow([])
            writer.writerow(["SUMMARY"])
            writer.writerow(["Total Rules Processed", len(rule_ids)])
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
            fallback_file = f"nat_rules_{timestamp}.csv"
            log_info(f"Attempting to write to fallback location: {fallback_file}")

            with open(fallback_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(rule_data)

            return fallback_file
        except Exception as fallback_error:
            log_error("Failed to write to fallback location", str(fallback_error))
            return None


def parse_arguments():
    """Parse command-line arguments for the NAT rule example script.

    This function sets up the argument parser with various options to customize
    the script's behavior at runtime, including:
    - Whether to skip cleanup of created rules
    - Which NAT rule types to create
    - Whether to generate a CSV report
    - Folder name to use for rule creation

    Returns:
        argparse.Namespace: The parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Strata Cloud Manager NAT Rules Example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Cleanup behavior
    parser.add_argument(
        "--skip-cleanup", action="store_true", help="Preserve created NAT rules (don't delete them)"
    )

    # Rule types to create
    rule_group = parser.add_argument_group("Rule Type Selection")
    rule_group.add_argument("--source-nat", action="store_true", help="Create source NAT examples")
    rule_group.add_argument(
        "--dest-nat", action="store_true", help="Create destination NAT examples"
    )
    rule_group.add_argument(
        "--special-nat",
        action="store_true",
        help="Create special NAT examples (DNS64, NPTv6, etc.)",
    )
    rule_group.add_argument("--bulk-nat", action="store_true", help="Create bulk NAT examples")
    rule_group.add_argument(
        "--all", action="store_true", help="Create all NAT rule types (default behavior)"
    )

    # Reporting
    parser.add_argument("--no-report", action="store_true", help="Skip CSV report generation")

    # Folder
    parser.add_argument(
        "--folder", type=str, default="Texas", help="Folder name in SCM to create rules in"
    )

    return parser.parse_args()


def main():
    """Execute the comprehensive set of NAT rule examples for Strata Cloud Manager.

    This is the main entry point for the script that orchestrates the following workflow:
    1. Parse command-line arguments to customize execution
    2. Initialize the SCM client with credentials from environment variables or .env file
    3. Create various types of NAT rules (source NAT, destination NAT, special types)
    4. Update an existing NAT rule to demonstrate modification capabilities
    5. List and filter NAT rules to show search functionality
    6. Generate a detailed CSV report of all created NAT rules
    7. Clean up created rules (unless skip_cleanup is enabled)
    8. Display execution statistics and summary information

    Command-line Arguments:
        --skip-cleanup: Preserve created NAT rules (don't delete them)
        --source-nat: Create only source NAT examples
        --dest-nat: Create only destination NAT examples
        --special-nat: Create only special NAT examples
        --bulk-nat: Create only bulk NAT examples
        --all: Create all NAT rule types (default behavior)
        --no-report: Skip CSV report generation
        --folder: Folder name in SCM to create rules in (default: "Texas")

    Environment Variables:
        SCM_CLIENT_ID: Client ID for SCM authentication (required)
        SCM_CLIENT_SECRET: Client secret for SCM authentication (required)
        SCM_TSG_ID: Tenant Service Group ID for SCM authentication (required)
        SCM_LOG_LEVEL: Logging level, defaults to DEBUG (optional)
        SKIP_CLEANUP: Alternative way to preserve created rules (optional)

    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Track execution time for reporting
    start_time = __import__("time").time()
    rule_count = 0

    # Determine whether to skip cleanup
    # Command-line argument takes precedence over environment variable
    skip_cleanup = args.skip_cleanup or os.environ.get("SKIP_CLEANUP", "").lower() == "true"

    # Determine which rule types to create
    # If no specific types are specified, create all (default behavior)
    create_all = args.all or not (
        args.source_nat or args.dest_nat or args.special_nat or args.bulk_nat
    )

    # Get folder name for rule creation
    folder_name = args.folder

    try:
        # Initialize client
        client = initialize_client()

        # Initialize NAT rules object
        log_section("NAT RULE CONFIGURATION")
        log_operation_start("Initializing NAT rule manager")
        nat_rules = NatRule(client)
        log_operation_complete("NAT rule manager initialization")

        # Create various NAT rules
        created_rules = []

        # Basic Source NAT rules
        if create_all or args.source_nat:
            log_section("BASIC SOURCE NAT CONFIGURATIONS")
            log_info("Creating common outbound NAT rule patterns used for internet access")
            log_info(f"Using folder: {folder_name}")

            # Create the source NAT rule with dynamic IP and port
            source_nat = create_source_nat_rule(nat_rules, folder_name)
            if source_nat:
                created_rules.append(source_nat.id)
                rule_count += 1

            # Create the source NAT rule with interface address
            source_nat_interface = create_source_nat_rule_with_interface(nat_rules, folder_name)
            if source_nat_interface:
                created_rules.append(source_nat_interface.id)
                rule_count += 1

            # Create the static NAT rule
            static_nat = create_static_nat_rule(nat_rules, folder_name)
            if static_nat:
                created_rules.append(static_nat.id)
                rule_count += 1

            # Create the dynamic IP NAT rule with fallback
            dynamic_ip_nat = create_dynamic_ip_with_fallback(nat_rules, folder_name)
            if dynamic_ip_nat:
                created_rules.append(dynamic_ip_nat.id)
                rule_count += 1

            log_success(f"Created {len(created_rules)} source NAT rules so far")

        # Basic Destination NAT rules
        if create_all or args.dest_nat:
            log_section("BASIC DESTINATION NAT CONFIGURATIONS")
            log_info("Creating common inbound NAT rule patterns used for service publishing")
            log_info(f"Using folder: {folder_name}")

            # Create a destination NAT rule
            dest_nat = create_destination_nat_rule(nat_rules, folder_name)
            if dest_nat:
                created_rules.append(dest_nat.id)
                rule_count += 1

            # Create a dynamic destination NAT rule
            dynamic_dest_nat = create_dynamic_dest_nat_rule(nat_rules, folder_name)
            if dynamic_dest_nat:
                created_rules.append(dynamic_dest_nat.id)
                rule_count += 1

        # Special NAT rule types
        if create_all or args.special_nat:
            log_section("SPECIAL NAT RULE TYPES")
            log_info("Creating specialized NAT rules for IPv6 transition")
            log_info(f"Using folder: {folder_name}")

            # Create a DNS64 NAT rule
            dns64_nat = create_dns64_nat_rule(nat_rules, folder_name)
            if dns64_nat:
                created_rules.append(dns64_nat.id)
                rule_count += 1

            # Create an NPTv6 NAT rule
            nptv6_nat = create_nptv6_rule(nat_rules, folder_name)
            if nptv6_nat:
                created_rules.append(nptv6_nat.id)
                rule_count += 1

        # Advanced NAT rule configurations - these fall under destination NAT category for argument purposes
        if create_all or args.dest_nat:
            log_section("ADVANCED NAT CONFIGURATIONS")
            log_info("Creating complex NAT scenarios for enterprise networks")
            log_info(f"Using folder: {folder_name}")

            # Create a bi-directional NAT rule
            bidir_nat = create_bidirectional_nat_rule(nat_rules, folder_name)
            if bidir_nat:
                created_rules.append(bidir_nat.id)
                rule_count += 1

            # Create a multi-port forwarding NAT rule
            multi_port_nat = create_multi_port_forwarding_rule(nat_rules, folder_name)
            if multi_port_nat:
                created_rules.append(multi_port_nat.id)
                rule_count += 1

            # Create a port forwarding rule (separate from bi-directional NAT)
            port_forwarding_nat = create_port_forwarding_rule(nat_rules, folder_name)
            if port_forwarding_nat:
                created_rules.append(port_forwarding_nat.id)
                rule_count += 1

            # Create an outbound NAT rule with different interfaces
            outbound_interface_nat = create_outbound_nat_different_interfaces(
                nat_rules, folder_name
            )
            if outbound_interface_nat:
                created_rules.append(outbound_interface_nat.id)
                rule_count += 1

            # Position-specific NAT rules
            log_section("POSITION-SPECIFIC NAT RULES")
            log_info("Creating NAT rules in specific rulebase positions")
            log_info(f"Using folder: {folder_name}")

            # Create a post-rulebase NAT rule
            post_nat = create_post_nat_rule(nat_rules, folder_name)
            if post_nat:
                created_rules.append(post_nat.id)
                rule_count += 1

        # Bulk/Programmatic NAT rule creation
        if create_all or args.bulk_nat:
            log_section("BULK NAT RULE CREATION")
            log_info("Demonstrating programmatic creation of multiple NAT rules")
            log_info(f"Using folder: {folder_name}")

            # Create bulk NAT rules for different services
            bulk_rule_ids = create_bulk_nat_rules(nat_rules, folder_name)
            if bulk_rule_ids:
                created_rules.extend(bulk_rule_ids)
                rule_count += len(bulk_rule_ids)
                log_success(f"Created {len(bulk_rule_ids)} bulk NAT rules")

            # Create NAT rules for multiple branch sites
            branch_site_rule_ids = create_nat_rules_for_multiple_sites(nat_rules, folder_name)
            if branch_site_rule_ids:
                created_rules.extend(branch_site_rule_ids)
                rule_count += len(branch_site_rule_ids)
                log_success(f"Created {len(branch_site_rule_ids)} branch site NAT rules")

        # Update one of the rules
        if source_nat:
            log_section("UPDATING NAT RULES")
            log_info("Demonstrating how to update existing NAT rules")
            fetch_and_update_nat_rule(nat_rules, source_nat.id)

        # List and filter NAT rules
        log_section("LISTING AND FILTERING NAT RULES")
        log_info("Demonstrating how to search and filter NAT rules")
        list_and_filter_nat_rules(nat_rules)

        # Calculate intermediate execution statistics for the report
        current_time = __import__("time").time()
        execution_time_so_far = current_time - start_time

        # Generate CSV report before cleanup if there are rules to report and report generation is not disabled
        if created_rules and not args.no_report:
            log_section("REPORT GENERATION")
            log_operation_start("Generating NAT rules CSV report")
            report_file = generate_nat_rule_report(nat_rules, created_rules, execution_time_so_far)
            if report_file:
                log_success(f"Generated NAT rules report: {report_file}")
                log_info(
                    f"The report contains details of all {len(created_rules)} NAT rules created"
                )
            else:
                log_error("Failed to generate NAT rules report")
        elif args.no_report:
            log_info("Report generation disabled by --no-report flag")
        else:
            log_info("No NAT rules were created, skipping report generation")

        # Clean up the created rules, unless skip_cleanup is true
        log_section("CLEANUP")
        if skip_cleanup:
            log_info(f"SKIP_CLEANUP is set to true - preserving {len(created_rules)} NAT rules")
            log_info(
                "To clean up these rules, run the script again with SKIP_CLEANUP unset or set to false"
            )
        else:
            log_operation_start(f"Cleaning up {len(created_rules)} created NAT rules")
            cleanup_nat_rules(nat_rules, created_rules)

        # Calculate and display final execution statistics
        end_time = __import__("time").time()
        execution_time = end_time - start_time
        minutes, seconds = divmod(execution_time, 60)

        log_section("EXECUTION SUMMARY")
        log_success("Example script completed successfully")
        log_info(f"Total NAT rules created: {rule_count}")
        log_info(f"Total execution time: {int(minutes)} minutes {int(seconds)} seconds")
        log_info(f"Average time per rule: {execution_time / max(rule_count, 1):.2f} seconds")

    except AuthenticationError as e:
        log_error("Authentication failed", e.message)
        log_info(f"Status code: {e.http_status_code}")
        log_info("Please verify your credentials in the .env file")
    except KeyboardInterrupt:
        log_warning("Script execution interrupted by user")
        log_info("Note: Some NAT rules may not have been cleaned up")
    except Exception as e:
        log_error("Unexpected error", str(e))
        # Print the full stack trace for debugging
        import traceback

        log_info(f"Stack trace: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
