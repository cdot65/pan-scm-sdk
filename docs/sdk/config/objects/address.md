# Address Configuration Object

The `Address` class is used to manage address objects in the Strata Cloud Manager. It provides methods to create,
retrieve, update, delete, and list address objects.

---

## Importing the Address Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.objects import Address
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> AddressResponseModel`

Creates a new address object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the address object data.

**Example 1: Creating an IP/Netmask Address**

<div class="termy">

<!-- termynal -->

```python
address_data = {
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network address",
    "folder": "Shared",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")
```

</div>

**Example 2: Creating an FQDN Address**

<div class="termy">

<!-- termynal -->

```python
address_data = {
    "name": "example_website",
    "fqdn": "www.example.com",
    "description": "Example website address",
    "folder": "Prisma Access",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")
```

</div>

### `get(object_id: str) -> AddressResponseModel`

Retrieves an address object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
address_object = address.get(address_id)
print(f"Address Name: {address_object.name}")
print(f"Address Type: {address_object.ip_netmask or address_object.fqdn}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> AddressResponseModel`

Updates an existing address object.

**Parameters:**

- `object_id` (str): The UUID of the address object.
- `data` (Dict[str, Any]): A dictionary containing the updated address data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Updated internal network description",
    "tag": ["internal", "updated"],
}

updated_address = address.update(address_id, update_data)
print(f"Updated address with ID: {updated_address.id}")
print(f"New description: {updated_address.description}")
print(f"New tags: {updated_address.tag}")
```

</div>

### `delete(object_id: str) -> None`

Deletes an address object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
address.delete(address_id)
print(f"Deleted address with ID: {address_id}")
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[AddressResponseModel]`

Lists address objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list addresses from.
- `snippet` (Optional[str]): The snippet to list addresses from.
- `device` (Optional[str]): The device to list addresses from.
- `**filters`: Additional filters (e.g., `types`, `values`, `names`, `tags`).

**Example 1: Listing Addresses in a Folder**

<div class="termy">

<!-- termynal -->

```python
addresses = address.list(folder='Prisma Access')

for addr in addresses:
    print(f"Address Name: {addr.name}, Type: {addr.ip_netmask or addr.fqdn}")
```

</div>

**Example 2: Listing Addresses with Filters**

<div class="termy">

<!-- termynal -->

```python
filtered_addresses = address.list(
    folder='Shared',
    types=['ip-netmask'],
    tags=['internal']
)

for addr in filtered_addresses:
    print(f"Address Name: {addr.name}, IP/Netmask: {addr.ip_netmask}")
```

</div>

---

## Full Usage Example

Here's a complete example demonstrating how to use the Address configuration object:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize the SCM client
api_client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an Address instance
address = Address(api_client)

# Create a new address
address_data = {
    "name": "example_network",
    "ip_netmask": "10.0.0.0/16",
    "description": "Example network address",
    "folder": "Shared",
    "tag": ["example", "network"]
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# Get the created address
retrieved_address = address.get(new_address.id)
print(f"Retrieved address: {retrieved_address.name}")

# Update the address
update_data = {
    "description": "Updated example network address",
    "tag": ["example", "network", "updated"]
}

updated_address = address.update(new_address.id, update_data)
print(f"Updated address description: {updated_address.description}")
print(f"Updated address tags: {updated_address.tag}")

# List addresses
addresses = address.list(folder='Shared', types=['ip-netmask'])
for addr in addresses:
    print(f"Address Name: {addr.name}, IP/Netmask: {addr.ip_netmask}")

# Delete the address
address.delete(new_address.id)
print(f"Deleted address with ID: {new_address.id}")
```

</div>

---

## Related Models

- [AddressCreateModel](../../models/objects/address_models.md#addressrequestmodel)
- [AddressResponseModel](../../models/objects/address_models.md#addressresponsemodel)