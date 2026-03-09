# File Blocking Profile Models

## Overview

The File Blocking Profile models provide a structured way to manage file blocking profiles in Palo Alto Networks' Strata Cloud Manager.
These models support defining file blocking rules with actions, applications, directions, and file types to control file
transfers. Profiles can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs
when interacting with the SCM API.

## Models

The module provides the following Pydantic models:

- `FileBlockingProfileBaseModel`: Base model with fields common to all profile operations
- `FileBlockingProfileCreateModel`: Model for creating new file blocking profiles
- `FileBlockingProfileUpdateModel`: Model for updating existing file blocking profiles
- `FileBlockingProfileResponseModel`: Response model for file blocking profile operations
- `FileBlockingRule`: Model for individual file blocking rules within a profile

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### FileBlockingProfileBaseModel

| Attribute   | Type                      | Required | Default | Description                                            |
|-------------|---------------------------|----------|---------|--------------------------------------------------------|
| name        | str                       | Yes      | None    | Profile name                                           |
| description | str                       | No       | None    | Description of the profile                             |
| rules       | List[FileBlockingRule]    | No       | None    | List of file blocking rules                            |
| folder      | str                       | No**     | None    | Folder location. Max 64 chars                          |
| snippet     | str                       | No**     | None    | Snippet location. Max 64 chars                         |
| device      | str                       | No**     | None    | Device location. Max 64 chars                          |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### FileBlockingProfileCreateModel

Inherits all fields from `FileBlockingProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### FileBlockingProfileUpdateModel

Extends `FileBlockingProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### FileBlockingProfileResponseModel

Extends `FileBlockingProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

The response model uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept additional
fields returned by the API without raising validation errors.

## Enum Types

### FileBlockingAction

Defines the available file blocking actions:

| Value      | Description                                    |
|------------|------------------------------------------------|
| `alert`    | Alert on file transfer but allow it            |
| `block`    | Block the file transfer                        |
| `continue` | Prompt user for confirmation before continuing |

### FileBlockingDirection

Defines the direction of file transfer to match:

| Value      | Description                |
|------------|----------------------------|
| `download` | Match file downloads only  |
| `upload`   | Match file uploads only    |
| `both`     | Match both directions      |

## Component Models

### FileBlockingRule

Represents a rule within a file blocking profile. Each rule defines the action to take based on application, direction, and file type.

| Attribute   | Type                   | Required | Default           | Description                              |
|-------------|------------------------|----------|-------------------|------------------------------------------|
| name        | str                    | Yes      | None              | Name of the rule                         |
| action      | FileBlockingAction     | No       | alert             | Action to take when rule matches         |
| application | List[str]              | No       | ["any"]           | Applications to match                    |
| direction   | FileBlockingDirection  | No       | both              | Direction of file transfer               |
| file_type   | List[str]              | No       | ["any"]           | File types to match                      |

## Exceptions

The File Blocking Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import FileBlockingProfileCreateModel

# Error: multiple containers specified
try:
    profile = FileBlockingProfileCreateModel(
        name="invalid-profile",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        rules=[{
            "name": "rule1",
            "action": "block",
            "application": ["any"],
            "direction": "both",
            "file_type": ["exe"]
        }]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    profile = FileBlockingProfileCreateModel(
        name="invalid-profile",
        rules=[{
            "name": "rule1",
            "action": "block",
            "application": ["any"],
            "direction": "both",
            "file_type": ["exe"]
        }]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

## Usage Examples

### Creating a Basic Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile_dict = {
    "name": "basic-file-blocking",
    "description": "Basic file blocking profile",
    "folder": "Texas",
    "rules": [{
        "name": "block-exe",
        "action": "block",
        "application": ["any"],
        "direction": "both",
        "file_type": ["exe", "dll"]
    }]
}

response = client.file_blocking_profile.create(profile_dict)
print(f"Created profile: {response.name}")
```

### Creating a Profile with Multiple Rules

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create the profile with multiple rules using dictionary
multi_rule_config = {
    "name": "comprehensive-file-blocking",
    "description": "Profile with multiple file blocking rules",
    "folder": "Texas",
    "rules": [
        {
            "name": "block-executables",
            "action": "block",
            "application": ["web-browsing", "ftp"],
            "direction": "download",
            "file_type": ["exe", "msi", "bat", "cmd"]
        },
        {
            "name": "alert-documents",
            "action": "alert",
            "application": ["any"],
            "direction": "upload",
            "file_type": ["doc", "docx", "pdf", "xls", "xlsx"]
        },
        {
            "name": "continue-archives",
            "action": "continue",
            "application": ["any"],
            "direction": "download",
            "file_type": ["zip", "tar", "gz", "rar"]
        }
    ]
}

response = client.file_blocking_profile.create(multi_rule_config)
print(f"Created profile with {len(response.rules)} rules")
```

### Updating a Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.file_blocking_profile.fetch(name="basic-file-blocking", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated file blocking profile"

# Add a new rule
if existing.rules:
    existing.rules.append({
        "name": "alert-scripts",
        "action": "alert",
        "application": ["any"],
        "direction": "both",
        "file_type": ["js", "vbs", "ps1"]
    })

# Pass modified object to update()
updated = client.file_blocking_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Listing and Filtering Profiles

```python
# List all file blocking profiles in a folder
all_profiles = client.file_blocking_profile.list(folder="Texas")
print(f"Found {len(all_profiles)} profiles")

# Process results
for profile in all_profiles:
    print(f"Profile: {profile.name}")
    if profile.rules:
        print(f"  Rules: {len(profile.rules)}")
        for rule in profile.rules:
            print(f"    - {rule.name}: {rule.action} ({rule.direction})")
            print(f"      File types: {rule.file_type}")
```
