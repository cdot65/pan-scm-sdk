# Anti-Spyware Profile Models

## Overview {#Overview}

The Anti-Spyware Profile models provide a structured way to manage anti-spyware security profiles in Palo Alto Networks' Strata Cloud Manager. These models support configuring rules, threat exceptions, and MICA engine settings to detect and prevent spyware threats. Profiles can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute                   | Type                                | Required | Default | Description                                            |
|-----------------------------|-------------------------------------|----------|---------|--------------------------------------------------------|
| name                        | str                                 | Yes      | None    | Name of the profile. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| description                 | str                                 | No       | None    | Description of the profile. Max length: 1023 chars      |
| cloud_inline_analysis       | bool                                | No       | False   | Enable/disable cloud inline analysis                   |
| inline_exception_edl_url    | List[str]                           | No       | None    | List of inline exception EDL URLs                      |
| inline_exception_ip_address | List[str]                           | No       | None    | List of inline exception IP addresses                  |
| mica_engine_spyware_enabled | List[MicaEngineSpywareEnabledEntry] | No       | None    | List of MICA engine spyware enabled entries            |
| rules                       | List[RuleRequest]                   | Yes      | None    | List of anti-spyware rules                             |
| threat_exception            | List[ThreatExceptionRequest]        | No       | None    | List of threat exceptions                              |
| folder                      | str                                 | No*      | None    | Folder where profile is defined. Max length: 64 chars  |
| snippet                     | str                                 | No*      | None    | Snippet where profile is defined. Max length: 64 chars |
| device                      | str                                 | No*      | None    | Device where profile is defined. Max length: 64 chars  |
| id                          | UUID                                | Yes**    | None    | UUID of the profile (response only)                    |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

### RuleRequest Attributes

| Attribute     | Type            | Required | Default | Description                                      |
|---------------|-----------------|----------|---------|--------------------------------------------------|
| name          | str             | Yes      | None    | Name of the rule                                 |
| severity      | List[str]       | Yes      | None    | Severity levels for the rule (critical/high/medium/low/informational) |
| category      | str             | Yes      | None    | Category for the rule (spyware/dns-security/command-and-control/...) |
| action        | ActionRequest   | Yes      | None    | Action to take when rule matches                 |
| packet_capture| str             | No       | None    | Packet capture setting (disable/single-packet/extended) |
| threat_name   | str             | No       | None    | Specific threat name to match                    |

### ThreatExceptionRequest Attributes

| Attribute       | Type                          | Required | Default | Description                                            |
|-----------------|-------------------------------|----------|---------|--------------------------------------------------------|
| name            | str                           | Yes      | None    | Name of the threat exception                           |
| action          | ActionRequest                 | No       | None    | Action for the exception                               |
| packet_capture  | str                           | No       | None    | Packet capture setting for the exception               |
| exempt_ip       | List[AntiSpywareExemptIpEntry]| No       | None    | List of exempt IP addresses                            |

### ActionRequest Attributes

The action configuration follows a discriminated union pattern where exactly one action type must be provided:

| Attribute    | Type          | Required | Description                                      |
|--------------|---------------|----------|--------------------------------------------------|
| root         | Dict[str, Any]| Yes      | Contains exactly one action type (alert/allow/block/block-ip/drop/reset-both/reset-client/reset-server) |

## Exceptions

The Anti-Spyware Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When multiple action types are specified in an action configuration
    - When invalid severity levels or categories are provided
    - When invalid packet capture settings are provided
    - When name pattern validation fails
    - When track_by pattern validation fails in block_ip actions
    - When duration values are outside allowed range (1-3600) in block_ip actions

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security_services import AntiSpywareProfileCreateModel

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

