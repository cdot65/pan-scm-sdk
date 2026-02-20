# PBF Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Sub-Models](#sub-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The PBF Rule models provide a structured way to represent and validate Policy-Based Forwarding (PBF) rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage PBF rules that override normal routing decisions and forward traffic based on source, destination, application, service, and user criteria.

### Models

The module provides the following Pydantic models:

- `PbfRuleBaseModel`: Base model with fields common to all PBF rule operations
- `PbfRuleCreateModel`: Model for creating new PBF rules
- `PbfRuleUpdateModel`: Model for updating existing PBF rules
- `PbfRuleResponseModel`: Response model for PBF rule operations

### Sub-Models

The module also provides several sub-models for nested configuration:

- `PbfRuleFrom`: Source zone/interface configuration
- `PbfRuleAction`: Action configuration (forward, discard, or no_pbf)
- `PbfRuleForward`: Forward action configuration
- `PbfRuleForwardNexthop`: Nexthop configuration for forward action
- `PbfRuleForwardMonitor`: Monitor configuration for forward action
- `PbfRuleEnforceSymmetricReturn`: Enforce symmetric return configuration
- `PbfRuleNexthopAddress`: Nexthop address entry for symmetric return

The `PbfRuleBaseModel` and `PbfRuleCreateModel` / `PbfRuleUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `PbfRuleResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

### Reserved Word Alias

The `from_` field in `PbfRuleBaseModel` uses an alias because `from` is a Python reserved word. The field is defined as:

```python
from_: Optional[PbfRuleFrom] = Field(None, alias="from")
```

This means:
- When providing data as a dictionary, use the key `"from"` (the API field name)
- When accessing the attribute on a model instance, use `rule.from_` (the Python attribute name)
- When serializing with `by_alias=True`, the field will be output as `"from"`

## Model Attributes

### PbfRuleBaseModel

This is the base model containing fields common to all PBF rule operations.

| Attribute                 | Type                            | Required | Default | Description                                                       |
|---------------------------|--------------------------------|----------|---------|-------------------------------------------------------------------|
| name                      | str                            | Yes      | None    | PBF rule name.                                                    |
| description               | str                            | No       | None    | Description of the PBF rule.                                      |
| tag                       | List[str]                      | No       | None    | Tags associated with the PBF rule.                                |
| schedule                  | str                            | No       | None    | Schedule for the PBF rule.                                        |
| disabled                  | bool                           | No       | None    | Is the PBF rule disabled.                                         |
| from_                     | PbfRuleFrom                    | No       | None    | Source zone or interface. Alias: `from`.                           |
| source                    | List[str]                      | No       | None    | Source addresses.                                                  |
| source_user               | List[str]                      | No       | None    | Source users.                                                      |
| destination               | List[str]                      | No       | None    | Destination addresses.                                             |
| destination_application   | Dict[str, Any]                 | No       | None    | Destination application configuration.                             |
| service                   | List[str]                      | No       | None    | Services.                                                          |
| application               | List[str]                      | No       | None    | Applications.                                                      |
| action                    | PbfRuleAction                  | No       | None    | Action configuration (forward, discard, or no_pbf).                |
| enforce_symmetric_return  | PbfRuleEnforceSymmetricReturn  | No       | None    | Enforce symmetric return configuration.                            |
| folder                    | str                            | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.     |
| snippet                   | str                            | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.    |
| device                    | str                            | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.     |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### PbfRuleCreateModel

Inherits all fields from `PbfRuleBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### PbfRuleUpdateModel

Extends `PbfRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the PBF rule              |

### PbfRuleResponseModel

Extends `PbfRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the PBF rule              |

> **Note:** The `PbfRuleResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Sub-Models

### PbfRuleFrom

Source zone/interface configuration. Supports one of: zone (list of zone names) or interface (list of interface names).

| Attribute | Type        | Required | Default | Description                              |
|-----------|-------------|----------|---------|------------------------------------------|
| zone      | List[str]   | No       | None    | Source zones.                            |
| interface | List[str]   | No       | None    | Source interfaces.                       |

### PbfRuleAction

Action configuration for PBF rules. Supports one of: forward, discard, or no_pbf.

| Attribute | Type              | Required | Default | Description                              |
|-----------|-------------------|----------|---------|------------------------------------------|
| forward   | PbfRuleForward    | No       | None    | Forward action configuration.            |
| discard   | Dict[str, Any]    | No       | None    | Discard action (empty object).           |
| no_pbf    | Dict[str, Any]    | No       | None    | No PBF action (empty object).            |

