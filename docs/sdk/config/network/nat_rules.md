# NAT Rules Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [NAT Rule Model Attributes](#nat-rule-model-attributes)
4. [Source Translation Types](#source-translation-types)
5. [Exceptions](#exceptions)
6. [Basic Configuration](#basic-configuration)
7. [Usage Examples](#usage-examples)
    - [Creating NAT Rules](#creating-nat-rules)
    - [Retrieving NAT Rules](#retrieving-nat-rules)
    - [Updating NAT Rules](#updating-nat-rules)
    - [Listing NAT Rules](#listing-nat-rules)
    - [Deleting NAT Rules](#deleting-nat-rules)
8. [Best Practices](#best-practices)
9. [Full Script Examples](#full-script-examples)
10. [Related Models](#related-models)

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

| Attribute                   | Type                 | Required      | Description                                                |
|-----------------------------|--------------------- |---------------|------------------------------------------------------------|
| `name`                      | str                  | Yes           | The name of the NAT rule.                                  |
| `id`                        | UUID                 | Yes*          | Unique identifier (response only).                         |
| `nat_type`                  | NatType              | No            | The type of NAT rule (`ipv4`, `nat64`, `nptv6`).          |
| `service`                   | str                  | No            | The service associated with the NAT translation.           |
| `destination`               | List[str]            | No            | Destination addresses or subnets for the NAT rule.         |
| `source`                    | List[str]            | No            | Source addresses or subnets for the NAT rule.              |
| `tag`                       | List[str]            | No            | Tags associated with the NAT rule (only 'Automation' and 'Decrypted' allowed). |
| `disabled`                  | bool                 | No            | Indicates whether the NAT rule is disabled.                |
| `source_translation`        | SourceTranslation    | No            | Source translation configuration.                          |
| `destination_translation`   | DestinationTranslation | No          | Destination translation configuration.                     |
| `folder`                    | str                  | Conditionally | The folder container where the NAT rule is defined.        |
| `snippet`                   | str                  | Conditionally | The snippet container (if applicable).                     |
| `device`                    | str                  | Conditionally | The device container (if applicable).                      |

*Note: The `id` field is assigned by the system and is only present in response objects.

## Source Translation Types

The NAT rules model supports three different types of source translation methods, following a discriminated union pattern where exactly one type must be provided:

### 1. Dynamic IP and Port (PAT)

This is the most common NAT type, where multiple internal IP addresses are translated to use a single external IP with dynamic ports.

```python
nat_rule_data = {
    "name": "dynamic-ip-port-rule",
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "translated_address": ["192.168.1.100"]  # Single or multiple IP addresses
        }
    },
    "folder": "NAT Rules"
}
```

Alternatively, you can use an interface for translation:

```python
nat_rule_data = {
    "name": "interface-translation-rule",
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "interface_address": {
                "interface": "ethernet1/1",
                "ip": "192.168.1.1",
                "floating_ip": "192.168.1.100"  # Optional
            }
        }
    },
    "folder": "NAT Rules"
}
```

### 2. Dynamic IP (NAT)

Dynamic IP NAT allows multiple internal IPs to be translated to a pool of external IPs without port translation.

```python
nat_rule_data = {
    "name": "dynamic-ip-rule",
    "source_translation": {
        "dynamic_ip": {
            "translated_address": ["192.168.1.100", "192.168.1.101"],
            "fallback_type": "translated_address",  # Optional
            "fallback_address": ["10.0.0.100"]  # Optional
        }
    },
    "folder": "NAT Rules"
}
```

### 3. Static IP

This provides a one-to-one mapping between internal and external IPs, optionally with bi-directional support.

```python
nat_rule_data = {
    "name": "static-ip-rule",
    "source_translation": {
        "static_ip": {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes"  # Optional, must be string "yes" or "no"
        }
    },
    "folder": "NAT Rules"
}
```

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid.                          |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing. |

In addition to these HTTP exceptions, the model validation may raise `ValueError` for various validation issues, such as:

- Using tags other than 'Automation' and 'Decrypted'
- Using DNS rewrite with NAT64 rule type
- Using bi-directional static NAT with destination translation
- Providing invalid source translation configurations
- Violating the container requirements

## Basic Configuration

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    nat_rule_max_limit=2500  # Optional: set custom max_limit for NAT rules
)

# Access the nat_rule module directly through the client
# client.nat_rule is automatically initialized for you
```

</div>

You can also use the traditional approach if preferred:

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

## Usage Examples

### Creating NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Define NAT rule configuration data with dynamic IP and port translation
nat_rule_data = {
    "name": "nat-rule-1",
    "nat_type": "ipv4",
    "service": "any",
    "destination": ["any"],
    "source": ["10.0.0.0/24"],
    "tag": ["Automation"],  # Only "Automation" and "Decrypted" tags allowed
    "disabled": False,
    "source_translation": {
        "dynamic_ip_and_port": {
            "type": "dynamic_ip_and_port",
            "translated_address": ["192.168.1.100"]
        }
    },
    "folder": "NAT Rules"
}

# Create a new NAT rule (default position is 'pre')
new_nat_rule = client.nat_rule.create(nat_rule_data)

# Create a static NAT rule with bi-directional translation
static_nat_data = {
    "name": "static-nat-rule",
    "nat_type": "ipv4",
    "service": "any",
    "destination": ["any"],
    "source": ["10.0.0.10"],
    "source_translation": {
        "static_ip": {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes"
        }
    },
    "folder": "NAT Rules"
}

static_nat_rule = client.nat_rule.create(static_nat_data)
```

</div>

### Retrieving NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Retrieve a NAT rule by name using fetch()
fetched_rule = client.nat_rule.fetch(
    name="nat-rule-1",
    folder="NAT Rules"
)
print(f"Fetched NAT Rule: {fetched_rule.name}")

# Retrieve a NAT rule by its unique ID using get()
rule_by_id = client.nat_rule.get(fetched_rule.id)
print(f"NAT Rule ID: {rule_by_id.id}, Name: {rule_by_id.name}")
```

</div>

### Updating NAT Rules

<div class="termy">

<!-- termynal -->
```python
from scm.models.network import NatRuleUpdateModel, SourceTranslation, DynamicIp

# Assume we have fetched the existing NAT rule
existing_rule = client.nat_rule.fetch(
    name="nat-rule-1",
    folder="NAT Rules"
)

# Change from dynamic IP and port to just dynamic IP translation
source_translation = SourceTranslation(
    dynamic_ip=DynamicIp(
        translated_address=["192.168.1.100", "192.168.1.101"]
    ),
    dynamic_ip_and_port=None,
    static_ip=None
)

# Update with new source translation configuration
updated_data = {
    "id": existing_rule.id,
    "disabled": True,
    "source_translation": source_translation
}
rule_update = NatRuleUpdateModel(**updated_data)

# Update the NAT rule (default position is 'pre')
updated_rule = client.nat_rule.update(rule_update)
print(f"Updated NAT Rule translation type to dynamic IP")
```

</div>

### Listing NAT Rules

<div class="termy">

<!-- termynal -->
```python
# List NAT rules in the "NAT Rules" folder with additional filtering
nat_rules_list = client.nat_rule.list(
    folder="NAT Rules",
    position="pre",
    nat_type=["ipv4"],
    disabled=False,
    tag=["Automation"]
)

# Iterate and process each NAT rule
for rule in nat_rules_list:
    print(f"Name: {rule.name}, Service: {rule.service}, Destination: {rule.destination}")
    
    # Check source translation type
    if rule.source_translation:
        if rule.source_translation.dynamic_ip_and_port:
            print("  Translation: Dynamic IP and Port (PAT)")
        elif rule.source_translation.dynamic_ip:
            print("  Translation: Dynamic IP (NAT)")
        elif rule.source_translation.static_ip:
            print("  Translation: Static IP")
            if rule.source_translation.static_ip.bi_directional == "yes":
                print("  Bi-directional: Yes")
```

</div>

### Deleting NAT Rules

<div class="termy">

<!-- termynal -->
```python
# Delete a NAT rule by its unique ID
rule_id_to_delete = "123e4567-e89b-12d3-a456-426655440000"
client.nat_rule.delete(rule_id_to_delete)
print(f"NAT Rule {rule_id_to_delete} deleted successfully.")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified `ScmClient` approach for simpler code
    - Access NAT rule operations via `client.nat_rule` property
    - Perform commit operations directly on the client
    - Monitor jobs directly on the client
    - Set appropriate max_limit parameters for large datasets using `nat_rule_max_limit`

2. **NAT Rule Configuration**
    - Use clear and descriptive names for NAT rules.
    - Validate IP addresses and subnets for both source and destination.
    - Use the appropriate source translation type for your use case.
    - Remember that only 'Automation' and 'Decrypted' tags are allowed.
    - Be aware that bi-directional static NAT cannot be used with destination translation.

3. **Source Translation Selection**
    - Use **Dynamic IP and Port** for most outbound traffic to the internet.
    - Use **Dynamic IP** when preserving the source port is important.
    - Use **Static IP** for one-to-one mapping, especially for inbound connections.
    - Enable bi-directional mode for static NAT when two-way connections are needed.

4. **Filtering and Container Parameters**
    - Always provide exactly one container parameter: `folder`, `snippet`, or `device`.
    - Use the `exact_match` parameter if strict container matching is required.
    - Leverage additional filters (e.g., `nat_type`, `service`) for precise listings.

5. **Error Handling**
    - Implement comprehensive error handling for invalid data and missing parameters.
    - Handle model validation errors for source translation configurations.
    - Log responses and exceptions to troubleshoot API issues effectively.

6. **Performance**
    - Adjust the `max_limit` based on your environment and API rate limits.
    - Utilize pagination effectively when working with large numbers of NAT rules.

## Full Script Examples

Refer to the [nat_rule.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/network/nat_rule.py) for a complete implementation.

## Related Models

The NAT rule configuration uses several nested models for comprehensive validation:

- [NatRuleCreateModel](../../models/network/nat_rule_models.md#natrulecreatemodel) - For creating new NAT rules
- [NatRuleUpdateModel](../../models/network/nat_rule_models.md#natruleupdatemodel) - For updating existing NAT rules
- [NatRuleResponseModel](../../models/network/nat_rule_models.md#natruleresponsemodel) - For representing API responses
- [SourceTranslation](../../models/network/nat_rule_models.md#sourcetranslation) - Main container for source translation configurations
- [DynamicIpAndPort](../../models/network/nat_rule_models.md#dynamicipandport) - For dynamic IP and port translation
- [DynamicIp](../../models/network/nat_rule_models.md#dynamicip) - For dynamic IP translation 
- [StaticIp](../../models/network/nat_rule_models.md#staticip) - For static IP translation
- [DestinationTranslation](../../models/network/nat_rule_models.md#destinationtranslation) - For destination translation configuration
- [NatRuleMoveModel](../../models/network/nat_rule_models.md#natrrulemovemodel) - For moving NAT rules
