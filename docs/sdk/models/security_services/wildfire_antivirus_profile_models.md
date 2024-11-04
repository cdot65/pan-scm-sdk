# WildFire Antivirus Profile Models

## Overview

The WildFire Antivirus Profile models provide a structured way to manage WildFire antivirus profiles in Palo Alto
Networks'
Strata Cloud Manager. These profiles define rules for malware analysis using either public or private cloud
infrastructure,
with support for packet capture, MLAV exceptions, and threat exceptions. The models handle validation of inputs and
outputs
when interacting with the SCM API.

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

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

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
        "folder": "Shared",
        "device": "fw01"  # Can't specify both folder and device
    }
    profile = WildfireAntivirusProfile(api_client)
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.security.wildfire_antivirus_profiles import WildfireAntivirusProfileCreateModel

# Error: no container specified
try:
    profile = WildfireAntivirusProfileCreateModel(
        name="invalid-profile",
        rules=[{
            "name": "rule1",
            "direction": "both"
        }]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### UUID Validation

For response models, the ID field must be a valid UUID:

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import WildfireAntivirusProfileResponseModel

# Error: invalid UUID
try:
    profile = WildfireAntivirusProfileResponseModel(
        id="invalid-uuid",
        name="test-profile",
        rules=[{
            "name": "rule1",
            "direction": "both"
        }],
        folder="Shared"
    )
except ValueError as e:
    print(e)  # "Invalid UUID format for 'id'"
```

</div>

## Usage Examples

### Creating a Basic Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.security import WildfireAntivirusProfile

profile_dict = {
    "name": "basic-profile",
    "description": "Basic WildFire profile",
    "folder": "Shared",
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
    WildfireAntivirusProfileCreateModel,
    RuleBase,
    Analysis,
    Direction
)

profile = WildfireAntivirusProfileCreateModel(
    name="basic-profile",
    description="Basic WildFire profile",
    folder="Shared",
    packet_capture=True,
    rules=[
        RuleBase(
            name="rule1",
            direction=Direction.both,
            analysis=Analysis.public_cloud,
            application=["web-browsing", "ssl"],
            file_type=["pe", "pdf"]
        )
    ]
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

</div>

### Creating a Profile with Exceptions

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
profile_dict = {
    "name": "advanced-profile",
    "description": "Profile with exceptions",
    "folder": "Shared",
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
    WildfireAntivirusProfileCreateModel,
    RuleBase,
    MlavExceptionEntry,
    ThreatExceptionEntry,
    Analysis,
    Direction
)

profile = WildfireAntivirusProfileCreateModel(
    name="advanced-profile",
    description="Profile with exceptions",
    folder="Shared",
    packet_capture=True,
    rules=[
        RuleBase(
            name="rule1",
            direction=Direction.both,
            analysis=Analysis.public_cloud,
            application=["any"],
            file_type=["any"]
        )
    ],
    mlav_exception=[
        MlavExceptionEntry(
            name="exception1",
            description="Test exception",
            filename="test.exe"
        )
    ],
    threat_exception=[
        ThreatExceptionEntry(
            name="threat1",
            notes="Known false positive"
        )
    ]
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

</div>

### Updating a Profile

<div class="termy">

<!-- termynal -->

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
    WildfireAntivirusProfileUpdateModel,
    RuleBase,
    Analysis,
    Direction
)

update = WildfireAntivirusProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="updated-profile",
    description="Updated description",
    packet_capture=False,
    rules=[
        RuleBase(
            name="updated-rule",
            direction=Direction.download,
            analysis=Analysis.private_cloud,
            application=["ftp"],
            file_type=["pe"]
        )
    ]
)

payload = update.model_dump(exclude_unset=True)
response = profile.update(payload)
```

</div>