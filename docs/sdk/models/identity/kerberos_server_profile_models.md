# Kerberos Server Profile Models

Models for Kerberos server profile objects in Strata Cloud Manager, defining KDC server configurations for Kerberos-based authentication.

## Overview

The Kerberos Server Profile models support the following key attributes:

- Profile name and container assignment
- List of Kerberos KDC servers with host and port configuration

## Base Models

### KerberosServerProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `server` | `List[KerberosServer]` | No | List of Kerberos servers |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### KerberosServerProfileCreateModel

Inherits from `KerberosServerProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### KerberosServerProfileUpdateModel

Inherits from `KerberosServerProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### KerberosServerProfileResponseModel

Inherits from `KerberosServerProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Component Models

### KerberosServer

Represents a single Kerberos server entry.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | No | Server name |
| `host` | `str` | No | Server hostname or IP address |
| `port` | `int` | No | Server port number (1-65535) |

## Usage Examples

### Creating a Kerberos Server Profile

```python
from scm.models.identity.kerberos_server_profiles import (
    KerberosServerProfileCreateModel,
    KerberosServer,
)

# Create model instance
profile = KerberosServerProfileCreateModel(
    name="corp-kerberos",
    folder="Texas",
    server=[
        KerberosServer(
            name="kdc-primary",
            host="kdc.example.com",
            port=88
        )
    ]
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.kerberos_server_profile.create(payload)
```

### Parsing a Kerberos Server Profile Response

```python
from scm.models.identity.kerberos_server_profiles import (
    KerberosServerProfileResponseModel,
)

# Parse API response
response = KerberosServerProfileResponseModel(**api_response)
print(f"Name: {response.name}")
if response.server:
    for server in response.server:
        print(f"  Server: {server.name} ({server.host}:{server.port})")
```

## Related Topics

- [Kerberos Server Profile Service](../../config/identity/kerberos_server_profile.md)
- [Authentication Profile Models](authentication_profile_models.md)
