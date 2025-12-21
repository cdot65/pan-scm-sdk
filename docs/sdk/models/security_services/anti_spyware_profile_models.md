# Anti-Spyware Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Anti-Spyware Profile models provide a structured way to manage anti-spyware security profiles in Palo Alto Networks' Strata Cloud Manager. These models support configuring rules, threat exceptions, and MICA engine settings to detect and prevent spyware threats. Profiles can be defined in folders, snippets, or devices. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `AntiSpywareProfileBase`: Base model with fields common to all profile operations
- `AntiSpywareProfileCreateModel`: Model for creating new anti-spyware profiles
- `AntiSpywareProfileUpdateModel`: Model for updating existing anti-spyware profiles
- `AntiSpywareProfileResponseModel`: Response model for anti-spyware profile operations
- `AntiSpywareRuleBaseModel`: Model for anti-spyware rules
- `AntiSpywareThreatExceptionBase`: Model for threat exceptions
- `AntiSpywareMicaEngineSpywareEnabledEntry`: Model for MICA engine entries
- `AntiSpywareBlockIpAction`: Model for block IP action configuration
- `AntiSpywareExemptIpEntry`: Model for exempt IP entries
- `AntiSpywareActionRequest`: Model for action configuration in requests
- `AntiSpywareActionResponse`: Model for action configuration in responses

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### AntiSpywareProfileBase

| Attribute                   | Type                                            | Required | Default | Description                                            |
|-----------------------------|-------------------------------------------------|----------|---------|--------------------------------------------------------|
| name                        | str                                             | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9][a-zA-Z0-9_\-. ]*$` |
| description                 | str                                             | No       | None    | Description of the profile                             |
| cloud_inline_analysis       | bool                                            | No       | False   | Enable/disable cloud inline analysis                   |
| inline_exception_edl_url    | List[str]                                       | No       | None    | List of inline exception EDL URLs                      |
| inline_exception_ip_address | List[str]                                       | No       | None    | List of inline exception IP addresses                  |
| mica_engine_spyware_enabled | List[AntiSpywareMicaEngineSpywareEnabledEntry]  | No       | None    | List of MICA engine spyware enabled entries            |
| rules                       | List[AntiSpywareRuleBaseModel]                  | No       | None    | List of anti-spyware rules                             |
| threat_exception            | List[AntiSpywareThreatExceptionBase]            | No       | None    | List of threat exceptions                              |
| folder                      | str                                             | No**     | None    | Folder location. Max 64 chars                          |
| snippet                     | str                                             | No**     | None    | Snippet location. Max 64 chars                         |
| device                      | str                                             | No**     | None    | Device location. Max 64 chars                          |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### AntiSpywareProfileCreateModel

Inherits all fields from `AntiSpywareProfileBase` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### AntiSpywareProfileUpdateModel

Extends `AntiSpywareProfileBase` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### AntiSpywareProfileResponseModel

Extends `AntiSpywareProfileBase` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

## Enum Types

### AntiSpywareInlinePolicyAction

Defines the inline policy actions for MICA engine entries:

| Value          | Description                        |
|----------------|------------------------------------|
| `alert`        | Alert on detection                 |
| `allow`        | Allow the traffic                  |
| `drop`         | Drop the traffic                   |
| `reset-both`   | Reset both client and server       |
| `reset-client` | Reset the client connection        |
| `reset-server` | Reset the server connection        |

### AntiSpywarePacketCapture

Defines the packet capture options:

| Value              | Description                    |
|--------------------|--------------------------------|
| `disable`          | Disable packet capture         |
| `single-packet`    | Capture a single packet        |
| `extended-capture` | Extended packet capture        |

### AntiSpywareSeverity

Defines the severity levels for rules:

| Value           | Description                    |
|-----------------|--------------------------------|
| `critical`      | Critical severity              |
| `high`          | High severity                  |
| `medium`        | Medium severity                |
| `low`           | Low severity                   |
| `informational` | Informational severity         |
| `any`           | Any severity level             |

### AntiSpywareCategory

Defines the threat categories (partial list):

| Value                 | Description                           |
|-----------------------|---------------------------------------|
| `spyware`             | Spyware threats                       |
| `command-and-control` | Command and control traffic           |
| `dns-security`        | DNS security threats                  |
| `backdoor`            | Backdoor threats                      |
| `botnet`              | Botnet traffic                        |
| `cryptominer`         | Cryptominer activity                  |
| `data-theft`          | Data theft attempts                   |
| `downloader`          | Malware downloaders                   |
| `keylogger`           | Keylogger activity                    |
| `phishing-kit`        | Phishing kit detection                |
| `webshell`            | Webshell detection                    |
| `any`                 | Any category                          |

See the source code for the complete list of category values.

## Supporting Models

### AntiSpywareRuleBaseModel

| Attribute      | Type                         | Required | Default | Description                                                    |
|----------------|------------------------------|----------|---------|----------------------------------------------------------------|
| name           | str                          | Yes      | None    | Name of the rule                                               |
| severity       | List[AntiSpywareSeverity]    | Yes      | None    | Severity levels for the rule                                   |
| category       | AntiSpywareCategory          | Yes      | None    | Category for the rule                                          |
| action         | AntiSpywareActionResponse    | No       | None    | Action to take when rule matches                               |
| packet_capture | AntiSpywarePacketCapture     | No       | None    | Packet capture setting                                         |
| threat_name    | str                          | No       | "any"   | Specific threat name to match. Min 3 chars                     |

### AntiSpywareThreatExceptionBase

| Attribute      | Type                           | Required | Default | Description                                   |
|----------------|--------------------------------|----------|---------|-----------------------------------------------|
| name           | str                            | Yes      | None    | Name of the threat exception                  |
| packet_capture | AntiSpywarePacketCapture       | Yes      | None    | Packet capture setting for the exception      |
| action         | AntiSpywareActionResponse      | No       | None    | Action for the exception                      |
| exempt_ip      | List[AntiSpywareExemptIpEntry] | No       | None    | List of exempt IP addresses                   |
| notes          | str                            | No       | None    | Notes for the exception                       |

### AntiSpywareMicaEngineSpywareEnabledEntry

| Attribute            | Type                          | Required | Default | Description                          |
|----------------------|-------------------------------|----------|---------|--------------------------------------|
| name                 | str                           | Yes      | None    | Name of the MICA engine detector     |
| inline_policy_action | AntiSpywareInlinePolicyAction | No       | alert   | Inline policy action                 |

### AntiSpywareBlockIpAction

| Attribute | Type | Required | Default | Description                                              |
|-----------|------|----------|---------|----------------------------------------------------------|
| track_by  | str  | Yes      | None    | Tracking method. Pattern: `^(source-and-destination|source)$` |
| duration  | int  | Yes      | None    | Duration in seconds (1-3600)                             |

### AntiSpywareExemptIpEntry

| Attribute | Type | Required | Default | Description                |
|-----------|------|----------|---------|----------------------------|
| name      | str  | Yes      | None    | Exempt IP name             |

### AntiSpywareActionRequest / AntiSpywareActionResponse

The action configuration follows a discriminated union pattern where exactly one action type must be provided:

| Action Type    | Description                                      |
|----------------|--------------------------------------------------|
| `alert`        | Alert on detection                               |
| `allow`        | Allow the traffic                                |
| `drop`         | Drop the traffic                                 |
| `reset_client` | Reset client connection                          |
| `reset_server` | Reset server connection                          |
| `reset_both`   | Reset both connections                           |
| `block_ip`     | Block IP with track_by and duration settings     |
| `default`      | Use default action                               |

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
from scm.models.security import AntiSpywareProfileCreateModel

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
from scm.models.security import AntiSpywareRuleBaseModel, AntiSpywareActionRequest

# This will raise a validation error
try:
    action = AntiSpywareActionRequest(root={
        "alert": {},
        "drop": {}  # Can't specify multiple actions
    })
    rule = AntiSpywareRuleBaseModel(
        name="invalid-rule",
        severity=["critical"],
        category="spyware",
        action=action
    )
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."

# This is the correct way to specify an action
action = AntiSpywareActionRequest(root={"alert": {}})
rule = AntiSpywareRuleBaseModel(
    name="valid-rule",
    severity=["critical"],
    category="spyware",
    action=action
)
```

