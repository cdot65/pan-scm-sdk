# Service

The `Service` service manages service objects in Strata Cloud Manager, defining network protocols and ports for use in security policies and NAT rules.

## Class Overview

The `Service` class provides CRUD operations for service objects. It is accessed through the `client.service` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Service service
services = client.service
```

### Key Attributes

| Attribute      | Type          | Required     | Description                                |
|----------------|---------------|--------------|--------------------------------------------|
| `name`         | `str`         | Yes          | Name of service (max 63 chars)             |
| `id`           | `UUID`        | Yes*         | Unique identifier (*response only)         |
| `protocol`     | `Protocol`    | Yes          | Protocol configuration (TCP/UDP)           |
| `protocol.tcp` | `TCPProtocol` | One Required | TCP protocol settings                      |
| `protocol.udp` | `UDPProtocol` | One Required | UDP protocol settings                      |
| `description`  | `str`         | No           | Description (max 1023 chars)               |
| `tag`          | `List[str]`   | No           | List of tags                               |
| `folder`       | `str`         | Yes**        | Folder location (**one container required) |
| `snippet`      | `str`         | Yes**        | Snippet location (**one container required)|
| `device`       | `str`         | Yes**        | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Services

Retrieves a list of service objects with optional filtering.

```python
services = client.service.list(
    folder="Texas",
    protocols=["tcp"],
    tags=["Production"]
)

for svc in services:
    print(f"Name: {svc.name}")
    if svc.protocol.tcp:
        print(f"TCP Ports: {svc.protocol.tcp.port}")
```

### Fetch a Service

Retrieves a single service by name and container.

```python
service = client.service.fetch(name="web-service", folder="Texas")
print(f"Found service: {service.name}")
```

### Create a Service

Creates a new service object.

```python
# TCP service
tcp_svc = client.service.create({
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,443",
            "override": {"timeout": 60, "halfclose_timeout": 30}
        }
    },
    "description": "Web service ports",
    "folder": "Texas",
    "tag": ["Web", "Production"]
})

# UDP service
udp_svc = client.service.create({
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53",
            "override": {"timeout": 30}
        }
    },
    "description": "DNS service",
    "folder": "Texas"
})
```

### Update a Service

Updates an existing service object.

```python
existing = client.service.fetch(name="web-service", folder="Texas")

if existing.protocol.tcp:
    existing.protocol.tcp.port = "80,443,8443"
    existing.protocol.tcp.override.timeout = 120

existing.description = "Updated web service ports"

updated = client.service.update(existing)
```

### Delete a Service

Deletes a service object by ID.

```python
client.service.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating TCP and UDP Services

Define services for different network protocols.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Web service with TCP ports and timeouts
client.service.create({
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,443",
            "override": {"timeout": 60, "halfclose_timeout": 30}
        }
    },
    "description": "Web service ports",
    "folder": "Texas",
    "tag": ["Web", "Production"]
})

# DNS service with UDP
client.service.create({
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53",
            "override": {"timeout": 30}
        }
    },
    "description": "DNS service",
    "folder": "Texas",
    "tag": ["DNS"]
})
```

### Filtering Services

Use advanced filtering to find specific services.

```python
# Exact match with exclusions
filtered = client.service.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"]
)

for svc in filtered:
    print(f"Service: {svc.name} in {svc.folder}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_service = client.service.create({
        "name": "test-service",
        "protocol": {"tcp": {"port": "8080"}},
        "folder": "Texas",
        "tag": ["Test"]
    })
except InvalidObjectError as e:
    print(f"Invalid service data: {e.message}")
except NameNotUniqueError as e:
    print(f"Service name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Service not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Service still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [Service Models](../../models/objects/service_models.md#Overview)
- [Service Group](service_group.md)
