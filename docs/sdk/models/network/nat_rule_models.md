# NAT Rule Models

## Overview {#Overview}

[comment]: # "Add anchors for the model types"
<span id="natrulecreatemodel"></span>
<span id="natruleupdatemodel"></span>
<span id="natruleresponsemodel"></span>
<span id="natrrulemovemodel"></span>
<span id="sourcetranslation"></span>
<span id="dynamicipandport"></span>
<span id="dynamicip"></span>
<span id="staticip"></span>
<span id="destinationtranslation"></span>

The NAT Rule models provide a structured way to represent and validate NAT rule configuration data for Palo Alto Networks' Strata Cloud Manager. These models support configuration of source and destination address translation with various options including static IP mappings, dynamic IP and port allocation, and DNS rewrite functionality. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute                    | Type                   | Required      | Default    | Description                                               |
|------------------------------|------------------------|---------------|------------|-----------------------------------------------------------|
| name                         | str                    | Yes           | None       | The name of the NAT rule. Max 63 chars, must match pattern: `^[a-zA-Z0-9_ \.-]+$` |
| description                  | str                    | No            | None       | Description of the NAT rule. Max length: 1023 chars        |
| tag                          | List[str]              | No            | []         | Tags associated with the NAT rule                         |
| disabled                     | bool                   | No            | False      | Whether the NAT rule is disabled                          |
| nat_type                     | NatType                | No            | ipv4       | Type of NAT operation (ipv4, nat64, nptv6)               |
| from_ (alias: from)          | List[str]              | No            | ["any"]    | Source zones for the NAT rule                            |
| to_ (alias: to)              | List[str]              | No            | ["any"]    | Destination zones for the NAT rule                       |
| to_interface                 | str                    | No            | None       | Destination interface of the original packet              |
| source                       | List[str]              | No            | ["any"]    | Source addresses for the NAT rule                        |
| destination                  | List[str]              | No            | ["any"]    | Destination addresses for the NAT rule                   |
| service                      | str                    | No            | "any"      | The TCP/UDP service associated with the NAT rule          |
| source_translation           | SourceTranslation      | No            | None       | Configuration for source translation                      |
| destination_translation      | DestinationTranslation | No            | None       | Configuration for destination translation                 |
| active_active_device_binding | str                    | No            | None       | Active/Active device binding                             |
| folder                       | str                    | Yes*          | None       | Folder where NAT rule is defined. Max length: 64 chars   |
| snippet                      | str                    | Yes*          | None       | Snippet where NAT rule is defined. Max length: 64 chars  |
| device                       | str                    | Yes*          | None       | Device where NAT rule is defined. Max length: 64 chars   |
| id                           | UUID                   | Yes**         | None       | UUID of the NAT rule (response/update only)              |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response and update models

### Source Translation Attributes

The source translation configuration follows a discriminated union pattern where exactly one translation type must be provided:

| Attribute           | Type            | Required | Description                                       |
|---------------------|-----------------|----------|---------------------------------------------------|
| dynamic_ip_and_port | DynamicIpAndPort| No*      | Dynamic IP and port translation configuration     |
| dynamic_ip          | DynamicIp       | No*      | Dynamic IP translation configuration              |
| static_ip           | StaticIp        | No*      | Static IP translation configuration               |

\* Exactly one of these translation types must be provided if source_translation is specified

### DynamicIpAndPort Attributes

| Attribute           | Type              | Required | Description                                     |
|---------------------|-------------------|----------|-------------------------------------------------|
| translated_address  | List[str]         | No*      | Translated source IP addresses                  |
| interface_address   | InterfaceAddress  | No*      | Interface configuration for translation         |

\* Exactly one of translated_address or interface_address must be provided

### DynamicIp Attributes

| Attribute           | Type            | Required | Description                                                           |
|---------------------|-----------------|----------|-----------------------------------------------------------------------|
| translated_address  | List[str]       | Yes      | Translated IP addresses                                               |
| fallback_type       | str             | No       | Type of fallback (translated_address or interface_address)            |
| fallback_address    | List[str]       | No       | Fallback IP addresses (when fallback_type is translated_address)      |
| fallback_interface  | str             | No       | Fallback interface name (when fallback_type is interface_address)     |
| fallback_ip         | str             | No       | Fallback IP address (when fallback_type is interface_address)         |

### StaticIp Attributes

| Attribute           | Type  | Required | Description                                                |
|---------------------|-------|----------|------------------------------------------------------------|
| translated_address  | str   | Yes      | Translated IP address                                      |
| bi_directional      | str   | No       | Enable bi-directional translation ('yes' or 'no')         |

### Destination Translation Attributes

