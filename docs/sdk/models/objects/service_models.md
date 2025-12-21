# Service Models

## Overview {#Overview}

The Service models provide a structured way to manage network services in Palo Alto Networks' Strata Cloud Manager.
These models support both TCP and UDP protocols with port configurations and protocol-specific overrides. Services can
be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with
the SCM API.

### Models

The module provides the following Pydantic models:

- `ServiceBaseModel`: Base model with fields common to all service operations
- `ServiceCreateModel`: Model for creating new services
- `ServiceUpdateModel`: Model for updating existing services
- `ServiceResponseModel`: Response model for service operations
- `Protocol`: Protocol configuration container (TCP or UDP)
- `TCPProtocol`: TCP protocol settings with port and override options
- `UDPProtocol`: UDP protocol settings with port and override options
- `Override`: Protocol override settings (timeout, halfclose_timeout, timewait_timeout)

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute   | Type      | Required | Default | Description                                                                        |
|-------------|-----------|----------|---------|------------------------------------------------------------------------------------|
| name        | str       | Yes      | None    | Name of the service. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| protocol    | Protocol  | Yes      | None    | Protocol configuration (TCP or UDP)                                                |
| description | str       | No       | None    | Description of the service. Max length: 1023 chars                                 |
| tag         | List[str] | No       | None    | List of tags                                                                       |
| folder      | str       | No*      | None    | Folder where service is defined. Max length: 64 chars                              |
| snippet     | str       | No*      | None    | Snippet where service is defined. Max length: 64 chars                             |
| device      | str       | No*      | None    | Device where service is defined. Max length: 64 chars                              |
| id          | UUID      | Yes**    | None    | UUID of the service (response only)                                                |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

### Protocol Attributes

| Attribute | Type     | Required | Default | Description                           |
|-----------|----------|----------|---------|---------------------------------------|
| tcp       | TCP      | No*      | None    | TCP protocol configuration            |
| udp       | UDP      | No*      | None    | UDP protocol configuration            |
| port      | str      | Yes      | None    | Port numbers (e.g. "80" or "80,8080") |
| override  | Override | No       | None    | Protocol override settings            |

\* Exactly one protocol type (tcp/udp) must be provided

## Exceptions

The Service models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When neither or both TCP and UDP protocols are provided in protocol configuration
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When port format validation fails

## Model Validators

### Protocol Type Validation

The models enforce that exactly one protocol type (TCP or UDP) must be specified:

```python
# Using dictionary
from scm.config.objects import Service

# Error: both TCP and UDP provided
try:
    service_dict = {
        "name": "invalid-service",
        "protocol": {
            "tcp": {"port": "80"},
            "udp": {"port": "53"}  # Can't specify both TCP and UDP
        },
        "folder": "Texas"
    }
    service = Service(api_client)
    response = service.create(service_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'."

# Using model directly
from scm.models.objects import ServiceCreateModel, Protocol

# Error: no protocol specified
try:
    service = ServiceCreateModel(
        name="invalid-service",
        protocol=Protocol(),
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'tcp' or 'udp' must be provided in 'protocol'."
```

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
try:
    service_dict = {
        "name": "invalid-service",
        "protocol": {"tcp": {"port": "80"}},
        "folder": "Texas",
        "device": "fw01"  # Can't specify both folder and device
    }
    response = service.create(service_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
try:
    service = ServiceCreateModel(
        name="invalid-service",
        protocol=Protocol(tcp=TCPProtocol(port="80")),
        folder="Texas",
        device="fw01"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a TCP Service

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
tcp_data = {
    "name": "web-service",
    "protocol": {
        "tcp": {
            "port": "80,443",
            "override": {
                "timeout": 30,
                "halfclose_timeout": 15
            }
        }
    },
    "description": "Web service ports",
    "folder": "Texas",
    "tag": ["web", "production"]
}

response = client.service.create(tcp_data)
print(f"Created service: {response.name} (ID: {response.id})")
```

### Creating a UDP Service

```python
# Using dictionary
udp_data = {
    "name": "dns-service",
    "protocol": {
        "udp": {
            "port": "53"
        }
    },
    "description": "DNS service",
    "snippet": "Network Services",
    "tag": ["dns", "network"]
}

response = client.service.create(udp_data)
print(f"Created UDP service: {response.name}")
```

### Updating a Service

```python
# Fetch existing service
existing = client.service.fetch(name="web-service", folder="Texas")

# Modify attributes using dot notation
existing.protocol.tcp.port = "80,443,8080"
existing.protocol.tcp.override.timeout = 60
existing.tag = ["web", "production", "updated"]

# Pass modified object to update()
updated = client.service.update(existing)
print(f"Updated service: {updated.name}")
print(f"New ports: {updated.protocol.tcp.port}")
```

### Working with Response Models

```python
# List and process services
services = client.service.list(folder="Texas")

for svc in services:
    print(f"Service: {svc.name} (ID: {svc.id})")
    if svc.protocol.tcp:
        print(f"  TCP Ports: {svc.protocol.tcp.port}")
        if svc.protocol.tcp.override:
            print(f"  Timeout: {svc.protocol.tcp.override.timeout}")
    elif svc.protocol.udp:
        print(f"  UDP Ports: {svc.protocol.udp.port}")
```
