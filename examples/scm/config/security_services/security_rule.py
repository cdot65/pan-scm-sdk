"""Example script for security rule management."""

from scm.client import Scm
from scm.config.security import SecurityRule
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
)

# Initialize client
client = Scm(
    client_id="your-client-id",
    client_secret="your-secret",
    tsg_id="your-tsg-id",
)

# Initialize security rule object
security_rule = SecurityRule(client)


# Create security rule
def create_security_rule():
    """Create a new security rule."""
    try:
        # Initialize security rule object
        security_rule = SecurityRule(client)

        # Rule configuration
        rule_data = {
            "name": "example_rule",
            "from_zone": ["trust"],
            "to_zone": ["untrust"],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
            "action": "allow",
            "folder": "Shared",
        }

        # Create the rule
        response = security_rule.create(rule_data)
        print(f"Created rule: {response.name}")
        print(f"Rule ID: {response.id}")

    except InvalidObjectError as e:
        print(f"Invalid data: {e}")
    except Exception as e:
        print(f"Error: {e}")


# Fetch by name
try:
    rule = security_rule.fetch(name="example_rule", folder="Shared")
    print(f"Found: {rule.name}")
except NotFoundError:
    print("Rule not found")


def fetch_and_update_security_rule():
    """Fetch and update a security rule."""
    security_rule = SecurityRule(client)

    try:
        rule = security_rule.fetch(name="example_rule", folder="Shared")
        print(f"Found: {rule.name}")
        # Update the rule
        security_rule.update(rule)
        print(f"Updated rule: {rule.name}")
    except Exception as e:
        print(f"Error: {e}")


def fetch_and_cleanup_security_rule():
    """Fetch and cleanup a security rule."""
    security_rule = SecurityRule(client)

    try:
        rule = security_rule.fetch(name="example_rule", folder="Shared")
        print(f"Found: {rule.name}")
        # Delete the rule
        security_rule.delete(rule.id)
        print(f"Deleted rule: {rule.name}")
    except Exception as e:
        print(f"Error: {e}")
