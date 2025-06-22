#!/usr/bin/env python3
"""Test script for security rule move operation in the SCM SDK.

This script tests the fixed UUID serialization issue in the .move() method.
"""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
from dotenv import load_dotenv

# SDK imports
from scm.client import ScmClient
from scm.exceptions import (
    APIError,
    AuthenticationError,
)

# Add the project root to the path to allow imports from the scm package
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))


def load_environment_variables():
    """Load environment variables from .env file."""
    env_path = Path(".") / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # If not found, try the script's directory
        script_dir = Path(__file__).parent.absolute()
        env_path = script_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            # If still not found, try the project root
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)

    # Get credentials from environment variables with fallbacks
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    tsg_id = os.environ.get("TSG_ID")
    log_level = os.environ.get("LOG_LEVEL", "DEBUG")
    folder = os.environ.get("FOLDER", "Texas")  # Default to Texas folder from your example

    if not all([client_id, client_secret, tsg_id]):
        print(
            "❌ Missing required environment variables. Please set CLIENT_ID, CLIENT_SECRET, and TSG_ID."
        )
        sys.exit(1)

    return client_id, client_secret, tsg_id, log_level, folder


def initialize_client(client_id, client_secret, tsg_id, log_level):
    """Initialize the SCM client."""
    print("Initializing SCM client...")
    try:
        client = ScmClient(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            log_level=log_level,
        )
        print("✅ Client initialized")
        return client
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e.message}")
        print(f"Status code: {e.http_status_code}")
        sys.exit(1)
    except APIError as e:
        print(f"❌ API error: {e.message}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


def list_security_rules(client, folder):
    """List security rules in a folder."""
    print(f"\nListing security rules in folder '{folder}'...")
    try:
        rules = client.security_rule.list(folder=folder, rulebase="pre", exact_match=True)

        if not rules:
            print(f"No security rules found in folder '{folder}'.")
            sys.exit(0)

        print(f"Found {len(rules)} security rules:")
        for i, rule in enumerate(rules, 1):
            print(f"{i}. {rule.name} - {rule.id}")

        return rules
    except Exception as e:
        print(f"❌ Error listing security rules: {str(e)}")
        sys.exit(1)


def move_security_rule(client, rules, folder):
    """Move a security rule to a new position.

    For this example, we'll move the last rule before the second-to-last rule.
    """
    if len(rules) < 2:
        print("Need at least 2 rules to perform a move operation.")
        sys.exit(1)

    # Select rules for the move operation
    source_rule = rules[-1]  # Last rule
    target_rule = rules[-2]  # Second-to-last rule

    print(f"\nMoving rule '{source_rule.name}' before '{target_rule.name}'...")

    try:
        # Prepare move configuration
        move_config = {
            "destination": "before",
            "rulebase": "pre",
            "destination_rule": str(target_rule.id),  # Convert UUID to string
        }

        # Execute the move operation
        client.security_rule.move(source_rule.id, move_config)
        print(f"✅ Successfully moved rule '{source_rule.name}' before '{target_rule.name}'")

        # Verify the move by listing rules again
        print("\nVerifying move operation...")
        updated_rules = client.security_rule.list(folder=folder, rulebase="pre", exact_match=True)

        print("Updated rule order:")
        for i, rule in enumerate(updated_rules, 1):
            print(f"{i}. {rule.name} - {rule.id}")

    except Exception as e:
        print(f"❌ Error moving security rule: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Load environment variables
    client_id, client_secret, tsg_id, log_level, folder = load_environment_variables()

    # Initialize client
    client = initialize_client(client_id, client_secret, tsg_id, log_level)

    # List security rules
    rules = list_security_rules(client, folder)

    # Move a rule
    move_security_rule(client, rules, folder)

    print("\nTest completed!")
