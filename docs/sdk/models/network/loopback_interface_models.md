# Loopback Interface Models

## Overview

The Loopback Interface models provide structured validation for loopback interface configuration. Loopback interfaces support IPv4 and IPv6 addressing for management and service endpoints.

### Models

- `LoopbackInterfaceCreateModel`: For creating new loopback interfaces
- `LoopbackInterfaceUpdateModel`: For updating existing interfaces (includes `id`)
- `LoopbackInterfaceResponseModel`: Response model from API operations

All models use `extra="forbid"` to reject undefined fields.

## Model Attributes

### LoopbackInterfaceBaseModel

| Attribute                      | Type         | Required | Default | Description                               |
|--------------------------------|--------------|----------|---------|-------------------------------------------|
| `name`                         | str          | Yes      | None    | Interface name (e.g., "loopback.1")       |
| `comment`                      | str          | No       | None    | Description (max 1023 chars)              |
| `ip`                           | List[str]    | No       | None    | IPv4 addresses (e.g., ["10.0.0.1/32"])    |
| `ipv6`                         | Ipv6Config   | No       | None    | IPv6 configuration                        |
| `mtu`                          | int          | No       | 1500    | MTU (576-9216)                            |
| `interface_management_profile` | str          | No       | None    | Management profile (max 31 chars)         |
| `folder`                       | str          | No*      | None    | Folder container                          |
| `snippet`                      | str          | No*      | None    | Snippet container                         |
| `device`                       | str          | No*      | None    | Device container                          |

\* Exactly one container required for create operations

### Ipv6Config

| Attribute | Type             | Default | Description                    |
|-----------|------------------|---------|--------------------------------|
| `enabled` | bool             | False   | Enable IPv6                    |
| `address` | List[Ipv6Address]| None    | IPv6 addresses                 |

## Usage Examples

### Create with IPv4

```python
from scm.models.network import LoopbackInterfaceCreateModel

loopback = LoopbackInterfaceCreateModel(
    name="loopback.1",
    ip=["10.0.0.1/32"],
    interface_management_profile="allow-ping",
    folder="Interfaces"
)
payload = loopback.model_dump(exclude_unset=True)
```

### Create with IPv6

```python
loopback = LoopbackInterfaceCreateModel(
    name="loopback.2",
    ip=["192.168.1.1/32"],
    ipv6={
        "enabled": True,
        "address": [{"name": "2001:db8::1/128"}]
    },
    folder="Interfaces"
)
```
