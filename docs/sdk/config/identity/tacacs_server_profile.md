# TACACS+ Server Profile

The `TacacsServerProfile` service manages TACACS+ server profile objects in Strata Cloud Manager, defining TACACS+ servers used for terminal access controller authentication, authorization, and accounting.

## Class Overview

The `TacacsServerProfile` class provides CRUD operations for TACACS+ server profile objects. It is accessed through the `client.tacacs_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the TacacsServerProfile service
tacacs_profiles = client.tacacs_server_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
| `server` | `List[TacacsServer]` | No | List of TACACS+ servers |
| `protocol` | `TacacsProtocol` | No | Protocol type (`CHAP` or `PAP`) |
| `timeout` | `int` | No | Timeout in seconds (1-30) |
| `use_single_connection` | `bool` | No | Use single connection |
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List TACACS+ Server Profiles

Retrieves a list of TACACS+ server profile objects with optional filtering.

```python
# List all TACACS+ server profiles in a folder
profiles = client.tacacs_server_profile.list(folder="Texas")

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

### Fetch a TACACS+ Server Profile

Retrieves a single TACACS+ server profile by name and container.

```python
# Fetch a specific TACACS+ server profile by name
profile = client.tacacs_server_profile.fetch(
    name="corp-tacacs",
    folder="Texas"
)

print(f"Name: {profile.name}, ID: {profile.id}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the TACACS+ server profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create a TACACS+ Server Profile

Creates a new TACACS+ server profile object.

```python
# Create a new TACACS+ server profile
profile = client.tacacs_server_profile.create({
    "name": "corp-tacacs",
    "folder": "Texas",
    "server": [
        {
            "name": "tacacs-primary",
            "address": "10.0.1.50",
            "port": 49,
            "secret": "shared-secret"
        }
    ],
    "protocol": "CHAP",
    "timeout": 5,
    "use_single_connection": True
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update a TACACS+ Server Profile

Updates an existing TACACS+ server profile object.

```python
# Fetch, modify, update
profile = client.tacacs_server_profile.fetch(name="corp-tacacs", folder="Texas")
profile.timeout = 10
profile.use_single_connection = False
updated = client.tacacs_server_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete a TACACS+ Server Profile

Deletes a TACACS+ server profile object by ID.

```python
# Delete by ID
client.tacacs_server_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### High-Availability TACACS+ Setup

```python
# Create a profile with primary and backup TACACS+ servers
profile = client.tacacs_server_profile.create({
    "name": "corp-tacacs-ha",
    "folder": "Texas",
    "server": [
        {
            "name": "tacacs-primary",
            "address": "10.0.1.50",
            "port": 49,
            "secret": "primary-secret"
        },
        {
            "name": "tacacs-backup",
            "address": "10.0.1.51",
            "port": 49,
            "secret": "backup-secret"
        }
    ],
    "protocol": "PAP",
    "timeout": 3,
    "use_single_connection": True
})
```

### Audit TACACS+ Configurations

```python
# List and audit all TACACS+ profiles
profiles = client.tacacs_server_profile.list(
    folder="Texas",
    exact_match=True
)

for profile in profiles:
    server_count = len(profile.server) if profile.server else 0
    protocol = profile.protocol if profile.protocol else "Not set"
    print(f"Profile: {profile.name}, Servers: {server_count}, Protocol: {protocol}")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.tacacs_server_profile.fetch(
        name="corp-tacacs",
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

- [TACACS+ Server Profile Models](../../models/identity/tacacs_server_profile_models.md)
- [Authentication Profile](authentication_profile.md)
