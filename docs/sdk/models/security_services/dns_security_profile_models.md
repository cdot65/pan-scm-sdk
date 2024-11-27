# DNS Security Profile Models

## Overview

The DNS Security Profile models provide a structured way to manage DNS security configurations in Palo Alto Networks'
Strata Cloud Manager.
These models support defining botnet domain protections, including security categories, custom lists, sinkhole settings,
and whitelisting.
The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute      | Type          | Required | Default | Description                                                               |
|----------------|---------------|----------|---------|---------------------------------------------------------------------------|
| name           | str           | Yes      | None    | Name of the profile. Must match pattern: ^[a-zA-Z0-9][a-zA-Z0-9_\-\.\s]*$ |
| description    | str           | No       | None    | Description of the profile                                                |
| botnet_domains | BotnetDomains | No       | None    | Botnet domain protection settings                                         |
| folder         | str           | No*      | None    | Folder where profile is defined. Max length: 64 chars                     |
| snippet        | str           | No*      | None    | Snippet where profile is defined. Max length: 64 chars                    |
| device         | str           | No*      | None    | Device where profile is defined. Max length: 64 chars                     |
| id             | UUID          | Yes**    | None    | UUID of the profile (response only)                                       |

\* Exactly one container type (folder/snippet/device) must be provided
\** Only required for response model

### Botnet Domains Attributes

| Attribute               | Type                           | Required | Default | Description                    |
|-------------------------|--------------------------------|----------|---------|--------------------------------|
| dns_security_categories | List[DNSSecurityCategoryEntry] | No       | None    | DNS security category settings |
| lists                   | List[ListEntry]                | No       | None    | Custom domain lists            |
| sinkhole                | SinkholeSettings               | No       | None    | Sinkhole configuration         |
| whitelist               | List[WhitelistEntry]           | No       | None    | Whitelisted domains            |

## Exceptions

The DNS Security Profile models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When multiple container types (folder/snippet/device) are specified
    - When no container type is specified for create operations
    - When invalid action formats are provided (must be string or dict)
    - When multiple actions are specified in a list entry (must be exactly one)
    - When action parameters are provided where none are allowed
    - When name pattern validation fails
    - When container field pattern validation fails
    - When field length limits are exceeded

## Model Validators

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
try:
    profile_dict = {
        "name": "invalid-profile",
        "folder": "Shared",
        "device": "fw01"  # Can't specify both folder and device
    }
    profile = DNSSecurityProfile(api_client)
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."

# Using model directly
from scm.models.security import DNSSecurityProfileCreateModel

try:
    profile = DNSSecurityProfileCreateModel(
        name="invalid-profile",
        folder="Shared",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder', 'snippet', or 'device' must be provided."
```

</div>

### List Action Validation

For list entries, exactly one action type must be specified:

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
try:
    list_dict = {
        "name": "custom-list",
        "action": {
            "block": {},
            "sinkhole": {}  # Can't specify multiple actions
        }
    }
    profile_dict = {
        "name": "test-profile",
        "folder": "Shared",
        "botnet_domains": {
            "lists": [list_dict]
        }
    }
    response = profile.create(profile_dict)
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."

# Using model directly
from scm.models.security import ListEntryBaseModel, ListActionRequestModel

try:
    list_entry = ListEntryBaseModel(
        name="custom-list",
        action=ListActionRequestModel({"block": {}, "sinkhole": {}})
    )
except ValueError as e:
    print(e)  # "Exactly one action must be provided in 'action' field."
```

</div>

## Usage Examples

### Creating a Basic DNS Security Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.security import DNSSecurityProfile

profile_dict = {
    "name": "basic-profile",
    "description": "Basic DNS security profile",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "block",
                "log_level": "medium"
            }
        ]
    }
}

profile = DNSSecurityProfile(api_client)
response = profile.create(profile_dict)

# Using model directly
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    BotnetDomainsModel,
    DNSSecurityCategoryEntryModel,
    ActionEnum,
    LogLevelEnum
)

profile = DNSSecurityProfileCreateModel(
    name="basic-profile",
    description="Basic DNS security profile",
    folder="Shared",
    botnet_domains=BotnetDomainsModel(
        dns_security_categories=[
            DNSSecurityCategoryEntryModel(
                name="grayware",
                action=ActionEnum.block,
                log_level=LogLevelEnum.medium
            )
        ]
    )
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

</div>

### Creating a Profile with Custom Lists and Sinkhole

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
profile_dict = {
    "name": "advanced-profile",
    "description": "Advanced DNS security profile",
    "folder": "Shared",
    "botnet_domains": {
        "lists": [
            {
                "name": "custom-blocklist",
                "action": {"block": {}},
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        }
    }
}

response = profile.create(profile_dict)

# Using model directly
from scm.models.security import (
    DNSSecurityProfileCreateModel,
    BotnetDomainsModel,
    ListEntryBaseModel,
    SinkholeSettingsModel,
    PacketCaptureEnum,
    IPv4AddressEnum,
    IPv6AddressEnum
)

profile = DNSSecurityProfileCreateModel(
    name="advanced-profile",
    description="Advanced DNS security profile",
    folder="Shared",
    botnet_domains=BotnetDomainsModel(
        lists=[
            ListEntryBaseModel(
                name="custom-blocklist",
                action={"block": {}},
                packet_capture=PacketCaptureEnum.single_packet
            )
        ],
        sinkhole=SinkholeSettingsModel(
            ipv4_address=IPv4AddressEnum.default_ip,
            ipv6_address=IPv6AddressEnum.localhost
        )
    )
)

payload = profile.model_dump(exclude_unset=True)
response = profile.create(payload)
```

</div>

### Updating a DNS Security Profile

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "updated-profile",
    "description": "Updated DNS security profile",
    "botnet_domains": {
        "whitelist": [
            {
                "name": "example.com",
                "description": "Trusted domain"
            }
        ]
    }
}

response = profile.update(update_dict)

# Using model directly
from scm.models.security import (
    DNSSecurityProfileUpdateModel,
    BotnetDomainsModel,
    WhitelistEntryModel
)

update = DNSSecurityProfileUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="updated-profile",
    description="Updated DNS security profile",
    botnet_domains=BotnetDomainsModel(
        whitelist=[
            WhitelistEntryModel(
                name="example.com",
                description="Trusted domain"
            )
        ]
    )
)

payload = update.model_dump(exclude_unset=True)
response = profile.update(payload)
```

</div>