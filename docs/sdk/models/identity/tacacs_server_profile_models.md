# TACACS+ Server Profile Models

Models for TACACS+ server profile objects in Strata Cloud Manager, defining TACACS+ server configurations for terminal access controller authentication, authorization, and accounting.

## Overview

The TACACS+ Server Profile models support the following key attributes:

- Profile name and container assignment
- List of TACACS+ servers with address, port, and shared secret
- Protocol selection (CHAP or PAP)
- Timeout and single connection settings

## Base Models

### TacacsServerProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `server` | `List[TacacsServer]` | No | List of TACACS+ servers |
| `protocol` | `TacacsProtocol` | No | TACACS+ protocol type |
| `timeout` | `int` | No | Timeout in seconds (1-30) |
| `use_single_connection` | `bool` | No | Use single connection |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### TacacsServerProfileCreateModel

Inherits from `TacacsServerProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### TacacsServerProfileUpdateModel

Inherits from `TacacsServerProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### TacacsServerProfileResponseModel

Inherits from `TacacsServerProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Component Models

### TacacsServer

Represents a single TACACS+ server entry.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | No | Server name |
| `address` | `str` | No | Server address |
| `port` | `int` | No | Server port number (1-65535) |
| `secret` | `str` | No | Shared secret |

### TacacsProtocol

Protocol type enumeration.

| Value | Description |
| --- | --- |
| `CHAP` | Challenge-Handshake Authentication Protocol |
| `PAP` | Password Authentication Protocol |

## Usage Examples

### Creating a TACACS+ Server Profile

```python
from scm.models.identity.tacacs_server_profiles import (
    TacacsServerProfileCreateModel,
    TacacsServer,
    TacacsProtocol,
)

# Create model instance
profile = TacacsServerProfileCreateModel(
    name="corp-tacacs",
    folder="Texas",
    server=[
        TacacsServer(
            name="tacacs-primary",
            address="10.0.1.50",
            port=49,
            secret="shared-secret"
        )
    ],
    protocol=TacacsProtocol.CHAP,
    timeout=5,
    use_single_connection=True
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.tacacs_server_profile.create(payload)
```

### Parsing a TACACS+ Server Profile Response

```python
from scm.models.identity.tacacs_server_profiles import (
    TacacsServerProfileResponseModel,
)

# Parse API response
response = TacacsServerProfileResponseModel(**api_response)
print(f"Name: {response.name}")
print(f"Protocol: {response.protocol}")
print(f"Timeout: {response.timeout}")
if response.server:
    for server in response.server:
        print(f"  Server: {server.name} ({server.address}:{server.port})")
```

## Related Topics

- [TACACS+ Server Profile Service](../../config/identity/tacacs_server_profile.md)
- [Authentication Profile Models](authentication_profile_models.md)
