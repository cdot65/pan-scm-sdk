# DNS Security Profile Models

## Overview

The DNS Security Profile models provide a structured way to manage DNS Security profiles in Palo Alto Networks' Strata Cloud Manager. These models support configuration of profiles that protect against DNS-based threats, including domain filtering and DNS sinkhole operations. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute       | Type          | Required | Default | Description                                                                        |
|-----------------|---------------|----------|---------|------------------------------------------------------------------------------------|
| name            | str           | Yes      | None    | Name of the profile. Max length: 63 chars. Pattern: ^[a-zA-Z0-9_ \.-]+$            |
| description     | str           | No       | None    | Description of the profile. Max length: 1023 chars                                 |
| botnet_domains  | BotnetDomains | No       | None    | Botnet domain filtering configuration                                              |
| folder          | str           | No*      | None    | Folder where profile is defined. Max length: 64 chars                              |
| snippet         | str           | No*      | None    | Snippet where profile is defined. Max length: 64 chars                             |
| device          | str           | No*      | None    | Device where profile is defined. Max length: 64 chars                              |
| id              | UUID          | Yes**    | None    | UUID of the profile (response only)                                                |

\* Exactly one container type (folder/snippet/device) must be provided for create operations
\** Only required for response model

### BotnetDomains Model Attributes

| Attribute         | Type           | Required | Default | Description                                                |
|-------------------|----------------|----------|---------|------------------------------------------------------------|
| enable            | bool           | No       | None    | Enable botnet domain filtering                             |
| packet_capture    | bool           | No       | None    | Enable packet capture for botnet domains                   |
| dns_security_categories | List[DNSSecurityCategory] | No     | None  | List of DNS security categories                |
| sinkhole_ipv4     | str            | No       | None    | IPv4 sinkhole address                                      |
| sinkhole_ipv6     | str            | No       | None    | IPv6 sinkhole address                                      |
| whitelist         | List[str]      | No       | None    | List of domains to whitelist                               |

### DNSSecurityCategory Model Attributes

| Attribute         | Type           | Required | Default | Description                                                |
|-------------------|----------------|----------|---------|------------------------------------------------------------|
| name              | str            | Yes      | None    | Category name                                              |
| action            | str            | Yes      | None    | Action to take (alert, allow, block, sinkhole)             |
| log_level         | str            | No       | None    | Log level (default, disable, medium, high, critical)       |
| packet_capture    | str            | No       | None    | Packet capture setting (disable, single-packet, extended)  |

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

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.security_services import DNSSecurityProfileCreateModel

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

</div>

### Category Action Validation

The category action must be one of the allowed values:

<div class="termy">

<!-- termynal -->

```python
from scm.models.security_services import DNSSecurityCategory

# Error: invalid action
try:
    category = DNSSecurityCategory(
        name="command-and-control",
        action="invalid-action"  # Must be alert, allow, block, or sinkhole
    )
except ValueError as e:
    print(e)  # "Value error, action must be one of ['alert', 'allow', 'block', 'sinkhole']"
```

</div>

### Log Level Validation

The log level must be one of the allowed values:

<div class="termy">

<!-- termynal -->

```python
from scm.models.security_services import DNSSecurityCategory

# Error: invalid log level
try:
    category = DNSSecurityCategory(
        name="command-and-control",
        action="block",
        log_level="invalid-level"  # Must be default, disable, medium, high, or critical
    )
except ValueError as e:
    print(e)  # "Value error, log_level must be one of ['default', 'disable', 'medium', 'high', 'critical']"
```

</div>

## Usage Examples

### Creating a DNS Security Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.security_services import DNSSecurityProfile

profile_dict = {
    "name": "dns-sec-profile",
    "description": "DNS security profile for production",
    "botnet_domains": {
        "enable": True,
        "packet_capture": True,
        "dns_security_categories": [
            {
                "name": "command-and-control",
                "action": "block",
                "log_level": "critical",
                "packet_capture": "extended"
            },
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "high",
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole_ipv4": "10.0.0.1",
        "whitelist": ["trusted-domain.com"]
    },
    "folder": "Texas"
}

dns_security = DNSSecurityProfile(api_client)
response = dns_security.create(profile_dict)

# Using model directly
from scm.models.security_services import (
    DNSSecurityProfileCreateModel,
    BotnetDomains,
    DNSSecurityCategory
)

botnet_domains = BotnetDomains(
    enable=True,
    packet_capture=True,
    dns_security_categories=[
        DNSSecurityCategory(
            name="command-and-control",
            action="block",
            log_level="critical",
            packet_capture="extended"
        ),
        DNSSecurityCategory(
            name="malware",
            action="sinkhole",
            log_level="high",
            packet_capture="single-packet"
        )
    ],
    sinkhole_ipv4="10.0.0.1",
    whitelist=["trusted-domain.com"]
)

profile = DNSSecurityProfileCreateModel(
    name="dns-sec-profile",
    description="DNS security profile for production",
    botnet_domains=botnet_domains,
    folder="Texas"
)

payload = profile.model_dump(exclude_unset=True)
response = dns_security.create(payload)
```

</div>

### Creating a Profile with Multiple Categories

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
profile_dict = {
    "name": "comprehensive-dns-profile",
    "description": "Comprehensive DNS security profile",
    "botnet_domains": {
        "enable": True,
        "dns_security_categories": [
            {
                "name": "command-and-control",
                "action": "block",
                "log_level": "critical"
            },
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "high"
            },
            {
                "name": "phishing",
                "action": "block",
                "log_level": "high"
            },
            {
                "name": "grayware",
                "action": "alert",
                "log_level": "medium"
            },
            {
                "name": "dns-tunneling",
                "action": "block",
                "log_level": "high"
            }
        ],
        "sinkhole_ipv4": "10.0.0.1",
        "sinkhole_ipv6": "2001:db8::1"
    },
    "folder": "Texas"
}

response = dns_security.create(profile_dict)
```

</div>

### Updating a DNS Security Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "dns-sec-profile",
    "description": "Updated DNS security profile",
    "botnet_domains": {
        "enable": True,
        "packet_capture": False,  # Changed from True to False
        "dns_security_categories": [
            {
                "name": "command-and-control",
                "action": "block",
                "log_level": "critical",
                "packet_capture": "single-packet"  # Changed from extended to single-packet
            },
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "high",
                "packet_capture": "single-packet"
            },
            {
                "name": "phishing",  # Added new category
                "action": "block",
                "log_level": "high"
            }
        ],
        "whitelist": ["trusted-domain.com", "another-trusted.org"]  # Added new domain
    }
}

response = dns_security.update(update_dict)

# Using model directly
from scm.models.security_services import (
    DNSSecurityProfileUpdateModel,
    BotnetDomains,
    DNSSecurityCategory
)

update_profile = DNSSecurityProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="dns-sec-profile",
    description="Updated DNS security profile",
    botnet_domains=BotnetDomains(
        enable=True,
        packet_capture=False,
        dns_security_categories=[
            DNSSecurityCategory(
                name="command-and-control",
                action="block",
                log_level="critical",
                packet_capture="single-packet"
            ),
            DNSSecurityCategory(
                name="malware",
                action="sinkhole",
                log_level="high",
                packet_capture="single-packet"
            ),
            DNSSecurityCategory(
                name="phishing",
                action="block",
                log_level="high"
            )
        ],
        whitelist=["trusted-domain.com", "another-trusted.org"]
    )
)

payload = update_profile.model_dump(exclude_unset=True)
response = dns_security.update(payload)
```

</div>
