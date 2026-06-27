# Authentication Rule Models

## Overview

The Authentication Rule models provide a structured way to manage authentication rules in Palo Alto Networks' Strata
Cloud Manager. These models support defining identity-based policies with source/destination zones, addresses, users,
and authentication enforcement profiles. Rules can be defined in folders, snippets, or devices and placed in either pre
or post rulebases. The models handle validation of inputs and outputs when interacting with the SCM API.

## Models

The module provides the following Pydantic models:

- `AuthenticationRuleBaseModel`: Base model with fields common to all rule operations
- `AuthenticationRuleCreateModel`: Model for creating new authentication rules
- `AuthenticationRuleUpdateModel`: Model for updating existing authentication rules
- `AuthenticationRuleResponseModel`: Response model for authentication rule operations
- `AuthenticationRuleMoveModel`: Model for moving rules within a rulebase

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### AuthenticationRuleBaseModel

| Attribute                    | Type           | Required | Default         | Description                                       |
|------------------------------|----------------|----------|-----------------|---------------------------------------------------|
| name                         | str            | Yes      | None            | Name of the rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`  |
| disabled                     | bool           | No       | False           | Whether the rule is disabled                      |
| description                  | str            | No       | None            | Description of the rule                           |
| tag                          | List[str]      | No       | []              | List of tags                                      |
| from_                        | List[str]      | No       | ["any"]         | Source security zones                             |
| source                       | List[str]      | No       | ["any"]         | Source addresses                                  |
| negate_source                | bool           | No       | False           | Negate source addresses                           |
| source_user                  | List[str]      | No       | ["any"]         | Source users/groups                               |
| source_hip                   | List[str]      | No       | ["any"]         | Source Host Integrity Profiles                    |
| to_                          | List[str]      | No       | ["any"]         | Destination security zones                        |
| destination                  | List[str]      | No       | ["any"]         | Destination addresses                             |
| negate_destination           | bool           | No       | False           | Negate destination addresses                      |
| destination_hip              | List[str]      | No       | ["any"]         | Destination Host Integrity Profiles               |
| service                      | List[str]      | No       | ["any"]         | Services                                          |
| category                     | List[str]      | No       | ["any"]         | URL categories                                    |
| authentication_enforcement   | str            | No       | None            | Authentication profile name                       |
| hip_profiles                 | List[str]      | No       | None            | Source Host Integrity Profiles                    |
| group_tag                    | str            | No       | None            | Group tag                                         |
| timeout                      | int            | No       | None            | Auth session timeout in minutes (1-1440)          |
| log_setting                  | str            | No       | None            | Log forwarding profile                            |
| log_authentication_timeout   | bool           | No       | False           | Log authentication timeouts                       |
| folder                       | str            | No**     | None            | Folder location. Max 64 chars                     |
| snippet                      | str            | No**     | None            | Snippet location. Max 64 chars                    |
| device                       | str            | No**     | None            | Device location. Max 64 chars                     |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### AuthenticationRuleCreateModel

Inherits all fields from `AuthenticationRuleBaseModel` and adds:

| Attribute | Type                         | Required | Default | Description                      |
|-----------|------------------------------|----------|---------|----------------------------------|
| rulebase  | AuthenticationRuleRulebase   | No       | None    | Which rulebase to use (pre/post) |

Enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### AuthenticationRuleUpdateModel

Extends `AuthenticationRuleBaseModel` by adding:

| Attribute | Type                         | Required | Default | Description                       |
|-----------|------------------------------|----------|---------|-----------------------------------|
| id        | UUID                         | Yes      | None    | The unique identifier of the rule |
| rulebase  | AuthenticationRuleRulebase   | No       | None    | Which rulebase to use (pre/post)  |

### AuthenticationRuleResponseModel

Extends `AuthenticationRuleBaseModel` by adding:

| Attribute | Type                         | Required | Default | Description                        |
|-----------|------------------------------|---------|---------|------------------------------------|
| id        | UUID                         | Yes      | None    | The unique identifier of the rule  |
| rulebase  | AuthenticationRuleRulebase   | No       | None    | Which rulebase the rule belongs to |

Note: The response model uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept
additional fields from the API response without raising errors. The `device` field in the response model also accepts
an empty dictionary in addition to a string or None.

### AuthenticationRuleMoveModel

| Attribute        | Type                                | Required | Default | Description                                    |
|------------------|-------------------------------------| ---------|---------|------------------------------------------------|
| destination      | AuthenticationRuleMoveDestination   | Yes      | None    | Where to move (top/bottom/before/after)        |
| rulebase         | AuthenticationRuleRulebase          | Yes      | None    | Which rulebase to use (pre/post)               |
| destination_rule | UUID                                | No       | None    | UUID of reference rule (for before/after moves) |

## Enum Types

### AuthenticationRuleRulebase

Defines the available rulebases:

| Value  | Description      |
|--------|------------------|
| `pre`  | Pre-rulebase     |
| `post` | Post-rulebase    |

### AuthenticationRuleMoveDestination

Defines the move destinations:

| Value    | Description                      |
|----------|----------------------------------|
| `top`    | Move to top of rulebase          |
| `bottom` | Move to bottom of rulebase       |
| `before` | Move before a specific rule      |
| `after`  | Move after a specific rule       |

## Exceptions

The Authentication Rule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When list field values are not unique
    - When list field values are not strings
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded
    - When `timeout` is outside the range 1-1440
    - When invalid move configurations are provided (e.g. missing destination_rule for before/after moves)
    - When destination_rule is provided for top/bottom moves

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import AuthenticationRuleCreateModel

# Error: multiple containers specified
try:
    rule = AuthenticationRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    rule = AuthenticationRuleCreateModel(
        name="invalid-rule",
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### List Field Validation

All list fields are validated to ensure they contain only unique string values:

```python
from scm.models.security import AuthenticationRuleCreateModel

