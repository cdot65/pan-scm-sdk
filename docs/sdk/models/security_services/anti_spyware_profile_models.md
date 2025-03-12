# Anti-Spyware Profile Models

## Overview

The Anti-Spyware Profile models provide a structured way to manage anti-spyware security profiles in Palo Alto Networks'
Strata Cloud Manager. These models support configuring rules, threat exceptions, and MICA engine settings to detect and
prevent spyware
threats. Profiles can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs
when interacting
with the SCM API.

## Attributes

| Attribute                   | Type                                | Required | Default | Description                                            |
|-----------------------------|-------------------------------------|----------|---------|--------------------------------------------------------|
| name                        | str                                 | Yes      | None    | Name of the profile                                    |
| description                 | str                                 | No       | None    | Description of the profile                             |
| cloud_inline_analysis       | bool                                | No       | False   | Enable/disable cloud inline analysis                   |
| inline_exception_edl_url    | List[str]                           | No       | None    | List of inline exception EDL URLs                      |
| inline_exception_ip_address | List[str]                           | No       | None    | List of inline exception IP addresses                  |
| mica_engine_spyware_enabled | List[MicaEngineSpywareEnabledEntry] | No       | None    | List of MICA engine spyware enabled entries            |
| folder                      | str                                 | No*      | None    | Folder where profile is defined. Max length: 64 chars  |
| snippet                     | str                                 | No*      | None    | Snippet where profile is defined. Max length: 64 chars |
| device                      | str                                 | No*      | None    | Device where profile is defined. Max length: 64 chars  |
| rules                       | List[RuleRequest]                   | Yes      | None    | List of anti-spyware rules                             |
| threat_exception            | List[ThreatExceptionRequest]        | No       | None    | List of threat exceptions                              |
| id                          | UUID                                | Yes**    | None    | UUID of the profile (response only)                    |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

## Exceptions

The Anti-Spyware Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When invalid action configurations are provided in rules or threat exceptions
    - When invalid severity levels or categories are specified
    - When invalid packet capture settings are provided
    - When name pattern validation fails
    - When track_by pattern validation fails in block_ip actions
    - When duration values are outside allowed range (1-3600) in block_ip actions

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
try:
    profile = AntiSpywareProfileCreateModel(
        name="invalid-profile",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        rules=[{
            "name": "rule1",
            "severity": ["critical"],
            "category": "spyware",
            "action": {"alert": {}}
        }]
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### Action Validation

For rules and threat exceptions, exactly one action type must be specified:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
try:
    rule_dict = {
        "name": "invalid-rule",
        "severity": ["critical"],
        "category": "spyware",
        "action": {
            "alert": {},
            "drop": {}  # Can't specify multiple actions
        }
    }
    profile_dict = {
        "name": "test-profile",
        "folder": "Texas",
        "rules": [rule_dict]
    }
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."

# Using model directly
from scm.models.security import RuleRequest, ActionRequest

try:
    action = ActionRequest(root={"alert": {}, "drop": {}})
    rule = RuleRequest(
        name="invalid-rule",
        severity=["critical"],
        category="spyware",
        action=action
    )
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."
```

</div>

## Usage Examples

### Creating a Basic Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
basic_dict = {
    "name": "basic-profile",
    "description": "Basic anti-spyware profile",
    "folder": "Texas",
    "rules": [{
        "name": "basic-rule",
        "severity": ["critical", "high"],
        "category": "spyware",
        "action": {"alert": {}}
    }]
}

profile = AntiSpywareProfile(api_client)
response = profile.create(basic_dict)

# Using model directly
from scm.models.security import (
    AntiSpywareProfileCreateModel,
    RuleRequest,
    ActionRequest,
    AntiSpywareSeverity,
    AntiSpywareCategory
)

basic_profile = AntiSpywareProfileCreateModel(
    name="basic-profile",
    description="Basic anti-spyware profile",
    folder="Texas",
    rules=[
        RuleRequest(
            name="basic-rule",
            severity=[AntiSpywareSeverity.critical, AntiSpywareSeverity.high],
            category=AntiSpywareCategory.spyware,
            action=ActionRequest(root={"alert": {}})
        )
    ]
)

payload = basic_profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

</div>

### Creating a Profile with Threat Exceptions

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
advanced_dict = {
    "name": "advanced-profile",
    "folder": "Texas",
    "cloud_inline_analysis": True,
    "rules": [{
        "name": "strict-rule",
        "severity": ["critical"],
        "category": "spyware",
        "action": {"block_ip": {"track_by": "source", "duration": 300}}
    }],
    "threat_exception": [{
        "name": "exception1",
        "packet_capture": "single-packet",
        "action": {"allow": {}},
        "exempt_ip": [{"name": "10.0.0.1"}]
    }]
}

response = profile.create(advanced_dict)

# Using model directly
from scm.models.security import (
    ThreatExceptionRequest,
    AntiSpywareExemptIpEntry,
    AntiSpywarePacketCapture
)

advanced_profile = AntiSpywareProfileCreateModel(
    name="advanced-profile",
    folder="Security",
    cloud_inline_analysis=True,
    rules=[
        RuleRequest(
            name="strict-rule",
            severity=[AntiSpywareSeverity.critical],
            category=AntiSpywareCategory.spyware,
            action=ActionRequest(root={
                "block_ip": {
                    "track_by": "source",
                    "duration": 300
                }
            })
        )
    ],
    threat_exception=[
        ThreatExceptionRequest(
            name="exception1",
            packet_capture=AntiSpywarePacketCapture.single_packet,
            action=ActionRequest(root={"allow": {}}),
            exempt_ip=[AntiSpywareExemptIpEntry(name="10.0.0.1")]
        )
    ]
)

payload = advanced_profile.model_dump(exclude_unset=True)
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
    "description": "Updated profile",
    "rules": [{
        "name": "updated-rule",
        "severity": ["high"],
        "category": "dns-security",
        "action": {"drop": {}}
    }]
}

response = profile.update(update_dict)

# Using model directly
from scm.models.security import AntiSpywareProfileUpdateModel

update_profile = AntiSpywareProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="updated-profile",
    description="Updated profile",
    rules=[
        RuleRequest(
            name="updated-rule",
            severity=[AntiSpywareSeverity.high],
            category=AntiSpywareCategory.dns_security,
            action=ActionRequest(root={"drop": {}})
        )
    ]
)

payload = update_profile.model_dump(exclude_unset=True)
response = profile.update(payload)
```

</div>
