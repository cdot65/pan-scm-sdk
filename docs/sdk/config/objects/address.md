# Address Configuration Object

The `Address` class is used to manage address objects in the Strata Cloud Manager. It provides methods to create,
retrieve, update, delete, and list address objects.

---

## Importing the Address Class

```python
from scm.config.objects import Address
```

## Methods

### `create(data: Dict[str, Any]) -> AddressResponseModel`

Creates a new address object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the address object data.

**Example:**

```python
address_data = {
    "name": "test123",
    "fqdn": "test123.example.com",
    "description": "Created via pan-scm-sdk",
    "folder": "Prisma Access",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")
```

### `get(object_id: str) -> AddressResponseModel`

Retrieves an address object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address object.

**Example:**

```python
address_id = "123e4567-e89b-12d3-a456-426655440000"
address_object = address.get(address_id)
print(f"Address Name: {address_object.name}")
```

### `update(object_id: str, data: Dict[str, Any]) -> AddressResponseModel`

Updates an existing address object.

**Parameters:**

- `object_id` (str): The UUID of the address object.
- `data` (Dict[str, Any]): A dictionary containing the updated address data.

**Example:**

```python
update_data = {
    "description": "Updated description",
}

updated_address = address.update(address_id, update_data)
print(f"Updated address with ID: {updated_address.id}")
```

### `delete(object_id: str) -> None`

Deletes an address object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the address object.

**Example:**

```python
address.delete(address_id)
print(f"Deleted address with ID: {address_id}")
```

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, **filters) -> List[AddressResponseModel]`

Lists address objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list addresses from.
- `snippet` (Optional[str]): The snippet to list addresses from.
- `device` (Optional[str]): The device to list addresses from.
- `**filters`: Additional filters (e.g., `types`, `values`, `names`, `tags`).

**Example:**

```python
addresses = address.list(folder='Prisma Access')

for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")
```

---

## Usage Example

```python
from scm.client import Scm
from scm.config.objects import Address

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create an Address instance
address = Address(scm)

# Create a new address
address_data = {
    "name": "test123",
    "fqdn": "test123.example.com",
    "description": "Created via pan-scm-sdk",
    "folder": "Prisma Access",
}

new_address = address.create(address_data)
print(f"Created address with ID: {new_address.id}")

# List addresses
addresses = address.list(folder='Prisma Access')
for addr in addresses:
    print(f"Address Name: {addr.name}, IP: {addr.ip_netmask or addr.fqdn}")
```

---

## Related Models

- [AddressRequestModel](../../models/objects/address_models.md#addressrequestmodel)
- [AddressResponseModel](../../models/objects/address_models.md#addressresponsemodel)
