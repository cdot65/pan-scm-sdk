# Zone Protection Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Zone Protection Profile models provide a structured way to represent and validate zone protection profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating zone protection profiles, enforcing proper flood protection, scan protection, protocol filtering, and field validations.

### Models

The module provides the following Pydantic models:

- `ZoneProtectionProfileBaseModel`: Base model with fields common to all zone protection profile operations
- `ZoneProtectionProfileCreateModel`: Model for creating new zone protection profiles
- `ZoneProtectionProfileUpdateModel`: Model for updating existing zone protection profiles
- `ZoneProtectionProfileResponseModel`: Response model for zone protection profile operations
- `FloodProtection`: Flood protection configuration model
- `FloodRed`: Random Early Detection (RED) configuration model
- `FloodSynCookies`: SYN Cookies configuration model for TCP SYN flood protection
- `TcpSynFlood`: TCP SYN flood protection configuration model
- `UdpFlood`: UDP flood protection configuration model
- `SctpInitFlood`: SCTP INIT flood protection configuration model
- `IcmpFlood`: ICMP flood protection configuration model
- `Icmpv6Flood`: ICMPv6 flood protection configuration model
- `OtherIpFlood`: Other IP flood protection configuration model
- `ScanEntry`: Scan protection entry configuration model
- `ScanAction`: Scan action configuration model
- `ScanActionBlockIp`: Block IP action configuration model for scan protection
- `ScanWhiteListEntry`: Scan whitelist entry configuration model
- `NonIpProtocol`: Non-IP protocol configuration model
- `NonIpProtocolEntry`: Non-IP protocol entry configuration model
- `L2SecGroupTagProtection`: Layer 2 Security Group Tag protection configuration model
- `SgtEntry`: Security Group Tag entry configuration model

The `ZoneProtectionProfileBaseModel` and `ZoneProtectionProfileCreateModel` / `ZoneProtectionProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `ZoneProtectionProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### ZoneProtectionProfileBaseModel

This is the base model containing fields common to all zone protection profile operations.

| Attribute                                    | Type                    | Required | Default | Description                                                    |
|----------------------------------------------|-------------------------|----------|---------|----------------------------------------------------------------|
| name                                         | str                     | Yes      | None    | Name of the profile. Max 31 chars.                             |
| description                                  | str                     | No       | None    | Description of the profile. Max 255 chars.                     |
| flood                                        | FloodProtection         | No       | None    | Flood protection configuration.                                |
| scan                                         | List[ScanEntry]         | No       | None    | Scan protection entries.                                       |
| scan_white_list                              | List[ScanWhiteListEntry]| No       | None    | Scan whitelist entries.                                        |
| spoofed_ip_discard                           | bool                    | No       | None    | Discard spoofed IP packets.                                    |
| strict_ip_check                              | bool                    | No       | None    | Enable strict IP address checking.                             |
| fragmented_traffic_discard                   | bool                    | No       | None    | Discard fragmented traffic.                                    |
| strict_source_routing_discard                | bool                    | No       | None    | Discard strict source routing packets.                         |
| loose_source_routing_discard                 | bool                    | No       | None    | Discard loose source routing packets.                          |
| timestamp_discard                            | bool                    | No       | None    | Discard timestamp option packets.                              |
| record_route_discard                         | bool                    | No       | None    | Discard record route option packets.                           |
| security_discard                             | bool                    | No       | None    | Discard security option packets.                               |
| stream_id_discard                            | bool                    | No       | None    | Discard stream ID option packets.                              |
| unknown_option_discard                       | bool                    | No       | None    | Discard unknown option packets.                                |
| malformed_option_discard                     | bool                    | No       | None    | Discard malformed option packets.                              |
| mismatched_overlapping_tcp_segment_discard   | bool                    | No       | None    | Discard mismatched overlapping TCP segments.                   |
| tcp_handshake_discard                        | bool                    | No       | None    | Discard incomplete TCP handshake packets.                      |
| tcp_syn_with_data_discard                    | bool                    | No       | None    | Discard TCP SYN packets with data.                             |
| tcp_synack_with_data_discard                 | bool                    | No       | None    | Discard TCP SYN-ACK packets with data.                         |
| reject_non_syn_tcp                           | str                     | No       | None    | Reject non-SYN TCP. Pattern: `^(global\|yes\|no)$`.           |
| asymmetric_path                              | str                     | No       | None    | Asymmetric path handling. Pattern: `^(global\|drop\|bypass)$`. |
| mptcp_option_strip                           | str                     | No       | None    | MPTCP option strip. Pattern: `^(no\|yes\|global)$`.           |
| tcp_timestamp_strip                          | bool                    | No       | None    | Strip TCP timestamp option.                                    |
| tcp_fast_open_and_data_strip                 | bool                    | No       | None    | Strip TCP Fast Open and data.                                  |
| icmp_ping_zero_id_discard                    | bool                    | No       | None    | Discard ICMP ping with zero ID.                                |
| icmp_frag_discard                            | bool                    | No       | None    | Discard fragmented ICMP packets.                               |
| icmp_large_packet_discard                    | bool                    | No       | None    | Discard large ICMP packets.                                    |
| discard_icmp_embedded_error                  | bool                    | No       | None    | Discard ICMP embedded error messages.                          |
| suppress_icmp_timeexceeded                   | bool                    | No       | None    | Suppress ICMP time exceeded messages.                          |
| suppress_icmp_needfrag                       | bool                    | No       | None    | Suppress ICMP need fragmentation messages.                     |
| ipv6                                         | Dict[str, Any]          | No       | None    | IPv6 protection configuration.                                 |
| non_ip_protocol                              | NonIpProtocol           | No       | None    | Non-IP protocol configuration.                                 |
| l2_sec_group_tag_protection                  | L2SecGroupTagProtection | No       | None    | Layer 2 Security Group Tag protection.                         |
| folder                                       | str                     | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| snippet                                      | str                     | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.|
| device                                       | str                     | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### ZoneProtectionProfileCreateModel

