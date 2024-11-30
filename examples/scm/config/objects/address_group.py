from scm.client import Scm
from scm.config.objects import Address, AddressGroup
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError,
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG",  # Enable detailed logging
    )

    # Initialize address and address group objects
    addresses = Address(client)
    address_groups = AddressGroup(client)

    try:
        # Create address objects
        ao1 = {
            "name": "test_network1",
            "ip_netmask": "10.0.0.0/24",
            "description": "Test network",
            "folder": "Texas",
            "tag": ["Automation"],
        }
        test_network1 = addresses.create(ao1)

        ao2 = {
            "name": "test_network2",
            "ip_netmask": "10.0.1.0/24",
            "description": "Test network",
            "folder": "Texas",
            "tag": ["Automation"],
        }
        test_network2 = addresses.create(ao2)

        # Create a new static group
        test_network_group = {
            "name": "test_network_group",
            "description": "Test networks",
            "static": [test_network1.name, test_network2.name],
            "folder": "Texas",
            "tag": ["Automation"],
        }

        new_group = address_groups.create(test_network_group)
        print(f"Created group: {new_group.name}")

        # Fetch and update the group
        try:
            fetched_group = address_groups.fetch(
                name="test_network_group", folder="Texas"
            )
            print(f"Found group: {fetched_group.name}")

            # Update the group using Pydantic model
            fetched_group.description = "Updated test networks"
            updated = address_groups.update(fetched_group)
            print(f"Updated description: {updated.description}")

        except NotFoundError as e:
            print(f"Group not found: {e.message}")

        # Clean up
        try:
            address_groups.delete(new_group.id)
            print("Group deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete group - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
