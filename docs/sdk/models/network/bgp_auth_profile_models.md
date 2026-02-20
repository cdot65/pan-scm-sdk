# BGP Auth Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Exceptions](#exceptions)
4. [Model Validators](#model-validators)
5. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Auth Profile models provide a structured way to represent and validate BGP authentication profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage BGP MD5 authentication keys used to secure BGP peering sessions between routers.

### Models

The module provides the following Pydantic models:

- `BgpAuthProfileBaseModel`: Base model with fields common to all BGP auth profile operations
- `BgpAuthProfileCreateModel`: Model for creating new BGP authentication profiles
- `BgpAuthProfileUpdateModel`: Model for updating existing BGP authentication profiles
- `BgpAuthProfileResponseModel`: Response model for BGP authentication profile operations

The `BgpAuthProfileBaseModel` and `BgpAuthProfileCreateModel` / `BgpAuthProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `BgpAuthProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### BgpAuthProfileBaseModel

This is the base model containing fields common to all BGP authentication profile operations.

| Attribute | Type | Required | Default | Description                                                     |
|-----------|------|----------|---------|-----------------------------------------------------------------|
| name      | str  | Yes      | None    | Profile name.                                                   |
| secret    | str  | No       | None    | BGP authentication key (MD5 secret).                            |
| folder    | str  | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str  | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str  | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpAuthProfileCreateModel

Inherits all fields from `BgpAuthProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpAuthProfileUpdateModel

Extends `BgpAuthProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP auth profile      |

### BgpAuthProfileResponseModel

Extends `BgpAuthProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP auth profile      |

> **Note:** The `BgpAuthProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`BgpAuthProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `BgpAuthProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP Auth Profile

#### Using a Dictionary

```python
from scm.models.network import BgpAuthProfileCreateModel

profile_data = {
    "name": "bgp-auth-1",
    "secret": "my-md5-secret-key",
    "folder": "Routing",
}

# Validate and create model instance
profile = BgpAuthProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import BgpAuthProfileCreateModel

# Create BGP auth profile
profile = BgpAuthProfileCreateModel(
    name="bgp-auth-2",
    secret="another-secret-key",
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a BGP Auth Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.bgp_auth_profile.fetch(name="bgp-auth-1", folder="Routing")

# Modify the secret
existing.secret = "new-md5-secret-key"

# Pass modified object to update()
updated = client.bgp_auth_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
