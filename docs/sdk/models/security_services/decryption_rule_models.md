# Decryption Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Decryption Rule models provide a structured way to manage decryption rules in Palo Alto Networks' Strata Cloud Manager.
These models support defining SSL/TLS decryption policies with source/destination zones, addresses, users, and actions.
Rules can be defined in folders, snippets, or devices and placed in either pre or post rulebases. The models handle
validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `DecryptionRuleBaseModel`: Base model with fields common to all rule operations
- `DecryptionRuleCreateModel`: Model for creating new decryption rules
- `DecryptionRuleUpdateModel`: Model for updating existing decryption rules
- `DecryptionRuleResponseModel`: Response model for decryption rule operations
- `DecryptionRuleMoveModel`: Model for moving rules within a rulebase
- `DecryptionRuleType`: Model for decryption type settings (SSL forward proxy or SSL inbound inspection)

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### DecryptionRuleBaseModel

| Attribute            | Type                   | Required | Default         | Description                                    |
|----------------------|------------------------|----------|-----------------|------------------------------------------------|
| name                 | str                    | Yes      | None            | Name of the rule. Pattern: `^[a-zA-Z0-9_ \.-]+$` |
| action               | DecryptionRuleAction   | Yes      | None            | Rule action (decrypt/no-decrypt)               |
| disabled             | bool                   | No       | False           | Whether the rule is disabled                   |
| description          | str                    | No       | None            | Description of the rule                        |
| tag                  | List[str]              | No       | []              | List of tags                                   |
| from_                | List[str]              | No       | ["any"]         | Source security zones                          |
| to_                  | List[str]              | No       | ["any"]         | Destination security zones                     |
| source               | List[str]              | No       | ["any"]         | Source addresses                               |
| destination          | List[str]              | No       | ["any"]         | Destination addresses                          |
| source_user          | List[str]              | No       | ["any"]         | Source users/groups                            |
| category             | List[str]              | No       | ["any"]         | URL categories                                 |
| service              | List[str]              | No       | ["any"]         | Services                                       |
| source_hip           | List[str]              | No       | ["any"]         | Source Host Integrity Profiles                 |
| destination_hip      | List[str]              | No       | ["any"]         | Destination Host Integrity Profiles            |
| negate_source        | bool                   | No       | False           | Negate source addresses                        |
| negate_destination   | bool                   | No       | False           | Negate destination addresses                   |
| profile              | str                    | No       | None            | Decryption profile name                        |
| type                 | DecryptionRuleType     | No       | None            | Decryption type settings                       |
| log_setting          | str                    | No       | None            | Log forwarding profile                         |
| log_fail             | bool                   | No       | None            | Log failed decryption events                   |
| log_success          | bool                   | No       | None            | Log successful decryption events               |
| folder               | str                    | No**     | None            | Folder location. Max 64 chars                  |
| snippet              | str                    | No**     | None            | Snippet location. Max 64 chars                 |
| device               | str                    | No**     | None            | Device location. Max 64 chars                  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### DecryptionRuleCreateModel

Inherits all fields from `DecryptionRuleBaseModel` and adds:

| Attribute | Type                    | Required | Default | Description                   |
|-----------|-------------------------|----------|---------|-------------------------------|
| rulebase  | DecryptionRuleRulebase  | No       | None    | Which rulebase to use (pre/post) |

Enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### DecryptionRuleUpdateModel

Extends `DecryptionRuleBaseModel` by adding:

| Attribute | Type                    | Required | Default | Description                      |
|-----------|-------------------------|----------|---------|----------------------------------|
| id        | UUID                    | Yes      | None    | The unique identifier of the rule |
| rulebase  | DecryptionRuleRulebase  | No       | None    | Which rulebase to use (pre/post)  |

### DecryptionRuleResponseModel

Extends `DecryptionRuleBaseModel` by adding:

| Attribute | Type                    | Required | Default | Description                       |
|-----------|-------------------------|----------|---------|-----------------------------------|
| id        | UUID                    | Yes      | None    | The unique identifier of the rule |
| rulebase  | DecryptionRuleRulebase  | No       | None    | Which rulebase the rule belongs to |

The response model uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept additional
fields returned by the API without raising validation errors. The `device` field in the response model also accepts
an empty dictionary in addition to `None` or a string value.

### DecryptionRuleMoveModel

| Attribute        | Type                           | Required | Default | Description                                    |
|------------------|--------------------------------|----------|---------|------------------------------------------------|
| destination      | DecryptionRuleMoveDestination  | Yes      | None    | Where to move (top/bottom/before/after)        |
| rulebase         | DecryptionRuleRulebase         | Yes      | None    | Which rulebase to use (pre/post)               |
| destination_rule | UUID                           | No       | None    | UUID of reference rule (for before/after moves) |

## Enum Types

### DecryptionRuleAction

Defines the available rule actions:

| Value        | Description                  |
|--------------|------------------------------|
| `decrypt`    | Decrypt the traffic          |
| `no-decrypt` | Do not decrypt the traffic   |

### DecryptionRuleRulebase

Defines the available rulebases:

| Value  | Description      |
|--------|------------------|
| `pre`  | Pre-rulebase     |
| `post` | Post-rulebase    |

### DecryptionRuleMoveDestination

Defines the move destinations:

| Value    | Description                      |
|----------|----------------------------------|
| `top`    | Move to top of rulebase          |
| `bottom` | Move to bottom of rulebase       |
| `before` | Move before a specific rule      |
| `after`  | Move after a specific rule       |

## Supporting Models

### DecryptionRuleType

