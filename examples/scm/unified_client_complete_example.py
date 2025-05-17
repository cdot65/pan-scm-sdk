"""Complete example demonstrating the unified client interface for the Palo Alto Networks SCM SDK.

This example shows how to use the unified client to:
1. Create address objects (FQDN and IP/Netmask)
2. Create tags with different colors
3. Create a security rule using the created objects
4. Perform cleanup by deleting all created objects
"""

import os
import time
from dotenv import load_dotenv
from scm.client import Scm
from scm.exceptions import APIError, NotFoundError

# Load environment variables from .env file if it exists
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv("SCM_CLIENT_ID")
CLIENT_SECRET = os.getenv("SCM_CLIENT_SECRET")
TSG_ID = os.getenv("SCM_TSG_ID")
FOLDER_NAME = os.getenv("SCM_FOLDER", "Testing")

# Store objects we create for later cleanup
created_objects = {"addresses": [], "tags": [], "security_rules": []}


def create_address_objects(client):
    """Create IP and FQDN address objects using the unified client."""
    print("\n=== Creating Address Objects ===")

    # Create an IP/Netmask address
    ip_address_data = {
        "name": "example-network",
        "ip_netmask": "192.168.1.0/24",
        "description": "Example network subnet",
        "folder": FOLDER_NAME,
    }

    try:
        # Access the address service directly through the client
        ip_address = client.address.create(ip_address_data)
        created_objects["addresses"].append(ip_address.id)
        print(f"✅ Created IP address: {ip_address.name} ({ip_address.ip_netmask})")
    except APIError as e:
        print(f"❌ Failed to create IP address: {e.message}")

    # Create an FQDN address
    fqdn_address_data = {
        "name": "example-server",
        "fqdn": "server.example.com",
        "description": "Example server hostname",
        "folder": FOLDER_NAME,
    }

    try:
        fqdn_address = client.address.create(fqdn_address_data)
        created_objects["addresses"].append(fqdn_address.id)
        print(f"✅ Created FQDN address: {fqdn_address.name} ({fqdn_address.fqdn})")
    except APIError as e:
        print(f"❌ Failed to create FQDN address: {e.message}")

    return ip_address, fqdn_address


def create_tags(client):
    """Create tags with different colors using the unified client."""
    print("\n=== Creating Tags ===")

    tags = []
    tag_colors = [{"name": "Production", "color": "red"}, {"name": "Development", "color": "blue"}]

    for tag_data in tag_colors:
        tag_data["folder"] = FOLDER_NAME

        try:
            # Access the tag service directly through the client
            tag = client.tag.create(tag_data)
            created_objects["tags"].append(tag.id)
            tags.append(tag)
            print(f"✅ Created tag: {tag.name} (color: {tag.color})")
        except APIError as e:
            print(f"❌ Failed to create tag '{tag_data['name']}': {e.message}")

    return tags


def create_security_rule(client, source_address, destination_address, tags):
    """Create a security rule using the created objects."""
    print("\n=== Creating Security Rule ===")

    rule_data = {
        "name": "Example-Unified-Rule",
        "folder": FOLDER_NAME,
        "description": "Example rule created with unified client",
        "source": {"address": [source_address.name]},
        "destination": {"address": [destination_address.name]},
        "application": ["web-browsing", "ssl"],
        "service": ["application-default"],
        "action": "allow",
        "tag": [tag.name for tag in tags],
        "log_setting": None,
        "log_start": False,
        "log_end": True,
        "disabled": False,
        "negate_source": False,
        "negate_destination": False,
    }

    try:
        # Access the security_rule service directly through the client
        security_rule = client.security_rule.create(rule_data)
        created_objects["security_rules"].append(security_rule.id)
        print(f"✅ Created security rule: {security_rule.name}")
        print(f"   - Source: {', '.join(security_rule.source.address)}")
        print(f"   - Destination: {', '.join(security_rule.destination.address)}")
        print(f"   - Applications: {', '.join(security_rule.application)}")
        print(f"   - Action: {security_rule.action}")
        print(f"   - Tags: {', '.join(security_rule.tag) if security_rule.tag else 'None'}")

        return security_rule
    except APIError as e:
        print(f"❌ Failed to create security rule: {e.message}")
        if hasattr(e, "details") and e.details:
            print(f"   Details: {e.details}")
        return None


