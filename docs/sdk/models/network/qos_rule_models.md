# QoS Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enumerations](#enumerations)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The QoS Rule models provide a structured way to represent and validate QoS policy rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage QoS rule definitions that classify traffic and assign it to QoS classes, supporting DSCP/TOS markings, schedule-based policies, and rule positioning within the rulebase.

### Models

The module provides the following Pydantic models:

- `QosRuleBaseModel`: Base model with fields common to all QoS rule operations
- `QosRuleCreateModel`: Model for creating new QoS rules
- `QosRuleUpdateModel`: Model for updating existing QoS rules
- `QosRuleResponseModel`: Response model for QoS rule operations
- `QosRuleMoveModel`: Model for QoS rule move (reorder) operations

### Enumerations

The module also provides:

- `QosMoveDestination`: Enum for valid move destinations (`top`, `bottom`, `before`, `after`)
- `QosRulebase`: Enum for valid rulebase values (`pre`, `post`)

The `QosRuleBaseModel` and `QosRuleCreateModel` / `QosRuleUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `QosRuleResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### QosRuleBaseModel

This is the base model containing fields common to all QoS rule operations.

| Attribute     | Type              | Required | Default | Description                                                                 |
|---------------|-------------------|----------|---------|-----------------------------------------------------------------------------|
| name          | str               | Yes      | None    | QoS rule name.                                                              |
| description   | str               | No       | None    | Description of the QoS rule.                                                |
| action        | Dict[str, Any]    | No       | None    | QoS action configuration with 'class' field referencing a QoS profile class.|
| schedule      | str               | No       | None    | Schedule for the QoS rule.                                                  |
| dscp_tos      | Dict[str, Any]    | No       | None    | DSCP/TOS codepoint settings.                                                |
| folder        | str               | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.              |
| snippet       | str               | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.             |
| device        | str               | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.              |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### QosRuleCreateModel

Inherits all fields from `QosRuleBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### QosRuleUpdateModel

Extends `QosRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the QoS rule              |

### QosRuleResponseModel

Extends `QosRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the QoS rule              |

> **Note:** The `QosRuleResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

### QosRuleMoveModel

Model for QoS rule move (reorder) operations within the rulebase.

| Attribute        | Type                | Required | Default | Description                                                       |
|------------------|---------------------|----------|---------|-------------------------------------------------------------------|
| destination      | QosMoveDestination  | Yes      | None    | Where to move the rule (top, bottom, before, after).              |
| rulebase         | QosRulebase         | Yes      | None    | Which rulebase to use (pre or post).                              |
| destination_rule | UUID                | No       | None    | UUID of the reference rule for before/after moves.                |

## Enumerations

### QosMoveDestination

Defines valid destination values for QoS rule movement operations.

| Value    | Description                                      |
|----------|--------------------------------------------------|
| `top`    | Move the rule to the top of the rulebase         |
| `bottom` | Move the rule to the bottom of the rulebase     |
| `before` | Move the rule before the specified reference rule|
| `after`  | Move the rule after the specified reference rule |

### QosRulebase

Defines valid rulebase values for QoS rules.

| Value  | Description                                       |
|--------|---------------------------------------------------|
| `pre`  | Pre-rulebase (evaluated before default rules)     |
| `post` | Post-rulebase (evaluated after default rules)     |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a rule (`QosRuleCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.
- When using `QosRuleMoveModel` with `destination` set to `before` or `after` without providing `destination_rule`.
- When using `QosRuleMoveModel` with `destination` set to `top` or `bottom` while also providing `destination_rule`.

## Model Validators

### Container Validation in `QosRuleCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

### Move Configuration Validation in `QosRuleMoveModel`

- **validate_move_configuration**:
  After model initialization, this validator ensures that:
  - When `destination` is `BEFORE` or `AFTER`, the `destination_rule` field is provided.
  - When `destination` is `TOP` or `BOTTOM`, the `destination_rule` field is not provided.

## Usage Examples

### Creating a QoS Rule

#### Using a Dictionary

```python
from scm.models.network import QosRuleCreateModel

rule_data = {
    "name": "voip-priority",
    "description": "Prioritize VoIP traffic",
    "action": {
        "class": "class1"
    },
    "dscp_tos": {
        "codepoints": [
            {"name": "ef", "type": {"af": {"codepoint": "ef"}}}
        ]
    },
    "folder": "QoS",
}

# Validate and create model instance
rule = QosRuleCreateModel(**rule_data)
payload = rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import QosRuleCreateModel

# Create QoS rule
rule = QosRuleCreateModel(
    name="business-apps-qos",
    description="QoS for business applications",
    action={"class": "class2"},
    schedule="business-hours",
    folder="QoS",
)
payload = rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Move Configuration

```python
from scm.models.network.qos_rule import QosRuleMoveModel, QosMoveDestination, QosRulebase

# Move to top of pre-rulebase
move_top = QosRuleMoveModel(
    destination=QosMoveDestination.TOP,
    rulebase=QosRulebase.PRE,
)
print(move_top.model_dump(exclude_none=True))

# Move before a specific rule
move_before = QosRuleMoveModel(
    destination=QosMoveDestination.BEFORE,
    rulebase=QosRulebase.PRE,
    destination_rule="987fcdeb-51a2-43e7-b890-123456789abc",
)
print(move_before.model_dump(exclude_none=True))
```

### Updating a QoS Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing rule
existing = client.qos_rule.fetch(name="voip-priority", folder="QoS")

# Modify the description
existing.description = "Updated VoIP priority rule"

# Pass modified object to update()
updated = client.qos_rule.update(existing)
print(f"Updated rule: {updated.name}")
```
