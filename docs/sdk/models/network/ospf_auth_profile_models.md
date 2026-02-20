# OSPF Auth Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The OSPF Auth Profile models provide a structured way to represent and validate OSPF authentication profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage OSPF authentication settings, supporting both simple password and MD5 key-based authentication. The two authentication types are mutually exclusive -- a profile uses either a password or a list of MD5 keys, but not both.

### Models

The module provides the following Pydantic models:

- `OspfAuthProfileBaseModel`: Base model with fields common to all OSPF auth profile operations
- `OspfAuthProfileCreateModel`: Model for creating new OSPF authentication profiles
- `OspfAuthProfileUpdateModel`: Model for updating existing OSPF authentication profiles
- `OspfAuthProfileResponseModel`: Response model for OSPF authentication profile operations
- `OspfAuthProfileMd5Key`: MD5 key entry model (for create/update input)
- `OspfAuthProfileMd5KeyResponse`: MD5 key entry model (for API responses with encrypted values)

The `OspfAuthProfileBaseModel` and `OspfAuthProfileCreateModel` / `OspfAuthProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `OspfAuthProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

> **Note:** The response model does NOT inherit from the base model. It defines its own fields because MD5 keys in responses use `OspfAuthProfileMd5KeyResponse` (with `extra="ignore"`) instead of `OspfAuthProfileMd5Key` (with `extra="forbid"`), since the API may return encrypted key values with additional metadata.

## Model Attributes

### OspfAuthProfileBaseModel

This is the base model containing fields common to create and update OSPF auth profile operations.

| Attribute | Type                        | Required | Default | Description                                                     |
|-----------|-----------------------------|----------|---------|-----------------------------------------------------------------|
| name      | str                         | Yes      | None    | Profile name.                                                   |
| password  | str                         | No*      | None    | Simple password authentication.                                 |
| md5       | List[OspfAuthProfileMd5Key] | No*      | None    | MD5 authentication keys.                                        |
| folder    | str                         | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                         | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                         | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\* `password` and `md5` are mutually exclusive.

\** Exactly one container (folder/snippet/device) must be provided for create operations

### OspfAuthProfileCreateModel

Inherits all fields from `OspfAuthProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### OspfAuthProfileUpdateModel

Extends `OspfAuthProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                       |
|-----------|------|----------|---------|---------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the OSPF auth profile    |

### OspfAuthProfileResponseModel

This model is defined independently (not inheriting from `OspfAuthProfileBaseModel`) to use the response-specific MD5 key model.

| Attribute | Type                                | Required | Default | Description                                                     |
|-----------|-------------------------------------|----------|---------|-----------------------------------------------------------------|
| id        | UUID                                | Yes      | None    | The unique identifier of the OSPF auth profile.                 |
| name      | str                                 | Yes      | None    | Profile name.                                                   |
| password  | str                                 | No       | None    | Simple password authentication (API returns encrypted value).   |
| md5       | List[OspfAuthProfileMd5KeyResponse] | No       | None    | MD5 authentication keys (API returns encrypted values).         |
| folder    | str                                 | No       | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                                 | No       | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                                 | No       | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

> **Note:** The `OspfAuthProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### OspfAuthProfileMd5Key

MD5 key entry for create/update operations. Uses `extra="forbid"`.

| Attribute | Type | Required | Default | Description                        |
|-----------|------|----------|---------|------------------------------------|
| name      | int  | No       | None    | Key ID (1-255).                    |
| key       | str  | No       | None    | MD5 hash. Max 16 characters.       |
| preferred | bool | No       | None    | Whether this is the preferred key. |

### OspfAuthProfileMd5KeyResponse

MD5 key entry for API responses. Uses `extra="ignore"` because the API may return encrypted key values with additional metadata.

| Attribute | Type | Required | Default | Description                                       |
|-----------|------|----------|---------|---------------------------------------------------|
| name      | int  | No       | None    | Key ID (1-255).                                   |
| key       | str  | No       | None    | MD5 hash (API returns encrypted value).            |
| preferred | bool | No       | None    | Whether this is the preferred key.                |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`OspfAuthProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When both `password` and `md5` are set simultaneously (mutually exclusive).
- When an MD5 key ID is outside the valid range (1-255).
- When an MD5 key exceeds 16 characters.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Authentication Type Validation in `OspfAuthProfileBaseModel`

- **validate_auth_type**:
  Ensures that `password` and `md5` are mutually exclusive. If both are set, it raises a `ValueError`. A profile must use either simple password authentication or MD5 key-based authentication, but not both.

### Container Validation in `OspfAuthProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating an OSPF Auth Profile with Password

#### Using a Dictionary

```python
from scm.models.network import OspfAuthProfileCreateModel

profile_data = {
    "name": "ospf-auth-password",
    "password": "my-ospf-password",
    "folder": "Routing",
}

# Validate and create model instance
profile = OspfAuthProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating an OSPF Auth Profile with MD5 Keys

```python
from scm.models.network import (
    OspfAuthProfileCreateModel,
    OspfAuthProfileMd5Key,
)

# Create profile with MD5 authentication
profile = OspfAuthProfileCreateModel(
    name="ospf-auth-md5",
    md5=[
        OspfAuthProfileMd5Key(
            name=1,
            key="md5-key-primary",
            preferred=True,
        ),
        OspfAuthProfileMd5Key(
            name=2,
            key="md5-key-backup",
            preferred=False,
        ),
    ],
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating an OSPF Auth Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.ospf_auth_profile.fetch(name="ospf-auth-md5", folder="Routing")

# Modify the password (note: must remove md5 first since they are mutually exclusive)
existing.md5 = None
existing.password = "new-simple-password"

# Pass modified object to update()
updated = client.ospf_auth_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Invalid: Setting Both Password and MD5

```python
from scm.models.network import OspfAuthProfileCreateModel

# This will raise a ValueError because password and md5 are mutually exclusive
try:
    profile = OspfAuthProfileCreateModel(
        name="invalid-profile",
        password="my-password",
        md5=[{"name": 1, "key": "md5-key"}],
        folder="Routing",
    )
except ValueError as e:
    print(f"Validation error: {e}")
    # Output: 'password' and 'md5' are mutually exclusive.
```
