# Ethernet Interface Models

## Overview

The Ethernet Interface models provide structured validation for ethernet interface configuration in Palo Alto Networks' Strata Cloud Manager. These models support Layer 2, Layer 3, and TAP modes with strict oneOf validation.

### Models

- `EthernetInterfaceCreateModel`: For creating new ethernet interfaces
- `EthernetInterfaceUpdateModel`: For updating existing interfaces (includes `id`)
- `EthernetInterfaceResponseModel`: Response model from API operations
- `EthernetLayer2`: Layer 2 mode configuration
- `EthernetLayer3`: Layer 3 mode configuration
- `EthernetTap`: TAP mode configuration

All models use `extra="forbid"` to reject undefined fields.

## Important: Naming Convention

Ethernet interface names in SCM must start with `$` (dollar sign) as they are variable references. The `default_value` field specifies the physical interface assignment.

```python
# Correct usage
name="$wan-interface"        # Variable name (required $ prefix)
default_value="ethernet1/1"  # Physical interface assignment
```

## Model Attributes

### EthernetInterfaceBaseModel

| Attribute       | Type            | Required | Default  | Description                                           |
|-----------------|-----------------|----------|----------|-------------------------------------------------------|
| `name`          | str             | Yes      | None     | Variable name (must start with $, max 63 chars)       |
| `default_value` | str             | No       | None     | Physical interface (e.g., ethernet1/1)                |
| `comment`       | str             | No       | None     | Description (max 1023 chars)                          |
| `link_speed`    | str             | No       | "auto"   | Link speed (auto/10/100/1000/10000/40000/100000)      |
| `link_duplex`   | str             | No       | "auto"   | Duplex (auto/half/full)                               |
| `link_state`    | str             | No       | "auto"   | State (auto/up/down)                                  |
| `poe`           | PoeConfig       | No       | None     | Power over Ethernet config                            |
| `layer2`        | EthernetLayer2  | No*      | None     | Layer 2 mode configuration                            |
| `layer3`        | EthernetLayer3  | No*      | None     | Layer 3 mode configuration                            |
| `tap`           | EthernetTap     | No*      | None     | TAP mode configuration                                |
| `folder`        | str             | No**     | None     | Folder container                                      |
| `snippet`       | str             | No**     | None     | Snippet container                                     |
| `device`        | str             | No**     | None     | Device container                                      |

\* Only one mode can be configured (oneOf validation)
\** Exactly one container required for create operations

### EthernetLayer2

| Attribute  | Type       | Required | Default | Description        |
|------------|------------|----------|---------|--------------------|
| `vlan_tag` | str        | No       | None    | VLAN tag (1-4096)  |
| `lldp`     | LldpConfig | No       | None    | LLDP configuration |

### EthernetLayer3

| Attribute                      | Type           | Required | Default | Description                    |
|--------------------------------|----------------|----------|---------|--------------------------------|
| `ip`                           | List[StaticIp] | No*      | None    | Static IP addresses            |
| `dhcp_client`                  | DhcpClient     | No*      | None    | DHCP client configuration      |
| `pppoe`                        | PppoeConfig    | No*      | None    | PPPoE configuration            |
| `mtu`                          | int            | No       | 1500    | MTU (576-9216)                 |
| `interface_management_profile` | str            | No       | None    | Management profile             |
| `arp`                          | List[ArpEntry] | No       | None    | Static ARP entries             |
| `ddns_config`                  | DdnsConfig     | No       | None    | Dynamic DNS config             |

\* Only one IP mode can be configured (oneOf validation)

## Model Validators

### Interface Mode Validation

Ensures only one of `layer2`, `layer3`, or `tap` is configured:

```python
@model_validator(mode="after")
def validate_interface_mode(self) -> "EthernetInterfaceBaseModel":
    modes = [self.layer2, self.layer3, self.tap]
    configured = [m for m in modes if m is not None]
    if len(configured) > 1:
        raise ValueError("Only one interface mode allowed")
    return self
```

### IP Mode Validation (Layer3)

Ensures only one of `ip`, `dhcp_client`, or `pppoe` is configured:

```python
@model_validator(mode="after")
def validate_ip_mode(self) -> "EthernetLayer3":
    modes = [self.ip, self.dhcp_client, self.pppoe]
    configured = [m for m in modes if m is not None]
    if len(configured) > 1:
        raise ValueError("Only one IP addressing mode allowed")
    return self
```

## Usage Examples

### Layer 3 with Static IP

```python
from scm.models.network import EthernetInterfaceCreateModel

interface = EthernetInterfaceCreateModel(
    name="$wan-interface",
    default_value="ethernet1/1",
    layer3={
        "ip": [{"name": "192.168.1.1/24"}],
        "mtu": 1500
    },
    folder="Interfaces"
)
payload = interface.model_dump(exclude_unset=True)
```

### Layer 3 with DHCP

```python
interface = EthernetInterfaceCreateModel(
    name="$dhcp-interface",
    default_value="ethernet1/2",
    layer3={
        "dhcp_client": {
            "enable": True,
            "create_default_route": True
        }
    },
    folder="Interfaces"
)
```

### Layer 2 with VLAN

```python
interface = EthernetInterfaceCreateModel(
    name="$layer2-interface",
    layer2={
        "vlan_tag": "100",
        "lldp": {"enable": True}
    },
    folder="Interfaces"
)
```

### TAP Mode

```python
interface = EthernetInterfaceCreateModel(
    name="$tap-interface",
    tap={},
    folder="Interfaces"
)
```
