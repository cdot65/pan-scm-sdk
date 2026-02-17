# Loopback Interface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Loopback Interface Model Attributes](#loopback-interface-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
7. [Managing Configuration Changes](#managing-configuration-changes)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `LoopbackInterface` class manages loopback interface objects in Palo Alto Networks' Strata Cloud Manager. Loopback interfaces are virtual interfaces that are always up and can be used for management access, BGP peering, and other services that require a stable IP address not tied to a physical interface.

## Core Methods

| Method     | Description                                                    | Parameters                                  | Return Type                         |
|------------|----------------------------------------------------------------|---------------------------------------------|-------------------------------------|
| `create()` | Creates a new loopback interface                               | `data: Dict[str, Any]`                      | `LoopbackInterfaceResponseModel`    |
| `get()`    | Retrieves a loopback interface by ID                           | `object_id: str`                            | `LoopbackInterfaceResponseModel`    |
| `update()` | Updates an existing loopback interface                         | `loopback: LoopbackInterfaceUpdateModel`    | `LoopbackInterfaceResponseModel`    |
| `list()`   | Lists loopback interfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters | `List[LoopbackInterfaceResponseModel]` |
| `fetch()`  | Fetches a single loopback interface by name within a container | `name: str`, `folder`, `snippet`, `device`  | `LoopbackInterfaceResponseModel`    |
| `delete()` | Deletes a loopback interface by ID                             | `object_id: str`                            | `None`                              |

## Loopback Interface Model Attributes

| Attribute                      | Type         | Required | Default | Description                                      |
|--------------------------------|--------------|----------|---------|--------------------------------------------------|
| `name`                         | str          | Yes      | None    | Interface name (e.g., "loopback.1")              |
| `id`                           | UUID         | Yes*     | None    | Unique identifier (*response/update only)        |
| `comment`                      | str          | No       | None    | Description. Max 1023 chars                      |
| `ip`                           | List[str]    | No       | None    | List of IPv4 addresses (e.g., ["10.0.0.1/32"])   |
| `ipv6`                         | Ipv6Config   | No       | None    | IPv6 configuration                               |
| `mtu`                          | int          | No       | 1500    | MTU (576-9216)                                   |
| `interface_management_profile` | str          | No       | None    | Management profile name. Max 31 chars            |
| `folder`                       | str          | No**     | None    | Folder location. Max 64 chars                    |
| `snippet`                      | str          | No**     | None    | Snippet location. Max 64 chars                   |
| `device`                       | str          | No**     | None    | Device location. Max 64 chars                    |

\* Only required for update and response models
\** Exactly one container must be provided for create operations

## Exceptions

| Exception                    | HTTP Code | Description                            |
|------------------------------|-----------|----------------------------------------|
| `InvalidObjectError`         | 400       | Invalid data or parameters             |
| `MissingQueryParameterError` | 400       | Missing required parameters            |
| `ObjectNotPresentError`      | 404       | Interface not found                    |
| `AuthenticationError`        | 401       | Authentication failed                  |
| `ServerError`                | 500       | Internal server error                  |

## Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

loopback_interfaces = client.loopback_interface
```

## Usage Examples

### Creating Loopback Interfaces

```python
# Create loopback with IPv4
loopback_data = {
    "name": "loopback.1",
    "comment": "Management loopback",
    "ip": ["10.0.0.1/32"],
    "interface_management_profile": "allow-ping",
    "folder": "Interfaces"
}

result = client.loopback_interface.create(loopback_data)
print(f"Created loopback: {result.id}")

# Create loopback with IPv6
loopback_ipv6 = {
    "name": "loopback.2",
    "ip": ["192.168.1.1/32"],
    "ipv6": {
        "enabled": True,
        "address": [{"name": "2001:db8::1/128"}]
    },
    "folder": "Interfaces"
}

result = client.loopback_interface.create(loopback_ipv6)
```

### Retrieving Loopback Interfaces

```python
# Fetch by name
loopback = client.loopback_interface.fetch(
    name="loopback.1",
    folder="Interfaces"
)
print(f"Found: {loopback.name}, IP: {loopback.ip}")

# Get by ID
loopback_by_id = client.loopback_interface.get(loopback.id)
```

### Updating Loopback Interfaces

```python
existing = client.loopback_interface.fetch(name="loopback.1", folder="Interfaces")

# Add additional IP
if existing.ip:
    existing.ip.append("10.0.0.2/32")
else:
    existing.ip = ["10.0.0.2/32"]

updated = client.loopback_interface.update(existing)
```

### Listing Loopback Interfaces

```python
# List all loopbacks
loopbacks = client.loopback_interface.list(folder="Interfaces")

for lb in loopbacks:
    print(f"Name: {lb.name}")
    if lb.ip:
        print(f"  IPv4: {', '.join(lb.ip)}")

# Filter by MTU
large_mtu = client.loopback_interface.list(folder="Interfaces", mtu=9000)
```

### Deleting Loopback Interfaces

```python
client.loopback_interface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated loopback interfaces",
    sync=True
)
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, ObjectNotPresentError

try:
    loopback = client.loopback_interface.fetch(
        name="nonexistent",
        folder="Interfaces"
    )
except ObjectNotPresentError as e:
    print(f"Interface not found: {e.message}")
```

## Best Practices

1. **Naming** - Use descriptive names like "loopback.mgmt" or "loopback.bgp"
2. **IP Addresses** - Use /32 for IPv4 and /128 for IPv6 on loopbacks
3. **Management Profile** - Apply interface management profiles for security
4. **Documentation** - Use comments to document the purpose of each loopback

## Related Models

- [LoopbackInterfaceCreateModel](../../models/network/loopback_interface_models.md)
- [LoopbackInterfaceUpdateModel](../../models/network/loopback_interface_models.md)
- [LoopbackInterfaceResponseModel](../../models/network/loopback_interface_models.md)
