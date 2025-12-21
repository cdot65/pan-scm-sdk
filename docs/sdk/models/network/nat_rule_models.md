# NAT Rule Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Source Translation Models](#source-translation-models)
5. [Destination Translation Models](#destination-translation-models)
6. [Move Model](#move-model)
7. [Exceptions](#exceptions)
8. [Model Validators](#model-validators)
9. [Usage Examples](#usage-examples)

## Overview {#Overview}

The NAT Rule models provide a structured way to represent and validate NAT rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models support configuration of source and destination address translation with various options including static IP mappings, dynamic IP and port allocation, and DNS rewrite functionality. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `NatRuleBaseModel`: Base model with fields common to all NAT rule operations
- `NatRuleCreateModel`: Model for creating new NAT rules
- `NatRuleUpdateModel`: Model for updating existing NAT rules
- `NatRuleResponseModel`: Response model for NAT rule operations
- `NatRuleMoveModel`: Model for moving/reordering NAT rules
- `SourceTranslation`: Source translation configuration model
- `DynamicIpAndPort`: Dynamic IP and port translation model
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

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

| Attribute                    | Type                   | Required | Default   | Description                                               |
|------------------------------|------------------------|----------|-----------|-----------------------------------------------------------|
| `name`                       | str                    | Yes      | None      | The name of the NAT rule. Pattern: `^[a-zA-Z0-9_ \.-]+$`  |
| `id`                         | UUID                   | Yes*     | None      | UUID of the NAT rule (*response/update only)              |
| `description`                | str                    | No       | None      | Description of the NAT rule                               |
| `tag`                        | List[str]              | No       | []        | Tags associated with the NAT rule                         |
| `disabled`                   | bool                   | No       | False     | Whether the NAT rule is disabled                          |
| `nat_type`                   | NatType                | No       | ipv4      | Type of NAT operation (ipv4, nat64, nptv6)                |
| `from_` (alias: from)        | List[str]              | No       | ["any"]   | Source zones for the NAT rule                             |
| `to_` (alias: to)            | List[str]              | No       | ["any"]   | Destination zones for the NAT rule                        |
| `to_interface`               | str                    | No       | None      | Destination interface of the original packet              |
| `source`                     | List[str]              | No       | ["any"]   | Source addresses for the NAT rule                         |
| `destination`                | List[str]              | No       | ["any"]   | Destination addresses for the NAT rule                    |
| `service`                    | str                    | No       | "any"     | The TCP/UDP service associated with the NAT rule          |
| `source_translation`         | SourceTranslation      | No       | None      | Configuration for source translation                      |
| `destination_translation`    | DestinationTranslation | No       | None      | Configuration for destination translation                 |
| `active_active_device_binding` | str                  | No       | None      | Active/Active device binding                              |
| `folder`                     | str                    | No**     | None      | Folder where NAT rule is defined. Max 64 chars            |
| `snippet`                    | str                    | No**     | None      | Snippet where NAT rule is defined. Max 64 chars           |
| `device`                     | str                    | No**     | None      | Device where NAT rule is defined. Max 64 chars            |

\* Only required for response and update models
\** Exactly one container type (folder/snippet/device) must be provided for create operations

## Enum Types

### NatType

Defines the NAT types supported by the system:

| Value   | Description                        |
|---------|------------------------------------|
| `ipv4`  | IPv4 NAT (default)                 |
| `nat64` | NAT64 translation                  |
| `nptv6` | NPTv6 translation                  |

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

| Value  | Description              |
|--------|--------------------------|
| `pre`  | Pre-rulebase (default)   |
| `post` | Post-rulebase            |

### DistributionMethod

Defines distribution methods for dynamic destination translation:

| Value            | Description                   |
|------------------|-------------------------------|
| `round-robin`    | Round-robin distribution      |
| `source-ip-hash` | Source IP hash distribution   |
| `ip-modulo`      | IP modulo distribution        |
| `ip-hash`        | IP hash distribution          |
| `least-sessions` | Least sessions distribution   |

### DnsRewriteDirection

Defines DNS rewrite direction options:

| Value     | Description              |
|-----------|--------------------------|
| `reverse` | Reverse DNS rewrite      |
| `forward` | Forward DNS rewrite      |

### BiDirectional

Defines bi-directional translation options:

| Value | Description                          |
|-------|--------------------------------------|
| `yes` | Enable bi-directional translation    |
| `no`  | Disable bi-directional translation   |

## Source Translation Models

### SourceTranslation Model

Main container for source translation configurations. Exactly one translation type must be provided:

| Attribute           | Type            | Required | Default | Description                                   |
|---------------------|-----------------|----------|---------|-----------------------------------------------|
| `dynamic_ip_and_port` | DynamicIpAndPort | No*    | None    | Dynamic IP and port translation configuration |
| `dynamic_ip`        | DynamicIp       | No*      | None    | Dynamic IP translation configuration          |
| `static_ip`         | StaticIp        | No*      | None    | Static IP translation configuration           |

\* Exactly one of these translation types must be provided

### DynamicIpAndPort Model

Dynamic IP and port (PAT) translation configuration:

| Attribute           | Type              | Required | Default | Description                                     |
|---------------------|-------------------|----------|---------|-------------------------------------------------|
| `type`              | Literal           | No       | "dynamic_ip_and_port" | Type identifier             |
| `translated_address`| List[str]         | No*      | None    | Translated source IP addresses                  |
| `interface_address` | InterfaceAddress  | No*      | None    | Interface configuration for translation         |

\* Exactly one of `translated_address` or `interface_address` must be provided

### InterfaceAddress Model

Interface address configuration for translation:

| Attribute     | Type | Required | Default | Description                    |
|---------------|------|----------|---------|--------------------------------|
| `interface`   | str  | Yes      | None    | Interface name                 |
| `ip`          | str  | No       | None    | IP address                     |
| `floating_ip` | str  | No       | None    | Floating IP address            |

### DynamicIp Model

Dynamic IP translation configuration:

| Attribute           | Type      | Required | Default | Description                                                    |
|---------------------|-----------|----------|---------|----------------------------------------------------------------|
| `translated_address`| List[str] | Yes      | None    | Translated IP addresses                                        |
| `fallback_type`     | str       | No       | None    | Type of fallback (translated_address or interface_address)     |
| `fallback_address`  | List[str] | No       | None    | Fallback IP addresses (when fallback_type is translated_address) |
| `fallback_interface`| str       | No       | None    | Fallback interface name (when fallback_type is interface_address) |
| `fallback_ip`       | str       | No       | None    | Fallback IP address (when fallback_type is interface_address)  |

### StaticIp Model

Static IP translation configuration:

| Attribute           | Type         | Required | Default | Description                                  |
|---------------------|--------------|----------|---------|----------------------------------------------|
| `translated_address`| str          | Yes      | None    | Translated IP address                        |
| `bi_directional`    | BiDirectional| No       | None    | Enable bi-directional translation (yes/no)   |

## Destination Translation Models

### DestinationTranslation Model

Destination translation configuration:

| Attribute           | Type       | Required | Default | Description                           |
|---------------------|------------|----------|---------|---------------------------------------|
| `translated_address`| str        | No       | None    | Translated destination IP address     |
| `translated_port`   | int        | No       | None    | Translated destination port (1-65535) |
| `dns_rewrite`       | DnsRewrite | No       | None    | DNS rewrite configuration             |

### DnsRewrite Model

DNS rewrite configuration:

| Attribute   | Type               | Required | Default | Description           |
|-------------|--------------------|----------|---------|-----------------------|
| `direction` | DnsRewriteDirection| Yes      | None    | DNS rewrite direction |

## Move Model

### NatRuleMoveModel

Model for NAT rule move operations:

| Attribute         | Type              | Required | Default | Description                                           |
|-------------------|-------------------|----------|---------|-------------------------------------------------------|
| `destination`     | NatMoveDestination| Yes      | None    | Where to move the rule (top, bottom, before, after)   |
| `rulebase`        | NatRulebase       | Yes      | None    | Which rulebase to use (pre or post)                   |
| `destination_rule`| UUID              | No*      | None    | UUID of the reference rule for before/after moves     |

\* Required when destination is `before` or `after`

## Exceptions

The NAT Rule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When multiple source translation types are provided (must be exactly one)
    - When both translated_address and interface_address are provided (or neither) for dynamic_ip_and_port
    - When bi-directional static NAT is used with destination translation in the same rule
    - When DNS rewrite is used with NAT64 rule type
    - When name pattern validation fails
    - When list fields contain duplicate values
    - When field length limits are exceeded
    - When destination_rule is missing for before/after moves
    - When destination_rule is provided for top/bottom moves

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.network.nat_rules import NatRuleCreateModel

# This will raise a validation error - multiple containers
try:
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        device="fw01",  # Can't specify both folder and device
        nat_type="ipv4"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Source Translation Validation

When specifying source translation, exactly one translation type must be provided:

```python
from scm.models.network.nat_rules import SourceTranslation

# This will raise a validation error - multiple translation types
try:
    source_translation = SourceTranslation(
        dynamic_ip_and_port={"translated_address": ["192.168.1.1"]},
        dynamic_ip={"translated_address": ["192.168.1.2"]}  # Can't specify multiple
    )
except ValueError as e:
    print(e)  # "Exactly one of dynamic_ip_and_port, dynamic_ip, or static_ip must be provided"
```

### DynamicIpAndPort Validation

For dynamic IP and port translation, exactly one of translated_address or interface_address must be provided:

```python
from scm.models.network.nat_rules import DynamicIpAndPort

# This will raise a validation error - neither provided
try:
    dynamic = DynamicIpAndPort()
except ValueError as e:
    print(e)  # "Either translated_address or interface_address must be provided, but not both"

# This will raise a validation error - both provided
try:
    dynamic = DynamicIpAndPort(
        translated_address=["192.168.1.1"],
        interface_address={"interface": "ethernet1/1"}
    )
except ValueError as e:
    print(e)  # "Either translated_address or interface_address must be provided, but not both"
```

### Bidirectional NAT Compatibility Validation

Bi-directional static NAT cannot be used with destination translation:

```python
from scm.models.network.nat_rules import NatRuleCreateModel

# This will raise a validation error
try:
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source_translation={
            "static_ip": {
                "translated_address": "192.168.1.100",
                "bi_directional": "yes"
            }
        },
        destination_translation={
            "translated_address": "192.168.2.100"  # Can't use with bi-directional
        }
    )
except ValueError as e:
    print(e)  # "Bi-directional static NAT cannot be used with destination translation..."
```

### NAT64 DNS Rewrite Validation

DNS rewrite is not available with NAT64 rules:

```python
from scm.models.network.nat_rules import NatRuleCreateModel

# This will raise a validation error
try:
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        nat_type="nat64",
        destination_translation={
            "translated_address": "192.168.1.100",
            "dns_rewrite": {"direction": "reverse"}  # Not available with NAT64
        }
    )
except ValueError as e:
    print(e)  # "DNS rewrite is not available with NAT64 rules"
```

### Move Model Validation

Move configuration validation for NAT rule reordering:

```python
from scm.models.network.nat_rules import NatRuleMoveModel

# This will raise a validation error - missing destination_rule
try:
    move = NatRuleMoveModel(
        destination="before",
        rulebase="pre"
        # Missing required destination_rule
    )
except ValueError as e:
    print(e)  # "destination_rule is required when destination is 'before'"

# This will raise a validation error - destination_rule not needed
try:
    move = NatRuleMoveModel(
        destination="top",
        rulebase="pre",
        destination_rule="123e4567-e89b-12d3-a456-426655440000"  # Not allowed for top
    )
except ValueError as e:
    print(e)  # "destination_rule should not be provided when destination is 'top'"
```

## Usage Examples

### Creating a Basic Source NAT Rule (Dynamic IP and Port)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
snat_dict = {
    "name": "outbound-snat",
    "description": "Dynamic IP/Port source NAT for outbound traffic",
    "folder": "Texas",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "source_translation": {
        "dynamic_ip_and_port": {
            "translated_address": ["192.168.1.100", "192.168.1.101"]
        }
    }
}

response = client.nat_rule.create(snat_dict)
print(f"Created NAT rule: {response.name} (ID: {response.id})")
```

### Creating a Destination NAT Rule

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

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

response = client.nat_rule.create(dnat_config)
print(f"Created destination NAT rule: {response.name}")
```

### Creating a Static IP NAT Rule with Bi-directional Support

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a bi-directional static NAT rule
static_nat_config = {
    "name": "server-static-nat",
    "description": "Bi-directional static NAT for server",
    "folder": "Texas",
    "from": ["any"],
    "to": ["any"],
    "source": ["10.0.0.10"],
    "destination": ["any"],
    "source_translation": {
        "static_ip": {
            "translated_address": "192.168.1.100",
            "bi_directional": "yes"
        }
    }
}

response = client.nat_rule.create(static_nat_config)
print(f"Created static NAT rule: {response.name}")
```

### Creating a NAT Rule with Interface Address

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a NAT rule using interface address
interface_nat_config = {
    "name": "interface-snat",
    "description": "Source NAT using interface address",
    "folder": "Texas",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "source_translation": {
        "dynamic_ip_and_port": {
            "interface_address": {
                "interface": "ethernet1/1"
            }
        }
    }
}

response = client.nat_rule.create(interface_nat_config)
print(f"Created interface NAT rule: {response.name}")
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
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Move a NAT rule to the top of the rulebase
move_config = {
    "destination": "top",
    "rulebase": "pre"
}

rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.nat_rule.move(rule_id, move_config)
print(f"Moved rule {rule_id} to the top")

# Move a NAT rule before another rule
move_before_config = {
    "destination": "before",
    "rulebase": "pre",
    "destination_rule": "987fcdeb-51d3-a456-426655440000"
}

client.nat_rule.move(rule_id, move_before_config)
print(f"Moved rule {rule_id} before the specified rule")
```