# This will also raise a validation error
try:
    profile = AntiSpywareProfileCreateModel(
        name="invalid-profile",
        # Missing folder/snippet/device
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

### Action Validation

For rules and threat exceptions, exactly one action type must be specified:

```python
from scm.models.security_services import RuleRequest, ActionRequest

# This will raise a validation error
try:
    action = ActionRequest(root={
        "alert": {},
        "drop": {}  # Can't specify multiple actions
    })
    rule = RuleRequest(
        name="invalid-rule",
        severity=["critical"],
        category="spyware",
        action=action
    )
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."

# This is the correct way to specify an action
action = ActionRequest(root={"alert": {}})
rule = RuleRequest(
    name="valid-rule",
    severity=["critical"],
    category="spyware",
    action=action
)
```

### Severity Validation

Rule severity must be one of the allowed values:

```python
from scm.models.security_services import RuleRequest, ActionRequest, AntiSpywareSeverity

# This will raise a validation error
try:
    rule = RuleRequest(
        name="invalid-rule",
        severity=["invalid"],  # Must be critical, high, medium, low, or informational
        category="spyware",
        action=ActionRequest(root={"alert": {}})
    )
except ValueError as e:
    print(e)  # "Invalid severity level: 'invalid'"

# This is the correct way to specify severity levels
rule = RuleRequest(
    name="valid-rule",
    severity=[AntiSpywareSeverity.critical, AntiSpywareSeverity.high],
    category="spyware",
    action=ActionRequest(root={"alert": {}})
)
```

## Usage Examples

### Creating a Basic Profile

```python
from scm.client import ScmClient
from scm.models.security_services import (
    AntiSpywareProfileCreateModel,
    RuleRequest,
    ActionRequest,
    AntiSpywareSeverity,
    AntiSpywareCategory
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
basic_dict = {
    "name": "basic-profile",
    "description": "Basic anti-spyware profile",
    "folder": "Security Profiles",
    "rules": [{
        "name": "basic-rule",
        "severity": ["critical", "high"],
        "category": "spyware",
        "action": {"alert": {}}
    }]
}

# Create the profile using the client
response = client.anti_spyware_profile.create(basic_dict)
print(f"Created profile: {response.name}")

# Using model directly
basic_profile = AntiSpywareProfileCreateModel(
    name="basic-profile-2",
    description="Another basic anti-spyware profile",
    folder="Security Profiles",
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
response = client.anti_spyware_profile.create(payload)
print(f"Created profile with ID: {response.id}")
```

### Creating a Profile with Multiple Rules

```python
from scm.models.security_services import (
    AntiSpywareProfileCreateModel,
    RuleRequest,
    ActionRequest,
    AntiSpywareSeverity,
    AntiSpywareCategory,
    AntiSpywarePacketCapture
)

# Create rules
rules = [
    RuleRequest(
        name="critical-spyware",
        severity=[AntiSpywareSeverity.critical],
        category=AntiSpywareCategory.spyware,
        action=ActionRequest(root={
            "block_ip": {
                "track_by": "source",
                "duration": 300
            }
        }),
        packet_capture=AntiSpywarePacketCapture.single_packet
    ),
    RuleRequest(
        name="high-dns-security",
        severity=[AntiSpywareSeverity.high],
        category=AntiSpywareCategory.dns_security,
        action=ActionRequest(root={"drop": {}})
    ),
    RuleRequest(
        name="medium-c2",
        severity=[AntiSpywareSeverity.medium],
        category=AntiSpywareCategory.command_and_control,
        action=ActionRequest(root={"alert": {}})
    )
]

# Create the profile with multiple rules
multi_rule_profile = AntiSpywareProfileCreateModel(
    name="comprehensive-profile",
    description="Profile with multiple rules for different threats",
    folder="Security Profiles",
    cloud_inline_analysis=True,
    rules=rules
)

payload = multi_rule_profile.model_dump(exclude_unset=True)
response = client.anti_spyware_profile.create(payload)
print(f"Created profile with {len(response.rules)} rules")
```

### Creating a Profile with Threat Exceptions

```python
from scm.models.security_services import (
    AntiSpywareProfileCreateModel,
    RuleRequest,
    ThreatExceptionRequest,
    ActionRequest,
    AntiSpywareExemptIpEntry,
    AntiSpywarePacketCapture
)

# Create profile with threat exceptions
advanced_profile = AntiSpywareProfileCreateModel(
    name="advanced-profile",
    folder="Security Profiles",
    cloud_inline_analysis=True,
    rules=[
        RuleRequest(
            name="strict-rule",
            severity=["critical"],
            category="spyware",
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
            name="trusted-source",
            packet_capture=AntiSpywarePacketCapture.single_packet,
            action=ActionRequest(root={"allow": {}}),
            exempt_ip=[
                AntiSpywareExemptIpEntry(name="10.0.0.1"),
                AntiSpywareExemptIpEntry(name="10.0.0.2")
            ]
        )
    ],
    inline_exception_ip_address=["192.168.1.10", "192.168.1.11"]
)

payload = advanced_profile.model_dump(exclude_unset=True)
response = client.anti_spyware_profile.create(payload)
print(f"Created profile with {len(response.threat_exception)} exceptions")
```

### Updating a Profile

```python
from scm.models.security_services import AntiSpywareProfileUpdateModel

# Fetch existing profile
existing_profile = client.anti_spyware_profile.get("123e4567-e89b-12d3-a456-426655440000")

# Update profile by adding a new rule
existing_rules = existing_profile.rules
existing_rules.append(
    RuleRequest(
        name="new-rule",
        severity=["informational"],
        category="dns-security",
        action=ActionRequest(root={"alert": {}})
    )
)

# Create update model
update_profile = AntiSpywareProfileUpdateModel(
    id=existing_profile.id,
    name=existing_profile.name,
    description="Updated profile description",
    rules=existing_rules,
    cloud_inline_analysis=True  # Enable cloud analysis
)

# Perform update
payload = update_profile.model_dump(exclude_unset=True)
response = client.anti_spyware_profile.update(payload)
print(f"Updated profile with {len(response.rules)} rules")
```

### Listing and Filtering Profiles

```python
# List all anti-spyware profiles in a folder
all_profiles = client.anti_spyware_profile.list(folder="Security Profiles")
print(f"Found {len(all_profiles)} profiles")

# Process results
for profile in all_profiles:
    print(f"Profile: {profile.name}")
    print(f"Rules: {len(profile.rules)}")

    # Count rules by severity
    severity_counts = {}
    for rule in profile.rules:
        for severity in rule.severity:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

    print(f"Severity distribution: {severity_counts}")

    # Check for cloud inline analysis
    if profile.cloud_inline_analysis:
        print("Cloud inline analysis: Enabled")
    else:
        print("Cloud inline analysis: Disabled")
```
