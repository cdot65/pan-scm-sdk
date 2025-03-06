#!/usr/bin/env python
"""
Example script demonstrating usage of the Security Zone module in the Strata Cloud Manager SDK.

This script shows how to create, retrieve, update, list, and delete security zones.
"""

import json
import os
import sys
from uuid import UUID

# Add the parent directory to the path so we can import the scm module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from scm.auth import OAuth2
from scm.client import Client
from scm.config.network import SecurityZone


def main():
    """Main execution function"""
    # Initialize the OAuth2 authentication
    auth = OAuth2(
        client_id=os.environ.get("SCM_CLIENT_ID"),
        client_secret=os.environ.get("SCM_CLIENT_SECRET"),
        token_url=os.environ.get("SCM_TOKEN_URL", "https://api.strata.paloaltonetworks.com/api/oauth2/token"),
    )

    # Initialize the API client
    client = Client(
        api_url=os.environ.get("SCM_API_URL", "https://api.strata.paloaltonetworks.com"),
        auth=auth,
    )

    # Create the SecurityZone instance
    security_zone = SecurityZone(client)

    # Example folder name to use
    folder_name = "Example Folder"

    # Create a security zone
    try:
        # Example security zone data
        zone_data = {
            "name": "example-zone",
            "folder": folder_name,
            "enable_user_identification": True,
            "enable_device_identification": False,
            "network": {
                "layer3": ["ethernet1/1", "ethernet1/2"],
                "zone_protection_profile": "default",
                "enable_packet_buffer_protection": True
            },
            "user_acl": {
                "include_list": ["user1", "user2"],
                "exclude_list": []
            }
        }

        # Create the security zone
        created_zone = security_zone.create(zone_data)
        print("Created security zone:")
        print(json.dumps(json.loads(created_zone.model_dump_json()), indent=2))
        print("\n")

        # Get the security zone by ID
        retrieved_zone = security_zone.get(str(created_zone.id))
        print("Retrieved security zone by ID:")
        print(json.dumps(json.loads(retrieved_zone.model_dump_json()), indent=2))
        print("\n")

        # Update the security zone
        update_data = {
            "id": created_zone.id,
            "name": created_zone.name,
            "folder": folder_name,
            "enable_user_identification": True,
            "enable_device_identification": True,  # Changed to True
            "network": {
                "layer3": ["ethernet1/1", "ethernet1/2", "ethernet1/3"],  # Added another interface
                "zone_protection_profile": "default",
                "enable_packet_buffer_protection": True
            }
        }
        updated_zone = security_zone.update(security_zone.models.SecurityZoneUpdateModel(**update_data))
        print("Updated security zone:")
        print(json.dumps(json.loads(updated_zone.model_dump_json()), indent=2))
        print("\n")

        # List security zones in the folder
        zones_list = security_zone.list(folder=folder_name)
        print(f"Listed {len(zones_list)} security zones in folder '{folder_name}':")
        for zone in zones_list:
            print(f"- {zone.name} (ID: {zone.id})")
        print("\n")

        # Fetch a security zone by name
        fetched_zone = security_zone.fetch(name="example-zone", folder=folder_name)
        print("Fetched security zone by name:")
        print(json.dumps(json.loads(fetched_zone.model_dump_json()), indent=2))
        print("\n")

        # Delete the security zone
        security_zone.delete(str(created_zone.id))
        print(f"Deleted security zone with ID: {created_zone.id}")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()