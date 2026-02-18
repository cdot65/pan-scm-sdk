# NAT Rules Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The NAT Rules models provide a structured way to represent and validate NAT rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models support configuration of source and destination address translation with various options including static IP mappings, dynamic IP and port allocation, and DNS rewrite functionality. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `NatRuleBaseModel`: Base model with fields common to all NAT rule operations
- `NatRuleCreateModel`: Model for creating new NAT rules
- `NatRuleUpdateModel`: Model for updating existing NAT rules
- `NatRuleResponseModel`: Response model for NAT rule operations
- `NatRuleMoveModel`: Model for moving/reordering NAT rules
- `SourceTranslation`: Source translation configuration model
- `DynamicIpAndPort`: Dynamic IP and port translation model
- `DynamicIpAndPortTranslatedAddress`: Translated address container for dynamic IP and port
- `DynamicIpAndPortInterfaceAddress`: Interface address container for dynamic IP and port
- `DynamicIp`: Dynamic IP translation model
- `StaticIp`: Static IP translation model
- `InterfaceAddress`: Interface address configuration model
- `DestinationTranslation`: Destination translation configuration model
- `DnsRewrite`: DNS rewrite configuration model
- `NatType`: Enum for NAT types
- `NatMoveDestination`: Enum for move destination options
- `NatRulebase`: Enum for rulebase options
- `DistributionMethod`: Enum for distribution methods
- `DnsRewriteDirection`: Enum for DNS rewrite directions
- `BiDirectional`: Enum for bi-directional options

All models use `extra="forbid"` configuration (except `NatRuleResponseModel` which uses `extra="ignore"`), which rejects any fields not explicitly defined in the model.

## Model Attributes

### NatRuleBaseModel

This is the base model containing fields common to all NAT rule operations.

| Attribute                      | Type                   | Required | Default   | Description                                                         |
|--------------------------------|------------------------|----------|-----------|---------------------------------------------------------------------|
| `name`                         | str                    | Yes      | None      | The name of the NAT rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`           |
| `description`                  | str                    | No       | None      | Description of the NAT rule                                        |
| `tag`                          | List[TagName]          | No       | []        | Tags associated with the NAT rule. Max 127 chars per tag           |
| `disabled`                     | bool                   | No       | False     | Whether the NAT rule is disabled                                   |
| `nat_type`                     | NatType                | No       | ipv4      | Type of NAT operation (ipv4, nat64, nptv6)                         |
| `from_` (alias: `from`)       | List[str]              | No       | ["any"]   | Source zone(s) for the NAT rule                                    |
| `to_` (alias: `to`)           | List[str]              | No       | ["any"]   | Destination zone(s) for the NAT rule                               |
| `to_interface`                 | str                    | No       | None      | Destination interface of the original packet                       |
| `source`                       | List[str]              | No       | ["any"]   | Source address(es) for the NAT rule                                |
| `destination`                  | List[str]              | No       | ["any"]   | Destination address(es) for the NAT rule                           |
| `service`                      | str                    | No       | "any"     | The TCP/UDP service associated with the NAT rule                   |
| `source_translation`           | SourceTranslation      | No       | None      | Configuration for source address translation                       |
| `destination_translation`      | DestinationTranslation | No       | None      | Configuration for destination address translation                  |
| `active_active_device_binding` | str                    | No       | None      | Active/Active device binding                                       |
| `folder`                       | str                    | No**     | None      | Folder where NAT rule is defined. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars |
| `snippet`                      | str                    | No**     | None      | Snippet where NAT rule is defined. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars |
| `device`                       | str                    | No**     | None      | Device where NAT rule is defined. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### NatRuleCreateModel

Inherits all fields from `NatRuleBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### NatRuleUpdateModel

Extends `NatRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `id`      | UUID | Yes      | None    | The unique identifier of the NAT rule |

### NatRuleResponseModel

Extends `NatRuleBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| `id`      | UUID | Yes      | None    | The unique identifier of the NAT rule |