Defines the type of decryption to apply. Exactly one of `ssl_forward_proxy` or `ssl_inbound_inspection` must be provided.

| Attribute              | Type          | Required | Default | Description                                  |
|------------------------|---------------|----------|---------|----------------------------------------------|
| ssl_forward_proxy      | Dict          | No*      | None    | SSL Forward Proxy decryption type (empty dict) |
| ssl_inbound_inspection | str           | No*      | None    | SSL Inbound Inspection certificate name       |

\* Exactly one of `ssl_forward_proxy` or `ssl_inbound_inspection` must be provided.

**SSL Forward Proxy** is used for outbound traffic inspection, where the firewall acts as a proxy between the client and
the server. It is specified as an empty dictionary `{}`.

**SSL Inbound Inspection** is used for inbound traffic to internal servers, where the firewall decrypts traffic using
the server's certificate. The value is the name of the certificate to use for decryption.

## Exceptions

The Decryption Rule models can raise the following exceptions during validation:

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
    - When both ssl_forward_proxy and ssl_inbound_inspection are provided in DecryptionRuleType
    - When neither ssl_forward_proxy nor ssl_inbound_inspection is provided in DecryptionRuleType

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import DecryptionRuleCreateModel

# Error: multiple containers specified
try:
    rule = DecryptionRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        action="decrypt"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    rule = DecryptionRuleCreateModel(
        name="invalid-rule",
        action="decrypt"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### List Field Validation

All list fields are validated to ensure they contain only unique string values:

```python
from scm.models.security import DecryptionRuleCreateModel

# Error: duplicate values
try:
    rule = DecryptionRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        action="decrypt",
        source=["10.0.0.0/8", "10.0.0.0/8"]  # Duplicate values not allowed
    )
except ValueError as e:
    print(e)  # "List items must be unique"
```

### Move Configuration Validation

The DecryptionRuleMoveModel validates that destination_rule is provided only for before/after moves:

```python
from scm.models.security import DecryptionRuleMoveModel

# Error: missing destination_rule for 'before' move
try:
    move = DecryptionRuleMoveModel(
        destination="before",
        rulebase="pre"
        # destination_rule is required for before/after
    )
except ValueError as e:
    print(e)  # "destination_rule is required when destination is 'before'"

# Error: destination_rule provided for 'top' move
try:
    move = DecryptionRuleMoveModel(
        destination="top",
        rulebase="pre",
        destination_rule="987fcdeb-51d3-a456-426655440000"  # Not allowed for top/bottom
    )
except ValueError as e:
    print(e)  # "destination_rule should not be provided when destination is 'top'"
```

### Decryption Type Validation

The DecryptionRuleType validates that exactly one type is specified:

```python
from scm.models.security.decryption_rules import DecryptionRuleType

# Error: both types specified
try:
    rule_type = DecryptionRuleType(
        ssl_forward_proxy={},
        ssl_inbound_inspection="server-cert"
    )
except ValueError as e:
    print(e)  # "Only one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' can be provided."

# Error: neither type specified
try:
    rule_type = DecryptionRuleType()
except ValueError as e:
    print(e)  # "Exactly one of 'ssl_forward_proxy' or 'ssl_inbound_inspection' must be provided."
```

## Usage Examples

### Creating a Basic Decryption Rule

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
    "name": "decrypt-web",
    "description": "Decrypt web traffic for inspection",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "service": ["application-default"],
    "action": "decrypt",
    "log_success": True,
    "log_fail": True
}

response = client.decryption_rule.create(rule_dict, rulebase="pre")
print(f"Created rule: {response.name}")
```

### Creating a Rule with SSL Forward Proxy

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
    "name": "ssl-forward-decrypt",
    "folder": "Texas",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/8"],
    "destination": ["any"],
    "action": "decrypt",
    "type": {
        "ssl_forward_proxy": {}
    },
    "profile": "strict-decryption",
    "log_setting": "detailed-logging",
    "log_success": True,
    "log_fail": True
}

response = client.decryption_rule.create(rule_dict, rulebase="pre")
print(f"Created rule with SSL forward proxy: {response.name}")
```

### Creating a Rule with SSL Inbound Inspection

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
    "name": "ssl-inbound-decrypt",
    "folder": "Texas",
    "from_": ["untrust"],
    "to_": ["dmz"],
    "source": ["any"],
    "destination": ["web-server"],
    "action": "decrypt",
    "type": {
        "ssl_inbound_inspection": "web-server-cert"
    },
    "log_success": True,
    "log_fail": True
}

response = client.decryption_rule.create(rule_dict, rulebase="pre")
print(f"Created rule with SSL inbound inspection: {response.name}")
```

### Updating a Decryption Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing rule
existing = client.decryption_rule.fetch(name="decrypt-web", folder="Texas", rulebase="pre")

# Modify attributes using dot notation
existing.description = "Updated decryption rule"
existing.source = ["10.0.0.0/8", "172.16.0.0/12"]

# Update decryption profile
existing.profile = "strict-decryption"

# Enable logging
existing.log_success = True
existing.log_fail = True

# Pass modified object to update()
updated = client.decryption_rule.update(existing, rulebase="pre")
print(f"Updated rule: {updated.name}")
```

### Moving a Decryption Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch the rule to move
rule = client.decryption_rule.fetch(name="decrypt-web", folder="Texas", rulebase="pre")

# Move to top of rulebase
move_config = {
    "destination": "top",
    "rulebase": "pre"
}
client.decryption_rule.move(rule.id, move_config)

# Move before another rule
move_before = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}
client.decryption_rule.move(rule.id, move_before)
```
