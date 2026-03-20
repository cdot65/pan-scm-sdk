# Address

The `Address` service manages address objects in Strata Cloud Manager, supporting IP/Netmask, IP Range, IP Wildcard, and FQDN address types for use in security policies.

## Class Overview

The `Address` class provides CRUD operations for address objects. It is accessed through the `client.address` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Address service
addresses = client.address
```

### Key Attributes

| Attribute     | Type        | Required     | Description                                |
|---------------|-------------|--------------|--------------------------------------------|
| `name`        | `str`       | Yes          | Name of address object (max 63 chars)      |
| `id`          | `UUID`      | Yes*         | Unique identifier (*response only)         |
| `ip_netmask`  | `str`       | One Required | IP address with CIDR notation              |
| `ip_range`    | `str`       | One Required | IP address range format                    |
| `ip_wildcard` | `str`       | One Required | IP wildcard mask format                    |
| `fqdn`        | `str`       | One Required | Fully qualified domain name                |
| `description` | `str`       | No           | Object description (max 1023 chars)        |
| `tag`         | `List[str]` | No           | List of tags (max 127 chars each)          |
| `folder`      | `str`       | Yes**        | Folder location (**one container required) |
| `snippet`     | `str`       | Yes**        | Snippet location (**one container required)|
| `device`      | `str`       | Yes**        | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Addresses

Retrieves a list of address objects with optional filtering.

```python
# List all addresses in a folder
addresses = client.address.list(folder="Texas")

# List with filters
filtered = client.address.list(
    folder="Texas",
    types=["fqdn"],
    tags=["Automation"]
)

for addr in filtered:
    print(f"Name: {addr.name}, Value: {addr.fqdn}")
```

**Parameters:**

| Parameter          | Type         | Required | Description                                      |
|--------------------|--------------|----------|--------------------------------------------------|
| `folder`           | `str`        | Yes*     | Folder in which the resource is defined          |
| `snippet`          | `str`        | Yes*     | Snippet in which the resource is defined         |
| `device`           | `str`        | Yes*     | Device in which the resource is defined          |
| `exact_match`      | `bool`       | No       | Only return objects exactly in the container     |
| `exclude_folders`  | `List[str]`  | No       | List of folders to exclude                       |
| `exclude_snippets` | `List[str]`  | No       | List of snippets to exclude                      |
| `exclude_devices`  | `List[str]`  | No       | List of devices to exclude                       |
| `**filters`        | `Any`        | No       | Additional filters (e.g., `types`, `values`, `tags`) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Fetch an Address

Retrieves a single address object by name and container.

```python
address = client.address.fetch(name="webserver", folder="Texas")
print(f"Found address: {address.name}")
```

### Create an Address

Creates a new address object.

```python
address_config = {
    "name": "webserver",
    "ip_netmask": "192.168.1.100/32",
    "description": "Primary web server",
    "folder": "Texas",
    "tag": ["Web", "Production"]
}

new_address = client.address.create(address_config)
print(f"Created address: {new_address.name} (ID: {new_address.id})")
```

### Update an Address

Updates an existing address object.

```python
existing = client.address.fetch(name="webserver", folder="Texas")
existing.description = "Updated web server address"
existing.tag = ["Web", "Production", "Updated"]

updated = client.address.update(existing)
```

### Delete an Address

Deletes an address object by ID.

```python
client.address.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating Multiple Address Types

Create different types of address objects for various network resources.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# IP/Netmask address for a network segment
client.address.create({
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network segment",
    "folder": "Texas",
    "tag": ["Internal", "Automation"]
})

# FQDN address for an external service
client.address.create({
    "name": "prod-server",
    "fqdn": "prod-server.example.com",
    "folder": "Texas",
    "description": "Production application server"
})

# IP Range for a DHCP pool
client.address.create({
    "name": "dhcp_pool",
    "ip_range": "192.168.1.100-192.168.1.200",
    "folder": "Texas",
    "description": "DHCP address pool"
})
```

### Filtering and Listing Addresses

Use filtering to find specific addresses within a large configuration.

```python
# Only return addresses defined exactly in 'Texas'
exact_addresses = client.address.list(
    folder="Texas",
    exact_match=True
)

# Exclude addresses from the 'All' folder
filtered = client.address.list(
    folder="Texas",
    exclude_folders=["All"]
)

# Combine filters
combined = client.address.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    types=["netmask"],
    tags=["Production"]
)

for addr in combined:
    print(f"Address: {addr.name} in {addr.folder}")
```

### Bulk Update with Commit

Update multiple addresses and commit the changes as a batch.

```python
# Update several addresses
for name in ["webserver", "prod-server"]:
    addr = client.address.fetch(name=name, folder="Texas")
    addr.tag = addr.tag + ["Reviewed"] if addr.tag else ["Reviewed"]
    client.address.update(addr)

# Commit changes
result = client.commit(
    folders=["Texas"],
    description="Tagged reviewed addresses",
    sync=True
)
print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_address = client.address.create({
        "name": "test_address",
        "ip_netmask": "192.168.1.0/24",
        "folder": "Texas",
        "description": "Test network segment",
        "tag": ["Test"]
    })
except InvalidObjectError as e:
    print(f"Invalid address data: {e.message}")
except NameNotUniqueError as e:
    print(f"Address name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Address not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Address still referenced: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Address Models](../../models/objects/address_models.md#Overview)
- [Address Group](address_group.md)
- [Tag](tag.md)
