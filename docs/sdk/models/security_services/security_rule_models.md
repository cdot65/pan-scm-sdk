# Security Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Security Rule models provide a structured way to manage security rules in Palo Alto Networks' Strata Cloud Manager.
These models support defining security policies with source/destination zones, addresses, applications, and actions.
Rules can be defined in folders, snippets, or devices and placed in either pre or post rulebases. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `SecurityRuleBaseModel`: Base model with fields common to all rule operations
- `SecurityRuleCreateModel`: Model for creating new security rules
- `SecurityRuleUpdateModel`: Model for updating existing security rules
- `SecurityRuleResponseModel`: Response model for security rule operations
- `SecurityRuleMoveModel`: Model for moving rules within a rulebase
- `SecurityRuleProfileSetting`: Model for security profile settings

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### SecurityRuleBaseModel

| Attribute            | Type                       | Required | Default         | Description                                    |
|----------------------|----------------------------|----------|-----------------|------------------------------------------------|
| name                 | str                        | Yes      | None            | Name of the rule. Pattern: `^[a-zA-Z0-9_ \.-]+$` |
| disabled             | bool                       | No       | False           | Whether the rule is disabled                   |
| description          | str                        | No       | None            | Description of the rule                        |
| tag                  | List[str]                  | No       | []              | List of tags                                   |
| from_                | List[str]                  | No       | ["any"]         | Source security zones                          |
| source               | List[str]                  | No       | ["any"]         | Source addresses                               |
| negate_source        | bool                       | No       | False           | Negate source addresses                        |
| source_user          | List[str]                  | No       | ["any"]         | Source users/groups                            |
| source_hip           | List[str]                  | No       | ["any"]         | Source Host Integrity Profiles                 |
| to_                  | List[str]                  | No       | ["any"]         | Destination security zones                     |
| destination          | List[str]                  | No       | ["any"]         | Destination addresses                          |
| negate_destination   | bool                       | No       | False           | Negate destination addresses                   |
| destination_hip      | List[str]                  | No       | ["any"]         | Destination Host Integrity Profiles            |
| application          | List[str]                  | No       | ["any"]         | Applications                                   |
| service              | List[str]                  | No       | ["any"]         | Services                                       |
| category             | List[str]                  | No       | ["any"]         | URL categories                                 |
| action               | SecurityRuleAction         | No       | allow           | Rule action                                    |
| profile_setting      | SecurityRuleProfileSetting | No       | None            | Security profile settings                      |
| log_setting          | str                        | No       | None            | Log forwarding profile                         |
| schedule             | str                        | No       | None            | Schedule profile                               |
| log_start            | bool                       | No       | None            | Log at session start                           |
| log_end              | bool                       | No       | None            | Log at session end                             |
| folder               | str                        | No**     | None            | Folder location. Max 64 chars                  |
| snippet              | str                        | No**     | None            | Snippet location. Max 64 chars                 |
| device               | str                        | No**     | None            | Device location. Max 64 chars                  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### SecurityRuleCreateModel

Inherits all fields from `SecurityRuleBaseModel` and adds:

| Attribute | Type                 | Required | Default | Description                   |
|-----------|----------------------|----------|---------|-------------------------------|
| rulebase  | SecurityRuleRulebase | No       | None    | Which rulebase to use (pre/post) |

Enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### SecurityRuleUpdateModel

Extends `SecurityRuleBaseModel` by adding:

| Attribute | Type                 | Required | Default | Description                      |
|-----------|----------------------|----------|---------|----------------------------------|
| id        | UUID                 | Yes      | None    | The unique identifier of the rule |
| rulebase  | SecurityRuleRulebase | No       | None    | Which rulebase to use (pre/post)  |

### SecurityRuleResponseModel

Extends `SecurityRuleBaseModel` by adding:

| Attribute   | Type                 | Required | Default | Description                       |
|-------------|----------------------|----------|---------|-----------------------------------|
| id          | UUID                 | Yes      | None    | The unique identifier of the rule |
| rulebase    | SecurityRuleRulebase | No       | None    | Which rulebase the rule belongs to |
| policy_type | str                  | No       | None    | The policy type (e.g., 'Security') |

### SecurityRuleMoveModel

| Attribute        | Type                        | Required | Default | Description                                    |
|------------------|-----------------------------| ---------|---------|------------------------------------------------|
| destination      | SecurityRuleMoveDestination | Yes      | None    | Where to move (top/bottom/before/after)        |
| rulebase         | SecurityRuleRulebase        | Yes      | None    | Which rulebase to use (pre/post)               |
| destination_rule | UUID                        | No       | None    | UUID of reference rule (for before/after moves) |

