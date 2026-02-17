# Tunnel Interface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Tunnel Interface Model Attributes](#tunnel-interface-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
7. [Managing Configuration Changes](#managing-configuration-changes)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Related Models](#related-models)

## Overview

The `TunnelInterface` class manages tunnel interface objects in Palo Alto Networks' Strata Cloud Manager. Tunnel interfaces are used for VPN tunnels (IPsec, GRE, etc.) and provide a logical interface for encrypted traffic.

## Core Methods

| Method     | Description                                                  | Parameters                                  | Return Type                        |
|------------|--------------------------------------------------------------|---------------------------------------------|------------------------------------|
| `create()` | Creates a new tunnel interface                               | `data: Dict[str, Any]`                      | `TunnelInterfaceResponseModel`     |
| `get()`    | Retrieves a tunnel interface by ID                           | `object_id: str`                            | `TunnelInterfaceResponseModel`     |
| `update()` | Updates an existing tunnel interface                         | `tunnel: TunnelInterfaceUpdateModel`        | `TunnelInterfaceResponseModel`     |
| `list()`   | Lists tunnel interfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters | `List[TunnelInterfaceResponseModel]` |
| `fetch()`  | Fetches a single tunnel interface by name within a container | `name: str`, `folder`, `snippet`, `device`  | `TunnelInterfaceResponseModel`     |
| `delete()` | Deletes a tunnel interface by ID                             | `object_id: str`                            | `None`                             |

## Tunnel Interface Model Attributes

| Attribute                      | Type         | Required | Default | Description                                      |
|--------------------------------|--------------|----------|---------|--------------------------------------------------|
| `name`                         | str          | Yes      | None    | Interface name (e.g., "tunnel.1")                |
| `id`                           | UUID         | Yes*     | None    | Unique identifier (*response/update only)        |
| `comment`                      | str          | No       | None    | Description. Max 1023 chars                      |
| `ip`                           | List[str]    | No       | None    | List of IPv4 addresses                           |
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

tunnel_interfaces = client.tunnel_interface
```

## Usage Examples

### Creating Tunnel Interfaces

```python
# Create tunnel interface for IPsec VPN
tunnel_data = {
    "name": "tunnel.1",
    "comment": "Site-to-Site VPN Tunnel",
    "ip": ["10.254.0.1/30"],
    "mtu": 1400,  # Lower MTU for encapsulation overhead
    "folder": "Interfaces"
}

result = client.tunnel_interface.create(tunnel_data)
print(f"Created tunnel: {result.id}")

# Create tunnel without IP (unnumbered)
unnumbered_tunnel = {
    "name": "tunnel.2",
    "comment": "GRE Tunnel",
    "mtu": 1476,
    "folder": "Interfaces"
}

result = client.tunnel_interface.create(unnumbered_tunnel)
```

### Retrieving Tunnel Interfaces

```python
# Fetch by name
tunnel = client.tunnel_interface.fetch(
    name="tunnel.1",
    folder="Interfaces"
)
print(f"Found: {tunnel.name}")

# Get by ID
tunnel_by_id = client.tunnel_interface.get(tunnel.id)
```

### Updating Tunnel Interfaces

```python
existing = client.tunnel_interface.fetch(name="tunnel.1", folder="Interfaces")

existing.mtu = 1380
existing.comment = "Updated VPN Tunnel"

updated = client.tunnel_interface.update(existing)
```

### Listing Tunnel Interfaces

```python
# List all tunnels
tunnels = client.tunnel_interface.list(folder="Interfaces")

for tunnel in tunnels:
    print(f"Name: {tunnel.name}, MTU: {tunnel.mtu}")
    if tunnel.ip:
        print(f"  IP: {', '.join(tunnel.ip)}")

# Filter by MTU
low_mtu = client.tunnel_interface.list(folder="Interfaces", mtu=1400)
```

### Deleting Tunnel Interfaces

```python
client.tunnel_interface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated tunnel interfaces",
    sync=True
)
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, ObjectNotPresentError

try:
    tunnel = client.tunnel_interface.create({
        "name": "tunnel.1",
        "mtu": 100,  # Error: MTU too low
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
```

## Best Practices

1. **MTU Settings** - Account for encapsulation overhead (typically 1400-1480 for IPsec)
2. **Naming** - Use descriptive names indicating the tunnel purpose
3. **IP Addressing** - Use /30 or /31 subnets for point-to-point tunnels
4. **Documentation** - Document the remote endpoint in comments

## Related Models

- [TunnelInterfaceCreateModel](../../models/network/tunnel_interface_models.md)
- [TunnelInterfaceUpdateModel](../../models/network/tunnel_interface_models.md)
- [TunnelInterfaceResponseModel](../../models/network/tunnel_interface_models.md)