| Attribute           | Type       | Required | Description                                  |
|---------------------|------------|----------|----------------------------------------------|
| translated_address  | str        | No       | Translated destination IP address            |
| translated_port     | int        | No       | Translated destination port (1-65535)        |
| dns_rewrite         | DnsRewrite | No       | DNS rewrite configuration                    |

## Exceptions

The NAT Rule models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
  - When multiple container types (folder/snippet/device) are specified for create operations
  - When no container type is specified for create operations
  - When multiple source translation types are provided (must be exactly one if source_translation is specified)
  - When both translated_address and interface_address are provided (or neither) for dynamic_ip_and_port
  - When bi-directional static NAT is used with destination translation in the same rule
  - When DNS rewrite is used with NAT64 rule type
  - When name pattern validation fails
  - When list fields contain duplicate values
  - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.network import NatRuleCreateModel

# This will raise a validation error
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
from scm.models.network import NatRuleCreateModel, SourceTranslation

# This will raise a validation error
try:
    source_translation = SourceTranslation(
        dynamic_ip_and_port={
            "translated_address": ["192.168.1.1"]
        },
        dynamic_ip={  # Can't specify multiple translation types
            "translated_address": ["192.168.1.2"]
        }
    )
    
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source_translation=source_translation
    )
except ValueError as e:
    print(e)  # "Exactly one source translation type must be provided"
```

### DynamicIpAndPort Validation

For dynamic IP and port translation, exactly one of translated_address or interface_address must be provided:

```python
from scm.models.network import NatRuleCreateModel, SourceTranslation, DynamicIpAndPort

# This will raise a validation error
try:
    source_translation = SourceTranslation(
        dynamic_ip_and_port=DynamicIpAndPort(
            # Neither translated_address nor interface_address provided
        )
    )
    
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source_translation=source_translation
    )
except ValueError as e:
    print(e)  # "Either translated_address or interface_address must be provided"

# This will also raise a validation error
try:
    source_translation = SourceTranslation(
        dynamic_ip_and_port=DynamicIpAndPort(
            translated_address=["192.168.1.1"],
            interface_address={  # Can't provide both
                "interface": "ethernet1/1"
            }
        )
    )
    
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source_translation=source_translation
    )
except ValueError as e:
    print(e)  # "Either translated_address or interface_address must be provided, not both"
```

### Bidirectional NAT Compatibility Validation

Bi-directional static NAT cannot be used with destination translation:

```python
from scm.models.network import (
    NatRuleCreateModel, 
    SourceTranslation, 
    StaticIp,
    DestinationTranslation
)

# This will raise a validation error
try:
    source_translation = SourceTranslation(
        static_ip=StaticIp(
            translated_address="192.168.1.100",
            bi_directional="yes"
        )
    )
    
    destination_translation = DestinationTranslation(
        translated_address="192.168.2.100"  # Can't use with bi-directional static NAT
    )
    
    nat_rule = NatRuleCreateModel(
        name="invalid-rule",
        folder="Texas",
        source_translation=source_translation,
        destination_translation=destination_translation
    )
except ValueError as e:
    print(e)  # "Bi-directional static NAT cannot be used with destination translation"
```

## Usage Examples

### Creating a Basic Source NAT Rule (Dynamic IP and Port)

```python
from scm.client import ScmClient
from scm.models.network import (
    NatRuleCreateModel, 
    SourceTranslation, 
    DynamicIpAndPort
)

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
    "folder": "NAT Policies",
    "from_": ["trust"],
    "to_": ["untrust"],
    "source": ["10.0.0.0/24"],
    "destination": ["any"],
    "source_translation": {
        "dynamic_ip_and_port": {
            "translated_address": ["192.168.1.100", "192.168.1.101"]
        }
    }
}

# Create the NAT rule using the client
response = client.nat_rule.create(snat_dict)
print(f"Created NAT rule: {response.name}")

# Using model directly
source_translation = SourceTranslation(
    dynamic_ip_and_port=DynamicIpAndPort(
        translated_address=["192.168.1.100", "192.168.1.101"]
    )
)

snat_rule = NatRuleCreateModel(
    name="outbound-snat-2",
    description="Another dynamic IP/Port source NAT for outbound traffic",
    folder="NAT Policies",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    source_translation=source_translation
)

payload = snat_rule.model_dump(exclude_unset=True)
response = client.nat_rule.create(payload)
print(f"Created NAT rule with ID: {response.id}")
```

### Creating a Destination NAT Rule

```python
from scm.models.network import (
    NatRuleCreateModel, 
    DestinationTranslation
)

# Create destination NAT rule (port forwarding)
destination_translation = DestinationTranslation(
    translated_address="10.0.0.100",
    translated_port=8080
)

