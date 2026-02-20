# BGP Address Family Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Address Family Profile models provide a structured way to represent and validate BGP address family profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models control per-neighbor address family settings including add-path, allowas-in, maximum prefix limits, next-hop behavior, private AS removal, community handling, and ORF configuration.

### Models

The module provides the following Pydantic models:

- `BgpAddressFamilyProfileBaseModel`: Base model with fields common to all BGP address family profile operations
- `BgpAddressFamilyProfileCreateModel`: Model for creating new BGP address family profiles
- `BgpAddressFamilyProfileUpdateModel`: Model for updating existing BGP address family profiles
- `BgpAddressFamilyProfileResponseModel`: Response model for BGP address family profile operations
- `BgpAddressFamilyProfileIpv4UnicastMulticast`: IPv4 container with unicast and multicast address families
- `BgpAddressFamily`: Core address family configuration (reused for unicast and multicast)
- `BgpAddressFamilyAddPath`: Add-path configuration
- `BgpAddressFamilyAllowasIn`: Allowas-in configuration (oneOf: origin or occurrence)
- `BgpAddressFamilyMaximumPrefix`: Maximum prefix configuration
- `BgpAddressFamilyMaximumPrefixAction`: Maximum prefix action (oneOf: warning_only or restart)
- `BgpAddressFamilyMaximumPrefixRestart`: Maximum prefix restart interval configuration
- `BgpAddressFamilyNextHop`: Next-hop configuration (oneOf: self or self_force)
- `BgpAddressFamilyRemovePrivateAS`: Remove private AS configuration (oneOf: all or replace_AS)
- `BgpAddressFamilySendCommunity`: Send community configuration (oneOf: all, both, extended, large, or standard)
- `BgpAddressFamilyOrf`: ORF (Outbound Route Filtering) configuration

The `BgpAddressFamilyProfileBaseModel` and `BgpAddressFamilyProfileCreateModel` / `BgpAddressFamilyProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `BgpAddressFamilyProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### BgpAddressFamilyProfileBaseModel

This is the base model containing fields common to all BGP address family profile operations.

| Attribute | Type                                       | Required | Default | Description                                                     |
|-----------|--------------------------------------------|----------|---------|-----------------------------------------------------------------|
| name      | str                                        | Yes      | None    | Profile name.                                                   |
| ipv4      | BgpAddressFamilyProfileIpv4UnicastMulticast | No       | None    | IPv4 address family configuration.                              |
| folder    | str                                        | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                                        | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                                        | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpAddressFamilyProfileCreateModel

Inherits all fields from `BgpAddressFamilyProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpAddressFamilyProfileUpdateModel

Extends `BgpAddressFamilyProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                             |
|-----------|------|----------|---------|---------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP address family profile |

### BgpAddressFamilyProfileResponseModel

Extends `BgpAddressFamilyProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                             |
|-----------|------|----------|---------|---------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP address family profile |

> **Note:** The `BgpAddressFamilyProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### BgpAddressFamilyProfileIpv4UnicastMulticast

IPv4 container wrapping unicast and multicast address families.

| Attribute | Type            | Required | Default | Description              |
|-----------|-----------------|----------|---------|--------------------------|
| unicast   | BgpAddressFamily | No       | None    | Unicast address family.  |
| multicast | BgpAddressFamily | No       | None    | Multicast address family.|

### BgpAddressFamily

Core address family configuration, reused for both unicast and multicast.

| Attribute                    | Type                          | Required | Default | Description                                              |
|------------------------------|-------------------------------|----------|---------|----------------------------------------------------------|
| enable                       | bool                          | No       | None    | Enable address family.                                   |
| soft_reconfig_with_stored_info | bool                        | No       | None    | Soft reconfiguration with stored routes.                 |
| add_path                     | BgpAddressFamilyAddPath       | No       | None    | Add-path configuration.                                  |
| as_override                  | bool                          | No       | None    | Override ASNs in outbound updates if AS-Path equals Remote-AS. |
| route_reflector_client       | bool                          | No       | None    | Route reflector client.                                  |
| default_originate            | bool                          | No       | None    | Originate default route.                                 |
| default_originate_map        | str                           | No       | None    | Default originate route map.                             |
| allowas_in                   | BgpAddressFamilyAllowasIn     | No       | None    | Allow-AS-in configuration.                               |
| maximum_prefix               | BgpAddressFamilyMaximumPrefix | No       | None    | Maximum prefix configuration.                            |
| next_hop                     | BgpAddressFamilyNextHop       | No       | None    | Next-hop configuration.                                  |
| remove_private_AS            | BgpAddressFamilyRemovePrivateAS | No     | None    | Remove private AS configuration.                         |
| send_community               | BgpAddressFamilySendCommunity | No       | None    | Send community configuration.                            |
| orf                          | BgpAddressFamilyOrf           | No       | None    | ORF configuration.                                       |

