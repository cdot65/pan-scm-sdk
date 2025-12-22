# Layer3 Subinterface Models

## Overview

The Layer3 Subinterface models provide structured validation for Layer 3 VLAN subinterface configuration. These subinterfaces support IP routing on VLAN-tagged traffic with static IP or DHCP addressing.

### Models

- `Layer3SubinterfaceCreateModel`: For creating new subinterfaces
- `Layer3SubinterfaceUpdateModel`: For updating existing subinterfaces (includes `id`)
- `Layer3SubinterfaceResponseModel`: Response model from API operations

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### Layer3SubinterfaceBaseModel

| Attribute                      | Type           | Required | Default | Description                               |
|--------------------------------|----------------|----------|---------|-------------------------------------------|
| `name`                         | str            | Yes      | None    | Interface name (e.g., "ethernet1/1.100")  |
| `tag`                          | str            | Yes      | None    | VLAN tag (1-4096)                         |
| `comment`                      | str            | No       | None    | Description (max 1023 chars)              |
| `ip`                           | List[StaticIp] | No*      | None    | Static IP addresses                       |
| `dhcp_client`                  | DhcpClient     | No*      | None    | DHCP client configuration                 |
| `mtu`                          | int            | No       | 1500    | MTU (576-9216)                            |
| `interface_management_profile` | str            | No       | None    | Management profile (max 31 chars)         |
| `arp`                          | List[ArpEntry] | No       | None    | Static ARP entries                        |
| `ddns_config`                  | DdnsConfig     | No       | None    | Dynamic DNS configuration                 |
| `folder`                       | str            | No**     | None    | Folder container                          |
| `snippet`                      | str            | No**     | None    | Snippet container                         |
| `device`                       | str            | No**     | None    | Device container                          |

\* Only one IP mode (static or DHCP) can be configured
\** Exactly one container required for create operations

## Model Validators

### IP Mode Validation

Ensures only one of `ip` or `dhcp_client` is configured:

```python
@model_validator(mode="after")
def validate_ip_mode(self) -> "Layer3SubinterfaceBaseModel":
    if self.ip and self.dhcp_client:
        raise ValueError("Only one IP addressing mode allowed")
    return self
```

## Usage Examples

### Static IP

```python
from scm.models.network import Layer3SubinterfaceCreateModel

subinterface = Layer3SubinterfaceCreateModel(
    name="ethernet1/1.100",
    tag="100",
    ip=[{"name": "192.168.100.1/24"}],
    mtu=1500,
    folder="Interfaces"
)
payload = subinterface.model_dump(exclude_unset=True)
```

### DHCP

```python
subinterface = Layer3SubinterfaceCreateModel(
    name="ethernet1/1.200",
    tag="200",
    dhcp_client={
        "enable": True,
        "create_default_route": True
    },
    folder="Interfaces"
)
```
