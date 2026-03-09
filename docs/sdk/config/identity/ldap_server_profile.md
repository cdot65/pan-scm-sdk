# LDAP Server Profile

The `LdapServerProfile` service manages LDAP server profile objects in Strata Cloud Manager, defining LDAP directory servers used for user authentication and group lookups.

## Class Overview

The `LdapServerProfile` class provides CRUD operations for LDAP server profile objects. It is accessed through the `client.ldap_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the LdapServerProfile service
ldap_profiles = client.ldap_server_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
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
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List LDAP Server Profiles

Retrieves a list of LDAP server profile objects with optional filtering.

```python
# List all LDAP server profiles in a folder
profiles = client.ldap_server_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}, Type: {profile.ldap_type}")
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

### Fetch an LDAP Server Profile

Retrieves a single LDAP server profile by name and container.

```python
# Fetch a specific LDAP server profile by name
profile = client.ldap_server_profile.fetch(
    name="corp-ldap",
    folder="Texas"
)

print(f"Name: {profile.name}, Base DN: {profile.base}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the LDAP server profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create an LDAP Server Profile

Creates a new LDAP server profile object.

```python
# Create a new LDAP server profile
profile = client.ldap_server_profile.create({
    "name": "corp-ldap",
    "folder": "Texas",
    "server": [
        {
            "name": "ldap-primary",
            "address": "ldap.example.com",
            "port": 389
        }
    ],
    "base": "dc=example,dc=com",
    "bind_dn": "cn=admin,dc=example,dc=com",
    "bind_password": "admin-password",
    "ldap_type": "active-directory",
    "ssl": True
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update an LDAP Server Profile

Updates an existing LDAP server profile object.

```python
# Fetch, modify, update
profile = client.ldap_server_profile.fetch(name="corp-ldap", folder="Texas")
profile.ssl = True
profile.verify_server_certificate = True
updated = client.ldap_server_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete an LDAP Server Profile

Deletes an LDAP server profile object by ID.

```python
# Delete by ID
client.ldap_server_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### Active Directory Integration

```python
# Create an LDAP profile for Active Directory
profile = client.ldap_server_profile.create({
    "name": "ad-integration",
    "folder": "Texas",
    "server": [
        {
            "name": "dc-primary",
            "address": "dc1.example.com",
            "port": 636
        },
        {
            "name": "dc-secondary",
            "address": "dc2.example.com",
            "port": 636
        }
    ],
    "base": "dc=example,dc=com",
    "bind_dn": "cn=svc-firewall,ou=services,dc=example,dc=com",
    "bind_password": "service-password",
    "ldap_type": "active-directory",
    "ssl": True,
    "verify_server_certificate": True,
    "timelimit": 30,
    "bind_timelimit": "30"
})
```

### Audit LDAP Configurations

```python
# List and audit all LDAP profiles for SSL compliance
profiles = client.ldap_server_profile.list(
    folder="Texas",
    exact_match=True
)

for profile in profiles:
    ssl_status = "Enabled" if profile.ssl else "Disabled"
    print(f"Profile: {profile.name}, SSL: {ssl_status}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.ldap_server_profile.fetch(
        name="corp-ldap",
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

- [LDAP Server Profile Models](../../models/identity/ldap_server_profile_models.md)
- [Authentication Profile](authentication_profile.md)