Inherits all fields from `ZoneProtectionProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### ZoneProtectionProfileUpdateModel

Extends `ZoneProtectionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                         |
|-----------|------|----------|---------|-----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the zone protection profile |

### ZoneProtectionProfileResponseModel

Extends `ZoneProtectionProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                         |
|-----------|------|----------|---------|-----------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the zone protection profile |

> **Note:** The `ZoneProtectionProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### FloodProtection

This model defines the top-level flood protection configuration.

| Attribute | Type          | Required | Default | Description                    |
|-----------|---------------|----------|---------|--------------------------------|
| tcp_syn   | TcpSynFlood   | No       | None    | TCP SYN flood protection.      |
| udp       | UdpFlood      | No       | None    | UDP flood protection.          |
| sctp_init | SctpInitFlood | No       | None    | SCTP INIT flood protection.    |
| icmp      | IcmpFlood     | No       | None    | ICMP flood protection.         |
| icmpv6    | Icmpv6Flood   | No       | None    | ICMPv6 flood protection.       |
| other_ip  | OtherIpFlood  | No       | None    | Other IP flood protection.     |

### FloodRed

Random Early Detection (RED) configuration shared by multiple flood protection types.

| Attribute     | Type | Required | Default | Description                        |
|---------------|------|----------|---------|------------------------------------|
| alarm_rate    | int  | No       | None    | Alarm rate threshold. Range: 0-2000000.    |
| activate_rate | int  | No       | None    | Activate rate threshold. Range: 0-2000000. |
| maximal_rate  | int  | No       | None    | Maximal rate threshold. Range: 0-2000000.  |

### FloodSynCookies

SYN Cookies configuration for TCP SYN flood protection.

| Attribute     | Type | Required | Default | Description                        |
|---------------|------|----------|---------|------------------------------------|
| alarm_rate    | int  | No       | None    | Alarm rate threshold. Range: 0-2000000.    |
| activate_rate | int  | No       | None    | Activate rate threshold. Range: 0-2000000. |
| maximal_rate  | int  | No       | None    | Maximal rate threshold. Range: 0-2000000.  |

### TcpSynFlood

TCP SYN flood protection configuration. Supports either RED or SYN Cookies mode, but not both.

| Attribute   | Type            | Required | Default | Description                              |
|-------------|-----------------|----------|---------|------------------------------------------|
| enable      | bool            | No       | None    | Enable TCP SYN flood protection.         |
| red         | FloodRed        | No*      | None    | Random Early Detection configuration.    |
| syn_cookies | FloodSynCookies | No*      | None    | SYN Cookies configuration.               |

