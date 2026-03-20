# HIP Profile

The `HIPProfile` service manages Host Information Profile (HIP) profiles in Strata Cloud Manager, defining security posture matching criteria that can be used in security policies to enforce endpoint compliance.

## Class Overview

The `HIPProfile` class provides CRUD operations for HIP profile objects. It is accessed through the `client.hip_profile` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the HIPProfile service
hip_profiles = client.hip_profile
```

### Key Attributes

| Attribute     | Type   | Required | Description                                      |
|---------------|--------|----------|--------------------------------------------------|
| `name`        | `str`  | Yes      | Name of HIP profile (max 31 chars)               |
| `id`          | `UUID` | Yes*     | Unique identifier (*response only)               |
| `description` | `str`  | No       | Profile description (max 255 chars)              |
| `match`       | `str`  | Yes      | Match expression for the profile (max 2048 chars)|
| `folder`      | `str`  | Yes**    | Folder location (**one container required)       |
| `snippet`     | `str`  | Yes**    | Snippet location (**one container required)      |
| `device`      | `str`  | Yes**    | Device location (**one container required)       |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List HIP Profiles

Retrieves a list of HIP profiles with optional filtering.

```python
profiles = client.hip_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}, Match: {profile.match}")
```

### Fetch a HIP Profile

Retrieves a single HIP profile by name and container.

```python
profile = client.hip_profile.fetch(
    name="windows-workstations",
    folder="Texas"
)
print(f"Found profile: {profile.name}")
```

### Create a HIP Profile

Creates a new HIP profile.

```python
new_profile = client.hip_profile.create({
    "name": "windows-workstations",
    "folder": "Texas",
    "description": "Windows workstations with basic security requirements",
    "match": '"is-win"'
})
```

### Update a HIP Profile

Updates an existing HIP profile.

```python
existing = client.hip_profile.fetch(
    name="windows-workstations",
    folder="Texas"
)
existing.match = '"is-win" and "is-firewall-enabled" and "is-disk-encrypted"'
existing.description = "Enhanced security requirements"

updated = client.hip_profile.update(existing)
```

### Delete a HIP Profile

Deletes a HIP profile by ID.

```python
client.hip_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Creating Profiles with Match Expressions

Define HIP profiles using boolean match expressions referencing HIP objects.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Simple match expression
client.hip_profile.create({
    "name": "windows-workstations",
    "folder": "Texas",
    "description": "Windows workstations",
    "match": '"is-win"'
})

# Combined AND/OR logic
client.hip_profile.create({
    "name": "secure-workstations",
    "folder": "Texas",
    "description": "Secured workstations with enhanced posture",
    "match": '"is-win" and "is-firewall-enabled"'
})

# Negative match expression
client.hip_profile.create({
    "name": "non-windows-devices",
    "folder": "Texas",
    "description": "All devices except Windows",
    "match": 'not ("is-win")'
})
```

### Filtering HIP Profiles

Use advanced filtering to find specific profiles.

```python
# Exact match with exclusions
filtered = client.hip_profile.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"]
)

for profile in filtered:
    print(f"Profile: {profile.name} in {profile.folder}")
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    new_profile = client.hip_profile.create({
        "name": "test-hip-profile",
        "folder": "Texas",
        "description": "Test HIP profile",
        "match": '"is-win" or "is-mac"'
    })
except InvalidObjectError as e:
    print(f"Invalid HIP profile data: {e.message}")
except NameNotUniqueError as e:
    print(f"HIP profile name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"HIP profile not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"HIP profile still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [HIP Profile Models](../../models/objects/hip_profile_models.md#Overview)
- [HIP Object](hip_object.md)