### BgpAddressFamilyAddPath

Add-path configuration for advertising multiple paths.

| Attribute          | Type | Required | Default | Description                          |
|--------------------|------|----------|---------|--------------------------------------|
| tx_all_paths       | bool | No       | None    | Advertise all paths to peer.         |
| tx_bestpath_per_AS | bool | No       | None    | Advertise bestpath per neighboring AS.|

### BgpAddressFamilyAllowasIn

Allow-AS-in configuration. Uses oneOf semantics: `origin` and `occurrence` are mutually exclusive.

| Attribute  | Type          | Required | Default | Description                                          |
|------------|---------------|----------|---------|------------------------------------------------------|
| origin     | Dict[str,Any] | No*      | None    | Allow origin AS in path.                             |
| occurrence | int           | No*      | None    | Number of times own AS can appear in AS_PATH (1-10). |

\* `origin` and `occurrence` are mutually exclusive.

### BgpAddressFamilyMaximumPrefix

Maximum prefix configuration for limiting the number of prefixes accepted from a peer.

| Attribute    | Type                               | Required | Default | Description                              |
|--------------|------------------------------------|----------|---------|------------------------------------------|
| num_prefixes | int                                | No       | None    | Maximum number of prefixes (1-4294967295).|
| threshold    | int                                | No       | None    | Threshold percentage (1-100).            |
| action       | BgpAddressFamilyMaximumPrefixAction | No       | None    | Action on limit.                         |

### BgpAddressFamilyMaximumPrefixAction

Maximum prefix action. Uses oneOf semantics: `warning_only` and `restart` are mutually exclusive.

| Attribute    | Type                                  | Required | Default | Description           |
|--------------|---------------------------------------|----------|---------|-----------------------|
| warning_only | Dict[str,Any]                         | No*      | None    | Warning only action.  |
| restart      | BgpAddressFamilyMaximumPrefixRestart  | No*      | None    | Restart action.       |

\* `warning_only` and `restart` are mutually exclusive.

### BgpAddressFamilyMaximumPrefixRestart

Restart configuration for maximum prefix action.

| Attribute | Type | Required | Default | Description                    |
|-----------|------|----------|---------|--------------------------------|
| interval  | int  | No       | None    | Restart interval (1-65535).    |

### BgpAddressFamilyNextHop

Next-hop configuration. Uses oneOf semantics: `self` and `self_force` are mutually exclusive.

| Attribute  | Type          | Required | Default | Description              |
|------------|---------------|----------|---------|--------------------------|
| self\_     | Dict[str,Any] | No*      | None    | Set next-hop to self. (alias: `self`) |
| self_force | Dict[str,Any] | No*      | None    | Force next-hop to self.  |

\* `self` and `self_force` are mutually exclusive. Note: the Python attribute is `self_` with an underscore to avoid conflict with the Python keyword, but the serialized alias is `self`.

### BgpAddressFamilyRemovePrivateAS

Remove private AS configuration. Uses oneOf semantics: `all` and `replace_AS` are mutually exclusive.

| Attribute  | Type          | Required | Default | Description                    |
|------------|---------------|----------|---------|--------------------------------|
| all        | Dict[str,Any] | No*      | None    | Remove all private AS numbers. |
| replace_AS | Dict[str,Any] | No*      | None    | Replace private AS numbers.    |

\* `all` and `replace_AS` are mutually exclusive.

### BgpAddressFamilySendCommunity

Send community configuration. Uses oneOf semantics: at most one type can be set.

| Attribute | Type          | Required | Default | Description                         |
|-----------|---------------|----------|---------|-------------------------------------|
| all       | Dict[str,Any] | No*      | None    | Send all communities.               |
| both      | Dict[str,Any] | No*      | None    | Send both standard and extended.    |
| extended  | Dict[str,Any] | No*      | None    | Send extended communities.          |
| large     | Dict[str,Any] | No*      | None    | Send large communities.             |
| standard  | Dict[str,Any] | No*      | None    | Send standard communities.          |

\* At most one of `all`, `both`, `extended`, `large`, or `standard` may be set.

### BgpAddressFamilyOrf

Outbound Route Filtering configuration.

