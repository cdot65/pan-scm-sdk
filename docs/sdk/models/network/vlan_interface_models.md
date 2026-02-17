# VLAN Interface Models

## Overview

The VLAN Interface models provide structured validation for VLAN interface configuration. VLAN interfaces are Layer 3 interfaces for inter-VLAN routing, supporting static IP or DHCP addressing with ARP and DDNS configuration.

### Models

- `VlanInterfaceCreateModel`: For creating new VLAN interfaces
- `VlanInterfaceUpdateModel`: For updating existing interfaces (includes `id`)
- `VlanInterfaceResponseModel`: Response model from API operations

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### VlanInterfaceBaseModel

| Attribute                      | Type                    | Required | Default | Description                               |
|--------------------------------|-------------------------|----------|---------|-------------------------------------------|
| `name`                         | str                     | Yes      | None    | Interface name (e.g., "vlan.100")         |
| `vlan_tag`                     | str                     | No       | None    | VLAN tag (1-4096)                         |
| `comment`                      | str                     | No       | None    | Description (max 1023 chars)              |
| `ip`                           | List[StaticIpEntry]     | No*      | None    | Static IP addresses                       |
| `dhcp_client`                  | DhcpClient              | No*      | None    | DHCP client configuration                 |
| `mtu`                          | int                     | No       | 1500    | MTU (576-9216)                            |
| `interface_management_profile` | str                     | No       | None    | Management profile (max 31 chars)         |
| `arp`                          | List[ArpEntryWithInterface] | No   | None    | Static ARP entries                        |
| `ddns_config`                  | DdnsConfig              | No       | None    | Dynamic DNS configuration                 |
| `folder`                       | str                     | No**     | None    | Folder container                          |
| `snippet`                      | str                     | No**     | None    | Snippet container                         |
| `device`                       | str                     | No**     | None    | Device container                          |

\* Only one IP mode (static or DHCP) can be configured
\** Exactly one container required for create operations

### ArpEntryWithInterface

| Attribute   | Type | Required | Description                   |
|-------------|------|----------|-------------------------------|
| `name`      | str  | Yes      | IP address                    |
| `hw_address`| str  | No       | MAC address                   |
| `interface` | str  | No       | Associated interface          |

## Model Validators

### IP Mode Validation

Ensures only one of `ip` or `dhcp_client` is configured:

```python
@model_validator(mode="after")
def validate_ip_mode(self) -> "VlanInterfaceBaseModel":
    if self.ip and self.dhcp_client:
        raise ValueError("Only one IP addressing mode allowed")
    return self
```

## Usage Examples

### Static IP

```python
from scm.models.network import VlanInterfaceCreateModel

vlan = VlanInterfaceCreateModel(
    name="vlan.100",
    vlan_tag="100",
    ip=[{"name": "10.100.0.1/24"}],
    mtu=1500,
    arp=[
        {"name": "10.100.0.10", "hw_address": "00:11:22:33:44:55", "interface": "ethernet1/1"}
    ],
    folder="Interfaces"
)
payload = vlan.model_dump(exclude_unset=True)
```

### DHCP with DDNS

```python
vlan = VlanInterfaceCreateModel(
    name="vlan.200",
    vlan_tag="200",
    dhcp_client={
        "enable": True,
        "create_default_route": False
    },
    ddns_config={
        "ddns_enabled": True,
        "ddns_vendor": "dyndns",
        "ddns_hostname": "vlan200.example.com"
    },
    folder="Interfaces"
)
```
