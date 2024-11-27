from scm.client import Scm
from scm.config.objects import Address
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id_here",
        client_secret="your_client_secret_here",
        tsg_id="your_scm_tsg_id_here",
        log_level="DEBUG",
    )

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")

# Initialize address object
addresses = Address(client)

try:
    # Create new address
    create_data = {
        "name": "test_network",
        "ip_netmask": "10.0.0.0/24",
        "description": "Test network segment",
        "folder": "Texas",
        "tag": ["Automation"],
    }

    new_address = addresses.create(create_data)
    print(f"Created address: {new_address.name}")

except NameNotUniqueError as e:
    print(f"Address name conflict: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid address data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")

# Fetch the address by name
try:
    fetched = addresses.fetch(name="test_network", folder="Texas")
    print(f"Found address: {fetched['name']}")

    # Update the address
    fetched["description"] = "Updated test network segment"
    updated = addresses.update(fetched)
    print(f"Updated description: {updated.description}")

except NotFoundError as e:
    print(f"Address not found: {e.message}")

# Clean up
addresses.delete(new_address.id)
print("Address deleted successfully")
