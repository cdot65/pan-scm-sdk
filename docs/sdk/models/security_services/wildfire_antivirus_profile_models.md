# WildFire Antivirus Profile Models

This section covers the data models associated with the `WildfireAntivirusProfile` configuration object.

---

## WildfireAntivirusProfileRequestModel

Used when creating or updating a WildFire Antivirus Profile object.

### Attributes

- `name` (str): **Required.** The name of the WildFire Antivirus Profile object.
- `description` (Optional[str]): A description of the WildFire Antivirus Profile object.
- `packet_capture` (Optional[bool]): Whether packet capture is enabled.
- `mlav_exception` (Optional[List[MlavExceptionEntry]]): List of MLAV exceptions.
- `rules` (List[RuleBase]): **Required.** List of rules for the profile.
- `threat_exception` (Optional[List[ThreatExceptionEntry]]): List of threat exceptions.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import WildfireAntivirusProfileRequestModel, RuleRequest, Analysis,
    Direction

profile_request = WildfireAntivirusProfileRequestModel(
    name="test-profile",
    description="Sample WildFire Antivirus Profile",
    folder="Prisma Access",
    packet_capture=True,
    rules=[
        RuleRequest(
            name="rule1",
            direction=Direction.both,
            analysis=Analysis.public_cloud,
            application=["web-browsing", "ssl"],
            file_type=["pe", "pdf"]
        )
    ]
)

print(profile_request.model_dump_json(indent=2))
```

</div>

---

## WildfireAntivirusProfileResponseModel

Used when parsing WildFire Antivirus Profile objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the WildFire Antivirus Profile object.
- `name` (str): The name of the WildFire Antivirus Profile object.
- `description` (Optional[str]): A description of the WildFire Antivirus Profile object.
- `packet_capture` (Optional[bool]): Whether packet capture is enabled.
- `mlav_exception` (Optional[List[MlavExceptionEntry]]): List of MLAV exceptions.
- `rules` (List[RuleBase]): List of rules for the profile.
- `threat_exception` (Optional[List[ThreatExceptionEntry]]): List of threat exceptions.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import WildfireAntivirusProfileResponseModel, RuleResponse,
    Analysis, Direction

profile_response = WildfireAntivirusProfileResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-profile",
    description="Sample WildFire Antivirus Profile",
    folder="Prisma Access",
    packet_capture=True,
    rules=[
        RuleResponse(
            name="rule1",
            direction=Direction.both,
            analysis=Analysis.public_cloud,
            application=["web-browsing", "ssl"],
            file_type=["pe", "pdf"]
        )
    ]
)

print(profile_response.model_dump_json(indent=2))
```

</div>

---

## RuleBase

Base class for Rule objects used in WildFire Antivirus Profiles.

### Attributes

- `name` (str): **Required.** Rule name.
- `analysis` (Optional[Analysis]): Analysis type (public-cloud or private-cloud).
- `application` (List[str]): List of applications (default: ["any"]).
- `direction` (Direction): **Required.** Direction (download, upload, or both).
- `file_type` (List[str]): List of file types (default: ["any"]).

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import RuleBase, Analysis, Direction

rule = RuleBase(
    name="example_rule",
    analysis=Analysis.public_cloud,
    application=["web-browsing", "ssl"],
    direction=Direction.both,
    file_type=["pe", "pdf"]
)

print(rule.model_dump_json(indent=2))
```

</div>

---

## MlavExceptionEntry

Represents an entry in the 'mlav_exception' list.

### Attributes

- `name` (str): **Required.** Exception name.
- `description` (Optional[str]): Description of the exception.
- `filename` (str): **Required.** Filename for the exception.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import MlavExceptionEntry

mlav_exception = MlavExceptionEntry(
    name="exception1",
    description="MLAV exception for specific file",
    filename="allowed_file.exe"
)

print(mlav_exception.model_dump_json(indent=2))
```

</div>

---

## ThreatExceptionEntry

Represents an entry in the 'threat_exception' list.

### Attributes

- `name` (str): **Required.** Threat exception name.
- `notes` (Optional[str]): Notes for the threat exception.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import ThreatExceptionEntry

threat_exception = ThreatExceptionEntry(
    name="threat_exception1",
    notes="Exception for known false positive"
)

print(threat_exception.model_dump_json(indent=2))
```

</div>

---

## Enums

### Analysis

Enumeration of analysis types:

- `public_cloud`
- `private_cloud`

### Direction

Enumeration of directions:

- `download`
- `upload`
- `both`

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import Analysis, Direction

print(f"Analysis types: {[a.value for a in Analysis]}")
print(f"Direction types: {[d.value for d in Direction]}")
```

</div>

---

## Full Example: Creating a Comprehensive WildFire Antivirus Profile Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.wildfire_antivirus_profiles import (
    WildfireAntivirusProfileRequestModel,
    RuleRequest,
    MlavExceptionEntry,
    ThreatExceptionEntry,
    Analysis,
    Direction
)

# Create a comprehensive WildFire Antivirus Profile model
comprehensive_profile = WildfireAntivirusProfileRequestModel(
    name="comprehensive_profile",
    description="Comprehensive WildFire Antivirus Profile",
    folder="Prisma Access",
    packet_capture=True,
    rules=[
        RuleRequest(
            name="rule1",
            direction=Direction.both,
            analysis=Analysis.public_cloud,
            application=["web-browsing", "ssl"],
            file_type=["pe", "pdf"]
        ),
        RuleRequest(
            name="rule2",
            direction=Direction.upload,
            analysis=Analysis.private_cloud,
            application=["ftp", "sftp"],
            file_type=["any"]
        )
    ],
    mlav_exception=[
        MlavExceptionEntry(
            name="mlav_exception1",
            description="MLAV exception for specific file",
            filename="allowed_file.exe"
        )
    ],
    threat_exception=[
        ThreatExceptionEntry(
            name="threat_exception1",
            notes="Exception for known false positive"
        )
    ]
)

# Print the JSON representation of the model
print(comprehensive_profile.model_dump_json(indent=2))

# Validate the model
comprehensive_profile.model_validate(comprehensive_profile.model_dump())
print("Model validation successful")
```

</div>

This example demonstrates how to create a comprehensive WildFire Antivirus Profile model using the provided classes and
enums. It includes multiple rules, MLAV exceptions, and threat exceptions to showcase the full capabilities of the
model.
