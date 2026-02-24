# App Override Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The App Override Rule models provide a structured way to manage app override rules in Palo Alto Networks' Strata Cloud Manager.
These models support defining application override policies with source/destination zones, addresses, ports, and protocols.
Rules can be defined in folders, snippets, or devices and placed in either pre or post rulebases. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `AppOverrideRuleBaseModel`: Base model with fields common to all rule operations
- `AppOverrideRuleCreateModel`: Model for creating new app override rules
- `AppOverrideRuleUpdateModel`: Model for updating existing app override rules
- `AppOverrideRuleResponseModel`: Response model for app override rule operations
- `AppOverrideRuleMoveModel`: Model for moving rules within a rulebase

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### AppOverrideRuleBaseModel

| Attribute            | Type                       | Required | Default         | Description                                                 |
|----------------------|----------------------------|----------|-----------------|-------------------------------------------------------------|
| name                 | str                        | Yes      | None            | Name of the rule. Pattern: `^[a-zA-Z0-9._-]+$`. Max 63 chars |
| application          | str                        | Yes      | None            | Application to override                                     |
| port                 | str                        | Yes      | None            | Port(s) for the rule                                        |
| protocol             | AppOverrideRuleProtocol    | Yes      | None            | Protocol (tcp/udp)                                          |
| disabled             | bool                       | No       | False           | Whether the rule is disabled                                |
| description          | str                        | No       | None            | Description of the rule. Max 1024 chars                     |
| tag                  | List[str]                  | No       | None            | List of tags                                                |
| from_                | List[str]                  | No       | ["any"]         | Source security zones (alias: `from`)                       |
| to_                  | List[str]                  | No       | ["any"]         | Destination security zones (alias: `to`)                    |
| source               | List[str]                  | No       | ["any"]         | Source addresses                                            |
| destination          | List[str]                  | No       | ["any"]         | Destination addresses                                       |
| negate_source        | bool                       | No       | False           | Negate source addresses                                     |
| negate_destination   | bool                       | No       | False           | Negate destination addresses                                |
| group_tag            | str                        | No       | None            | Group tag for the rule                                      |
| folder               | str                        | No**     | None            | Folder location. Max 64 chars                               |
| snippet              | str                        | No**     | None            | Snippet location. Max 64 chars                              |
| device               | str                        | No**     | None            | Device location. Max 64 chars                               |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### AppOverrideRuleCreateModel

Inherits all fields from `AppOverrideRuleBaseModel` and adds:

| Attribute | Type                      | Required | Default | Description                      |
|-----------|---------------------------|----------|---------|----------------------------------|
| rulebase  | AppOverrideRuleRulebase   | No       | None    | Which rulebase to use (pre/post) |

Enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### AppOverrideRuleUpdateModel

Extends `AppOverrideRuleBaseModel` by adding:

| Attribute | Type                      | Required | Default | Description                       |
|-----------|---------------------------|----------|---------|-----------------------------------|
| id        | UUID                      | Yes      | None    | The unique identifier of the rule |
| rulebase  | AppOverrideRuleRulebase   | No       | None    | Which rulebase to use (pre/post)  |

### AppOverrideRuleResponseModel

Extends `AppOverrideRuleBaseModel` by adding:

| Attribute   | Type                      | Required | Default | Description                         |
|-------------|---------------------------|----------|---------|-------------------------------------|
| id          | UUID                      | Yes      | None    | The unique identifier of the rule   |
| rulebase    | AppOverrideRuleRulebase   | No       | None    | Which rulebase the rule belongs to  |
| application | str                       | No       | None    | Application (optional in response)  |
| port        | str                       | No       | None    | Port (optional in response)         |
| protocol    | AppOverrideRuleProtocol   | No       | None    | Protocol (optional in response)     |

The response model uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept additional
fields returned by the API without raising validation errors. The `device` field in the response model also accepts
an empty dictionary in addition to `None` or a string value. The `application`, `port`, and `protocol` fields are
optional in the response model as the API may omit them for system or default rules.

### AppOverrideRuleMoveModel

| Attribute        | Type                           | Required | Default | Description                                    |
|------------------|--------------------------------|----------|---------|------------------------------------------------|
| destination      | AppOverrideRuleMoveDestination | Yes      | None    | Where to move (top/bottom/before/after)        |
| rulebase         | AppOverrideRuleRulebase        | Yes      | None    | Which rulebase to use (pre/post)               |
| destination_rule | UUID                           | No       | None    | UUID of reference rule (for before/after moves) |

