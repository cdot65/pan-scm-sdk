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

## Methods

| Method     | Description                                   |
|------------|-----------------------------------------------|
| `create()` | Creates a new address object                  |
| `get()`    | Retrieves an address object by ID             |
| `update()` | Updates an existing address object            |
| `delete()` | Deletes an address object                     |
| `list()`   | Lists address objects with optional filtering |
| `fetch()`  | Retrieves a single address object by name     |

## Creating Address Objects

The `create()` method allows you to create new address objects. You must specify exactly one address type (ip_netmask,
ip_range, ip_wildcard, or fqdn) and one container type (folder, snippet, or device).

**Example: Creating an IP/Netmask Address**

<div class="termy">

<!-- termynal -->

```python
address_data = {
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network segment",
    "folder": "Shared",
    "tag": ["internal", "network"]
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address['id']}")
```

</div>

**Example: Creating an FQDN Address**

<div class="termy">

<!-- termynal -->

```python
address_data = {
    "name": "example_website",
    "fqdn": "www.example.com",
    "description": "Example website address",
    "folder": "Prisma Access",
    "tag": ["external", "web"]
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address['id']}")
```

</div>

## Getting Address Objects

Use the `get()` method to retrieve an address object by its ID.

<div class="termy">

<!-- termynal -->

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
address_obj = address.get(address_id)
print(f"Address Name: {address_obj['name']}")
print(f"Address Type: {address_obj.get('ip_netmask') or address_obj.get('fqdn')}")
```

</div>

## Updating Address Objects

The `update()` method allows you to modify existing address objects.

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "description": "Updated network description",
    "tag": ["internal", "updated", "2023"]
}

updated_address = address.update(update_data)
print(f"Updated address description: {updated_address['description']}")
```

</div>

## Deleting Address Objects

Use the `delete()` method to remove an address object.

<div class="termy">

<!-- termynal -->

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
address.delete(address_id)
print("Address object deleted successfully")
```

</div>

## Listing Address Objects

The `list()` method retrieves multiple address objects with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all addresses in a folder with specific tags
addresses = address.list(
    folder="Shared",
    tags=["internal"],
    types=["ip-netmask"]
)

for addr in addresses:
    print(f"Name: {addr['name']}, Value: {addr.get('ip_netmask')}")
```

</div>

## Fetching Address Objects

The `fetch()` method retrieves a single address object by name and container.

<div class="termy">

<!-- termynal -->

```python
# Fetch an address by name from a specific folder
address_obj = address.fetch(
    name="internal_network",
    folder="Shared"
)
print(f"Found address: {address_obj['name']}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of an address object:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize address object
address = Address(client)

# Create new address
create_data = {
    "name": "test_network",
    "ip_netmask": "10.0.0.0/24",
    "description": "Test network segment",
    "folder": "Shared",
    "tag": ["test"]
}

new_address = address.create(create_data)
print(f"Created address: {new_address['name']}")

# Fetch the address by name
fetched = address.fetch(name="test_network", folder="Shared")

# Modify the fetched object
fetched["description"] = "Updated test network segment"
fetched["tag"] = ["test", "updated"]

# Update using the modified object
updated = address.update(fetched)
print(f"Updated description: {updated['description']}")

# List addresses with filters
addresses = address.list(
    folder="Shared",
    tags=["test"]
)

for addr in addresses:
    print(f"Listed address: {addr['name']}")

# Clean up
address.delete(new_address['id'])
print("Address deleted successfully")
```

</div>

## Related Models

- [AddressCreateModel](../../models/objects/address_models.md#addresscreatemodel)
- [AddressUpdateModel](../../models/objects/address_models.md#addressupdatemodel)
- [AddressResponseModel](../../models/objects/address_models.md#addressresponsemodel)