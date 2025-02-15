# NAT Rule Models

## Overview

The NAT Rule models provide a structured way to represent and validate NAT rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating, updating, and moving NAT rules, enforcing proper value types, unique list entries, and correct container specifications.

## Attributes

### NatRuleBaseModel

This is the base model containing fields common to all NAT rule operations.

| Attribute           | Type              | Required      | Default    | Description                                                                                                     |
|---------------------|-------------------|---------------|------------|-----------------------------------------------------------------------------------------------------------------|
| name                | str               | Yes           | –          | The name of the NAT rule. Allowed pattern: `^[a-zA-Z0-9_ \.-]+$`.                                               |
| description         | str               | No            | None       | A description for the NAT rule.                                                                                 |
| tag                 | List[str]         | No            | Empty list | Tags associated with the NAT rule.                                                                              |
| disabled            | bool              | No            | False      | Indicates whether the NAT rule is disabled.                                                                     |
| nat_type            | NatType           | No            | `ipv4`     | The type of NAT operation. Allowed values: `ipv4`, `nat64`, `nptv6`.                                            |
| from_ (alias: from) | List[str]         | No            | `["any"]`  | Source zone(s) for the NAT rule.                                                                                |
| to_ (alias: to)     | List[str]         | No            | `["any"]`  | Destination zone(s) for the NAT rule.                                                                           |
| source              | List[str]         | No            | `["any"]`  | Source address(es) for the NAT rule.                                                                            |
| destination         | List[str]         | No            | `["any"]`  | Destination address(es) for the NAT rule.                                                                       |
| service             | str               | No            | None       | The TCP/UDP service associated with the NAT rule.                                                               |
| source_translation  | SourceTranslation | No            | None       | Configuration for source translation.                                                                           |
| folder              | str               | Conditionally | None       | The folder container where the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars.  |
| snippet             | str               | Conditionally | None       | The snippet container where the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars. |
| device              | str               | Conditionally | None       | The device container where the resource is defined. Must match pattern `^[a-zA-Z\d\-_. ]+$` and be ≤ 64 chars.  |

### NatRuleCreateModel

Inherits all fields from `NatRuleBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### NatRuleUpdateModel / NatRuleResponseModel

Both models extend `NatRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                                     |
|-----------|------|----------|---------|-----------------------------------------------------------------|
| id        | UUID | Yes      | –       | The unique identifier of the NAT rule (assigned by the system). |

### NatRuleMoveModel

This model is used for moving NAT rules within a rulebase.

| Attribute        | Type               | Required      | Default | Description                                                                                                  |
|------------------|--------------------|---------------|---------|--------------------------------------------------------------------------------------------------------------|
| destination      | NatMoveDestination | Yes           | –       | Indicates where to move the rule. Allowed values: `top`, `bottom`, `before`, `after`.                        |
| rulebase         | NatRulebase        | Yes           | –       | Specifies which rulebase to use. Allowed values: `pre`, `post`.                                              |
| destination_rule | UUID               | Conditionally | None    | The reference NAT rule UUID for `before` or `after` moves. Required when destination is `before` or `after`. |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When fields expected to be lists (e.g., `from_`, `to_`, `source`, `destination`, `tag`) are not provided as lists or contain non-string items.
- When list fields contain duplicate values.
- When creating a NAT rule (`NatRuleCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When moving a NAT rule (`NatRuleMoveModel`), if `destination_rule` is missing for `before`/`after` destinations or provided when not applicable.

## Model Validators

### Field Validators in `NatRuleBaseModel`

- **ensure_list_of_strings**:  
  Ensures that fields like `from_`, `to_`, `source`, `destination`, and `tag` are lists of strings. If a single string is provided, it converts it into a list.

- **ensure_unique_items**:  
  Ensures that the items in list fields are unique, preventing duplicate entries.

### Container Validation in `NatRuleCreateModel`

- **validate_container**:  
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

### Move Configuration Validation in `NatRuleMoveModel`

- **validate_move_configuration**:  
  Ensures that when the `destination` is `before` or `after`, the `destination_rule` field is provided. Conversely, if the `destination` is `top` or `bottom`, `destination_rule` must not be provided.

## Usage Examples

### Creating a NAT Rule

#### Using a Dictionary

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import NatRuleCreateModel

nat_rule_data = {
    "name": "nat-rule-1",
    "description": "NAT rule for outbound traffic",
    "tag": ["web", "prod"],
    "disabled": False,
    "nat_type": "ipv4",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["192.168.1.100"],
    "service": "tcp-80",
    "folder": "NAT Rules"
}

# Validate and create model instance
nat_rule = NatRuleCreateModel(**nat_rule_data)
payload = nat_rule.model_dump(exclude_unset=True)
print(payload)
```

</div>

#### Using the Model Directly

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import NatRuleCreateModel

nat_rule = NatRuleCreateModel(
    name="nat-rule-1",
    description="NAT rule for outbound traffic",
    tag=["web", "prod"],
    disabled=False,
    nat_type="ipv4",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["192.168.1.100"],
    service="tcp-80",
    folder="NAT Rules"
)
payload = nat_rule.model_dump(exclude_unset=True)
print(payload)
```

</div>

### Updating a NAT Rule

<div class="termy">

<!-- termynal -->
```python
import uuid
from scm.models.network import NatRuleUpdateModel

update_data = {
    "id": str(uuid.uuid4()),
    "name": "nat-rule-1-updated",
    "description": "Updated description",
    "tag": ["web", "updated"],
    "disabled": True,
    "nat_type": "nat64",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.1.0/24"],
    "destination": ["192.168.1.101"],
    "service": "tcp-443",
    "folder": "NAT Rules"
}

updated_rule = NatRuleUpdateModel(**update_data)
payload = updated_rule.model_dump(exclude_unset=True)
print(payload)
```

</div>

### Moving a NAT Rule

<div class="termy">

<!-- termynal -->
```python
import uuid
from scm.models.network import NatRuleMoveModel

move_data = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": str(uuid.uuid4())
}

move_rule = NatRuleMoveModel(**move_data)
payload = move_rule.model_dump(exclude_unset=True)
print(payload)
```

</div>

## Related Enums and Models

- **Enums:**
  - `NatType`: Allowed values are `ipv4`, `nat64`, `nptv6`.
  - `NatMoveDestination`: Allowed values are `top`, `bottom`, `before`, `after`.
  - `NatRulebase`: Allowed values are `pre`, `post`.

- **Additional Models:**
  - `InterfaceAddress`: Model for interface address configuration.
  - `SourceTranslation`: Model for configuring source translation options.
  - `NatRuleCreateModel`: Model for creating NAT rules.
  - `NatRuleUpdateModel`: Model for updating NAT rules.
  - `NatRuleResponseModel`: Model for NAT rule responses.
  - `NatRuleMoveModel`: Model for moving NAT rules.
