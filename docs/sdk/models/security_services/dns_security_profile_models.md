# DNS Security Profile Models

This section covers the data models associated with the `DNSSecurityProfile` configuration object.

---

## DNSSecurityProfileRequestModel

Used when creating or updating a DNS Security Profile object.

### Attributes

- `name` (str): **Required.** The name of the DNS Security Profile object.
- `description` (Optional[str]): A description of the DNS Security Profile object.
- `botnet_domains` (Optional[BotnetDomainsRequest]): Botnet domains settings.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import DNSSecurityProfileRequestModel, BotnetDomainsRequest,
    DNSSecurityCategoryEntry, ListEntryRequest, SinkholeSettings, WhitelistEntry
from scm.models.security.dns_security_profiles import ActionEnum, LogLevelEnum, PacketCaptureEnum, IPv4AddressEnum,
    IPv6AddressEnum

profile_request = DNSSecurityProfileRequestModel(
    name="test-profile",
    description="Sample DNS Security Profile",
    folder="Shared",
    botnet_domains=BotnetDomainsRequest(
        dns_security_categories=[
            DNSSecurityCategoryEntry(
                name="grayware",
                action=ActionEnum.block,
                log_level=LogLevelEnum.medium,
                packet_capture=PacketCaptureEnum.single_packet
            )
        ],
        lists=[
            ListEntryRequest(
                name="custom_list",
                action={"block": {}},
                packet_capture=PacketCaptureEnum.disable
            )
        ],
        sinkhole=SinkholeSettings(
            ipv4_address=IPv4AddressEnum.default_ip,
            ipv6_address=IPv6AddressEnum.localhost
        ),
        whitelist=[
            WhitelistEntry(
                name="example.com",
                description="Whitelisted domain"
            )
        ]
    )
)

print(profile_request.model_dump_json(indent=2))
```

</div>

---

## DNSSecurityProfileResponseModel

Used when parsing DNS Security Profile objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the DNS Security Profile object.
- `name` (str): The name of the DNS Security Profile object.
- `description` (Optional[str]): A description of the DNS Security Profile object.
- `botnet_domains` (Optional[BotnetDomainsResponse]): Botnet domains settings.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the profile is defined.
    - `snippet` (Optional[str]): The snippet where the profile is defined.
    - `device` (Optional[str]): The device where the profile is defined.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import DNSSecurityProfileResponseModel, BotnetDomainsResponse,
    DNSSecurityCategoryEntry, ListEntryResponse, SinkholeSettings, WhitelistEntry
from scm.models.security.dns_security_profiles import ActionEnum, LogLevelEnum, PacketCaptureEnum, IPv4AddressEnum,
    IPv6AddressEnum

profile_response = DNSSecurityProfileResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-profile",
    description="Sample DNS Security Profile",
    folder="Shared",
    botnet_domains=BotnetDomainsResponse(
        dns_security_categories=[
            DNSSecurityCategoryEntry(
                name="grayware",
                action=ActionEnum.block,
                log_level=LogLevelEnum.medium,
                packet_capture=PacketCaptureEnum.single_packet
            )
        ],
        lists=[
            ListEntryResponse(
                name="custom_list",
                action={"block": {}},
                packet_capture=PacketCaptureEnum.disable
            )
        ],
        sinkhole=SinkholeSettings(
            ipv4_address=IPv4AddressEnum.default_ip,
            ipv6_address=IPv6AddressEnum.localhost
        ),
        whitelist=[
            WhitelistEntry(
                name="example.com",
                description="Whitelisted domain"
            )
        ]
    )
)

print(profile_response.model_dump_json(indent=2))
```

</div>

---

## BotnetDomainsRequest

Represents the 'botnet_domains' settings for requests.

### Attributes

- `dns_security_categories` (Optional[List[DNSSecurityCategoryEntry]]): DNS security categories.
- `lists` (Optional[List[ListEntryRequest]]): Lists of DNS domains.
- `sinkhole` (Optional[SinkholeSettings]): DNS sinkhole settings.
- `whitelist` (Optional[List[WhitelistEntry]]): DNS security overrides.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import BotnetDomainsRequest, DNSSecurityCategoryEntry, ListEntryRequest,
    SinkholeSettings, WhitelistEntry
from scm.models.security.dns_security_profiles import ActionEnum, LogLevelEnum, PacketCaptureEnum, IPv4AddressEnum,
    IPv6AddressEnum

botnet_domains = BotnetDomainsRequest(
    dns_security_categories=[
        DNSSecurityCategoryEntry(
            name="malware",
            action=ActionEnum.sinkhole,
            log_level=LogLevelEnum.high,
            packet_capture=PacketCaptureEnum.extended_capture
        )
    ],
    lists=[
        ListEntryRequest(
            name="custom_blocklist",
            action={"block": {}},
            packet_capture=PacketCaptureEnum.single_packet
        )
    ],
    sinkhole=SinkholeSettings(
        ipv4_address=IPv4AddressEnum.localhost,
        ipv6_address=IPv6AddressEnum.localhost
    ),
    whitelist=[
        WhitelistEntry(
            name="trusteddomain.com",
            description="Trusted domain"
        )
    ]
)

print(botnet_domains.model_dump_json(indent=2))
```

</div>

---

## DNSSecurityCategoryEntry

Represents an entry in 'dns_security_categories'.

### Attributes

- `name` (str): **Required.** DNS Security Category Name.
- `action` (ActionEnum): Action to be taken.
- `log_level` (Optional[LogLevelEnum]): Log level.
- `packet_capture` (Optional[PacketCaptureEnum]): Packet capture setting.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import DNSSecurityCategoryEntry, ActionEnum, LogLevelEnum,
    PacketCaptureEnum

category_entry = DNSSecurityCategoryEntry(
    name="phishing",
    action=ActionEnum.block,
    log_level=LogLevelEnum.critical,
    packet_capture=PacketCaptureEnum.extended_capture
)

print(category_entry.model_dump_json(indent=2))
```