def cleanup(client):
    """Clean up all created objects."""
    print("\n=== Cleaning Up Resources ===")

    # Delete security rules first
    for rule_id in created_objects["security_rules"]:
        try:
            client.security_rule.delete(rule_id)
            print(f"✅ Deleted security rule with ID: {rule_id}")
        except NotFoundError:
            print(f"⚠️ Security rule with ID {rule_id} not found")
        except APIError as e:
            print(f"❌ Failed to delete security rule {rule_id}: {e.message}")

    time.sleep(1)  # Brief pause to ensure resources are freed

    # Delete addresses
    for address_id in created_objects["addresses"]:
        try:
            client.address.delete(address_id)
            print(f"✅ Deleted address with ID: {address_id}")
        except NotFoundError:
            print(f"⚠️ Address with ID {address_id} not found")
        except APIError as e:
            print(f"❌ Failed to delete address {address_id}: {e.message}")

    # Delete tags
    for tag_id in created_objects["tags"]:
        try:
            client.tag.delete(tag_id)
            print(f"✅ Deleted tag with ID: {tag_id}")
        except NotFoundError:
            print(f"⚠️ Tag with ID {tag_id} not found")
        except APIError as e:
            print(f"❌ Failed to delete tag {tag_id}: {e.message}")


def main():
    """Main function to demonstrate the unified client."""
    if not all([CLIENT_ID, CLIENT_SECRET, TSG_ID]):
        print("❌ Environment variables not set. Please create a .env file with:")
        print("SCM_CLIENT_ID=<your_client_id>")
        print("SCM_CLIENT_SECRET=<your_client_secret>")
        print("SCM_TSG_ID=<your_tsg_id>")
        print("SCM_FOLDER=<your_folder>  # Optional, defaults to 'Testing'")
        return

    try:
        # Initialize the unified client
        print(f"Initializing SCM client for folder: {FOLDER_NAME}")
        client = Scm(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tsg_id=TSG_ID,
            log_level="INFO",
        )
        print("✅ Client initialized successfully")

        # Create all resources
        source_address, dest_address = create_address_objects(client)
        tags = create_tags(client)
        security_rule = create_security_rule(client, source_address, dest_address, tags)

        if security_rule:
            print("\n=== Success! ===")
            print("All resources were created successfully using the unified client pattern.")

            # Demonstrate committing changes
            commit_changes = (
                input("\nWould you like to commit these changes? (y/n): ").lower().strip() == "y"
            )
            if commit_changes:
                print("\n=== Committing Changes ===")
                result = client.commit(
                    folders=[FOLDER_NAME], description="Unified client example changes", sync=True
                )
                if result.success:
                    print(f"✅ Changes committed successfully. Job ID: {result.job_id}")
                else:
                    print(
                        f"❌ Commit failed: {result.message if hasattr(result, 'message') else 'Unknown error'}"
                    )

        # Ask to clean up
        cleanup_resources = (
            input("\nWould you like to clean up created resources? (y/n): ").lower().strip() == "y"
        )
        if cleanup_resources:
            cleanup(client)

            # Commit cleanup if requested
            commit_cleanup = (
                input("\nWould you like to commit the cleanup changes? (y/n): ").lower().strip()
                == "y"
            )
            if commit_cleanup:
                print("\n=== Committing Cleanup ===")
                result = client.commit(
                    folders=[FOLDER_NAME], description="Unified client example cleanup", sync=True
                )
                if result.success:
                    print(f"✅ Cleanup committed successfully. Job ID: {result.job_id}")
                else:
                    print(
                        f"❌ Cleanup commit failed: {result.message if hasattr(result, 'message') else 'Unknown error'}"
                    )

    except APIError as e:
        print(f"❌ API error: {e.message}")
        if hasattr(e, "details") and e.details:
            print(f"Details: {e.details}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
