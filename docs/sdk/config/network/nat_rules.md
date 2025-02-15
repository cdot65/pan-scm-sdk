# NAT Rules Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [NAT Rule Model Attributes](#nat-rule-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating NAT Rules](#creating-nat-rules)
    - [Retrieving NAT Rules](#retrieving-nat-rules)
    - [Updating NAT Rules](#updating-nat-rules)
    - [Listing NAT Rules](#listing-nat-rules)
    - [Deleting NAT Rules](#deleting-nat-rules)
7. [Best Practices](#best-practices)
8. [Full Script Examples](#full-script-examples)
9. [Related Models](#related-models)

## Overview

The `NatRule` class manages NAT rule objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete NAT rules. Additionally, it provides client-side filtering for listing operations and enforces container requirements using the `folder`, `snippet`, or `device` parameters.

## Core Methods

| Method     | Description                                                               | Parameters                                                                                                                                                | Return Type                  |
|------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| `create()` | Creates a new NAT rule object.                                            | `data: Dict[str, Any]`, `position: str = "pre"`                                                                                                           | `NatRuleResponseModel`       |
| `get()`    | Retrieves a NAT rule object by its unique ID.                             | `object_id: str`                                                                                                                                          | `NatRuleResponseModel`       |
| `update()` | Updates an existing NAT rule object.                                      | `rule: NatRuleUpdateModel`, `position: str = "pre"`                                                                                                       | `NatRuleResponseModel`       |
| `list()`   | Lists NAT rule objects with optional filtering and container constraints. | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `position: str = "pre"`, `exact_match: bool = False`, plus additional filters | `List[NatRuleResponseModel]` |
| `fetch()`  | Fetches a single NAT rule by its name within a specified container.       | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `position: str = "pre"`                                          | `NatRuleResponseModel`       |
| `delete()` | Deletes a NAT rule object by its ID.                                      | `object_id: str`                                                                                                                                          | `None`                       |

## NAT Rule Model Attributes

| Attribute     | Type      | Required | Description                                           |
|---------------|-----------|----------|-------------------------------------------------------|
| `name`        | str       | Yes      | The name of the NAT rule.                             |
| `id`          | UUID      | Yes*     | Unique identifier (response only).                    |
| `nat_type`    | str       | Yes      | The type of NAT rule (e.g., static, dynamic).         |
| `service`     | str       | Yes      | The service associated with the NAT translation.      |
| `destination` | List[str] | Yes      | Destination addresses or subnets for the NAT rule.    |
| `source`      | List[str] | Yes      | Source addresses or subnets for the NAT rule.         |
| `tag`         | List[str] | No       | Tags associated with the NAT rule for categorization. |
| `disabled`    | bool      | No       | Indicates whether the NAT rule is disabled.           |
| `folder`      | str       | Yes      | The folder container where the NAT rule is defined.   |
| `snippet`     | str       | No       | The snippet container (if applicable).                |
| `device`      | str       | No       | The device container (if applicable).                 |

*Note: The `id` field is assigned by the system and is only present in response objects.

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid.                          |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing. |

## Basic Configuration

<div class="termy">

<!-- termynal -->
```python
from scm.client import Scm
from scm.config.network import NatRule

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize NatRule object with a custom max_limit (optional)
nat_rule = NatRule(client, max_limit=2500)
```

</div>

## Usage Examples

### Creating NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Define NAT rule configuration data
nat_rule_data = {
    "name": "nat-rule-1",
    "nat_type": "static",
    "service": "tcp-80",
    "destination": ["192.168.1.100"],
    "source": ["10.0.0.0/24"],
    "tag": ["web", "prod"],
    "disabled": False,
    "folder": "NAT Rules"
}

# Create a new NAT rule (default position is 'pre')
new_nat_rule = nat_rule.create(nat_rule_data)

# Optionally, specify a different rule position (e.g., 'post')
# new_nat_rule = nat_rule.create(nat_rule_data, position="post")
```

</div>

### Retrieving NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Retrieve a NAT rule by name using fetch()
fetched_rule = nat_rule.fetch(
    name="nat-rule-1",
    folder="NAT Rules"
)
print(f"Fetched NAT Rule: {fetched_rule.name}")

# Retrieve a NAT rule by its unique ID using get()
rule_by_id = nat_rule.get(fetched_rule.id)
print(f"NAT Rule ID: {rule_by_id.id}, Name: {rule_by_id.name}")
```

</div>

### Updating NAT Rules

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import NatRuleUpdateModel

# Assume we have fetched the existing NAT rule
existing_rule = nat_rule.fetch(
    name="nat-rule-1",
    folder="NAT Rules"
)

# Update attributes (e.g., disable the rule and change destination)
updated_data = {
    "id": existing_rule.id,
    "disabled": True,
    "destination": ["192.168.1.200"]
}
rule_update = NatRuleUpdateModel(**updated_data)

# Update the NAT rule (default position is 'pre')
updated_rule = nat_rule.update(rule_update)
print(f"Updated NAT Rule Disabled Status: {updated_rule.disabled}")
```

</div>

### Listing NAT Rules

<div class="termy">

<!-- termynal -->
```python
# List NAT rules in the "NAT Rules" folder with additional filtering
nat_rules_list = nat_rule.list(
    folder="NAT Rules",
    position="pre",
    nat_type=["static"],
    disabled=False
)

# Iterate and process each NAT rule
for rule in nat_rules_list:
    print(f"Name: {rule.name}, Service: {rule.service}, Destination: {rule.destination}")
```

</div>

### Deleting NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Delete a NAT rule by its unique ID
rule_id_to_delete = "123e4567-e89b-12d3-a456-426655440000"
nat_rule.delete(rule_id_to_delete)
print(f"NAT Rule {rule_id_to_delete} deleted successfully.")
```

</div>

## Best Practices

1. **NAT Rule Configuration**
    - Use clear and descriptive names for NAT rules.
    - Validate IP addresses and subnets for both source and destination.
    - Clearly document the intended use (e.g., static vs. dynamic NAT).

2. **Filtering and Container Parameters**
    - Always provide exactly one container parameter: `folder`, `snippet`, or `device`.
    - Use the `exact_match` parameter if strict container matching is required.
    - Leverage additional filters (e.g., `nat_type`, `service`) for precise listings.

3. **Error Handling**
    - Implement comprehensive error handling for invalid data and missing parameters.
    - Log responses and exceptions to troubleshoot API issues effectively.

4. **Performance**
    - Adjust the `max_limit` based on your environment and API rate limits.
    - Utilize pagination effectively when working with large numbers of NAT rules.

## Full Script Examples

Refer to the [nat_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/nat_rule.py) for a complete implementation.

## Related Models

- [NatRuleCreateModel](../../models/network/nat_rule_models.md#natrulecreatemodel)
- [NatRuleUpdateModel](../../models/network/nat_rule_models.md#natruleupdatemodel)
- [NatRuleResponseModel](../../models/network/nat_rule_models.md#natruleresponsemodel)