</div>

---

## ListEntryRequest

Represents a 'lists' entry for requests.

### Attributes

- `name` (str): **Required.** List name.
- `action` (ListActionRequest): **Required.** Action to be taken.
- `packet_capture` (Optional[PacketCaptureEnum]): Packet capture setting.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import ListEntryRequest, PacketCaptureEnum

list_entry = ListEntryRequest(
    name="custom_sinkhole_list",
    action={"sinkhole": {}},
    packet_capture=PacketCaptureEnum.single_packet
)

print(list_entry.model_dump_json(indent=2))
```

</div>

---

## SinkholeSettings

Represents the 'sinkhole' settings.

### Attributes

- `ipv4_address` (IPv4AddressEnum): **Required.** IPv4 address for sinkhole.
- `ipv6_address` (IPv6AddressEnum): **Required.** IPv6 address for sinkhole.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import SinkholeSettings, IPv4AddressEnum, IPv6AddressEnum

sinkhole = SinkholeSettings(
    ipv4_address=IPv4AddressEnum.pan_sinkhole_default_ip,
    ipv6_address=IPv6AddressEnum.localhost
)

print(sinkhole.model_dump_json(indent=2))
```

</div>

---

## WhitelistEntry

Represents an entry in the 'whitelist'.

### Attributes

- `name` (str): **Required.** DNS domain or FQDN to be whitelisted.
- `description` (Optional[str]): Description of the whitelist entry.

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import WhitelistEntry

whitelist_entry = WhitelistEntry(
    name="example.com",
    description="Trusted domain for our organization"
)

print(whitelist_entry.model_dump_json(indent=2))
```

</div>

---

## Enums

### ActionEnum

Enumeration of allowed actions for DNS security categories:

- `default`
- `allow`
- `block`
- `sinkhole`

### LogLevelEnum

Enumeration of log levels:

- `default`
- `none`
- `low`
- `informational`
- `medium`
- `high`
- `critical`

### PacketCaptureEnum

Enumeration of packet capture options:

- `disable`
- `single_packet`
- `extended_capture`

### IPv4AddressEnum

Enumeration of allowed IPv4 sinkhole addresses:

- `pan_sinkhole_default_ip`
- `localhost`

### IPv6AddressEnum

Enumeration of allowed IPv6 sinkhole addresses:

- `localhost`

### Example

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import ActionEnum, LogLevelEnum, PacketCaptureEnum, IPv4AddressEnum,
    IPv6AddressEnum

print(f"Action types: {[a.value for a in ActionEnum]}")
print(f"Log levels: {[l.value for l in LogLevelEnum]}")
print(f"Packet capture options: {[p.value for p in PacketCaptureEnum]}")
print(f"IPv4 sinkhole addresses: {[i.value for i in IPv4AddressEnum]}")
print(f"IPv6 sinkhole addresses: {[i.value for i in IPv6AddressEnum]}")
```

</div>

---

## Full Example: Creating a Comprehensive DNS Security Profile Model

<div class="termy">

<!-- termynal -->

```python
from scm.models.security.dns_security_profiles import (
    DNSSecurityProfileRequestModel,
    BotnetDomainsRequest,
    DNSSecurityCategoryEntry,
    ListEntryRequest,
    SinkholeSettings,
    WhitelistEntry,
    ActionEnum,
    LogLevelEnum,
    PacketCaptureEnum,
    IPv4AddressEnum,
    IPv6AddressEnum
)

# Create a comprehensive DNS Security Profile model
comprehensive_profile = DNSSecurityProfileRequestModel(
    name="comprehensive_profile",
    description="Comprehensive DNS Security Profile",
    folder="Shared",
    botnet_domains=BotnetDomainsRequest(
        dns_security_categories=[
            DNSSecurityCategoryEntry(
                name="grayware",
                action=ActionEnum.block,
                log_level=LogLevelEnum.medium,
                packet_capture=PacketCaptureEnum.single_packet
            ),
            DNSSecurityCategoryEntry(
                name="malware",
                action=ActionEnum.sinkhole,
                log_level=LogLevelEnum.critical,
                packet_capture=PacketCaptureEnum.extended_capture
            )
        ],
        lists=[
            ListEntryRequest(
                name="custom_blocklist",
                action={"block": {}},
                packet_capture=PacketCaptureEnum.disable
            ),
            ListEntryRequest(
                name="custom_sinkhole_list",
                action={"sinkhole": {}},
                packet_capture=PacketCaptureEnum.single_packet
            )
        ],
        sinkhole=SinkholeSettings(
            ipv4_address=IPv4AddressEnum.pan_sinkhole_default_ip,
            ipv6_address=IPv6AddressEnum.localhost
        ),
        whitelist=[
            WhitelistEntry(
                name="example.com",
                description="Whitelisted domain"
            ),
            WhitelistEntry(
                name="trusteddomain.org",
                description="Another trusted domain"
            )
        ]
    )
)

# Print the JSON representation of the model
print(comprehensive_profile.model_dump_json(indent=2))

# Validate the model
comprehensive_profile.model_validate(comprehensive_profile.model_dump())
print("Model validation successful")
```

</div>

This example demonstrates how to create a comprehensive DNS Security Profile model using the provided classes and enums.
It includes multiple DNS security categories, custom lists, sinkhole settings, and whitelist entries to showcase the
full capabilities of the model.