## Enum Types

### SecurityRuleAction

Defines the available rule actions:

| Value          | Description             |
|----------------|-------------------------|
| `allow`        | Allow the traffic       |
| `deny`         | Deny the traffic        |
| `drop`         | Drop the traffic        |
| `reset-client` | Reset client connection |
| `reset-server` | Reset server connection |
| `reset-both`   | Reset both connections  |

### SecurityRuleRulebase

Defines the available rulebases:

| Value  | Description      |
|--------|------------------|
| `pre`  | Pre-rulebase     |
| `post` | Post-rulebase    |

### SecurityRuleMoveDestination

Defines the move destinations:

| Value    | Description                      |
|----------|----------------------------------|
| `top`    | Move to top of rulebase          |
| `bottom` | Move to bottom of rulebase       |
| `before` | Move before a specific rule      |
| `after`  | Move after a specific rule       |

## Supporting Models

### SecurityRuleProfileSetting

| Attribute | Type       | Required | Default           | Description              |
|-----------|------------|----------|-------------------|--------------------------|
| group     | List[str]  | No       | ["best-practice"] | Security profile group   |

## Exceptions

The Security Rule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When list field values are not unique
    - When list field values are not strings
    - When invalid action types are provided
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded
    - When invalid move configurations are provided (e.g. missing destination_rule for before/after moves)
    - When destination_rule is provided for top/bottom moves

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import SecurityRuleCreateModel

# Error: multiple containers specified
try:
    rule = SecurityRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        action="allow"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    rule = SecurityRuleCreateModel(
        name="invalid-rule",
        action="allow"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### List Field Validation

All list fields are validated to ensure they contain only unique string values:

```python
from scm.models.security import SecurityRuleCreateModel

# Error: duplicate values
try:
    rule = SecurityRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source=["10.0.0.0/8", "10.0.0.0/8"]  # Duplicate values not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"
```

### Move Configuration Validation

The SecurityRuleMoveModel validates that destination_rule is provided only for before/after moves:

```python
from scm.models.security import SecurityRuleMoveModel

# Error: missing destination_rule for 'before' move
try:
    move = SecurityRuleMoveModel(
        destination="before",
        rulebase="pre"
        # destination_rule is required for before/after
    )
except ValueError as e:
    print(e)  # "destination_rule is required when destination is 'before'"

# Error: destination_rule provided for 'top' move
try:
    move = SecurityRuleMoveModel(
        destination="top",
        rulebase="pre",
        destination_rule="987fcdeb-51d3-a456-426655440000"  # Not allowed for top/bottom
    )
except ValueError as e:
    print(e)  # "destination_rule should not be provided when destination is 'top'"
```

## Usage Examples

### Creating a Basic Security Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
rule_dict = {
    "name": "allow-web",
    "description": "Allow web traffic",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "service": ["application-default"],
    "action": "allow",
    "log_end": True
}

response = client.security_rule.create(rule_dict, rulebase="pre")
print(f"Created rule: {response.name}")
```

### Creating a Rule with Security Profiles

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
rule_dict = {
    "name": "secure-web",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "action": "allow",
    "profile_setting": {
        "group": ["strict-security"]
    },
    "log_setting": "detailed-logging",
    "log_start": True,
    "log_end": True
}

response = client.security_rule.create(rule_dict, rulebase="pre")
print(f"Created rule with profile: {response.name}")
```

### Updating a Security Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing rule
existing = client.security_rule.fetch(name="allow-web", folder="Texas", rulebase="pre")

# Modify attributes using dot notation
existing.description = "Updated web access rule"
existing.application = ["web-browsing", "ssl", "http2"]

# Update profile setting
existing.profile_setting = {"group": ["strict-security"]}

# Enable logging
existing.log_start = True
existing.log_end = True

# Pass modified object to update()
updated = client.security_rule.update(existing, rulebase="pre")
print(f"Updated rule: {updated.name}")
```

### Moving a Security Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch the rule to move
rule = client.security_rule.fetch(name="allow-web", folder="Texas", rulebase="pre")

# Move to top of rulebase
move_config = {
    "destination": "top",
    "rulebase": "pre"
}
client.security_rule.move(rule.id, move_config)

# Move before another rule
move_before = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
client.security_rule.move(rule.id, move_before)
```