\* `red` and `syn_cookies` are mutually exclusive. Only one may be set at a time.

### UdpFlood

UDP flood protection configuration.

| Attribute | Type     | Required | Default | Description                          |
|-----------|----------|----------|---------|--------------------------------------|
| enable    | bool     | No       | None    | Enable UDP flood protection.         |
| red       | FloodRed | No       | None    | Random Early Detection configuration.|

### SctpInitFlood

SCTP INIT flood protection configuration.

| Attribute | Type     | Required | Default | Description                          |
|-----------|----------|----------|---------|--------------------------------------|
| enable    | bool     | No       | None    | Enable SCTP INIT flood protection.   |
| red       | FloodRed | No       | None    | Random Early Detection configuration.|

### IcmpFlood

ICMP flood protection configuration.

| Attribute | Type     | Required | Default | Description                          |
|-----------|----------|----------|---------|--------------------------------------|
| enable    | bool     | No       | None    | Enable ICMP flood protection.        |
| red       | FloodRed | No       | None    | Random Early Detection configuration.|

### Icmpv6Flood

ICMPv6 flood protection configuration.

| Attribute | Type     | Required | Default | Description                          |
|-----------|----------|----------|---------|--------------------------------------|
| enable    | bool     | No       | None    | Enable ICMPv6 flood protection.      |
| red       | FloodRed | No       | None    | Random Early Detection configuration.|

### OtherIpFlood

Other IP flood protection configuration.

| Attribute | Type     | Required | Default | Description                          |
|-----------|----------|----------|---------|--------------------------------------|
| enable    | bool     | No       | None    | Enable other IP flood protection.    |
| red       | FloodRed | No       | None    | Random Early Detection configuration.|

### ScanEntry

Scan protection entry configuration.

| Attribute | Type       | Required | Default | Description                                        |
|-----------|------------|----------|---------|----------------------------------------------------|
| name      | str        | Yes      | None    | Scan entry name. Pattern: `^(8001\|8002\|8003\|8006)$`. |
| action    | ScanAction | No       | None    | Scan action configuration.                         |
| interval  | int        | No       | None    | Scan interval. Range: 2-65535.                     |
| threshold | int        | No       | None    | Scan threshold. Range: 2-65535.                    |

### ScanAction

Scan action configuration. Exactly one action must be specified.

| Attribute | Type              | Required | Default | Description     |
|-----------|-------------------|----------|---------|-----------------|
| allow     | Dict[str, Any]    | No*      | None    | Allow action.   |
| alert     | Dict[str, Any]    | No*      | None    | Alert action.   |
| block     | Dict[str, Any]    | No*      | None    | Block action.   |
| block_ip  | ScanActionBlockIp | No*      | None    | Block IP action.|

\* Exactly one of `allow`, `alert`, `block`, or `block_ip` must be set.

### ScanActionBlockIp

Block IP action configuration for scan protection.

| Attribute | Type | Required | Default | Description                                                    |
|-----------|------|----------|---------|----------------------------------------------------------------|
| track_by  | str  | Yes      | None    | Track by method. Pattern: `^(source\|source-and-destination)$`. |
| duration  | int  | Yes      | None    | Block duration in seconds. Range: 1-3600.                      |

### ScanWhiteListEntry

Scan whitelist entry configuration.

| Attribute | Type | Required | Default | Description          |
|-----------|------|----------|---------|----------------------|
| name      | str  | Yes      | None    | Whitelist entry name.|
| ipv4      | str  | No       | None    | IPv4 address.        |
| ipv6      | str  | No       | None    | IPv6 address.        |

### NonIpProtocol

Non-IP protocol configuration.

| Attribute | Type                    | Required | Default | Description                                        |
|-----------|-------------------------|----------|---------|----------------------------------------------------|
| list_type | str                     | No       | None    | List type. Pattern: `^(exclude\|include)$`.         |
| protocol  | List[NonIpProtocolEntry]| No       | None    | Protocol entries.                                  |

### NonIpProtocolEntry

Non-IP protocol entry configuration.

| Attribute  | Type | Required | Default | Description                    |
|------------|------|----------|---------|--------------------------------|
| name       | str  | Yes      | None    | Protocol entry name.           |
| ether_type | str  | Yes      | None    | Ethernet type.                 |
| enable     | bool | No       | None    | Enable this protocol entry.    |

### L2SecGroupTagProtection

