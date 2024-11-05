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
    "folder": "Texas",
    "tag": ["Python", "Automation"]
}

new_address = addresses.create(address_data)
print(f"Created address with ID: {new_address.id}")
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
    "folder": "Texas",
    "tag": ["Python", "Automation"]
}

new_address = addresses.create(address_data)
print(f"Created address with ID: {new_address.id}")
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

The `list()` method retrieves multiple address objects with optional filtering.

<div class="termy">

<!-- termynal -->

```python
# List all addresses in a folder
texas_addresses = addresses.list(
    folder="Texas",
)

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
addresses = Address(client)

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
fetched = addresses.fetch(name="test_network", folder="Texas")

# Modify the fetched object
fetched["description"] = "Updated test network segment"
fetched["tag"] = ["Python"]

# Update using the modified object
updated = addresses.update(fetched)
print(f"Updated description: {updated.description}")

# Clean up
addresses.delete(new_address.id)
print("Address deleted successfully")
```

</div>

## Related Models

- [AddressCreateModel](../../models/objects/address_models.md#addresscreatemodel)
- [AddressUpdateModel](../../models/objects/address_models.md#addressupdatemodel)
- [AddressResponseModel](../../models/objects/address_models.md#addressresponsemodel)