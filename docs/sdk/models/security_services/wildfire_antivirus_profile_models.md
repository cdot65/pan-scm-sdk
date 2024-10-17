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
profile_request = WildfireAntivirusProfileRequestModel(
    name="test-profile",
    description="Sample WildFire Antivirus Profile",
    folder="Prisma Access",
    rules=[
        RuleRequest(
            name="rule1",
            direction="both",
            analysis="public-cloud"
        )
    ]
)
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
profile_response = WildfireAntivirusProfileResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-profile",
    description="Sample WildFire Antivirus Profile",
    folder="Prisma Access",
    rules=[
        RuleResponse(
            name="rule1",
            direction="both",
            analysis="public-cloud"
        )
    ]
)
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

---

## MlavExceptionEntry

Represents an entry in the 'mlav_exception' list.

### Attributes

- `name` (str): **Required.** Exception name.
- `description` (Optional[str]): Description of the exception.
- `filename` (str): **Required.** Filename for the exception.

---

## ThreatExceptionEntry

Represents an entry in the 'threat_exception' list.

### Attributes

- `name` (str): **Required.** Threat exception name.
- `notes` (Optional[str]): Notes for the threat exception.

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
