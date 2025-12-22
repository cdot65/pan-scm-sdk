# Tunnel Interface Models

## Overview

The Tunnel Interface models provide structured validation for tunnel interface configuration. Tunnel interfaces are used for VPN tunnels (IPsec, GRE) and other encapsulated traffic.

### Models

- `TunnelInterfaceCreateModel`: For creating new tunnel interfaces
- `TunnelInterfaceUpdateModel`: For updating existing interfaces (includes `id`)
- `TunnelInterfaceResponseModel`: Response model from API operations

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### TunnelInterfaceBaseModel

| Attribute                      | Type       | Required | Default | Description                               |
|--------------------------------|------------|----------|---------|-------------------------------------------|
| `name`                         | str        | Yes      | None    | Interface name (e.g., "tunnel.1")         |
| `comment`                      | str        | No       | None    | Description (max 1023 chars)              |
| `ip`                           | List[str]  | No       | None    | IPv4 addresses                            |
| `mtu`                          | int        | No       | 1500    | MTU (576-9216)                            |
| `interface_management_profile` | str        | No       | None    | Management profile (max 31 chars)         |
| `folder`                       | str        | No*      | None    | Folder container                          |
| `snippet`                      | str        | No*      | None    | Snippet container                         |
| `device`                       | str        | No*      | None    | Device container                          |

\* Exactly one container required for create operations

## Usage Examples

### Create Tunnel Interface

```python
from scm.models.network import TunnelInterfaceCreateModel

tunnel = TunnelInterfaceCreateModel(
    name="tunnel.1",
    comment="Site-to-Site VPN",
    ip=["10.254.0.1/30"],
    mtu=1400,
    folder="Interfaces"
)
payload = tunnel.model_dump(exclude_unset=True)
```

### Unnumbered Tunnel

```python
tunnel = TunnelInterfaceCreateModel(
    name="tunnel.2",
    comment="GRE Tunnel",
    mtu=1476,
    folder="Interfaces"
)
```