Note: `NatRuleResponseModel` uses `extra="ignore"` configuration instead of `extra="forbid"`, allowing it to accept additional fields returned by the API without raising validation errors.

## Enum Types

### NatType

Defines the NAT types supported by the system:

| Value   | Description                |
|---------|----------------------------|
| `ipv4`  | IPv4 NAT (default)         |
| `nat64` | NAT64 translation          |
| `nptv6` | NPTv6 translation          |

### NatMoveDestination

Defines valid destination values for rule movement:

| Value    | Description                        |
|----------|------------------------------------|
| `top`    | Move to the top of the rulebase    |
| `bottom` | Move to the bottom of the rulebase |
| `before` | Move before a specified rule       |
| `after`  | Move after a specified rule        |

### NatRulebase

Defines valid rulebase values:

| Value  | Description    |
|--------|----------------|
| `pre`  | Pre-rulebase   |
| `post` | Post-rulebase  |

### DistributionMethod

Defines distribution methods for dynamic destination translation:

| Value            | Description                 |
|------------------|-----------------------------|
| `round-robin`    | Round-robin distribution    |
| `source-ip-hash` | Source IP hash distribution |
| `ip-modulo`      | IP modulo distribution      |
| `ip-hash`        | IP hash distribution        |
| `least-sessions` | Least sessions distribution |

### DnsRewriteDirection

Defines DNS rewrite direction options:

| Value     | Description         |
|-----------|---------------------|
| `reverse` | Reverse DNS rewrite |
| `forward` | Forward DNS rewrite |

### BiDirectional

Defines bi-directional translation options:

| Value | Description                        |
|-------|------------------------------------|
| `yes` | Enable bi-directional translation  |
| `no`  | Disable bi-directional translation |

## Supporting Models

### SourceTranslation

Main container for source translation configurations. Exactly one translation type must be provided.

| Attribute             | Type             | Required | Default | Description                                   |
|-----------------------|------------------|----------|---------|-----------------------------------------------|
| `dynamic_ip_and_port` | DynamicIpAndPort | No*      | None    | Dynamic IP and port translation configuration |
| `dynamic_ip`          | DynamicIp        | No*      | None    | Dynamic IP translation configuration          |
| `static_ip`           | StaticIp         | No*      | None    | Static IP translation configuration           |

\* Exactly one of these translation types must be provided

### DynamicIpAndPort

Dynamic IP and port (PAT) translation configuration. Either `translated_address` or `interface_address` must be provided, but not both.

| Attribute           | Type             | Required | Default              | Description                             |
|---------------------|------------------|----------|----------------------|-----------------------------------------|
| `type`              | Literal          | No       | "dynamic_ip_and_port"| Type identifier                         |
| `translated_address`| List[str]        | No*      | None                 | Translated source IP addresses          |
| `interface_address` | InterfaceAddress | No*      | None                 | Interface configuration for translation |

\* Exactly one of `translated_address` or `interface_address` must be provided

### DynamicIpAndPortTranslatedAddress

Container model for dynamic IP and port translated address configuration.

| Attribute            | Type      | Required | Default | Description                    |
|----------------------|-----------|----------|---------|--------------------------------|
| `translated_address` | List[str] | Yes      | None    | Translated source IP addresses |

### DynamicIpAndPortInterfaceAddress

Container model for dynamic IP and port interface address configuration.

| Attribute     | Type | Required | Default | Description           |
|---------------|------|----------|---------|-----------------------|
| `interface`   | str  | Yes      | None    | Interface name        |
| `ip`          | str  | No       | None    | Translated source IP address |
| `floating_ip` | str  | No       | None    | Floating IP address   |

### InterfaceAddress

Interface address configuration for translation.

| Attribute     | Type | Required | Default | Description         |
|---------------|------|----------|---------|---------------------|
| `interface`   | str  | Yes      | None    | Interface name      |
| `ip`          | str  | No       | None    | IP address          |
| `floating_ip` | str  | No       | None    | Floating IP address |

