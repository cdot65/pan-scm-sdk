# VLAN Interface

The `VlanInterface` class manages VLAN interface objects in Palo Alto Networks' Strata Cloud Manager. VLAN interfaces are Layer 3 interfaces associated with VLAN objects, used for inter-VLAN routing. They support static IP addressing or DHCP, along with ARP and DDNS configuration.

## Class Overview

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

vlan_interfaces = client.vlan_interface
```

| Method     | Description                                                | Parameters                                  | Return Type                      |
|------------|------------------------------------------------------------|---------------------------------------------|----------------------------------|
| `create()` | Creates a new VLAN interface                               | `data: Dict[str, Any]`                      | `VlanInterfaceResponseModel`     |
| `get()`    | Retrieves a VLAN interface by ID                           | `object_id: str`                            | `VlanInterfaceResponseModel`     |
| `update()` | Updates an existing VLAN interface                         | `vlan: VlanInterfaceUpdateModel`            | `VlanInterfaceResponseModel`     |
| `list()`   | Lists VLAN interfaces with optional filtering              | `folder`, `snippet`, `device`, plus filters | `List[VlanInterfaceResponseModel]` |
| `fetch()`  | Fetches a single VLAN interface by name within a container | `name: str`, `folder`, `snippet`, `device`  | `VlanInterfaceResponseModel`     |
| `delete()` | Deletes a VLAN interface by ID                             | `object_id: str`                            | `None`                           |

### VLAN Interface Model Attributes

| Attribute                      | Type                    | Required | Default | Description                                      |
|--------------------------------|-------------------------|----------|---------|--------------------------------------------------|
| `name`                         | str                     | Yes      | None    | Interface name (e.g., "vlan.100")                |
| `id`                           | UUID                    | Yes*     | None    | Unique identifier (*response/update only)        |
| `vlan_tag`                     | str                     | No       | None    | VLAN tag (1-4096)                                |
| `comment`                      | str                     | No       | None    | Description. Max 1023 chars                      |
| `ip`                           | List[StaticIpEntry]     | No**     | None    | Static IP addresses                              |
| `dhcp_client`                  | DhcpClient              | No**     | None    | DHCP client configuration                        |
| `mtu`                          | int                     | No       | 1500    | MTU (576-9216)                                   |
| `interface_management_profile` | str                     | No       | None    | Management profile name. Max 31 chars            |
| `arp`                          | List[ArpEntryWithInterface] | No   | None    | Static ARP entries with interface                |
| `ddns_config`                  | DdnsConfig              | No       | None    | Dynamic DNS configuration                        |
| `folder`                       | str                     | No***    | None    | Folder location. Max 64 chars                    |
| `snippet`                      | str                     | No***    | None    | Snippet location. Max 64 chars                   |
| `device`                       | str                     | No***    | None    | Device location. Max 64 chars                    |

\* Only required for update and response models
\** Only one IP mode (static or DHCP) can be configured
\*** Exactly one container must be provided for create operations

### IP Addressing Modes

#### Static IP

```python
vlan_data = {
    "name": "vlan.100",
    "vlan_tag": "100",
    "ip": [{"name": "192.168.100.1/24"}],
    "mtu": 1500,
    "folder": "Interfaces"
}
```

#### DHCP

```python
vlan_data = {
    "name": "vlan.100",
    "vlan_tag": "100",
    "dhcp_client": {
        "enable": True,
        "create_default_route": True,
        "default_route_metric": 10
    },
    "folder": "Interfaces"
}
```

### Exceptions

| Exception                    | HTTP Code | Description                            |
|------------------------------|-----------|----------------------------------------|
| `InvalidObjectError`         | 400       | Invalid data or parameters             |
| `MissingQueryParameterError` | 400       | Missing required parameters            |
| `ObjectNotPresentError`      | 404       | Interface not found                    |
| `AuthenticationError`        | 401       | Authentication failed                  |
| `ServerError`                | 500       | Internal server error                  |

## Methods

### List VLAN Interfaces

```python
# List all VLAN interfaces
vlans = client.vlan_interface.list(folder="Interfaces")

for vlan in vlans:
    print(f"Name: {vlan.name}, Tag: {vlan.vlan_tag}")
    if vlan.ip:
        for ip in vlan.ip:
            print(f"  IP: {ip.name}")
    if vlan.dhcp_client:
        print(f"  DHCP: Enabled")

# Filter by VLAN tag
vlan100_list = client.vlan_interface.list(folder="Interfaces", vlan_tag="100")

# Filter by MTU
jumbo_vlans = client.vlan_interface.list(folder="Interfaces", mtu=9000)
```

### Fetch a VLAN Interface

```python
# Fetch by name
vlan = client.vlan_interface.fetch(
    name="vlan.100",
    folder="Interfaces"
)
print(f"Found: {vlan.name}, Tag: {vlan.vlan_tag}")

# Get by ID
vlan_by_id = client.vlan_interface.get(vlan.id)
```

### Create a VLAN Interface

```python
# Create VLAN interface with static IP
vlan_static = {
    "name": "vlan.100",
    "vlan_tag": "100",
    "comment": "Corporate LAN Gateway",
    "ip": [{"name": "10.100.0.1/24"}],
    "mtu": 1500,
    "interface_management_profile": "allow-ping",
    "arp": [
        {
            "name": "10.100.0.10",
            "hw_address": "00:11:22:33:44:55",
            "interface": "ethernet1/1"
        }
    ],
    "folder": "Interfaces"
}

result = client.vlan_interface.create(vlan_static)
print(f"Created VLAN interface: {result.id}")

# Create VLAN interface with DHCP
vlan_dhcp = {
    "name": "vlan.200",
    "vlan_tag": "200",
    "dhcp_client": {
        "enable": True,
        "create_default_route": False,
        "send_hostname": {
            "enable": True,
            "hostname": "firewall-vlan200"
        }
    },
    "folder": "Interfaces"
}

result = client.vlan_interface.create(vlan_dhcp)
```

### Update a VLAN Interface

```python
existing = client.vlan_interface.fetch(
    name="vlan.100",
    folder="Interfaces"
)

# Update MTU
existing.mtu = 9000

# Update comment
existing.comment = "Updated Corporate LAN Gateway"

# Add DDNS configuration
existing.ddns_config = {
    "ddns_enabled": True,
    "ddns_vendor": "dyndns",
    "ddns_hostname": "vlan100.example.com"
}

updated = client.vlan_interface.update(existing)
```

### Delete a VLAN Interface

```python
client.vlan_interface.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

#### Managing Configuration Changes

```python
result = client.commit(
    folders=["Interfaces"],
    description="Updated VLAN interfaces",
    sync=True
)

print(f"Commit job ID: {result.job_id}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, ObjectNotPresentError

try:
    vlan = client.vlan_interface.create({
        "name": "vlan.100",
        "vlan_tag": "100",
        "ip": [{"name": "10.0.0.1/24"}],
        "dhcp_client": {"enable": True},  # Error: both IP modes
        "folder": "Interfaces"
    })
except InvalidObjectError as e:
    print(f"Invalid configuration: {e.message}")
```

## Related Topics

- [VlanInterfaceCreateModel](../../models/network/vlan_interface_models.md)
- [VlanInterfaceUpdateModel](../../models/network/vlan_interface_models.md)
- [VlanInterfaceResponseModel](../../models/network/vlan_interface_models.md)
