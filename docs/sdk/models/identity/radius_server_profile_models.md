# RADIUS Server Profile Models

Models for RADIUS server profile objects in Strata Cloud Manager, defining RADIUS server configurations for centralized authentication, authorization, and accounting.

## Overview

The RADIUS Server Profile models support the following key attributes:

- Profile name and container assignment
- List of RADIUS servers with IP address, port, and shared secret
- Protocol selection (CHAP, PAP, EAP-TTLS with PAP, PEAP-MSCHAPv2, PEAP with GTC)
- Retry and timeout configuration

## Base Models

### RadiusServerProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `server` | `List[RadiusServer]` | No | List of RADIUS servers |
| `protocol` | `RadiusProtocol` | No | RADIUS protocol configuration |
| `retries` | `int` | No | Number of retries (1-5) |
| `timeout` | `int` | No | Timeout in seconds (1-120) |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### RadiusServerProfileCreateModel

Inherits from `RadiusServerProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### RadiusServerProfileUpdateModel

Inherits from `RadiusServerProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### RadiusServerProfileResponseModel

Inherits from `RadiusServerProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Component Models

### RadiusServer

Represents a single RADIUS server entry.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | No | Server name |
| `ip_address` | `str` | No | Server IP address |
| `port` | `int` | No | Server port number (1-65535) |
| `secret` | `str` | No | Shared secret |

### RadiusProtocol

RADIUS protocol configuration. Exactly one protocol type should be provided.

| Field | Type | Description |
| --- | --- | --- |
| `CHAP` | `Dict` | CHAP protocol |
| `PAP` | `Dict` | PAP protocol |
| `EAP_TTLS_with_PAP` | `Dict` | EAP-TTLS with PAP protocol |
| `PEAP_MSCHAPv2` | `Dict` | PEAP-MSCHAPv2 protocol |
| `PEAP_with_GTC` | `Dict` | PEAP with GTC protocol |

## Usage Examples

### Creating a RADIUS Server Profile

```python
from scm.models.identity.radius_server_profiles import (
    RadiusServerProfileCreateModel,
    RadiusServer,
    RadiusProtocol,
)

# Create model instance
profile = RadiusServerProfileCreateModel(
    name="corp-radius",
    folder="Texas",
    server=[
        RadiusServer(
            name="radius-primary",
            ip_address="10.0.1.100",
            port=1812,
            secret="shared-secret"
        )
    ],
    protocol=RadiusProtocol(CHAP={}),
    timeout=5,
    retries=3
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.radius_server_profile.create(payload)
```

### Parsing a RADIUS Server Profile Response

```python
from scm.models.identity.radius_server_profiles import (
    RadiusServerProfileResponseModel,
)

# Parse API response
response = RadiusServerProfileResponseModel(**api_response)
print(f"Name: {response.name}")
print(f"Timeout: {response.timeout}")
print(f"Retries: {response.retries}")
if response.server:
    for server in response.server:
        print(f"  Server: {server.name} ({server.ip_address}:{server.port})")
```

## Related Topics

- [RADIUS Server Profile Service](../../config/identity/radius_server_profile.md)
- [Authentication Profile Models](authentication_profile_models.md)
