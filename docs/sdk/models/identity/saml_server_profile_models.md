# SAML Server Profile Models

Models for SAML server profile objects in Strata Cloud Manager, defining SAML Identity Provider (IdP) configurations for single sign-on authentication.

## Overview

The SAML Server Profile models support the following key attributes:

- Profile name and container assignment
- Entity ID and certificate for IdP identification
- SSO URL and binding type configuration
- SLO binding type configuration
- Clock skew tolerance and certificate validation settings

## Base Models

### SamlServerProfileBaseModel

The base model contains fields common to all CRUD operations.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `entity_id` | `str` | Yes | Entity ID (max 1024 chars) |
| `certificate` | `str` | Yes | Certificate name (max 63 chars) |
| `sso_url` | `str` | Yes | Single Sign-On URL (max 255 chars) |
| `sso_bindings` | `SamlSsoBindings` | Yes | SSO binding type |
| `slo_bindings` | `SamlSloBindings` | No | SLO binding type |
| `max_clock_skew` | `int` | No | Maximum clock skew in seconds (1-900) |
| `validate_idp_certificate` | `bool` | No | Validate IDP certificate |
| `want_auth_requests_signed` | `bool` | No | Want authentication requests signed |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### SamlServerProfileCreateModel

Inherits from `SamlServerProfileBaseModel` and adds container validation ensuring exactly one of `folder`, `snippet`, or `device` is provided.

### SamlServerProfileUpdateModel

Inherits from `SamlServerProfileBaseModel` with an additional required field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

### SamlServerProfileResponseModel

Inherits from `SamlServerProfileBaseModel` with an additional field:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | `UUID` | Yes | The unique identifier of the profile |

!!! note
    The response model uses `extra="ignore"` to handle any additional fields returned by the API.

## Enums

### SamlSsoBindings

SSO binding type enumeration.

| Value | Description |
| --- | --- |
| `post` | HTTP POST binding |
| `redirect` | HTTP Redirect binding |

### SamlSloBindings

SLO binding type enumeration.

| Value | Description |
| --- | --- |
| `post` | HTTP POST binding |
| `redirect` | HTTP Redirect binding |

## Usage Examples

### Creating a SAML Server Profile

```python
from scm.models.identity.saml_server_profiles import (
    SamlServerProfileCreateModel,
    SamlSsoBindings,
    SamlSloBindings,
)

# Create model instance
profile = SamlServerProfileCreateModel(
    name="corp-saml-idp",
    folder="Texas",
    entity_id="https://idp.example.com/saml/metadata",
    certificate="idp-signing-cert",
    sso_url="https://idp.example.com/saml/sso",
    sso_bindings=SamlSsoBindings.post,
    slo_bindings=SamlSloBindings.post,
    max_clock_skew=60,
    validate_idp_certificate=True,
    want_auth_requests_signed=True
)

# Use with SDK
payload = profile.model_dump(exclude_unset=True)
result = client.saml_server_profile.create(payload)
```

### Parsing a SAML Server Profile Response

```python
from scm.models.identity.saml_server_profiles import (
    SamlServerProfileResponseModel,
)

# Parse API response
response = SamlServerProfileResponseModel(**api_response)
print(f"Name: {response.name}")
print(f"Entity ID: {response.entity_id}")
print(f"SSO URL: {response.sso_url}")
print(f"SSO Binding: {response.sso_bindings}")
```

## Related Topics

- [SAML Server Profile Service](../../config/identity/saml_server_profile.md)
- [Authentication Profile Models](authentication_profile_models.md)
