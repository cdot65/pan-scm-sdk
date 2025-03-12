"""
Example script demonstrating the unified client interface for the Palo Alto Networks SCM SDK.

This example shows how to use the new attribute-based access pattern to create, read,
update, and delete objects without instantiating individual service objects.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from scm.client import Scm
from scm.exceptions import (
    APIError,
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)


def demonstrate_fqdn_address(client):
    """Demonstrate creating and working with an FQDN address"""
    print("\n=== Working with FQDN Address ===")

    try:
        # Create a new FQDN address using the attribute access pattern
        address_data = {
            "name": "example-hostname",
            "fqdn": "example.domain.com",
            "description": "Example hostname created with unified client",
            "folder": "Texas",
            "tag": ["Decrypted", "Automation"],
        }

        print("Creating new FQDN address...")
        new_address = client.address.create(address_data)
        print(f"✅ Created address: {new_address.name} with ID: {new_address.id}")

        # Fetch the address by name
        print(f"Fetching address by name: {new_address.name}...")
        fetched = client.address.fetch(name=new_address.name, folder="Texas")
        print(f"✅ Found address: {fetched.name} with FQDN: {fetched.fqdn}")

        # Update the address description
        print("Updating address description...")
        fetched.description = "Updated example hostname description"
        updated = client.address.update(fetched)
        print(f"✅ Updated description: {updated.description}")

        # Delete the address
        print(f"Deleting address: {new_address.name}...")
        client.address.delete(new_address.id)
        print("✅ Address deleted successfully")

    except NotFoundError as e:
        print(f"❌ Address not found: {e.message}")
    except NameNotUniqueError as e:
        print(f"❌ Address name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"❌ Invalid address data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def demonstrate_tag(client):
    """Demonstrate creating and working with tags"""
    print("\n=== Working with Tags ===")

    try:
        # Create a new tag using the attribute access pattern
        tag_data = {"name": "UnifiedClient", "color": "red", "folder": "Texas"}

        print("Creating new tag...")
        new_tag = client.tag.create(tag_data)
        print(f"✅ Created tag: {new_tag.name} with ID: {new_tag.id}")

        # Fetch the tag
        print(f"Fetching tag: {new_tag.name}...")
        tags = client.tag.list(folder="Texas")
        matching_tags = [tag for tag in tags if tag.name == new_tag.name]

        if matching_tags:
            tag = matching_tags[0]
            print(f"✅ Found tag: {tag.name} with color: {tag.color}")

            # Update tag color
            print("Updating tag color to blue...")
            tag.color = "blue"
            updated_tag = client.tag.update(tag)
            print(f"✅ Updated tag color: {updated_tag.color}")

            # Delete the tag
            print(f"Deleting tag: {tag.name}...")
            client.tag.delete(tag.id)
            print("✅ Tag deleted successfully")
        else:
            print(f"❌ Tag not found: {new_tag.name}")

    except Exception as e:
        print(f"❌ Error working with tags: {str(e)}")


def main():
    # Load environment variables from .env file
    # First try to load from current directory
    env_path = Path(".") / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        # If not found, try the script's directory
        script_dir = Path(__file__).parent.absolute()
        env_path = script_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)

    # Get credentials from environment variables with fallbacks
    client_id = os.environ.get("SCM_CLIENT_ID", None)
    client_secret = os.environ.get("SCM_CLIENT_SECRET", None)
    tsg_id = os.environ.get("SCM_TSG_ID", None)
    log_level = os.environ.get("SCM_LOG_LEVEL", "DEBUG")
    try:
        # Initialize client with the unified interface
        print("Initializing SCM client...")
        client = Scm(
            client_id=client_id,
            client_secret=client_secret,
            tsg_id=tsg_id,
            log_level=log_level,
        )
        print("✅ Client initialized")

        # Demonstrate working with different services
        demonstrate_fqdn_address(client)
        demonstrate_tag(client)

        print("\n=== Example Completed Successfully ===")

    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e.message}")
        print(f"Status code: {e.http_status_code}")
    except APIError as e:
        print(f"❌ API error: {e.message}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