## Enum Types

### AppOverrideRuleProtocol

Defines the available protocols:

| Value | Description          |
|-------|----------------------|
| `tcp` | TCP protocol         |
| `udp` | UDP protocol         |

### AppOverrideRuleRulebase

Defines the available rulebases:

| Value  | Description      |
|--------|------------------|
| `pre`  | Pre-rulebase     |
| `post` | Post-rulebase    |

### AppOverrideRuleMoveDestination

Defines the move destinations:

| Value    | Description                      |
|----------|----------------------------------|
| `top`    | Move to top of rulebase          |
| `bottom` | Move to bottom of rulebase       |
| `before` | Move before a specific rule      |
| `after`  | Move after a specific rule       |

## Exceptions

The App Override Rule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When list field values are not unique
    - When list field values are not strings
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded
    - When invalid move configurations are provided (e.g. missing destination_rule for before/after moves)
    - When destination_rule is provided for top/bottom moves

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import AppOverrideRuleCreateModel

# Error: multiple containers specified
try:
    rule = AppOverrideRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        application="custom-app",
        port="8080",
        protocol="tcp"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    rule = AppOverrideRuleCreateModel(
        name="invalid-rule",
        application="custom-app",
        port="8080",
        protocol="tcp"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### List Field Validation

All list fields are validated to ensure they contain only unique string values:

```python
from scm.models.security import AppOverrideRuleCreateModel

# Error: duplicate values
try:
    rule = AppOverrideRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        application="custom-app",
        port="8080",
        protocol="tcp",
        source=["10.0.0.0/8", "10.0.0.0/8"]  # Duplicate values not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"
```

### Move Configuration Validation

The AppOverrideRuleMoveModel validates that destination_rule is provided only for before/after moves:

```python
from scm.models.security.app_override_rules import AppOverrideRuleMoveModel

# Error: missing destination_rule for 'before' move
try:
    move = AppOverrideRuleMoveModel(
        destination="before",
        rulebase="pre"
        # destination_rule is required for before/after
    )
except ValueError as e:
    print(e)  # "destination_rule is required when destination is 'before'"

# Error: destination_rule provided for 'top' move
try:
    move = AppOverrideRuleMoveModel(
        destination="top",
        rulebase="pre",
        destination_rule="987fcdeb-51d3-a456-426655440000"  # Not allowed for top/bottom
    )
except ValueError as e:
    print(e)  # "destination_rule should not be provided when destination is 'top'"
```

## Usage Examples

### Creating a Basic App Override Rule

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
    "name": "override-custom-app",
    "description": "Override traffic identification for custom application",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "port": "8080",
    "protocol": "tcp",
    "application": "custom-app"
}

response = client.app_override_rule.create(rule_dict, rulebase="pre")
print(f"Created rule: {response.name}")
```

### Creating a Rule with Multiple Ports and Tags

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
    "name": "override-multi-port",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["server-farm"],
    "port": "8080,8443,9090",
    "protocol": "tcp",
    "application": "custom-web-app",
    "tag": ["Override", "Production"],
    "description": "Multi-port app override for custom web application"
}

response = client.app_override_rule.create(rule_dict, rulebase="pre")
print(f"Created rule: {response.name}")
print(f"Port: {response.port}")
```

### Creating a UDP Rule

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
    "name": "override-voip",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["any"],
    "destination": ["voip-servers"],
    "port": "5060-5061",
    "protocol": "udp",
    "application": "sip",
    "description": "Override SIP traffic identification"
}

response = client.app_override_rule.create(rule_dict, rulebase="pre")
print(f"Created UDP rule: {response.name}")
```

### Updating an App Override Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing rule
existing = client.app_override_rule.fetch(name="override-custom-app", folder="Texas", rulebase="pre")

# Modify attributes using dot notation
existing.description = "Updated app override rule"
existing.source = ["10.0.0.0/8", "172.16.0.0/12"]

# Update port range
existing.port = "8080,8443"

# Pass modified object to update()
updated = client.app_override_rule.update(existing, rulebase="pre")
print(f"Updated rule: {updated.name}")
```

### Moving an App Override Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch the rule to move
rule = client.app_override_rule.fetch(name="override-custom-app", folder="Texas", rulebase="pre")

# Move to top of rulebase
move_config = {
    "destination": "top",
    "rulebase": "pre"
}
client.app_override_rule.move(rule.id, move_config)

# Move before another rule
move_before = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
client.app_override_rule.move(rule.id, move_before)
```