### DynamicIp

Dynamic IP translation configuration with optional fallback settings.

| Attribute            | Type      | Required | Default | Description                                                      |
|----------------------|-----------|----------|---------|------------------------------------------------------------------|
| `translated_address` | List[str] | Yes      | None    | Translated IP addresses                                          |
| `fallback_type`      | str       | No       | None    | Type of fallback configuration (translated_address or interface_address) |
| `fallback_address`   | List[str] | No       | None    | Fallback IP addresses (when fallback_type is translated_address) |
| `fallback_interface` | str       | No       | None    | Fallback interface name (when fallback_type is interface_address) |
| `fallback_ip`        | str       | No       | None    | Fallback IP address (when fallback_type is interface_address)    |

### StaticIp

Static IP translation configuration.

| Attribute            | Type          | Required | Default | Description                                |
|----------------------|---------------|----------|---------|--------------------------------------------|
| `translated_address` | str           | Yes      | None    | Translated IP address                      |
| `bi_directional`     | BiDirectional | No       | None    | Enable bi-directional translation (yes/no) |

### DestinationTranslation

Destination translation configuration.

| Attribute            | Type       | Required | Default | Description                           |
|----------------------|------------|----------|---------|---------------------------------------|
| `translated_address` | str        | No       | None    | Translated destination IP address     |
| `translated_port`    | int        | No       | None    | Translated destination port (1-65535) |
| `dns_rewrite`        | DnsRewrite | No       | None    | DNS rewrite configuration             |

### DnsRewrite

DNS rewrite configuration.

| Attribute   | Type                | Required | Default | Description           |
|-------------|---------------------|----------|---------|-----------------------|
| `direction` | DnsRewriteDirection | Yes      | None    | DNS rewrite direction |

### NatRuleMoveModel

Model for NAT rule move operations.

| Attribute          | Type               | Required | Default | Description                                         |
|--------------------|--------------------|----------|---------|-----------------------------------------------------|
| `destination`      | NatMoveDestination | Yes      | None    | Where to move the rule (top, bottom, before, after) |
| `rulebase`         | NatRulebase        | Yes      | None    | Which rulebase to use (pre or post)                 |
| `destination_rule` | UUID               | No*      | None    | UUID of the reference rule for before/after moves   |

