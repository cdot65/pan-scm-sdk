# LDAP Server Profile Models

Models for LDAP server profile objects in Strata Cloud Manager, defining LDAP directory server configurations for user authentication and group lookups.

## Overview

The LDAP Server Profile models support the following key attributes:

- Profile name and container assignment
- List of LDAP servers with address and port configuration
- Base DN, bind DN, and bind password for directory access
- LDAP type selection (Active Directory, eDirectory, Sun, other)
- SSL and certificate verification settings
- Timeout and retry configuration

## Base Models

### LdapServerProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `server` | `List[LdapServer]` | No | List of LDAP servers |
| `base` | `str` | No | Base distinguished name (max 255 chars) |
| `bind_dn` | `str` | No | Bind distinguished name (max 255 chars) |
| `bind_password` | `str` | No | Bind password (max 121 chars) |
| `bind_timelimit` | `str` | No | Bind time limit |
| `ldap_type` | `LdapType` | No | LDAP server type |
| `retry_interval` | `int` | No | Retry interval in seconds |
| `ssl` | `bool` | No | Enable SSL |
| `timelimit` | `int` | No | Time limit in seconds |
| `verify_server_certificate` | `bool` | No | Verify server certificate |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### LdapServerProfileCreateModel

Inherits from `LdapServerProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### LdapServerProfileUpdateModel

Inherits from `LdapServerProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### LdapServerProfileResponseModel

Inherits from `LdapServerProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Component Models

### LdapServer

Represents a single LDAP server entry.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | No | Server name |
| `address` | `str` | No | Server address |
| `port` | `int` | No | Server port number (1-65535) |

### LdapType

Enumeration of LDAP server types.

| Value | Description |
| --- | --- |
| `active-directory` | Microsoft Active Directory |
| `e-directory` | Novell eDirectory |
| `sun` | Sun Directory Server |
| `other` | Other LDAP server |

## Usage Examples

### Creating an LDAP Server Profile

```python
from scm.models.identity.ldap_server_profiles import (
    LdapServerProfileCreateModel,
    LdapServer,
    LdapType,
)

# Create model instance
profile = LdapServerProfileCreateModel(
    name="corp-ldap",
    folder="Texas",
    server=[
        LdapServer(
            name="ldap-primary",
            address="ldap.example.com",
            port=636
        )
    ],
    base="dc=example,dc=com",
    bind_dn="cn=admin,dc=example,dc=com",
    bind_password="admin-password",
    ldap_type=LdapType.active_directory,
    ssl=True,
    verify_server_certificate=True
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.ldap_server_profile.create(payload)
```

### Parsing an LDAP Server Profile Response

```python
from scm.models.identity.ldap_server_profiles import (
    LdapServerProfileResponseModel,
)

# Parse API response
response = LdapServerProfileResponseModel(**api_response)
print(f"Name: {response.name}")
print(f"Type: {response.ldap_type}")
print(f"Base DN: {response.base}")
print(f"SSL: {response.ssl}")
```

## Related Topics

- [LDAP Server Profile Service](../../config/identity/ldap_server_profile.md)
- [Authentication Profile Models](authentication_profile_models.md)