dnat_rule = NatRuleCreateModel(
    name="web-server-dnat",
    description="Port forwarding to internal web server",
    folder="NAT Policies",
    from_=["untrust"],
    to_=["trust"],
    source=["any"],
    destination=["203.0.113.10"],
    service="tcp-80",
    destination_translation=destination_translation
)

payload = dnat_rule.model_dump(exclude_unset=True)
response = client.nat_rule.create(payload)
print(f"Created destination NAT rule: {response.name}")
```

### Creating a Static IP NAT Rule with Bi-directional Support

```python
from scm.models.network import (
    NatRuleCreateModel, 
    SourceTranslation, 
    StaticIp
)

# Create a bi-directional static NAT rule
source_translation = SourceTranslation(
    static_ip=StaticIp(
        translated_address="192.168.1.100",
        bi_directional="yes"  # Enable bi-directional translation
    )
)

static_nat_rule = NatRuleCreateModel(
    name="server-static-nat",
    description="Bi-directional static NAT for server",
    folder="NAT Policies",
    from_=["any"],
    to_=["any"],
    source=["10.0.0.10"],
    destination=["any"],
    source_translation=source_translation
)

payload = static_nat_rule.model_dump(exclude_unset=True)
response = client.nat_rule.create(payload)
print(f"Created static NAT rule: {response.name}")
```

### Creating a Dynamic IP Source NAT Rule with Fallback

```python
from scm.models.network import (
    NatRuleCreateModel, 
    SourceTranslation, 
    DynamicIp
)

# Create a dynamic IP NAT rule with fallback
source_translation = SourceTranslation(
    dynamic_ip=DynamicIp(
        translated_address=["192.168.1.100", "192.168.1.101"],
        fallback_type="translated_address",
        fallback_address=["192.168.2.100"]
    )
)

dynamic_ip_rule = NatRuleCreateModel(
    name="outbound-dynamic-ip",
    description="Dynamic IP source NAT with fallback",
    folder="NAT Policies",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    source_translation=source_translation
)

payload = dynamic_ip_rule.model_dump(exclude_unset=True)
response = client.nat_rule.create(payload)
print(f"Created dynamic IP NAT rule: {response.name}")
```

### Creating a NAT Rule with Interface Address

```python
from scm.models.network import (
    NatRuleCreateModel, 
    SourceTranslation, 
    DynamicIpAndPort,
    InterfaceAddress
)

# Create a NAT rule using interface address
interface_address = InterfaceAddress(
    interface="ethernet1/1"
)

source_translation = SourceTranslation(
    dynamic_ip_and_port=DynamicIpAndPort(
        interface_address=interface_address
    )
)

interface_rule = NatRuleCreateModel(
    name="interface-snat",
    description="Source NAT using interface address",
    folder="NAT Policies",
    from_=["trust"],
    to_=["untrust"],
    source=["10.0.0.0/24"],
    destination=["any"],
    source_translation=source_translation
)

payload = interface_rule.model_dump(exclude_unset=True)
response = client.nat_rule.create(payload)
print(f"Created interface NAT rule: {response.name}")
```

### Moving a NAT Rule

```python
from scm.models.network import NatRuleMoveModel

# Move a NAT rule to the top of the rulebase
move_top = NatRuleMoveModel(
    destination="top",
    rulebase="pre"
)

rule_id = "123e4567-e89b-12d3-a456-426655440000"
client.nat_rule.move(rule_id, move_top.model_dump())
print(f"Moved rule {rule_id} to the top")

# Move a NAT rule before another rule
move_before = NatRuleMoveModel(
    destination="before",
    rulebase="pre",
    destination_rule="987fcdeb-51d3-a456-426655440000"
)

client.nat_rule.move(rule_id, move_before.model_dump())
print(f"Moved rule {rule_id} before the specified rule")
```

### Updating a NAT Rule

```python
from scm.models.network import (
    NatRuleUpdateModel, 
    SourceTranslation, 
    DynamicIpAndPort
)

# Update an existing NAT rule
source_translation = SourceTranslation(
    dynamic_ip_and_port=DynamicIpAndPort(
        translated_address=["192.168.1.100", "192.168.1.101", "192.168.1.102"]  # Added address
    )
)

update_rule = NatRuleUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="outbound-snat",
    description="Updated dynamic IP/Port source NAT",
    folder="NAT Policies",
    source=["10.0.0.0/24", "10.0.1.0/24"],  # Added subnet
    source_translation=source_translation,
    disabled=False  # Ensure rule is enabled
)

payload = update_rule.model_dump(exclude_unset=True)
response = client.nat_rule.update(payload)
print(f"Updated NAT rule: {response.name}")
```
