# RADIUS Server Profile

The `RadiusServerProfile` service manages RADIUS server profile objects in Strata Cloud Manager, defining RADIUS servers used for centralized authentication, authorization, and accounting (AAA).

## Class Overview

The `RadiusServerProfile` class provides CRUD operations for RADIUS server profile objects. It is accessed through the `client.radius_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the RadiusServerProfile service
radius_profiles = client.radius_server_profile
```

### Key Attributes

| Attribute | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | Profile name |
| `id` | `UUID` | Yes* | Unique identifier (*response only) |
| `server` | `List[RadiusServer]` | No | List of RADIUS servers |
| `protocol` | `RadiusProtocol` | No | RADIUS protocol configuration |
| `retries` | `int` | No | Number of retries (1-5) |
| `timeout` | `int` | No | Timeout in seconds (1-120) |
| `folder` | `str` | No* | Folder location |
| `snippet` | `str` | No* | Snippet location |
| `device` | `str` | No* | Device location |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List RADIUS Server Profiles

Retrieves a list of RADIUS server profile objects with optional filtering.

```python
# List all RADIUS server profiles in a folder
profiles = client.radius_server_profile.list(folder="Texas")

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

### Fetch a RADIUS Server Profile

Retrieves a single RADIUS server profile by name and container.

```python
# Fetch a specific RADIUS server profile by name
profile = client.radius_server_profile.fetch(
    name="corp-radius",
    folder="Texas"
)

print(f"Name: {profile.name}, ID: {profile.id}")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | `str` | Yes | The name of the RADIUS server profile |
| `folder` | `str` | No* | Folder in which the resource is defined |
| `snippet` | `str` | No* | Snippet in which the resource is defined |
| `device` | `str` | No* | Device in which the resource is defined |

\* Exactly one of `folder`, `snippet`, or `device` is required.

### Create a RADIUS Server Profile

Creates a new RADIUS server profile object.

```python
# Create a new RADIUS server profile
profile = client.radius_server_profile.create({
    "name": "corp-radius",
    "folder": "Texas",
    "server": [
        {
            "name": "radius-primary",
            "ip_address": "10.0.1.100",
            "port": 1812,
            "secret": "shared-secret"
        }
    ],
    "protocol": {"CHAP": {}},
    "timeout": 5,
    "retries": 3
})

print(f"Created profile: {profile.name} (ID: {profile.id})")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `data` | `Dict[str, Any]` | Yes | Dictionary containing the profile configuration |

### Update a RADIUS Server Profile

Updates an existing RADIUS server profile object.

```python
# Fetch, modify, update
profile = client.radius_server_profile.fetch(name="corp-radius", folder="Texas")
profile.timeout = 10
profile.retries = 5
updated = client.radius_server_profile.update(profile)

print(f"Updated profile: {updated.name}")
```

### Delete a RADIUS Server Profile

Deletes a RADIUS server profile object by ID.

```python
# Delete by ID
client.radius_server_profile.delete("abcd1234-5678-9abc-def0-123456789abc")
```

**Parameters:**

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `object_id` | `str` | Yes | The UUID of the profile to delete |

## Use Cases

### High-Availability RADIUS Setup

```python
# Create a profile with primary and backup RADIUS servers
profile = client.radius_server_profile.create({
    "name": "corp-radius-ha",
    "folder": "Texas",
    "server": [
        {
            "name": "radius-primary",
            "ip_address": "10.0.1.100",
            "port": 1812,
            "secret": "primary-secret"
        },
        {
            "name": "radius-backup",
            "ip_address": "10.0.1.101",
            "port": 1812,
            "secret": "backup-secret"
        }
    ],
    "protocol": {"PAP": {}},
    "timeout": 3,
    "retries": 3
})
```

### EAP-TTLS with PAP Protocol

```python
# Create a RADIUS profile with EAP-TTLS
profile = client.radius_server_profile.create({
    "name": "eap-radius",
    "folder": "Texas",
    "server": [
        {
            "name": "radius-eap",
            "ip_address": "10.0.1.100",
            "port": 1812,
            "secret": "eap-secret"
        }
    ],
    "protocol": {"EAP_TTLS_with_PAP": {}},
    "timeout": 10,
    "retries": 3
})
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    profile = client.radius_server_profile.fetch(
        name="corp-radius",
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

- [RADIUS Server Profile Models](../../models/identity/radius_server_profile_models.md)
- [Authentication Profile](authentication_profile.md)
