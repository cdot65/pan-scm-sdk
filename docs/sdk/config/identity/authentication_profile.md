# Authentication Profile

The `AuthenticationProfile` service manages authentication profile objects in Strata Cloud Manager, defining how users authenticate using methods such as LDAP, RADIUS, SAML, Kerberos, TACACS+, local database, or cloud.

## Class Overview

The `AuthenticationProfile` class provides CRUD operations for authentication profile objects. It is accessed through the `client.authentication_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the AuthenticationProfile service
auth_profiles = client.authentication_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
| `method` | `AuthProfileMethod` | No | Authentication method configuration |
| `allow_list` | `List[str]` | No | Allow list (defaults to `["all"]`) |
| `lockout` | `AuthProfileLockout` | No | Account lockout configuration |
| `multi_factor_auth` | `Dict` | No | Multi-factor authentication configuration |
| `single_sign_on` | `Dict` | No | Single sign-on configuration |
| `user_domain` | `str` | No | User domain |
| `username_modifier` | `str` | No | Username modifier |
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Authentication Profiles

Retrieves a list of authentication profile objects with optional filtering.

```python
# List all authentication profiles in a folder
profiles = client.authentication_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}")
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

### Fetch an Authentication Profile

Retrieves a single authentication profile by name and container.

```python
# Fetch a specific authentication profile by name
profile = client.authentication_profile.fetch(
    name="corp-auth",
    folder="Texas"
)

print(f"Name: {profile.name}, ID: {profile.id}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the authentication profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create an Authentication Profile

Creates a new authentication profile object.

```python
# Create with LDAP method
profile = client.authentication_profile.create({
    "name": "corp-auth",
    "folder": "Texas",
    "method": {
        "ldap": {
            "server_profile": "corp-ldap",
            "login_attribute": "sAMAccountName",
            "passwd_exp_days": 90
        }
    },
    "allow_list": ["all"],
    "user_domain": "example.com"
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update an Authentication Profile

Updates an existing authentication profile object.

```python
# Fetch, modify, update
profile = client.authentication_profile.fetch(name="corp-auth", folder="Texas")
profile.user_domain = "internal.example.com"
updated = client.authentication_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete an Authentication Profile

Deletes an authentication profile object by ID.

```python
# Delete by ID
client.authentication_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### SAML-Based Single Sign-On

```python
# Create an authentication profile with SAML
profile = client.authentication_profile.create({
    "name": "saml-sso-profile",
    "folder": "Texas",
    "method": {
        "saml_idp": {
            "server_profile": "corp-saml-idp",
            "attribute_name_username": "email",
            "attribute_name_usergroup": "groups",
            "enable_single_logout": True
        }
    },
    "allow_list": ["all"]
})
```

### RADIUS Authentication with Lockout

```python
# Create an authentication profile with RADIUS and account lockout
profile = client.authentication_profile.create({
    "name": "radius-auth-profile",
    "folder": "Texas",
    "method": {
        "radius": {
            "server_profile": "corp-radius",
            "checkgroup": True
        }
    },
    "lockout": {
        "failed_attempts": 5,
        "lockout_time": 30
    },
    "allow_list": ["all"]
})
```

### List and Filter Profiles

```python
# List profiles with exact match and exclusions
profiles = client.authentication_profile.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"]
)

for profile in profiles:
    print(f"Profile: {profile.name}, Domain: {profile.user_domain}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.authentication_profile.fetch(
        name="corp-auth",
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

- [Authentication Profile Models](../../models/identity/authentication_profile_models.md)
- [LDAP Server Profile](ldap_server_profile.md)
- [RADIUS Server Profile](radius_server_profile.md)
- [SAML Server Profile](saml_server_profile.md)
- [Kerberos Server Profile](kerberos_server_profile.md)
- [TACACS+ Server Profile](tacacs_server_profile.md)
