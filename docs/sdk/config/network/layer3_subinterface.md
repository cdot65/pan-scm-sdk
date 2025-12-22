# Layer3 Subinterface Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Layer3 Subinterface Model Attributes](#layer3-subinterface-model-attributes)
4. [IP Addressing Modes](#ip-addressing-modes)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
8. [Managing Configuration Changes](#managing-configuration-changes)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)
11. [Related Models](#related-models)

## Overview

The `Layer3Subinterface` class manages Layer 3 subinterface objects in Palo Alto Networks' Strata Cloud Manager. Layer 3 subinterfaces operate at the network layer, supporting IP routing on VLAN-tagged traffic. They support static IP addressing or DHCP.

## Core Methods

| Method     | Description                                                      | Parameters                                    | Return Type                           |
|------------|------------------------------------------------------------------|-----------------------------------------------|---------------------------------------|
| `create()` | Creates a new Layer 3 subinterface                               | `data: Dict[str, Any]`                        | `Layer3SubinterfaceResponseModel`     |
| `get()`    | Retrieves a Layer 3 subinterface by ID                           | `object_id: str`                              | `Layer3SubinterfaceResponseModel`     |
| `update()` | Updates an existing Layer 3 subinterface                         | `subinterface: Layer3SubinterfaceUpdateModel` | `Layer3SubinterfaceResponseModel`     |
| `list()`   | Lists Layer 3 subinterfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters   | `List[Layer3SubinterfaceResponseModel]` |
| `fetch()`  | Fetches a single Layer 3 subinterface by name within a container | `name: str`, `folder`, `snippet`, `device`    | `Layer3SubinterfaceResponseModel`     |
| `delete()` | Deletes a Layer 3 subinterface by ID                             | `object_id: str`                              | `None`                                |

## Layer3 Subinterface Model Attributes

| Attribute                      | Type           | Required | Default | Description                                      |
|--------------------------------|----------------|----------|---------|--------------------------------------------------|
| `name`                         | str            | Yes      | None    | Interface name (e.g., "ethernet1/1.100")         |
| `id`                           | UUID           | Yes*     | None    | Unique identifier (*response/update only)        |
| `tag`                          | str            | Yes      | None    | VLAN tag (1-4096)                                |
| `comment`                      | str            | No       | None    | Description. Max 1023 chars                      |
| `ip`                           | List[StaticIp] | No**     | None    | Static IP addresses                              |
| `dhcp_client`                  | DhcpClient     | No**     | None    | DHCP client configuration                        |
| `mtu`                          | int            | No       | 1500    | MTU (576-9216)                                   |
| `interface_management_profile` | str            | No       | None    | Management profile name. Max 31 chars            |
| `arp`                          | List[ArpEntry] | No       | None    | Static ARP entries                               |
| `ddns_config`                  | DdnsConfig     | No       | None    | Dynamic DNS configuration                        |
| `folder`                       | str            | No***    | None    | Folder location. Max 64 chars                    |
| `snippet`                      | str            | No***    | None    | Snippet location. Max 64 chars                   |
| `device`                       | str            | No***    | None    | Device location. Max 64 chars                    |

\* Only required for update and response models
\** Only one IP mode (static or DHCP) can be configured
\*** Exactly one container must be provided for create operations

## IP Addressing Modes

### Static IP

```python
subinterface_data = {
    "name": "ethernet1/1.100",
    "tag": "100",
    "ip": [{"name": "192.168.100.1/24"}],
    "mtu": 1500,
    "folder": "Interfaces"
}
```

### DHCP

```python
subinterface_data = {
    "name": "ethernet1/1.100",
    "tag": "100",
    "dhcp_client": {
        "enable": True,
        "create_default_route": True,
        "default_route_metric": 10
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

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

layer3_subinterfaces = client.layer3_subinterface
```

## Usage Examples

### Creating Layer3 Subinterfaces

```python
# Create with static IP
static_subinterface = {
    "name": "ethernet1/1.100",
    "tag": "100",
    "comment": "VLAN 100 Gateway",
    "ip": [{"name": "192.168.100.1/24"}],
    "mtu": 1500,
    "interface_management_profile": "allow-ping",
    "arp": [
        {"name": "192.168.100.10", "hw_address": "00:11:22:33:44:55"}
    ],
    "folder": "Interfaces"
}

result = client.layer3_subinterface.create(static_subinterface)
print(f"Created: {result.id}")

# Create with DHCP
dhcp_subinterface = {
    "name": "ethernet1/2.200",
    "tag": "200",
    "dhcp_client": {
        "enable": True,
        "create_default_route": False
    },
    "folder": "Interfaces"
}

result = client.layer3_subinterface.create(dhcp_subinterface)
```

### Retrieving Layer3 Subinterfaces

```python
# Fetch by name
subinterface = client.layer3_subinterface.fetch(
    name="ethernet1/1.100",
    folder="Interfaces"
)
print(f"Found: {subinterface.name}, VLAN: {subinterface.tag}")

# Get by ID
subinterface_by_id = client.layer3_subinterface.get(subinterface.id)
```

### Updating Layer3 Subinterfaces

```python
existing = client.layer3_subinterface.fetch(
    name="ethernet1/1.100",
    folder="Interfaces"
)

# Update MTU
existing.mtu = 9000

# Add static ARP entry
if existing.arp is None:
    existing.arp = []
existing.arp.append({"name": "192.168.100.20", "hw_address": "00:11:22:33:44:66"})

updated = client.layer3_subinterface.update(existing)
```

### Listing Layer3 Subinterfaces

```python
# List all Layer 3 subinterfaces
subinterfaces = client.layer3_subinterface.list(folder="Interfaces")

for sub in subinterfaces:
    print(f"Name: {sub.name}, VLAN: {sub.tag}")
    if sub.ip:
        for ip in sub.ip:
            print(f"  IP: {ip.name}")

# Filter by VLAN tag
vlan100 = client.layer3_subinterface.list(folder="Interfaces", tag="100")

# Filter by MTU
jumbo = client.layer3_subinterface.list(folder="Interfaces", mtu=9000)
```

### Deleting Layer3 Subinterfaces

```python
client.layer3_subinterface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated Layer 3 subinterfaces",
    sync=True
)
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError

try:
    subinterface = client.layer3_subinterface.create({
        "name": "ethernet1/1.100",
        "tag": "100",
        "ip": [{"name": "192.168.100.1/24"}],
        "dhcp_client": {"enable": True},  # Error: both modes
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
```

## Best Practices

1. **IP Mode** - Choose only one IP addressing mode (static or DHCP)
2. **VLAN Planning** - Coordinate VLAN tags with network infrastructure
3. **MTU** - Consider jumbo frames (9000) for high-throughput VLANs
4. **ARP Entries** - Add static ARP for critical devices
5. **Management Profile** - Apply appropriate management profiles

## Related Models

- [Layer3SubinterfaceCreateModel](../../models/network/layer3_subinterface_models.md)
- [Layer3SubinterfaceUpdateModel](../../models/network/layer3_subinterface_models.md)
- [Layer3SubinterfaceResponseModel](../../models/network/layer3_subinterface_models.md)
