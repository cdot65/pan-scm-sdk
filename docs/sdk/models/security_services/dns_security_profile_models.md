# DNS Security Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Enum Types](#enum-types)
4. [Supporting Models](#supporting-models)
5. [Exceptions](#exceptions)
6. [Model Validators](#model-validators)
7. [Usage Examples](#usage-examples)

## Overview {#Overview}

The DNS Security Profile models provide a structured way to manage DNS Security profiles in Palo Alto Networks' Strata Cloud Manager. These models support configuration of profiles that protect against DNS-based threats, including domain filtering and DNS sinkhole operations. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `DNSSecurityProfileBaseModel`: Base model with fields common to all profile operations
- `DNSSecurityProfileCreateModel`: Model for creating new DNS security profiles
- `DNSSecurityProfileUpdateModel`: Model for updating existing DNS security profiles
- `DNSSecurityProfileResponseModel`: Response model for DNS security profile operations
- `BotnetDomainsModel`: Model for botnet domains configuration
- `DNSSecurityCategoryEntryModel`: Model for DNS security category entries
- `ListEntryBaseModel`: Model for custom domain list entries
- `SinkholeSettingsModel`: Model for sinkhole configuration
- `WhitelistEntryModel`: Model for whitelist entries

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### DNSSecurityProfileBaseModel

| Attribute        | Type              | Required | Default | Description                                                      |
|------------------|-------------------|----------|---------|------------------------------------------------------------------|
| name             | str               | Yes      | None    | Profile name. Pattern: `^[a-zA-Z0-9][a-zA-Z0-9_\-\.\s]*$`        |
| description      | str               | No       | None    | Description of the profile                                       |
| botnet_domains   | BotnetDomainsModel| No       | None    | Botnet domains settings                                          |
| folder           | str               | No**     | None    | Folder location. Max 64 chars                                    |
| snippet          | str               | No**     | None    | Snippet location. Max 64 chars                                   |
| device           | str               | No**     | None    | Device location. Max 64 chars                                    |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### DNSSecurityProfileCreateModel

Inherits all fields from `DNSSecurityProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### DNSSecurityProfileUpdateModel

Extends `DNSSecurityProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

### DNSSecurityProfileResponseModel

Extends `DNSSecurityProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the profile |

## Enum Types

### ActionEnum

Defines the allowed actions for DNS security categories:

| Value      | Description         |
|------------|---------------------|
| `default`  | Use default action  |
| `allow`    | Allow the traffic   |
| `block`    | Block the traffic   |
| `sinkhole` | Sinkhole the domain |

### LogLevelEnum

Defines the log levels:

| Value           | Description             |
|-----------------|-------------------------|
| `default`       | Default log level       |
| `none`          | No logging              |
| `low`           | Low priority logging    |
| `informational` | Informational logging   |
| `medium`        | Medium priority logging |
| `high`          | High priority logging   |
| `critical`      | Critical priority logging |

### PacketCaptureEnum

Defines the packet capture options:

| Value              | Description              |
|--------------------|--------------------------|
| `disable`          | Disable packet capture   |
| `single-packet`    | Capture a single packet  |
| `extended-capture` | Extended packet capture  |

### IPv4AddressEnum

Defines the allowed IPv4 sinkhole addresses:

| Value                     | Description                |
|---------------------------|----------------------------|
| `pan-sinkhole-default-ip` | Default sinkhole IP        |
| `127.0.0.1`               | Localhost                  |

### IPv6AddressEnum

Defines the allowed IPv6 sinkhole addresses:

| Value | Description |
|-------|-------------|
| `::1` | Localhost   |

## Supporting Models

### BotnetDomainsModel

| Attribute                 | Type                                | Required | Default | Description                    |
|---------------------------|-------------------------------------|----------|---------|--------------------------------|
| dns_security_categories   | List[DNSSecurityCategoryEntryModel] | No       | None    | DNS security categories        |
| lists                     | List[ListEntryBaseModel]            | No       | None    | Lists of DNS domains           |
| sinkhole                  | SinkholeSettingsModel               | No       | None    | DNS sinkhole settings          |
| whitelist                 | List[WhitelistEntryModel]           | No       | None    | DNS security overrides         |

### DNSSecurityCategoryEntryModel

| Attribute      | Type              | Required | Default   | Description                 |
|----------------|-------------------|----------|-----------|-----------------------------|
| name           | str               | Yes      | None      | DNS Security Category Name  |
| action         | ActionEnum        | No       | default   | Action to be taken          |
| log_level      | LogLevelEnum      | No       | default   | Log level                   |
| packet_capture | PacketCaptureEnum | No       | None      | Packet capture setting      |

### ListEntryBaseModel

| Attribute      | Type                   | Required | Default | Description            |
|----------------|------------------------|----------|---------|------------------------|
| name           | str                    | Yes      | None    | List name              |
| packet_capture | PacketCaptureEnum      | No       | None    | Packet capture setting |
| action         | ListActionRequestModel | Yes      | None    | Action                 |

### SinkholeSettingsModel

| Attribute      | Type            | Required | Default | Description               |
|----------------|-----------------|----------|---------|---------------------------|
| ipv4_address   | IPv4AddressEnum | Yes      | None    | IPv4 address for sinkhole |
| ipv6_address   | IPv6AddressEnum | Yes      | None    | IPv6 address for sinkhole |

### WhitelistEntryModel

| Attribute   | Type | Required | Default | Description                          |
|-------------|------|----------|---------|--------------------------------------|
| name        | str  | Yes      | None    | DNS domain or FQDN to be whitelisted |
| description | str  | No       | None    | Description                          |

## Exceptions

The DNS Security Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified for create operations
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded
    - When invalid action or log level values are provided
    - When invalid packet capture settings are provided
    - When multiple actions are specified in list entry action field

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

```python
from scm.models.security import DNSSecurityProfileCreateModel

# Error: multiple containers specified
try:
    profile = DNSSecurityProfileCreateModel(
        name="dns-security-profile",
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Error: no container specified
try:
    profile = DNSSecurityProfileCreateModel(
        name="dns-security-profile"
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

### Action Validation

For list entries, exactly one action type must be specified:

```python
from scm.models.security import ListActionRequestModel

# Error: multiple actions specified
try:
    action = ListActionRequestModel(root={
        "alert": {},
        "block": {}  # Can't specify multiple actions
    })
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."

# Correct way to specify an action
action = ListActionRequestModel(root={"block": {}})
```

## Usage Examples

### Creating a DNS Security Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile_dict = {
    "name": "dns-sec-profile",
    "description": "DNS security profile for production",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "pan-dns-sec-malware",
                "action": "block",
                "log_level": "critical",
                "packet_capture": "extended-capture"
            },
            {
                "name": "pan-dns-sec-phishing",
                "action": "sinkhole",
                "log_level": "high",
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        },
        "whitelist": [
            {"name": "trusted-domain.com", "description": "Trusted domain"}
        ]
    },
    "folder": "Texas"
}

response = client.dns_security_profile.create(profile_dict)
print(f"Created profile: {response.name}")
```

### Creating a Profile with Multiple Categories

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile_dict = {
    "name": "comprehensive-dns-profile",
    "description": "Comprehensive DNS security profile",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "pan-dns-sec-cc",
                "action": "block",
                "log_level": "critical"
            },
            {
                "name": "pan-dns-sec-malware",
                "action": "sinkhole",
                "log_level": "high"
            },
            {
                "name": "pan-dns-sec-phishing",
                "action": "block",
                "log_level": "high"
            },
            {
                "name": "pan-dns-sec-grayware",
                "action": "alert",
                "log_level": "medium"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        }
    },
    "folder": "Texas"
}

response = client.dns_security_profile.create(profile_dict)
print(f"Created profile with {len(response.botnet_domains.dns_security_categories)} categories")
```

### Updating a DNS Security Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.dns_security_profile.fetch(name="dns-sec-profile", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated DNS security profile"

# Add a new category to the existing list
if existing.botnet_domains and existing.botnet_domains.dns_security_categories:
    existing.botnet_domains.dns_security_categories.append({
        "name": "pan-dns-sec-recent",
        "action": "alert",
        "log_level": "medium"
    })

# Add whitelist entry if needed
if existing.botnet_domains:
    if existing.botnet_domains.whitelist is None:
        existing.botnet_domains.whitelist = []
    existing.botnet_domains.whitelist.append({
        "name": "new-trusted.com",
        "description": "Newly trusted domain"
    })

# Pass modified object to update()
updated = client.dns_security_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
