# SAML Server Profile

The `SamlServerProfile` service manages SAML server profile objects in Strata Cloud Manager, defining SAML Identity Provider (IdP) configurations for single sign-on authentication.

## Class Overview

The `SamlServerProfile` class provides CRUD operations for SAML server profile objects. It is accessed through the `client.saml_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the SamlServerProfile service
saml_profiles = client.saml_server_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
| `entity_id` | `str` | Yes | Entity ID (max 1024 chars) |
| `certificate` | `str` | Yes | Certificate name (max 63 chars) |
| `sso_url` | `str` | Yes | Single Sign-On URL (max 255 chars) |
| `sso_bindings` | `SamlSsoBindings` | Yes | SSO binding type (`post` or `redirect`) |
| `slo_bindings` | `SamlSloBindings` | No | SLO binding type (`post` or `redirect`) |
| `max_clock_skew` | `int` | No | Maximum clock skew in seconds (1-900) |
| `validate_idp_certificate` | `bool` | No | Validate IDP certificate |
| `want_auth_requests_signed` | `bool` | No | Want authentication requests signed |
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List SAML Server Profiles

Retrieves a list of SAML server profile objects with optional filtering.

```python
# List all SAML server profiles in a folder
profiles = client.saml_server_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}, Entity ID: {profile.entity_id}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |
| `exact_match` | `bool` | No | Only return objects exactly in the container |
| `exclude_folders` | `List[str]` | No | List of folders to exclude |
| `exclude_snippets` | `List[str]` | No | List of snippets to exclude |
| `exclude_devices` | `List[str]` | No | List of devices to exclude |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Fetch a SAML Server Profile

Retrieves a single SAML server profile by name and container.

```python
# Fetch a specific SAML server profile by name
profile = client.saml_server_profile.fetch(
    name="corp-saml-idp",
    folder="Texas"
)

print(f"Name: {profile.name}, SSO URL: {profile.sso_url}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the SAML server profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create a SAML Server Profile

Creates a new SAML server profile object.

```python
# Create a new SAML server profile
profile = client.saml_server_profile.create({
    "name": "corp-saml-idp",
    "folder": "Texas",
    "entity_id": "https://idp.example.com/saml/metadata",
    "certificate": "idp-signing-cert",
    "sso_url": "https://idp.example.com/saml/sso",
    "sso_bindings": "post",
    "slo_bindings": "post",
    "max_clock_skew": 60,
    "validate_idp_certificate": True
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update a SAML Server Profile

Updates an existing SAML server profile object.

```python
# Fetch, modify, update
profile = client.saml_server_profile.fetch(name="corp-saml-idp", folder="Texas")
profile.max_clock_skew = 120
profile.want_auth_requests_signed = True
updated = client.saml_server_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete a SAML Server Profile

Deletes a SAML server profile object by ID.

```python
# Delete by ID
client.saml_server_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### Okta SAML Integration

```python
# Create a SAML profile for Okta
profile = client.saml_server_profile.create({
    "name": "okta-saml",
    "folder": "Texas",
    "entity_id": "http://www.okta.com/exk1234567890",
    "certificate": "okta-signing-cert",
    "sso_url": "https://company.okta.com/app/paloalto/exk1234567890/sso/saml",
    "sso_bindings": "post",
    "slo_bindings": "redirect",
    "max_clock_skew": 60,
    "validate_idp_certificate": True,
    "want_auth_requests_signed": True
})
```

### Azure AD SAML Integration

```python
# Create a SAML profile for Azure AD
profile = client.saml_server_profile.create({
    "name": "azure-ad-saml",
    "folder": "Texas",
    "entity_id": "https://sts.windows.net/tenant-id/",
    "certificate": "azure-ad-cert",
    "sso_url": "https://login.microsoftonline.com/tenant-id/saml2",
    "sso_bindings": "redirect",
    "max_clock_skew": 120,
    "validate_idp_certificate": True
})
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.saml_server_profile.fetch(
        name="corp-saml-idp",
        folder="Texas"
    )
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid object: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Related Topics

- [SAML Server Profile Models](../../models/identity/saml_server_profile_models.md)
- [Authentication Profile](authentication_profile.md)
