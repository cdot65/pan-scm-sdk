# Interface Management Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Interface Management Profile models provide a structured way to represent and validate interface management profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating interface management profiles, enforcing proper management service settings, container specifications, and field validations.

### Models

The module provides the following Pydantic models:

- `InterfaceManagementProfileBaseModel`: Base model with fields common to all interface management profile operations
- `InterfaceManagementProfileCreateModel`: Model for creating new interface management profiles
- `InterfaceManagementProfileUpdateModel`: Model for updating existing interface management profiles
- `InterfaceManagementProfileResponseModel`: Response model for interface management profile operations

The `InterfaceManagementProfileBaseModel` and `InterfaceManagementProfileCreateModel` / `InterfaceManagementProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `InterfaceManagementProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

> **Note:** Several fields in this model use aliases for kebab-case API field names (e.g., `http_ocsp` maps to `http-ocsp`, `response_pages` maps to `response-pages`). When working with dictionaries, use the kebab-case names. When working with model attributes directly, use the underscore names.

## Model Attributes

### InterfaceManagementProfileBaseModel

This is the base model containing fields common to all interface management profile operations.

| Attribute                     | Type           | Required | Default | Description                                                                   |
|-------------------------------|----------------|----------|---------|-------------------------------------------------------------------------------|
| name                          | str            | Yes      | None    | Name of the profile. Pattern: `^[0-9a-zA-Z._\- ]+$`. Max 63 chars.           |
| http                          | bool           | No       | None    | Enable HTTP management.                                                       |
| https                         | bool           | No       | None    | Enable HTTPS management.                                                      |
| telnet                        | bool           | No       | None    | Enable Telnet management.                                                     |
| ssh                           | bool           | No       | None    | Enable SSH management.                                                        |
| ping                          | bool           | No       | None    | Enable ping.                                                                  |
| http_ocsp                     | bool           | No       | None    | Enable HTTP OCSP. Alias: `http-ocsp`.                                         |
| response_pages                | bool           | No       | None    | Enable response pages. Alias: `response-pages`.                               |
| userid_service                | bool           | No       | None    | Enable User-ID service. Alias: `userid-service`.                              |
| userid_syslog_listener_ssl    | bool           | No       | None    | Enable User-ID syslog listener SSL. Alias: `userid-syslog-listener-ssl`.      |
| userid_syslog_listener_udp    | bool           | No       | None    | Enable User-ID syslog listener UDP. Alias: `userid-syslog-listener-udp`.      |
| permitted_ip                  | List[str]      | No       | None    | List of permitted IP addresses. Alias: `permitted-ip`.                        |
| folder                        | str            | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.                |
| snippet                       | str            | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.               |
| device                        | str            | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.                |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### InterfaceManagementProfileCreateModel

Inherits all fields from `InterfaceManagementProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### InterfaceManagementProfileUpdateModel

Extends `InterfaceManagementProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                            |
|-----------|------|----------|---------|--------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the interface management profile |

### InterfaceManagementProfileResponseModel

Extends `InterfaceManagementProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                            |
|-----------|------|----------|---------|--------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the interface management profile |

> **Note:** The `InterfaceManagementProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating an interface management profile (`InterfaceManagementProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When the profile name does not match the required pattern or exceeds the maximum length.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `InterfaceManagementProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating an Interface Management Profile

#### Using a Dictionary

```python
from scm.models.network import InterfaceManagementProfileCreateModel

profile_data = {
    "name": "mgmt-profile-1",
    "https": True,
    "ssh": True,
    "ping": True,
    "http-ocsp": False,
    "response-pages": True,
    "userid-service": False,
    "permitted-ip": ["10.0.0.0/8", "192.168.1.0/24"],
    "folder": "Network Profiles"
}

# Validate and create model instance
profile = InterfaceManagementProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import InterfaceManagementProfileCreateModel

# Create profile using Python attribute names
profile = InterfaceManagementProfileCreateModel(
    name="mgmt-profile-2",
    https=True,
    ssh=True,
    ping=True,
    http_ocsp=False,
    response_pages=True,
    userid_service=True,
    userid_syslog_listener_ssl=False,
    userid_syslog_listener_udp=False,
    permitted_ip=["10.0.0.0/8"],
    folder="Network Profiles"
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating an Interface Management Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.interface_management_profile.fetch(
    name="mgmt-profile-1",
    folder="Network Profiles"
)

# Modify attributes using dot notation
existing.telnet = False
existing.ssh = True
existing.permitted_ip = ["10.0.0.0/8", "172.16.0.0/12"]

# Pass modified object to update()
updated = client.interface_management_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Creating a Minimal Profile

```python
from scm.models.network import InterfaceManagementProfileCreateModel

# Create a profile with only ping enabled
profile_data = {
    "name": "ping-only",
    "ping": True,
    "folder": "Network Profiles"
}

profile = InterfaceManagementProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