### PbfRuleForward

Forward action configuration.

| Attribute        | Type                    | Required | Default | Description                              |
|------------------|-------------------------|----------|---------|------------------------------------------|
| egress_interface | str                     | No       | None    | Egress interface.                        |
| nexthop          | PbfRuleForwardNexthop   | No       | None    | Next hop configuration.                  |
| monitor          | PbfRuleForwardMonitor   | No       | None    | Monitor configuration.                   |

### PbfRuleForwardNexthop

Nexthop configuration for forward action. Supports one of: ip_address or fqdn.

| Attribute  | Type | Required | Default | Description                              |
|------------|------|----------|---------|------------------------------------------|
| ip_address | str  | No       | None    | Next hop IP address.                     |
| fqdn       | str  | No       | None    | Next hop FQDN.                           |

### PbfRuleForwardMonitor

Monitor configuration for forward action.

| Attribute              | Type | Required | Default | Description                                                |
|------------------------|------|----------|---------|------------------------------------------------------------|
| profile                | str  | No       | None    | Monitoring profile.                                        |
| disable_if_unreachable | bool | No       | None    | Disable this rule if nexthop/monitor IP is unreachable.    |
| ip_address             | str  | No       | None    | Monitor IP address.                                        |

### PbfRuleEnforceSymmetricReturn

Enforce symmetric return configuration.

| Attribute            | Type                      | Required | Default | Description                              |
|----------------------|---------------------------|----------|---------|------------------------------------------|
| enabled              | bool                      | No       | None    | Enforce symmetric return.                |
| nexthop_address_list | List[PbfRuleNexthopAddress]| No      | None    | Next hop IP addresses for symmetric return.|

### PbfRuleNexthopAddress

Nexthop address entry for enforce symmetric return.

| Attribute | Type | Required | Default | Description                              |
|-----------|------|----------|---------|------------------------------------------|
| name      | str  | Yes      | None    | Next hop IP address.                     |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a rule (`PbfRuleCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `PbfRuleCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a PBF Rule

#### Using a Dictionary

```python
from scm.models.network import PbfRuleCreateModel

# Note: use "from" (the API field name) in dictionaries
rule_data = {
    "name": "redirect-to-wan2",
    "description": "Forward traffic through WAN2",
    "from": {
        "zone": ["trust"]
    },
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "action": {
        "forward": {
            "egress_interface": "ethernet1/2",
            "nexthop": {
                "ip_address": "203.0.113.1"
            }
        }
    },
    "folder": "Networking",
}

# Validate and create model instance
rule = PbfRuleCreateModel(**rule_data)
payload = rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import PbfRuleCreateModel
from scm.models.network.pbf_rule import (
    PbfRuleFrom,
    PbfRuleAction,
    PbfRuleForward,
    PbfRuleForwardNexthop,
    PbfRuleForwardMonitor,
)

# Create PBF rule with sub-models
# Note: use from_ (the Python attribute name) when using keyword arguments
rule = PbfRuleCreateModel(
    name="monitored-redirect",
    description="Redirect with monitoring",
    from_=PbfRuleFrom(zone=["trust"]),
    source=["any"],
    destination=["any"],
    action=PbfRuleAction(
        forward=PbfRuleForward(
            egress_interface="ethernet1/2",
            nexthop=PbfRuleForwardNexthop(ip_address="203.0.113.1"),
            monitor=PbfRuleForwardMonitor(
                profile="default",
                ip_address="203.0.113.1",
                disable_if_unreachable=True
            )
        )
    ),
    folder="Networking",
)
payload = rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
# The output will contain "from" (not "from_") due to by_alias=True
```

### Creating a Discard Rule

```python
from scm.models.network import PbfRuleCreateModel

rule = PbfRuleCreateModel(
    name="block-p2p",
    description="Discard peer-to-peer traffic",
    from_={"zone": ["trust"]},
    source=["any"],
    destination=["any"],
    application=["bittorrent"],
    action={"discard": {}},
    folder="Networking",
)
payload = rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a PBF Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing rule
existing = client.pbf_rule.fetch(name="redirect-to-wan2", folder="Networking")

# Access the 'from' field using the Python attribute name 'from_'
if existing.from_:
    print(f"Source zones: {existing.from_.zone}")

# Modify the description
existing.description = "Updated WAN2 redirect rule"
existing.disabled = True

# Pass modified object to update()
updated = client.pbf_rule.update(existing)
print(f"Updated rule: {updated.name}")
```
