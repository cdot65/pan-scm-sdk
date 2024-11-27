# Address Configuration Object

The `Address` class provides functionality to manage address objects in Palo Alto Networks' Strata Cloud Manager. This
includes creating, retrieving, updating, and deleting address objects of various types including IP/Netmask, IP Range,
IP Wildcard, and FQDN (Fully Qualified Domain Name).

## Overview

Address objects are fundamental building blocks used in security policies and NAT rules. They can represent:

- Individual IP addresses or networks (using CIDR notation)
- IP address ranges
- IP addresses with wildcard masks
- Fully Qualified Domain Names (FQDNs)

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during address object
management.

## Methods

| Method     | Description                                   |
|------------|-----------------------------------------------|
| `create()` | Creates a new address object                  |
| `get()`    | Retrieves an address object by ID             |
| `update()` | Updates an existing address object            |
| `delete()` | Deletes an address object                     |
| `list()`   | Lists address objects with optional filtering |
| `fetch()`  | Retrieves a single address object by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when address object data is invalid
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when an address object doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when address names conflict
- `NameNotUniqueError`: Raised when creating duplicate address names

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Address Objects

The `create()` method allows you to create new address objects with proper error handling.

**Example: Creating an IP/Netmask Address**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

addresses = Address(client)

try:
    address_data = {
        "name": "internal_network",
        "ip_netmask": "192.168.1.0/24",
        "description": "Internal network segment",
        "folder": "Texas",
        "tag": ["Python", "Automation"]
    }

    new_address = addresses.create(address_data)
    print(f"Created address with ID: {new_address.id}")

except NameNotUniqueError as e:
    print(f"Address name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid address data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Address Objects

Use the `get()` method to retrieve an address object by its ID.

<div class="termy">

<!-- termynal -->

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
address_obj = addresses.get(address_id)
print(f"Address Name: {address_obj.name}")
```

</div>

## Updating Address Objects

The `update()` method allows you to modify existing address objects.

<div class="termy">

<!-- termynal -->

```python
# first fetch an existing object by its folder and name
example_website = addresses.fetch(folder='Texas', name='example_website')

# update the dictionary's description
example_website['description'] = "this is just a test"
addresses.update(example_website)
```

</div>

## Deleting Address Objects

Use the `delete()` method to remove an address object.

<div class="termy">

<!-- termynal -->

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
addresses.delete(address_id)
print("Address object deleted successfully")
```

</div>

## Listing Address Objects

The `list()` method retrieves multiple address objects with optional filtering. You can filter the results using the
following kwargs:

- `types`: List[str] - Filter by address types (e.g., ['netmask', 'range', 'wildcard', 'fqdn'])
- `values`: List[str] - Filter by address values (e.g., ['10.0.0.0/24', '192.168.1.0/24'])
- `tags`: List[str] - Filter by tags (e.g., ['Automation', 'Production'])

<div class="termy">

<!-- termynal -->

```python
# List all addresses in a folder
texas_addresses = addresses.list(
    folder="Texas",
)

# List only netmask addresses
netmask_addresses = addresses.list(
    folder="Texas",
    types=['netmask']
)

# List addresses with specific values
specific_networks = addresses.list(
    folder="Texas",
    values=['10.0.0.0/24', '192.168.1.0/24']
)

# List addresses with specific tags
tagged_addresses = addresses.list(
    folder="Texas",
    tags=['Automation', 'Production']
)

# Combine multiple filters
filtered_addresses = addresses.list(
    folder="Texas",
    types=['netmask', 'range'],
    tags=['Production']
)

# Print the results
for addr in texas_addresses:
    if addr.ip_netmask:
        print(f"Name: {addr.name}, Value: {addr.ip_netmask}")
    elif addr.fqdn:
        print(f"Name: {addr.name}, Value: {addr.fqdn}")
    elif addr.ip_range:
        print(f"Name: {addr.name}, Value: {addr.ip_range}")
    else:
        print(f"Name: {addr.name}, Value: {addr.wildcard}")
```

</div>

## Fetching Address Objects

The `fetch()` method retrieves a single address object by name and container.

<div class="termy">

<!-- termynal -->

```python
# Fetch an address by name from a specific folder
desktop1 = addresses.fetch(
    name="dallas-desktop1",
    folder="Texas"
)

# fetch will return a Python dictionary, not a pydantic model
print(f"Found address: {desktop1['name']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an address object with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"
    )

    # Initialize address object
    addresses = Address(client)

    try:
        # Create new address
        create_data = {
            "name": "test_network",
            "ip_netmask": "10.0.0.0/24",
            "description": "Test network segment",
            "folder": "Texas",
            "tag": ["Python", "Automation"]
        }

        new_address = addresses.create(create_data)
        print(f"Created address: {new_address.name}")

        # Fetch the address by name
        try:
            fetched = addresses.fetch(
                name="test_network",
                folder="Texas"
            )
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

    except NameNotUniqueError as e:
        print(f"Address name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid address data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Full script examples

Refer to the [examples](../../../../examples/scm/config/objects) directory.

## Related Models

- [AddressCreateModel](../../models/objects/address_models.md#Overview)
- [AddressUpdateModel](../../models/objects/address_models.md#Overview)
- [AddressResponseModel](../../models/objects/address_models.md#Overview)