\* Required when destination is `before` or `after`; must not be provided when destination is `top` or `bottom`

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a NAT rule (`NatRuleCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When multiple source translation types are provided in `SourceTranslation` (must be exactly one of `dynamic_ip_and_port`, `dynamic_ip`, or `static_ip`).
- When both `translated_address` and `interface_address` are provided (or neither) in `DynamicIpAndPort`.
- When bi-directional static NAT (`bi_directional="yes"`) is used together with destination translation in the same rule.
- When DNS rewrite is used with NAT64 rule type.
- When the NAT rule name does not match the required pattern `^[a-zA-Z0-9_ \.-]+$`.
- When list fields (`from_`, `to_`, `source`, `destination`, `tag`) contain duplicate values.
- When container identifiers (folder, snippet, device) do not match the pattern `^[a-zA-Z\d\-_. ]+$` or exceed 64 characters.
- When `translated_port` is outside the valid range of 1-65535.
- When `destination_rule` is missing for `before`/`after` moves in `NatRuleMoveModel`.
- When `destination_rule` is provided for `top`/`bottom` moves in `NatRuleMoveModel`.

## Model Validators

### Field Validators in `NatRuleBaseModel`

- **ensure_list_of_strings**:
  Applied to `from_`, `to_`, `source`, `destination`, and `tag` fields. Converts a single string value to a list containing that string. Raises `ValueError` if the value is not a string or a list of strings.

- **ensure_unique_items**:
  Applied to `from_`, `to_`, `source`, `destination`, and `tag` fields. Ensures all items in the list are unique. Raises `ValueError` if duplicate items are found.

### Model Validators in `NatRuleBaseModel`

- **validate_nat64_dns_rewrite_compatibility**:
  Ensures that DNS rewrite is not used with NAT64 type rules. If `nat_type` is `nat64` and `destination_translation.dns_rewrite` is set, raises a `ValueError`.

- **validate_bidirectional_nat_compatibility**:
  Ensures that bi-directional static NAT is not used together with destination translation. If `source_translation.static_ip.bi_directional` is `"yes"` and `destination_translation` is also set, raises a `ValueError`.

### Field Validators in `StaticIp`

- **convert_boolean_to_enum**:
  Applied to the `bi_directional` field. Converts boolean values to the corresponding `BiDirectional` enum value (`True` becomes `BiDirectional.YES`, `False` becomes `BiDirectional.NO`).

### Model Validators in `DynamicIpAndPort`

- **validate_dynamic_ip_and_port**:
  Ensures that exactly one of `translated_address` or `interface_address` is provided. Raises `ValueError` if both are provided or neither is provided.

### Model Validators in `SourceTranslation`

- **validate_source_translation**:
  Ensures that exactly one source translation type is provided among `dynamic_ip_and_port`, `dynamic_ip`, and `static_ip`. Raises `ValueError` if zero or more than one type is set.

### Container Validation in `NatRuleCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

### Move Configuration Validation in `NatRuleMoveModel`

- **validate_move_configuration**:
  Validates the move configuration for NAT rule reordering. When `destination` is `before` or `after`, `destination_rule` must be provided. When `destination` is `top` or `bottom`, `destination_rule` must not be provided. Raises `ValueError` if these constraints are violated.

## Usage Examples

### Creating a Basic Source NAT Rule (Dynamic IP and Port)

#### Using a Dictionary

```python
from scm.models.network.nat_rules import NatRuleCreateModel

nat_rule_data = {
    "name": "outbound-snat",
    "description": "Dynamic IP/Port source NAT for outbound traffic",
    "folder": "Texas",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "service": "any",
    "source_translation": {
        "dynamic_ip_and_port": {
            "translated_address": ["192.168.1.100", "192.168.1.101"]
        }
    }
}

# Validate and create model instance
nat_rule = NatRuleCreateModel(**nat_rule_data)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    SourceTranslation,
    DynamicIpAndPort,
)

# Create the source translation configuration
source_translation = SourceTranslation(
    dynamic_ip_and_port=DynamicIpAndPort(
        translated_address=["192.168.1.100", "192.168.1.101"]
    )
)

# Create the NAT rule
nat_rule = NatRuleCreateModel(
    name="outbound-snat",
    description="Dynamic IP/Port source NAT for outbound traffic",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    service="any",
    source_translation=source_translation,
    folder="Texas",
)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a NAT Rule with Interface Address Translation

```python
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    SourceTranslation,
    DynamicIpAndPort,
    InterfaceAddress,
)

# Create interface address configuration
interface_addr = InterfaceAddress(
    interface="ethernet1/1",
    ip="192.168.1.1",
)

# Create the NAT rule using interface address
nat_rule = NatRuleCreateModel(
    name="interface-snat",
    description="Source NAT using interface address",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    source_translation=SourceTranslation(
        dynamic_ip_and_port=DynamicIpAndPort(
            interface_address=interface_addr
        )
    ),
    folder="Texas",
)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Destination NAT Rule

```python
from scm.models.network.nat_rules import NatRuleCreateModel

# Create destination NAT rule (port forwarding)
dnat_config = {
    "name": "web-server-dnat",
    "description": "Port forwarding to internal web server",
    "folder": "Texas",
    "from": ["untrust"],
    "to": ["trust"],
    "source": ["any"],
    "destination": ["203.0.113.10"],
    "service": "tcp-80",
    "destination_translation": {
        "translated_address": "10.0.0.100",
        "translated_port": 8080
    }
}

nat_rule = NatRuleCreateModel(**dnat_config)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Static IP NAT Rule with Bi-directional Support

```python
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    SourceTranslation,
    StaticIp,
    BiDirectional,
)