| Attribute       | Type | Required | Default | Description                                            |
|-----------------|------|----------|---------|--------------------------------------------------------|
| orf_prefix_list | str  | No       | None    | ORF prefix list mode. Pattern: `^(none\|both\|receive\|send)$` |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`BgpAddressFamilyProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When both `origin` and `occurrence` are set in `BgpAddressFamilyAllowasIn` (mutually exclusive).
- When both `warning_only` and `restart` are set in `BgpAddressFamilyMaximumPrefixAction` (mutually exclusive).
- When both `self` and `self_force` are set in `BgpAddressFamilyNextHop` (mutually exclusive).
- When both `all` and `replace_AS` are set in `BgpAddressFamilyRemovePrivateAS` (mutually exclusive).
- When more than one community type is set in `BgpAddressFamilySendCommunity` (at most one allowed).

## Model Validators

### OneOf Validators

- **validate_allowas_in_type** (in `BgpAddressFamilyAllowasIn`):
  Ensures that `origin` and `occurrence` are mutually exclusive. If both are set, it raises a `ValueError`.

- **validate_action_type** (in `BgpAddressFamilyMaximumPrefixAction`):
  Ensures that `warning_only` and `restart` are mutually exclusive. If both are set, it raises a `ValueError`.

- **validate_next_hop_type** (in `BgpAddressFamilyNextHop`):
  Ensures that `self` and `self_force` are mutually exclusive. If both are set, it raises a `ValueError`.

- **validate_remove_type** (in `BgpAddressFamilyRemovePrivateAS`):
  Ensures that `all` and `replace_AS` are mutually exclusive. If both are set, it raises a `ValueError`.

- **validate_send_community_type** (in `BgpAddressFamilySendCommunity`):
  Ensures that at most one send community type is set. If more than one of `all`, `both`, `extended`, `large`, or `standard` is configured, it raises a `ValueError`.

### Container Validation in `BgpAddressFamilyProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP Address Family Profile

#### Using a Dictionary

```python
from scm.models.network import BgpAddressFamilyProfileCreateModel

profile_data = {
    "name": "af-profile-1",
    "ipv4": {
        "unicast": {
            "enable": True,
            "soft_reconfig_with_stored_info": True,
            "add_path": {
                "tx_all_paths": True,
            },
            "allowas_in": {
                "occurrence": 3,
            },
            "maximum_prefix": {
                "num_prefixes": 10000,
                "threshold": 80,
                "action": {
                    "warning_only": {},
                },
            },
            "next_hop": {
                "self": {},
            },
            "send_community": {
                "all": {},
            },
        },
        "multicast": {
            "enable": True,
        },
    },
    "folder": "Routing",
}

# Validate and create model instance
profile = BgpAddressFamilyProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    BgpAddressFamilyProfileCreateModel,
    BgpAddressFamilyProfileIpv4UnicastMulticast,
    BgpAddressFamily,
    BgpAddressFamilyAddPath,
    BgpAddressFamilyAllowasIn,
    BgpAddressFamilyMaximumPrefix,
    BgpAddressFamilyMaximumPrefixAction,
    BgpAddressFamilyNextHop,
    BgpAddressFamilySendCommunity,
)

# Build address family configuration
unicast = BgpAddressFamily(
    enable=True,
    add_path=BgpAddressFamilyAddPath(tx_all_paths=True),
    allowas_in=BgpAddressFamilyAllowasIn(occurrence=3),
    maximum_prefix=BgpAddressFamilyMaximumPrefix(
        num_prefixes=10000,
        threshold=80,
        action=BgpAddressFamilyMaximumPrefixAction(warning_only={}),
    ),
    next_hop=BgpAddressFamilyNextHop(self_={}),
    send_community=BgpAddressFamilySendCommunity(all={}),
)

# Create the profile
profile = BgpAddressFamilyProfileCreateModel(
    name="af-profile-2",
    ipv4=BgpAddressFamilyProfileIpv4UnicastMulticast(
        unicast=unicast,
        multicast=BgpAddressFamily(enable=True),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a BGP Address Family Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.bgp_address_family_profile.fetch(name="af-profile-1", folder="Routing")

# Modify attributes
existing.ipv4.unicast.maximum_prefix.num_prefixes = 20000
existing.ipv4.unicast.maximum_prefix.threshold = 90

# Pass modified object to update()
updated = client.bgp_address_family_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

### Creating a Profile with Remove Private AS

```python
from scm.models.network import (
    BgpAddressFamilyProfileCreateModel,
    BgpAddressFamilyProfileIpv4UnicastMulticast,
    BgpAddressFamily,
    BgpAddressFamilyRemovePrivateAS,
)

profile = BgpAddressFamilyProfileCreateModel(
    name="af-profile-remove-private-as",
    ipv4=BgpAddressFamilyProfileIpv4UnicastMulticast(
        unicast=BgpAddressFamily(
            enable=True,
            remove_private_AS=BgpAddressFamilyRemovePrivateAS(all={}),
        ),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
