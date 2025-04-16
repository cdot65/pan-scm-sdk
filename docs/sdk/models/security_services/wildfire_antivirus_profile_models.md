# WildFire Antivirus Profile Models

## Overview {#Overview}

The WildFire Antivirus Profile models provide a structured way to manage WildFire antivirus profiles in Palo Alto
Networks' Strata Cloud Manager. These profiles define rules for malware analysis using either public or private cloud
infrastructure, with support for packet capture, MLAV exceptions, and threat exceptions. The models handle validation of
inputs and
outputs when interacting with the SCM API.

## Attributes

| Attribute        | Type                       | Required | Default | Description                                            |
|------------------|----------------------------|----------|---------|--------------------------------------------------------|
| name             | str                        | Yes      | None    | Profile name. Must match pattern: ^[a-zA-Z0-9._-]+$    |
| description      | str                        | No       | None    | Description of the profile                             |
| packet_capture   | bool                       | No       | False   | Whether packet capture is enabled                      |
| mlav_exception   | List[MlavExceptionEntry]   | No       | None    | List of MLAV exceptions                                |
| rules            | List[RuleBase]             | Yes      | None    | List of rules for the profile                          |
| threat_exception | List[ThreatExceptionEntry] | No       | None    | List of threat exceptions                              |
| folder           | str                        | No*      | None    | Folder where profile is defined. Max length: 64 chars  |
| snippet          | str                        | No*      | None    | Snippet where profile is defined. Max length: 64 chars |
| device           | str                        | No*      | None    | Device where profile is defined. Max length: 64 chars  |
| id               | UUID                       | Yes**    | None    | UUID of the profile (response only)                    |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The WildFire Antivirus Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When the name pattern validation fails (must match ^[a-zA-Z0-9._-]+$)
    - When container field pattern validation fails (must match ^[a-zA-Z\d\-_. ]+$)
    - When field length limits are exceeded (e.g., name > 63 chars, container fields > 64 chars)

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
from scm.config.security import WildfireAntivirusProfile

# Error: multiple containers specified
try:
    profile_dict = {
        "name": "invalid-profile",
        "rules": [{
            "name": "rule1",
            "direction": "both"
        }],
        "folder": "Texas",
        "device": "fw01"  # Can't specify both folder and device
    }
    profile = WildfireAntivirusProfile(api_client)
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.security.wildfire_antivirus_profiles import WildfireAvProfileCreateModel

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

### UUID Validation

For response models, the ID field must be a valid UUID:

```python
from scm.models.security.wildfire_antivirus_profiles import WildfireAvProfileResponseModel

# Error: invalid UUID
try:
    profile = WildfireAvProfileResponseModel(
        id="invalid-uuid",
        name="test-profile",
        rules=[{
            "name": "rule1",
            "direction": "both"
        }],
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "Invalid UUID format for 'id'"
```

## Usage Examples

### Creating a Basic Profile

```python
# Using dictionary
from scm.config.security import WildfireAntivirusProfile

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

profile = WildfireAntivirusProfile(api_client)
response = profile.create(profile_dict)

# Using model directly
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvProfileCreateModel,
    WildfireAvRuleBase,
    WildfireAvAnalysis,
    WildfireAvDirection
)

profile = WildfireAvProfileCreateModel(
    name="basic-profile",
    description="Basic WildFire profile",
    folder="Texas",
    packet_capture=True,
    rules=[
        WildfireAvRuleBase(
            name="rule1",
            direction=WildfireAvDirection.both,
            analysis=WildfireAvAnalysis.public_cloud,
            application=["web-browsing", "ssl"],
            file_type=["pe", "pdf"]
        )
    ]
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

### Creating a Profile with Exceptions

```python
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

response = profile.create(profile_dict)

# Using model directly
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvProfileCreateModel,
    WildfireAvRuleBase,
    WildfireAvMlavExceptionEntry,
    WildfireAvThreatExceptionEntry,
    WildfireAvAnalysis,
    WildfireAvDirection
)

profile = WildfireAvProfileCreateModel(
    name="advanced-profile",
    description="Profile with exceptions",
    folder="Texas",
    packet_capture=True,
    rules=[
        WildfireAvRuleBase(
            name="rule1",
            direction=WildfireAvDirection.both,
            analysis=WildfireAvAnalysis.public_cloud,
            application=["any"],
            file_type=["any"]
        )
    ],
    mlav_exception=[
        WildfireAvMlavExceptionEntry(
            name="exception1",
            description="Test exception",
            filename="test.exe"
        )
    ],
    threat_exception=[
        WildfireAvThreatExceptionEntry(
            name="threat1",
            notes="Known false positive"
        )
    ]
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

### Updating a Profile

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "updated-profile",
    "description": "Updated description",
    "packet_capture": False,
    "rules": [{
        "name": "updated-rule",
        "direction": "download",
        "analysis": "private-cloud",
        "application": ["ftp"],
        "file_type": ["pe"]
    }]
}

response = profile.update(update_dict)

# Using model directly
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAvProfileUpdateModel,
    WildfireAvRuleBase,
    WildfireAvAnalysis,
    WildfireAvDirection
)

update = WildfireAvProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="updated-profile",
    description="Updated description",
    packet_capture=False,
    rules=[
        WildfireAvRuleBase(
            name="updated-rule",
            direction=WildfireAvDirection.download,
            analysis=WildfireAvAnalysis.private_cloud,
            application=["ftp"],
            file_type=["pe"]
        )
    ]
)

payload = update.model_dump(exclude_unset=True)
response = profile.update(payload)
```
