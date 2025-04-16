# Service Models

## Overview {#Overview}

The Service models provide a structured way to manage network services in Palo Alto Networks' Strata Cloud Manager.
These models support both TCP and UDP protocols with port configurations and protocol-specific overrides. Services can
be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with
the
SCM API.

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
# Using dictionary
from scm.config.objects import Service

tcp_dict = {
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

service = Service(api_client)
response = service.create(tcp_dict)

# Using model directly
from scm.models.objects import ServiceCreateModel, Protocol, TCPProtocol, Override

tcp_service = ServiceCreateModel(
    name="web-service",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,443",
            override=Override(
                timeout=30,
                halfclose_timeout=15
            )
        )
    ),
    description="Web service ports",
    folder="Texas",
    tag=["web", "production"]
)

payload = tcp_service.model_dump(exclude_unset=True)
response = service.create(payload)
```

### Creating a UDP Service

```python
# Using dictionary
udp_dict = {
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

response = service.create(udp_dict)

# Using model directly
from scm.models.objects import ServiceCreateModel, Protocol, UDPProtocol

udp_service = ServiceCreateModel(
    name="dns-service",
    protocol=Protocol(
        udp=UDPProtocol(
            port="53"
        )
    ),
    description="DNS service",
    snippet="Network Services",
    tag=["dns", "network"]
)

payload = udp_service.model_dump(exclude_unset=True)
response = service.create(payload)
```

### Updating a Service

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "web-service-updated",
    "protocol": {
        "tcp": {
            "port": "80,443,8080",
            "override": {
                "timeout": 60
            }
        }
    },
    "tag": ["web", "production", "updated"]
}

response = service.update(update_dict)

# Using model directly
from scm.models.objects import ServiceUpdateModel, Protocol, TCPProtocol, Override

update = ServiceUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="web-service-updated",
    protocol=Protocol(
        tcp=TCPProtocol(
            port="80,443,8080",
            override=Override(
                timeout=60
            )
        )
    ),
    tag=["web", "production", "updated"]
)

payload = update.model_dump(exclude_unset=True)
response = service.update(payload)
```
