# Aggregate Interface Models

## Overview

The Aggregate Interface models provide structured validation for aggregate (bonded) ethernet interface configuration. These models support Layer 2 and Layer 3 modes with LACP (Link Aggregation Control Protocol) configuration.

### Models

- `AggregateInterfaceCreateModel`: For creating new aggregate interfaces
- `AggregateInterfaceUpdateModel`: For updating existing interfaces (includes `id`)
- `AggregateInterfaceResponseModel`: Response model from API operations
- `AggregateLayer2`: Layer 2 mode configuration
- `AggregateLayer3`: Layer 3 mode configuration

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### AggregateInterfaceBaseModel

| Attribute      | Type            | Required | Default | Description                              |
|----------------|-----------------|----------|---------|------------------------------------------|
| `name`         | str             | Yes      | None    | Interface name (e.g., "ae1")             |
| `comment`      | str             | No       | None    | Description (max 1023 chars)             |
| `layer2`       | AggregateLayer2 | No*      | None    | Layer 2 mode configuration               |
| `layer3`       | AggregateLayer3 | No*      | None    | Layer 3 mode configuration               |
| `folder`       | str             | No**     | None    | Folder container                         |
| `snippet`      | str             | No**     | None    | Snippet container                        |
| `device`       | str             | No**     | None    | Device container                         |

\* Only one mode can be configured (oneOf validation)
\** Exactly one container required for create operations

### AggregateLayer2

| Attribute  | Type       | Required | Default | Description         |
|------------|------------|----------|---------|---------------------|
| `vlan_tag` | str        | No       | None    | VLAN tag (1-4096)   |
| `lacp`     | LacpConfig | No       | None    | LACP configuration  |

### AggregateLayer3

| Attribute                      | Type           | Required | Default | Description                    |
|--------------------------------|----------------|----------|---------|--------------------------------|
| `ip`                           | List[StaticIp] | No*      | None    | Static IP addresses            |
| `dhcp_client`                  | DhcpClient     | No*      | None    | DHCP client configuration      |
| `mtu`                          | int            | No       | 1500    | MTU (576-9216)                 |
| `interface_management_profile` | str            | No       | None    | Management profile             |
| `arp`                          | List[ArpEntry] | No       | None    | Static ARP entries             |
| `ddns_config`                  | DdnsConfig     | No       | None    | Dynamic DNS config             |
| `lacp`                         | LacpConfig     | No       | None    | LACP configuration             |

\* Only one IP mode can be configured (oneOf validation)

### LacpConfig

| Attribute           | Type   | Default  | Description                    |
|---------------------|--------|----------|--------------------------------|
| `enable`            | bool   | False    | Enable LACP                    |
| `fast_failover`     | bool   | False    | Enable fast failover           |
| `mode`              | str    | "passive"| LACP mode (passive/active)     |
| `transmission_rate` | str    | "slow"   | Rate (fast/slow)               |
| `system_priority`   | int    | 32768    | System priority (1-65535)      |
| `max_ports`         | int    | 8        | Max ports (1-8)                |

## Model Validators

### Interface Mode Validation

Ensures only one of `layer2` or `layer3` is configured:

```python
@model_validator(mode="after")
def validate_interface_mode(self) -> "AggregateInterfaceBaseModel":
    modes = [self.layer2, self.layer3]
    configured = [m for m in modes if m is not None]
    if len(configured) > 1:
        raise ValueError("Only one interface mode allowed: layer2 or layer3")
    return self
```

## Usage Examples

### Layer 3 with LACP

```python
from scm.models.network import AggregateInterfaceCreateModel

interface = AggregateInterfaceCreateModel(
    name="ae1",
    layer3={
        "ip": [{"name": "10.0.0.1/24"}],
        "mtu": 9000,
        "lacp": {
            "enable": True,
            "mode": "active",
            "fast_failover": True
        }
    },
    folder="Interfaces"
)
payload = interface.model_dump(exclude_unset=True)
```

### Layer 2 with VLAN

```python
interface = AggregateInterfaceCreateModel(
    name="ae2",
    layer2={
        "vlan_tag": "100",
        "lacp": {"enable": True, "mode": "passive"}
    },
    folder="Interfaces"
)
```