# Error: duplicate values
try:
    rule = AuthenticationRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source=["10.0.0.0/8", "10.0.0.0/8"]  # Duplicate values not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"
```

### Timeout Validation

The `timeout` field validates that values fall within the range of 1 to 1440 minutes:

```python
from scm.models.security import AuthenticationRuleCreateModel

# Error: timeout too low
try:
    rule = AuthenticationRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        timeout=0  # Must be >= 1
    )
except ValueError as e:
    print(e)  # Validation error for timeout

# Error: timeout too high
try:
    rule = AuthenticationRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        timeout=1441  # Must be <= 1440
    )
except ValueError as e:
    print(e)  # Validation error for timeout
```

### Move Configuration Validation

The AuthenticationRuleMoveModel validates that destination_rule is provided only for before/after moves:

```python
from scm.models.security import AuthenticationRuleMoveModel

# Error: missing destination_rule for 'before' move
try:
    move = AuthenticationRuleMoveModel(
        destination="before",
        rulebase="pre"
        # destination_rule is required for before/after
    )
except ValueError as e:
    print(e)  # "destination_rule is required when destination is 'before'"

# Error: destination_rule provided for 'top' move
try:
    move = AuthenticationRuleMoveModel(
        destination="top",
        rulebase="pre",
        destination_rule="987fcdeb-51d3-a456-426655440000"  # Not allowed for top/bottom
    )
except ValueError as e:
    print(e)  # "destination_rule should not be provided when destination is 'top'"
```

## Usage Examples

### Creating a Basic Authentication Rule

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
rule_dict = {
    "name": "auth-web-traffic",
    "description": "Authenticate web traffic",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "service": ["service-http", "service-https"],
    "authentication_enforcement": "auth-profile-1",
    "log_authentication_timeout": True
}

response = client.authentication_rule.create(rule_dict, rulebase="pre")
print(f"Created rule: {response.name}")
```

### Creating a Rule with Timeout and HIP Profiles

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
rule_dict = {
    "name": "auth-compliant-devices",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "service": ["any"],
    "authentication_enforcement": "strict-auth-profile",
    "hip_profiles": ["hip-compliant", "hip-patched"],
    "timeout": 120,
    "group_tag": "compliance-group",
    "log_setting": "detailed-logging",
    "log_authentication_timeout": True,
    "tag": ["Compliance"]
}

response = client.authentication_rule.create(rule_dict, rulebase="pre")
print(f"Created rule with HIP profiles: {response.name}")
```

### Updating an Authentication Rule

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing rule
existing = client.authentication_rule.fetch(name="auth-web-traffic", folder="Texas", rulebase="pre")

# Modify attributes using dot notation
existing.description = "Updated authentication rule"
existing.timeout = 60
existing.authentication_enforcement = "updated-auth-profile"

# Enable authentication timeout logging
existing.log_authentication_timeout = True

# Pass modified object to update()
updated = client.authentication_rule.update(existing, rulebase="pre")
print(f"Updated rule: {updated.name}")
```

### Moving an Authentication Rule

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch the rule to move
rule = client.authentication_rule.fetch(name="auth-web-traffic", folder="Texas", rulebase="pre")

# Move to top of rulebase
move_config = {
    "destination": "top",
    "rulebase": "pre"
}
client.authentication_rule.move(rule.id, move_config)

# Move before another rule
move_before = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
client.authentication_rule.move(rule.id, move_before)
```
