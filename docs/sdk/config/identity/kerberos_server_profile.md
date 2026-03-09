# Kerberos Server Profile

The `KerberosServerProfile` service manages Kerberos server profile objects in Strata Cloud Manager, defining Kerberos Key Distribution Center (KDC) servers used for authentication.

## Class Overview

The `KerberosServerProfile` class provides CRUD operations for Kerberos server profile objects. It is accessed through the `client.kerberos_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the KerberosServerProfile service
kerberos_profiles = client.kerberos_server_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
| `server` | `List[KerberosServer]` | No | List of Kerberos servers |
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List Kerberos Server Profiles

Retrieves a list of Kerberos server profile objects with optional filtering.

```python
# List all Kerberos server profiles in a folder
profiles = client.kerberos_server_profile.list(folder="Texas")

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

### Fetch a Kerberos Server Profile

Retrieves a single Kerberos server profile by name and container.

```python
# Fetch a specific Kerberos server profile by name
profile = client.kerberos_server_profile.fetch(
    name="corp-kerberos",
    folder="Texas"
)

print(f"Name: {profile.name}, ID: {profile.id}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the Kerberos server profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create a Kerberos Server Profile

Creates a new Kerberos server profile object.

```python
# Create a new Kerberos server profile
profile = client.kerberos_server_profile.create({
    "name": "corp-kerberos",
    "folder": "Texas",
    "server": [
        {
            "name": "kdc-primary",
            "host": "kdc.example.com",
            "port": 88
        }
    ]
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update a Kerberos Server Profile

Updates an existing Kerberos server profile object.

```python
# Fetch, modify, update
profile = client.kerberos_server_profile.fetch(name="corp-kerberos", folder="Texas")
profile.server = [
    {"name": "kdc-primary", "host": "kdc1.example.com", "port": 88},
    {"name": "kdc-secondary", "host": "kdc2.example.com", "port": 88}
]
updated = client.kerberos_server_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete a Kerberos Server Profile

Deletes a Kerberos server profile object by ID.

```python
# Delete by ID
client.kerberos_server_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### Multiple KDC Servers

```python
# Create a profile with primary and backup KDC servers
profile = client.kerberos_server_profile.create({
    "name": "corp-kerberos-ha",
    "folder": "Texas",
    "server": [
        {
            "name": "kdc-primary",
            "host": "kdc1.example.com",
            "port": 88
        },
        {
            "name": "kdc-backup",
            "host": "kdc2.example.com",
            "port": 88
        }
    ]
})
```

### Bulk Profile Management

```python
# List and audit all Kerberos server profiles
profiles = client.kerberos_server_profile.list(
    folder="Texas",
    exact_match=True
)

for profile in profiles:
    server_count = len(profile.server) if profile.server else 0
    print(f"Profile: {profile.name}, Servers: {server_count}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.kerberos_server_profile.fetch(
        name="corp-kerberos",
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

- [Kerberos Server Profile Models](../../models/identity/kerberos_server_profile_models.md)
- [Authentication Profile](authentication_profile.md)
