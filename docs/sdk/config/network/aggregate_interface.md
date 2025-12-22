# Aggregate Interface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Aggregate Interface Model Attributes](#aggregate-interface-model-attributes)
4. [Interface Modes](#interface-modes)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating Aggregate Interfaces](#creating-aggregate-interfaces)
    - [Retrieving Aggregate Interfaces](#retrieving-aggregate-interfaces)
    - [Updating Aggregate Interfaces](#updating-aggregate-interfaces)
    - [Listing Aggregate Interfaces](#listing-aggregate-interfaces)
    - [Deleting Aggregate Interfaces](#deleting-aggregate-interfaces)
8. [Managing Configuration Changes](#managing-configuration-changes)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `AggregateInterface` class manages aggregate ethernet interface (ae) objects in Palo Alto Networks' Strata Cloud Manager. Aggregate interfaces bundle multiple physical interfaces into a single logical interface for link redundancy and increased bandwidth. They support Layer 2 and Layer 3 modes with LACP (Link Aggregation Control Protocol) configuration.

## Core Methods

| Method     | Description                                                     | Parameters                                   | Return Type                          |
|------------|-----------------------------------------------------------------|----------------------------------------------|--------------------------------------|
| `create()` | Creates a new aggregate interface                               | `data: Dict[str, Any]`                       | `AggregateInterfaceResponseModel`    |
| `get()`    | Retrieves an aggregate interface by ID                          | `object_id: str`                             | `AggregateInterfaceResponseModel`    |
| `update()` | Updates an existing aggregate interface                         | `aggregate: AggregateInterfaceUpdateModel`   | `AggregateInterfaceResponseModel`    |
| `list()`   | Lists aggregate interfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters  | `List[AggregateInterfaceResponseModel]` |
| `fetch()`  | Fetches a single aggregate interface by name within a container | `name: str`, `folder`, `snippet`, `device`   | `AggregateInterfaceResponseModel`    |
| `delete()` | Deletes an aggregate interface by ID                            | `object_id: str`                             | `None`                               |

## Aggregate Interface Model Attributes

| Attribute      | Type            | Required | Default | Description                                      |
|----------------|-----------------|----------|---------|--------------------------------------------------|
| `name`         | str             | Yes      | None    | Interface name (e.g., "ae1")                     |
| `id`           | UUID            | Yes*     | None    | Unique identifier (*response/update only)        |
| `comment`      | str             | No       | None    | Description. Max 1023 chars                      |
| `layer2`       | AggregateLayer2 | No**     | None    | Layer 2 mode configuration                       |
| `layer3`       | AggregateLayer3 | No**     | None    | Layer 3 mode configuration                       |
| `folder`       | str             | No***    | None    | Folder location. Max 64 chars                    |
| `snippet`      | str             | No***    | None    | Snippet location. Max 64 chars                   |
| `device`       | str             | No***    | None    | Device location. Max 64 chars                    |

\* Only required for update and response models
\** Only one mode (layer2/layer3) can be configured at a time
\*** Exactly one container must be provided for create operations

### LACP Configuration Options

| Attribute           | Type   | Default  | Description                              |
|---------------------|--------|----------|------------------------------------------|
| `enable`            | bool   | False    | Enable LACP                              |
| `fast_failover`     | bool   | False    | Enable fast failover                     |
| `mode`              | str    | "passive"| LACP mode (passive/active)               |
| `transmission_rate` | str    | "slow"   | Transmission rate (fast/slow)            |
| `system_priority`   | int    | 32768    | System priority (1-65535)                |
| `max_ports`         | int    | 8        | Maximum ports (1-8)                      |

## Interface Modes

### Layer 2 Mode

Layer 2 mode with VLAN tagging and LACP support.

```python
interface_data = {
    "name": "ae1",
    "layer2": {
        "vlan_tag": "100",
        "lacp": {
            "enable": True,
            "mode": "active"
        }
    },
    "folder": "Interfaces"
}
```

### Layer 3 Mode with Static IP

Layer 3 mode with static IP addresses.

```python
interface_data = {
    "name": "ae1",
    "layer3": {
        "ip": [{"name": "10.0.0.1/24"}],
        "mtu": 9000,
        "lacp": {
            "enable": True,
            "mode": "active",
            "fast_failover": True
        }
    },
    "folder": "Interfaces"
}
```

### Layer 3 Mode with DHCP

Layer 3 mode using DHCP for dynamic IP assignment.

```python
interface_data = {
    "name": "ae1",
    "layer3": {
        "dhcp_client": {
            "enable": True,
            "create_default_route": True
        },
        "lacp": {"enable": True}
    },
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

# Access aggregate interfaces via the client
aggregate_interfaces = client.aggregate_interface
```

## Usage Examples

### Creating Aggregate Interfaces

```python
# Create Layer 3 aggregate with LACP
layer3_aggregate = {
    "name": "ae1",
    "comment": "Primary link aggregation",
    "layer3": {
        "ip": [{"name": "10.0.0.1/24"}],
        "mtu": 9000,
        "lacp": {
            "enable": True,
            "mode": "active",
            "fast_failover": True,
            "transmission_rate": "fast",
            "max_ports": 4
        }
    },
    "folder": "Interfaces"
}

result = client.aggregate_interface.create(layer3_aggregate)
print(f"Created aggregate interface: {result.id}")

# Create Layer 2 aggregate
layer2_aggregate = {
    "name": "ae2",
    "layer2": {
        "vlan_tag": "200",
        "lacp": {"enable": True, "mode": "passive"}
    },
    "folder": "Interfaces"
}

result = client.aggregate_interface.create(layer2_aggregate)
```

### Retrieving Aggregate Interfaces

```python
# Fetch by name
interface = client.aggregate_interface.fetch(
    name="ae1",
    folder="Interfaces"
)
print(f"Found aggregate interface: {interface.name}")

# Get by ID
interface_by_id = client.aggregate_interface.get(interface.id)
```

### Updating Aggregate Interfaces

```python
# Fetch existing interface
existing = client.aggregate_interface.fetch(
    name="ae1",
    folder="Interfaces"
)

# Modify LACP settings
if existing.layer3 and existing.layer3.lacp:
    existing.layer3.lacp.fast_failover = True
    existing.layer3.lacp.max_ports = 8

# Update
updated = client.aggregate_interface.update(existing)
```

### Listing Aggregate Interfaces

```python
# List all aggregate interfaces
interfaces = client.aggregate_interface.list(folder="Interfaces")

for iface in interfaces:
    print(f"Name: {iface.name}")
    if iface.layer2:
        print(f"  Mode: Layer 2")
    elif iface.layer3:
        print(f"  Mode: Layer 3")
        if iface.layer3.lacp:
            print(f"  LACP: {iface.layer3.lacp.mode}")

# Filter by mode
layer3_only = client.aggregate_interface.list(
    folder="Interfaces",
    mode="layer3"
)
```

### Deleting Aggregate Interfaces

```python
client.aggregate_interface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated aggregate interfaces",
    sync=True
)

print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    interface = client.aggregate_interface.create({
        "name": "ae1",
        "layer2": {"vlan_tag": "100"},
        "layer3": {"ip": [{"name": "10.0.0.1/24"}]},  # Error: both modes
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
```

## Best Practices

1. **LACP Configuration** - Enable LACP for proper link aggregation with bonded interfaces
2. **Mode Selection** - Choose only one mode (layer2 or layer3) per aggregate interface
3. **Fast Failover** - Enable fast_failover for critical links
4. **Port Limits** - Set max_ports based on your physical port availability
5. **Container Management** - Always specify exactly one container

## Related Models

- [AggregateInterfaceCreateModel](../../models/network/aggregate_interface_models.md)
- [AggregateInterfaceUpdateModel](../../models/network/aggregate_interface_models.md)
- [AggregateInterfaceResponseModel](../../models/network/aggregate_interface_models.md)
- [AggregateLayer2](../../models/network/aggregate_interface_models.md)
- [AggregateLayer3](../../models/network/aggregate_interface_models.md)