Layer 2 Security Group Tag protection configuration.

| Attribute | Type           | Required | Default | Description                  |
|-----------|----------------|----------|---------|------------------------------|
| tags      | List[SgtEntry] | No       | None    | Security Group Tag entries.  |

### SgtEntry

Security Group Tag entry configuration.

| Attribute | Type | Required | Default | Description                |
|-----------|------|----------|---------|----------------------------|
| name      | str  | Yes      | None    | SGT entry name.            |
| tag       | str  | Yes      | None    | Security group tag value.  |
| enable    | bool | No       | None    | Enable this SGT entry.     |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a zone protection profile (`ZoneProtectionProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When both `red` and `syn_cookies` are configured in a `TcpSynFlood` model (they are mutually exclusive).
- When a `ScanAction` does not have exactly one action set (must have exactly one of `allow`, `alert`, `block`, or `block_ip`).
- When the profile name exceeds the maximum length.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Field Validators in `TcpSynFlood`

- **validate_red_syn_cookies_mutual_exclusivity**:
  Ensures that `red` and `syn_cookies` are mutually exclusive. If both are set, it raises a `ValueError`. Only one flood mitigation strategy can be active for TCP SYN flood protection at a time.

### Field Validators in `ScanAction`

- **validate_exactly_one_action**:
  Ensures that exactly one action is configured. If zero or more than one of `allow`, `alert`, `block`, or `block_ip` is set, it raises a `ValueError`.

### Container Validation in `ZoneProtectionProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a Zone Protection Profile

#### Using a Dictionary with Flood Protection

```python
from scm.models.network import ZoneProtectionProfileCreateModel

profile_data = {
    "name": "zone-protect-1",
    "description": "Standard zone protection profile",
    "flood": {
        "tcp_syn": {
            "enable": True,
            "red": {
                "alarm_rate": 10000,
                "activate_rate": 20000,
                "maximal_rate": 40000
            }
        },
        "udp": {
            "enable": True,
            "red": {
                "alarm_rate": 10000,
                "activate_rate": 20000,
                "maximal_rate": 40000
            }
        },
        "icmp": {
            "enable": True,
            "red": {
                "alarm_rate": 10000,
                "activate_rate": 20000,
                "maximal_rate": 40000
            }
        }
    },
    "spoofed_ip_discard": True,
    "strict_ip_check": True,
    "folder": "Network Profiles"
}

# Validate and create model instance
profile = ZoneProtectionProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly with Scan Protection

```python
from scm.models.network import (
    ZoneProtectionProfileCreateModel,
    ScanEntry,
    ScanAction,
    ScanActionBlockIp,
)

# Create scan entries
scan_entries = [
    ScanEntry(
        name="8001",
        action=ScanAction(
            block_ip=ScanActionBlockIp(
                track_by="source",
                duration=300
            )
        ),
        interval=10,
        threshold=100,
    ),
    ScanEntry(
        name="8002",
        action=ScanAction(alert={}),
        interval=10,
        threshold=100,
    ),
]

# Create zone protection profile
profile = ZoneProtectionProfileCreateModel(
    name="scan-protect-1",
    description="Profile with scan protection",
    scan=scan_entries,
    spoofed_ip_discard=True,
    folder="Network Profiles"
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a Zone Protection Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Fetch existing profile
existing = client.zone_protection_profile.fetch(
    name="zone-protect-1",
    folder="Network Profiles"
)

# Modify attributes using dot notation
existing.spoofed_ip_discard = True
existing.strict_ip_check = True
existing.fragmented_traffic_discard = True

# Pass modified object to update()
updated = client.zone_protection_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Creating a Profile with TCP SYN Cookies

```python
from scm.models.network import (
    ZoneProtectionProfileCreateModel,
    FloodProtection,
    TcpSynFlood,
    FloodSynCookies,
)

# Create flood protection with SYN Cookies instead of RED
flood = FloodProtection(
    tcp_syn=TcpSynFlood(
        enable=True,
        syn_cookies=FloodSynCookies(
            alarm_rate=10000,
            activate_rate=20000,
            maximal_rate=40000
        )
    )
)

profile = ZoneProtectionProfileCreateModel(
    name="syn-cookies-profile",
    description="Profile using SYN Cookies for TCP SYN flood protection",
    flood=flood,
    folder="Network Profiles"
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
