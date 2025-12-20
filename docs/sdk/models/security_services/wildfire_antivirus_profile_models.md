# WildFire Antivirus Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The WildFire Antivirus Profile models provide a structured way to manage WildFire antivirus profiles in Palo Alto
Networks' Strata Cloud Manager. These profiles define rules for malware analysis using either public or private cloud
infrastructure, with support for packet capture, MLAV exceptions, and threat exceptions. The models handle validation of
inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `WildfireAvProfileBase`: Base model with fields common to all profile operations
- `WildfireAvProfileCreateModel`: Model for creating new WildFire antivirus profiles
- `WildfireAvProfileUpdateModel`: Model for updating existing WildFire antivirus profiles
- `WildfireAvProfileResponseModel`: Response model for WildFire antivirus profile operations
- `WildfireAvRuleBase`: Model for rule configuration
- `WildfireAvMlavExceptionEntry`: Model for MLAV exception entries
- `WildfireAvThreatExceptionEntry`: Model for threat exception entries

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### WildfireAvProfileBase

| Attribute        | Type                                 | Required | Default | Description                                            |
|------------------|--------------------------------------|----------|---------|--------------------------------------------------------|
| name             | str                                  | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9._-]+$`             |
| description      | str                                  | No       | None    | Description of the profile                             |
| packet_capture   | bool                                 | No       | False   | Whether packet capture is enabled                      |
| rules            | List[WildfireAvRuleBase]             | Yes      | None    | List of rules for the profile                          |
| mlav_exception   | List[WildfireAvMlavExceptionEntry]   | No       | None    | List of MLAV exceptions                                |
| threat_exception | List[WildfireAvThreatExceptionEntry] | No       | None    | List of threat exceptions                              |
| folder           | str                                  | No**     | None    | Folder where profile is defined. Max length: 64 chars  |
| snippet          | str                                  | No**     | None    | Snippet where profile is defined. Max length: 64 chars |
| device           | str                                  | No**     | None    | Device where profile is defined. Max length: 64 chars  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### WildfireAvProfileCreateModel

Inherits all fields from `WildfireAvProfileBase` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### WildfireAvProfileUpdateModel

Extends `WildfireAvProfileBase` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### WildfireAvProfileResponseModel

Extends `WildfireAvProfileBase` by adding:

| Attribute     | Type | Required | Default | Description                          |
|---------------|------|----------|---------|--------------------------------------|
| id            | UUID | Yes      | None    | The unique identifier of the profile |
| override_loc  | str  | No       | None    | Override location                    |
| override_type | str  | No       | None    | Override type                        |
| override_id   | str  | No       | None    | Override ID                          |

## Enum Types

### WildfireAvAnalysis

Defines the analysis type options:

| Value           | Description                        |
|-----------------|------------------------------------|
| `public-cloud`  | Use public cloud for analysis      |
| `private-cloud` | Use private cloud for analysis     |

### WildfireAvDirection

Defines the traffic direction options:

| Value      | Description                          |
|------------|--------------------------------------|
| `download` | Analyze downloaded files             |
| `upload`   | Analyze uploaded files               |
| `both`     | Analyze both uploaded and downloaded |

## Supporting Models

### WildfireAvRuleBase

| Attribute   | Type                | Required | Default | Description                |
|-------------|---------------------|----------|---------|----------------------------|
| name        | str                 | Yes      | None    | Rule name                  |
| analysis    | WildfireAvAnalysis  | No       | None    | Analysis type              |
| direction   | WildfireAvDirection | Yes      | None    | Traffic direction          |
| application | List[str]           | No       | ["any"] | List of applications       |
| file_type   | List[str]           | No       | ["any"] | List of file types         |

### WildfireAvMlavExceptionEntry

| Attribute   | Type | Required | Default | Description      |
|-------------|------|----------|---------|------------------|
| name        | str  | Yes      | None    | Exception name   |
| description | str  | No       | None    | Description      |
| filename    | str  | Yes      | None    | Filename         |

### WildfireAvThreatExceptionEntry

| Attribute | Type | Required | Default | Description            |
|-----------|------|----------|---------|------------------------|
| name      | str  | Yes      | None    | Threat exception name  |
| notes     | str  | No       | None    | Notes                  |

## Exceptions

The WildFire Antivirus Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When the name pattern validation fails (must match `^[a-zA-Z0-9._-]+$`)
    - When container field pattern validation fails (must match `^[a-zA-Z\d\-_. ]+$`)
    - When field length limits are exceeded (e.g., container fields > 64 chars)

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security.wildfire_antivirus_profiles import WildfireAvProfileCreateModel

# Error: multiple containers specified
try:
    profile = WildfireAvProfileCreateModel(
        name="invalid-profile",
        rules=[{
            "name": "rule1",
            "direction": "both"
        }],
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    profile = WildfireAvProfileCreateModel(
        name="invalid-profile",
        rules=[{
            "name": "rule1",
            "direction": "both"
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
    "name": "basic-profile",
    "description": "Basic WildFire profile",
    "folder": "Texas",
    "packet_capture": True,
    "rules": [{
        "name": "rule1",
        "direction": "both",
        "analysis": "public-cloud",
        "application": ["web-browsing", "ssl"],
        "file_type": ["pe", "pdf"]
    }]
}

response = client.wildfire_antivirus_profile.create(profile_dict)
print(f"Created profile: {response.name}")
```

### Creating a Profile with Exceptions

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
    "name": "advanced-profile",
    "description": "Profile with exceptions",
    "folder": "Texas",
    "packet_capture": True,
    "rules": [{
        "name": "rule1",
        "direction": "both",
        "analysis": "public-cloud",
        "application": ["any"],
        "file_type": ["any"]
    }],
    "mlav_exception": [{
        "name": "exception1",
        "description": "Test exception",
        "filename": "test.exe"
    }],
    "threat_exception": [{
        "name": "threat1",
        "notes": "Known false positive"
    }]
}

response = client.wildfire_antivirus_profile.create(profile_dict)
print(f"Created profile with exceptions: {response.name}")
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
existing = client.wildfire_antivirus_profile.fetch(name="basic-profile", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated description"
existing.packet_capture = False

# Modify rule settings
if existing.rules:
    existing.rules[0].analysis = "private-cloud"
    existing.rules[0].direction = "download"

# Add a new rule
existing.rules.append({
    "name": "new-rule",
    "direction": "upload",
    "analysis": "public-cloud",
    "application": ["ftp"],
    "file_type": ["pe"]
})

# Pass modified object to update()
updated = client.wildfire_antivirus_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
