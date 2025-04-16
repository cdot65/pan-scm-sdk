# Security Rule Models

## Overview {#Overview}

The Security Rule models provide a structured way to manage security rules in Palo Alto Networks' Strata Cloud Manager.
These models support defining security policies with source/destination zones, addresses, applications, and actions.
Rules can be defined in folders, snippets, or devices and placed in either pre or post rulebases. The models handle
validation
of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute          | Type           | Required | Default | Description                                                                     |
|--------------------|----------------|----------|---------|---------------------------------------------------------------------------------|
| name               | str            | Yes      | None    | Name of the rule. Max length: 63 chars. Must match pattern: ^[a-zA-Z0-9_ \.-]+$ |
| disabled           | bool           | No       | False   | Whether the rule is disabled                                                    |
| description        | str            | No       | None    | Description of the rule                                                         |
| tag                | List[str]      | No       | []      | List of tags                                                                    |
| from_              | List[str]      | No       | ["any"] | Source security zones                                                           |
| source             | List[str]      | No       | ["any"] | Source addresses                                                                |
| negate_source      | bool           | No       | False   | Negate source addresses                                                         |
| source_user        | List[str]      | No       | ["any"] | Source users/groups                                                             |
| source_hip         | List[str]      | No       | ["any"] | Source Host Integrity Profiles                                                  |
| to_                | List[str]      | No       | ["any"] | Destination security zones                                                      |
| destination        | List[str]      | No       | ["any"] | Destination addresses                                                           |
| negate_destination | bool           | No       | False   | Negate destination addresses                                                    |
| destination_hip    | List[str]      | No       | ["any"] | Destination Host Integrity Profiles                                             |
| application        | List[str]      | No       | ["any"] | Applications                                                                    |
| service            | List[str]      | No       | ["any"] | Services                                                                        |
| category           | List[str]      | No       | ["any"] | URL categories                                                                  |
| action             | Action         | No       | "allow" | Rule action (allow/deny/drop/reset-client/reset-server/reset-both)              |
| profile_setting    | ProfileSetting | No       | None    | Security profile settings                                                       |
| log_setting        | str            | No       | None    | Log forwarding profile                                                          |
| schedule           | str            | No       | None    | Schedule profile                                                                |
| log_start          | bool           | No       | None    | Log at session start                                                            |
| log_end            | bool           | No       | None    | Log at session end                                                              |
| folder             | str            | No*      | None    | Folder where rule is defined. Max length: 64 chars                              |
| snippet            | str            | No*      | None    | Snippet where rule is defined. Max length: 64 chars                             |
| device             | str            | No*      | None    | Device where rule is defined. Max length: 64 chars                              |
| id                 | UUID           | Yes**    | None    | UUID of the rule (response only)                                                |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

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

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
# Using dictionary
from scm.config.security import SecurityRule

# Error: multiple containers specified
try:
    rule_dict = {
        "name": "invalid-rule",
        "folder": "Texas",
        "device": "fw01",  # Can't specify both folder and device
        "action": "allow"
    }
    security_rule = SecurityRule(api_client)
    response = security_rule.create(rule_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.security import SecurityRuleCreateModel

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
# Using dictionary
try:
    rule_dict = {
        "name": "invalid-rule",
        "folder": "Texas",
        "source": ["10.0.0.0/8", "10.0.0.0/8"],  # Duplicate values not allowed
        "action": "allow"
    }
    response = security_rule.create(rule_dict)
except ValueError as e:
    print(e)  # "List items must be unique"

# Using model directly
try:
    rule = SecurityRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source=["10.0.0.0/8", "10.0.0.0/8"]
    )
except ValueError as e:
    print(e)  # "List items must be unique"
```

## Usage Examples

### Creating a Basic Security Rule

```python
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

response = security_rule.create(rule_dict)

# Using model directly
rule = SecurityRuleCreateModel(
    name="allow-web",
    description="Allow web traffic",
    folder="Texas",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/8"],
    destination=["any"],
    application=["web-browsing", "ssl"],
    service=["application-default"],
    action="allow",
    log_end=True
)

payload = rule.model_dump(exclude_unset=True)
response = security_rule.create(payload)
```

### Creating a Rule with Security Profiles

```python
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

response = security_rule.create(rule_dict)

# Using model directly
from scm.models.security import SecurityRuleCreateModel, SecurityRuleProfileSetting

rule = SecurityRuleCreateModel(
    name="secure-web",
    folder="Texas",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/8"],
    destination=["any"],
    application=["web-browsing", "ssl"],
    action="allow",
    profile_setting=SecurityRuleProfileSetting(
        group=["strict-security"]
    ),
    log_setting="detailed-logging",
    log_start=True,
    log_end=True
)

payload = rule.model_dump(exclude_unset=True)
response = security_rule.create(payload)
```

### Moving a Security Rule

```python
# Using dictionary
move_dict = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

security_rule.move("123e4567-e89b-12d3-a456-426655440000", move_dict)

# Using model directly
from scm.models.security import SecurityRuleMoveModel, SecurityRuleMoveDestination, SecurityRuleRulebase

move_config = SecurityRuleMoveModel(
    destination=SecurityRuleMoveDestination.BEFORE,
    rulebase=SecurityRuleRulebase.PRE,
    destination_rule="987fcdeb-51d3-a456-426655440000"
)

payload = move_config.model_dump(exclude_unset=True)
security_rule.move("123e4567-e89b-12d3-a456-426655440000", payload)
```