### Severity Validation

Rule severity must be one of the allowed values:

```python
from scm.models.security import (
    AntiSpywareRuleBaseModel,
    AntiSpywareActionRequest,
    AntiSpywareSeverity
)

# This will raise a validation error
try:
    rule = AntiSpywareRuleBaseModel(
        name="invalid-rule",
        severity=["invalid"],  # Must be critical, high, medium, low, or informational
        category="spyware",
        action=AntiSpywareActionRequest(root={"alert": {}})
    )
except ValueError as e:
    print(e)  # "Invalid severity level: 'invalid'"

# This is the correct way to specify severity levels
rule = AntiSpywareRuleBaseModel(
    name="valid-rule",
    severity=[AntiSpywareSeverity.critical, AntiSpywareSeverity.high],
    category="spyware",
    action=AntiSpywareActionRequest(root={"alert": {}})
)
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
    "name": "comprehensive-profile",
    "description": "Profile with multiple rules for different threats",
    "folder": "Security Profiles",
    "cloud_inline_analysis": True,
    "rules": [
        {
            "name": "critical-spyware",
            "severity": ["critical"],
            "category": "spyware",
            "action": {
                "block_ip": {
                    "track_by": "source",
                    "duration": 300
                }
            },
            "packet_capture": "single-packet"
        },
        {
            "name": "high-dns-security",
            "severity": ["high"],
            "category": "dns-security",
            "action": {"drop": {}}
        },
        {
            "name": "medium-c2",
            "severity": ["medium"],
            "category": "command-and-control",
            "action": {"alert": {}}
        }
    ]
}

response = client.anti_spyware_profile.create(multi_rule_config)
print(f"Created profile with {len(response.rules)} rules")
```

### Creating a Profile with Threat Exceptions

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create profile with threat exceptions using dictionary
advanced_config = {
    "name": "advanced-profile",
    "folder": "Security Profiles",
    "cloud_inline_analysis": True,
    "rules": [
        {
            "name": "strict-rule",
            "severity": ["critical"],
            "category": "spyware",
            "action": {
                "block_ip": {
                    "track_by": "source",
                    "duration": 300
                }
            }
        }
    ],
    "threat_exception": [
        {
            "name": "trusted-source",
            "packet_capture": "single-packet",
            "action": {"allow": {}},
            "exempt_ip": [
                {"name": "10.0.0.1"},
                {"name": "10.0.0.2"}
            ]
        }
    ],
    "inline_exception_ip_address": ["192.168.1.10", "192.168.1.11"]
}

response = client.anti_spyware_profile.create(advanced_config)
print(f"Created profile with {len(response.threat_exception)} exceptions")
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
existing = client.anti_spyware_profile.fetch(name="basic-profile", folder="Security Profiles")

# Modify attributes using dot notation
existing.description = "Updated profile description"
existing.cloud_inline_analysis = True

# Add a new rule to the existing rules
if existing.rules:
    existing.rules.append({
        "name": "new-rule",
        "severity": ["informational"],
        "category": "dns-security",
        "action": {"alert": {}}
    })

# Pass modified object to update()
updated = client.anti_spyware_profile.update(existing)
print(f"Updated profile: {updated.name}")
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