# Create a bi-directional static NAT rule
nat_rule = NatRuleCreateModel(
    name="server-static-nat",
    description="Bi-directional static NAT for server",
    from_=["any"],
    to_=["any"],
    source=["10.0.0.10"],
    destination=["any"],
    source_translation=SourceTranslation(
        static_ip=StaticIp(
            translated_address="192.168.1.100",
            bi_directional=BiDirectional.YES,
        )
    ),
    folder="Texas",
)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Destination NAT Rule with DNS Rewrite

```python
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    DestinationTranslation,
    DnsRewrite,
    DnsRewriteDirection,
)

# Create a destination NAT rule with DNS rewrite
nat_rule = NatRuleCreateModel(
    name="dns-rewrite-dnat",
    description="Destination NAT with DNS rewrite",
    from_=["untrust"],
    to_=["dmz"],
    source=["any"],
    destination=["203.0.113.50"],
    service="tcp-443",
    destination_translation=DestinationTranslation(
        translated_address="10.0.2.50",
        translated_port=443,
        dns_rewrite=DnsRewrite(
            direction=DnsRewriteDirection.REVERSE,
        ),
    ),
    folder="Texas",
)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Dynamic IP NAT Rule with Fallback

```python
from scm.models.network.nat_rules import (
    NatRuleCreateModel,
    SourceTranslation,
    DynamicIp,
)

# Create a dynamic IP NAT rule with fallback
nat_rule = NatRuleCreateModel(
    name="dynamic-ip-with-fallback",
    description="Dynamic IP NAT with translated address fallback",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    source_translation=SourceTranslation(
        dynamic_ip=DynamicIp(
            translated_address=["192.168.1.100", "192.168.1.101"],
            fallback_type="translated_address",
            fallback_address=["192.168.2.100", "192.168.2.101"],
        )
    ),
    folder="Texas",
)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a NAT Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing NAT rule
existing = client.nat_rule.fetch(name="outbound-snat", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated dynamic IP/Port source NAT"
existing.source = ["10.0.0.0/24", "10.0.1.0/24"]
existing.disabled = False

# Update the source translation addresses
existing.source_translation = {
    "dynamic_ip_and_port": {
        "translated_address": ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
    }
}

# Pass modified object to update()
updated = client.nat_rule.update(existing)
print(f"Updated NAT rule: {updated.name}")
```

### Moving a NAT Rule

```python
from scm.models.network.nat_rules import NatRuleMoveModel, NatMoveDestination, NatRulebase

# Move a NAT rule to the top of the pre-rulebase
move_top = NatRuleMoveModel(
    destination=NatMoveDestination.TOP,
    rulebase=NatRulebase.PRE,
)
payload = move_top.model_dump(exclude_unset=True)
print(payload)

# Move a NAT rule before another rule
move_before = NatRuleMoveModel(
    destination=NatMoveDestination.BEFORE,
    rulebase=NatRulebase.PRE,
    destination_rule="987fcdeb-51d3-a456-426655440000",
)
payload = move_before.model_dump(exclude_unset=True)
print(payload)
```

### Creating a NAT Rule with Tags

```python
from scm.models.network.nat_rules import NatRuleCreateModel

nat_rule_data = {
    "name": "tagged-nat-rule",
    "description": "NAT rule with tags for organization",
    "folder": "Texas",
    "tag": ["Production", "Web-Traffic", "Outbound"],
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "nat_type": "ipv4",
    "source_translation": {
        "dynamic_ip_and_port": {
            "translated_address": ["203.0.113.100"]
        }
    }
}

nat_rule = NatRuleCreateModel(**nat_rule_data)
payload = nat_rule.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
