# HIP Object

The `HIPObject` service manages Host Information Profile (HIP) objects in Strata Cloud Manager, defining security posture requirements for endpoints such as host info, disk encryption, and patch management criteria.

## Class Overview

The `HIPObject` class provides CRUD operations for HIP objects. It is accessed through the `client.hip_object` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the HIPObject service
hip_objects = client.hip_object
```

### Key Attributes

| Attribute          | Type                   | Required | Description                                |
|--------------------|------------------------|----------|--------------------------------------------|
| `name`             | `str`                  | Yes      | Name of HIP object (max 31 chars)          |
| `id`               | `UUID`                 | Yes*     | Unique identifier (*response only)         |
| `description`      | `str`                  | No       | Object description (max 255 chars)         |
| `host_info`        | `HostInfoModel`        | No       | Host information criteria                  |
| `network_info`     | `NetworkInfoModel`     | No       | Network information criteria               |
| `patch_management` | `PatchManagementModel` | No       | Patch management criteria                  |
| `disk_encryption`  | `DiskEncryptionModel`  | No       | Disk encryption criteria                   |
| `mobile_device`    | `MobileDeviceModel`    | No       | Mobile device criteria                     |
| `certificate`      | `CertificateModel`     | No       | Certificate criteria                       |
| `custom_checks`    | `CustomChecksModel`    | No       | Custom checks (registry, process, plist)   |
| `folder`           | `str`                  | Yes**    | Folder location (**one container required) |
| `snippet`          | `str`                  | Yes**    | Snippet location (**one container required)|
| `device`           | `str`                  | Yes**    | Device location (**one container required) |

\* Exactly one of `folder`, `snippet`, or `device` is required.

## Methods

### List HIP Objects

Retrieves a list of HIP objects with optional filtering.

```python
hips = client.hip_object.list(
    folder="Texas",
    criteria_types=["host_info", "disk_encryption"]
)

for hip in hips:
    print(f"Name: {hip.name}")
```

### Fetch a HIP Object

Retrieves a single HIP object by name and container.

```python
hip = client.hip_object.fetch(
    name="windows-workstation",
    folder="Texas"
)
print(f"Found HIP object: {hip.name}")
```

### Create a HIP Object

Creates a new HIP object.

```python
new_hip = client.hip_object.create({
    "name": "windows-workstation",
    "folder": "Texas",
    "description": "Windows workstation requirements",
    "host_info": {
        "criteria": {
            "os": {"contains": {"Microsoft": "All"}},
            "managed": True
        }
    }
})
```

### Update a HIP Object

Updates an existing HIP object.

```python
existing = client.hip_object.fetch(
    name="windows-workstation",
    folder="Texas"
)
existing.description = "Updated Windows workstation requirements"

updated = client.hip_object.update(existing)
```

### Delete a HIP Object

Deletes a HIP object by ID.

```python
client.hip_object.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Defining Endpoint Security Requirements

Create HIP objects for different security posture checks.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Host info based HIP object
client.hip_object.create({
    "name": "windows-workstation",
    "folder": "Texas",
    "description": "Windows workstation requirements",
    "host_info": {
        "criteria": {
            "os": {"contains": {"Microsoft": "All"}},
            "managed": True
        }
    }
})

# Disk encryption based HIP object
client.hip_object.create({
    "name": "encrypted-endpoints",
    "folder": "Texas",
    "description": "Disk encryption requirements",
    "disk_encryption": {
        "criteria": {
            "is_installed": True,
            "encrypted_locations": [
                {
                    "name": "C:",
                    "encryption_state": {"is": "encrypted"}
                }
            ]
        }
    }
})
```

### Filtering HIP Objects

Use advanced filtering to find specific HIP objects.

```python
# Exact match with exclusions
filtered = client.hip_object.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"]
)

for hip in filtered:
    print(f"HIP Object: {hip.name} in {hip.folder}")
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
    new_hip = client.hip_object.create({
        "name": "test-hip",
        "folder": "Texas",
        "description": "Test HIP object",
        "host_info": {
            "criteria": {"managed": True}
        }
    })
except InvalidObjectError as e:
    print(f"Invalid HIP object data: {e.message}")
except NameNotUniqueError as e:
    print(f"HIP object name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"HIP object not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"HIP object still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Related Topics

- [HIP Object Models](../../models/objects/hip_object_models.md#Overview)
- [HIP Profile](hip_profile.md)
