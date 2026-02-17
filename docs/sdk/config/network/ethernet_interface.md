# Ethernet Interface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Ethernet Interface Model Attributes](#ethernet-interface-model-attributes)
4. [Interface Modes](#interface-modes)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating Ethernet Interfaces](#creating-ethernet-interfaces)
    - [Retrieving Ethernet Interfaces](#retrieving-ethernet-interfaces)
    - [Updating Ethernet Interfaces](#updating-ethernet-interfaces)
    - [Listing Ethernet Interfaces](#listing-ethernet-interfaces)
    - [Filtering Responses](#filtering-responses)
    - [Deleting Ethernet Interfaces](#deleting-ethernet-interfaces)
8. [Managing Configuration Changes](#managing-configuration-changes)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `EthernetInterface` class manages ethernet interface objects in Palo Alto Networks' Strata Cloud Manager. Ethernet interfaces support three modes: Layer 2, Layer 3, and TAP. Layer 3 mode supports static IP, DHCP, or PPPoE addressing. The class provides methods for CRUD operations and enforces container requirements using `folder`, `snippet`, or `device` parameters.

## Important: Naming Convention

Ethernet interface names in SCM must start with `$` (dollar sign) as they are variable references. The `default_value` field specifies the physical interface assignment.

```python
# Correct usage
{
    "name": "$wan-interface",        # Variable name (required $ prefix)
    "default_value": "ethernet1/1",  # Physical interface assignment
    "folder": "Interfaces"
}
```

## Core Methods

| Method     | Description                                                    | Parameters                                  | Return Type                         |
|------------|----------------------------------------------------------------|---------------------------------------------|-------------------------------------|
| `create()` | Creates a new ethernet interface                               | `data: Dict[str, Any]`                      | `EthernetInterfaceResponseModel`    |
| `get()`    | Retrieves an ethernet interface by ID                          | `object_id: str`                            | `EthernetInterfaceResponseModel`    |
| `update()` | Updates an existing ethernet interface                         | `ethernet: EthernetInterfaceUpdateModel`    | `EthernetInterfaceResponseModel`    |
| `list()`   | Lists ethernet interfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters | `List[EthernetInterfaceResponseModel]` |
| `fetch()`  | Fetches a single ethernet interface by name within a container | `name: str`, `folder`, `snippet`, `device`  | `EthernetInterfaceResponseModel`    |
| `delete()` | Deletes an ethernet interface by ID                            | `object_id: str`                            | `None`                              |

## Ethernet Interface Model Attributes

| Attribute       | Type            | Required | Default  | Description                                         |
|-----------------|-----------------|----------|----------|-----------------------------------------------------|
| `name`          | str             | Yes      | None     | Variable name (must start with $, max 63 chars)     |
| `default_value` | str             | No       | None     | Physical interface (e.g., "ethernet1/1")            |
| `id`            | UUID            | Yes*     | None     | Unique identifier (*response/update only)           |
| `comment`       | str             | No       | None     | Description. Max 1023 chars                         |
| `link_speed`    | str             | No       | "auto"   | Link speed (auto, 10, 100, 1000, 10000, etc.)       |
| `link_duplex`   | str             | No       | "auto"   | Link duplex (auto, half, full)                      |
| `link_state`    | str             | No       | "auto"   | Link state (auto, up, down)                         |
| `poe`           | PoeConfig       | No       | None     | Power over Ethernet configuration                   |
| `layer2`        | EthernetLayer2  | No**     | None     | Layer 2 mode configuration                          |
| `layer3`        | EthernetLayer3  | No**     | None     | Layer 3 mode configuration                          |
| `tap`           | EthernetTap     | No**     | None     | TAP mode configuration                              |
| `folder`        | str             | No***    | None     | Folder location. Max 64 chars                       |
| `snippet`       | str             | No***    | None     | Snippet location. Max 64 chars                      |
| `device`        | str             | No***    | None     | Device location. Max 64 chars                       |

\* Only required for update and response models
\** Only one mode (layer2/layer3/tap) can be configured at a time
\*** Exactly one container must be provided for create operations

## Interface Modes

### Layer 2 Mode

Layer 2 mode operates at the data link layer with VLAN tagging and LLDP support.

```python
interface_data = {
    "name": "$layer2-interface",
    "layer2": {
        "vlan_tag": "100",
        "lldp": {"enable": True}
    },
    "folder": "Interfaces"
}
```

### Layer 3 Mode with Static IP

Layer 3 mode with static IP addresses for routed interfaces.

```python
interface_data = {
    "name": "$wan-interface",
    "default_value": "ethernet1/1",
    "layer3": {
        "ip": [{"name": "192.168.1.1/24"}],
        "mtu": 1500,
        "interface_management_profile": "allow-ping"
    },
    "folder": "Interfaces"
}
```

### Layer 3 Mode with DHCP

Layer 3 mode using DHCP for dynamic IP assignment.

```python
interface_data = {
    "name": "$dhcp-interface",
    "default_value": "ethernet1/1",
    "layer3": {
        "dhcp_client": {
            "enable": True,
            "create_default_route": True,
            "default_route_metric": 10
        }
    },
    "folder": "Interfaces"
}
```

### Layer 3 Mode with PPPoE

Layer 3 mode using PPPoE for ISP connections.

```python
interface_data = {
    "name": "$pppoe-interface",
    "default_value": "ethernet1/1",
    "layer3": {
        "pppoe": {
            "enable": True,
            "username": "user@isp.com",
            "password": "secret",
            "authentication": "auto"
        }
    },
    "folder": "Interfaces"
}
```

### TAP Mode

TAP mode for traffic monitoring without affecting traffic flow.

```python
interface_data = {
    "name": "$tap-interface",
    "tap": {},
    "folder": "Interfaces"
}
```

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

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access ethernet interfaces via the client
ethernet_interfaces = client.ethernet_interface
```

## Usage Examples

### Creating Ethernet Interfaces

```python
# Create Layer 3 interface with static IP
layer3_interface = {
    "name": "$wan-interface",
    "default_value": "ethernet1/1",
    "comment": "WAN Interface",
    "link_speed": "1000",
    "link_duplex": "full",
    "layer3": {
        "ip": [{"name": "203.0.113.1/24"}],
        "mtu": 1500,
        "arp": [
            {"name": "203.0.113.254", "hw_address": "00:11:22:33:44:55"}
        ]
    },
    "folder": "Interfaces"
}

result = client.ethernet_interface.create(layer3_interface)
print(f"Created interface: {result.name} ({result.id})")

# Create Layer 2 interface
layer2_interface = {
    "name": "$layer2-interface",
    "layer2": {
        "vlan_tag": "200",
        "lldp": {"enable": True}
    },
    "folder": "Interfaces"
}

result = client.ethernet_interface.create(layer2_interface)
```

### Retrieving Ethernet Interfaces

```python
# Fetch by name
interface = client.ethernet_interface.fetch(
    name="$wan-interface",
    folder="Interfaces"
)
print(f"Found interface: {interface.name}")

# Get by ID
interface_by_id = client.ethernet_interface.get(interface.id)
```

### Updating Ethernet Interfaces

```python
# Fetch existing interface
existing = client.ethernet_interface.fetch(
    name="$wan-interface",
    folder="Interfaces"
)

# Modify attributes
existing.comment = "Updated WAN Interface"
if existing.layer3:
    existing.layer3.mtu = 9000

# Update
updated = client.ethernet_interface.update(existing)
```

### Listing Ethernet Interfaces

```python
# List all interfaces in a folder
interfaces = client.ethernet_interface.list(folder="Interfaces")

for iface in interfaces:
    print(f"Name: {iface.name}")
    if iface.layer2:
        print(f"  Mode: Layer 2, VLAN: {iface.layer2.vlan_tag}")
    elif iface.layer3:
        print(f"  Mode: Layer 3")
    elif iface.tap:
        print(f"  Mode: TAP")

# Filter by mode
layer3_interfaces = client.ethernet_interface.list(
    folder="Interfaces",
    mode="layer3"
)

# Filter by link speed
gigabit_interfaces = client.ethernet_interface.list(
    folder="Interfaces",
    link_speed="1000"
)
```

### Filtering Responses

```python
# Exact match only
exact_interfaces = client.ethernet_interface.list(
    folder="Interfaces",
    exact_match=True
)

# Exclude specific folders
filtered = client.ethernet_interface.list(
    folder="Interfaces",
    exclude_folders=["All"]
)
```

### Deleting Ethernet Interfaces

```python
client.ethernet_interface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
# Commit changes
result = client.commit(
    folders=["Interfaces"],
    description="Updated ethernet interfaces",
    sync=True
)

print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError
)

try:
    interface = client.ethernet_interface.create({
        "name": "$test-interface",
        "layer2": {"vlan_tag": "100"},
        "layer3": {"ip": [{"name": "10.0.0.1/24"}]},  # Error: both modes
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")

# Name pattern validation
try:
    interface = client.ethernet_interface.create({
        "name": "ethernet1/1",  # Error: missing $ prefix
        "folder": "Interfaces"
    })
except ValidationError as e:
    print("Name must start with $ (dollar sign)")
```

## Best Practices

1. **Naming Convention** - Always use `$` prefix for interface names (e.g., `$wan-interface`)
2. **Physical Interface** - Use `default_value` to specify the physical interface (e.g., `ethernet1/1`)
3. **Mode Selection** - Choose only one mode (layer2, layer3, or tap) per interface
4. **IP Addressing** - In layer3 mode, use only one IP method (static, DHCP, or PPPoE)
5. **Link Settings** - Set link_speed and link_duplex to "auto" unless specific values are required
6. **Container Management** - Always specify exactly one container (folder/snippet/device)
7. **Error Handling** - Implement comprehensive error handling for all operations

## Related Models

- [EthernetInterfaceCreateModel](../../models/network/ethernet_interface_models.md)
- [EthernetInterfaceUpdateModel](../../models/network/ethernet_interface_models.md)
- [EthernetInterfaceResponseModel](../../models/network/ethernet_interface_models.md)
- [EthernetLayer2](../../models/network/ethernet_interface_models.md)
- [EthernetLayer3](../../models/network/ethernet_interface_models.md)
