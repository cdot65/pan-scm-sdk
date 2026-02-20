# BGP Filtering Profile Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Filtering Profile models provide a structured way to represent and validate BGP filtering profile configuration data for Palo Alto Networks' Strata Cloud Manager. These models manage route filtering through filter lists, network filters (distribute lists and prefix lists), route maps, conditional advertisement, and unsuppress maps. The IPv4 configuration supports separate unicast and multicast filtering, with multicast supporting either inheritance from unicast or its own independent filter configuration.

### Models

The module provides the following Pydantic models:

- `BgpFilteringProfileBaseModel`: Base model with fields common to all BGP filtering profile operations
- `BgpFilteringProfileCreateModel`: Model for creating new BGP filtering profiles
- `BgpFilteringProfileUpdateModel`: Model for updating existing BGP filtering profiles
- `BgpFilteringProfileResponseModel`: Response model for BGP filtering profile operations
- `BgpFilteringProfileIpv4`: IPv4 container with unicast and multicast filtering
- `BgpFilter`: Shared BGP filter schema used by unicast
- `BgpFilteringProfileMulticast`: Multicast filtering (oneOf: inherit or filter fields)
- `BgpFilterList`: Filter list with inbound/outbound references
- `BgpNetworkFilters`: Network filters with distribute_list and prefix_list
- `BgpRouteMaps`: Route maps with inbound/outbound references
- `BgpConditionalAdvertisement`: Conditional advertisement with exist/non_exist conditions
- `BgpConditionalAdvertisementCondition`: Condition for conditional advertisement

The `BgpFilteringProfileBaseModel` and `BgpFilteringProfileCreateModel` / `BgpFilteringProfileUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `BgpFilteringProfileResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### BgpFilteringProfileBaseModel

This is the base model containing fields common to all BGP filtering profile operations.

| Attribute | Type                      | Required | Default | Description                                                     |
|-----------|---------------------------|----------|---------|-----------------------------------------------------------------|
| name      | str                       | Yes      | None    | Profile name.                                                   |
| ipv4      | BgpFilteringProfileIpv4   | No       | None    | IPv4 filtering configuration.                                   |
| folder    | str                       | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                       | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                       | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpFilteringProfileCreateModel

Inherits all fields from `BgpFilteringProfileBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpFilteringProfileUpdateModel

Extends `BgpFilteringProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                          |
|-----------|------|----------|---------|------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP filtering profile   |

### BgpFilteringProfileResponseModel

Extends `BgpFilteringProfileBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                          |
|-----------|------|----------|---------|------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP filtering profile   |

> **Note:** The `BgpFilteringProfileResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### BgpFilteringProfileIpv4

IPv4 container with unicast and multicast filtering.

| Attribute | Type                         | Required | Default | Description           |
|-----------|------------------------------|----------|---------|-----------------------|
| unicast   | BgpFilter                    | No       | None    | Unicast filtering.    |
| multicast | BgpFilteringProfileMulticast | No       | None    | Multicast filtering.  |

### BgpFilter

Shared BGP filter schema used by unicast filtering.

| Attribute                 | Type                         | Required | Default | Description                          |
|---------------------------|------------------------------|----------|---------|--------------------------------------|
| filter_list               | BgpFilterList                | No       | None    | Filter list configuration.           |
| inbound_network_filters   | BgpNetworkFilters            | No       | None    | Inbound network filters.             |
| outbound_network_filters  | BgpNetworkFilters            | No       | None    | Outbound network filters.            |
| route_maps                | BgpRouteMaps                 | No       | None    | Route maps configuration.            |
| conditional_advertisement | BgpConditionalAdvertisement  | No       | None    | Conditional advertisement config.    |
| unsuppress_map            | str                          | No       | None    | Unsuppress map name.                 |

### BgpFilteringProfileMulticast

IPv4 multicast filtering. Uses oneOf semantics: `inherit` and filter fields are mutually exclusive. When `inherit=True`, no other filter fields should be set. When filter fields are set, `inherit` should not be set.

| Attribute                 | Type                         | Required | Default | Description                          |
|---------------------------|------------------------------|----------|---------|--------------------------------------|
| inherit                   | bool                         | No*      | None    | Inherit filtering from unicast.      |
| filter_list               | BgpFilterList                | No*      | None    | Filter list configuration.           |
| inbound_network_filters   | BgpNetworkFilters            | No*      | None    | Inbound network filters.             |
| outbound_network_filters  | BgpNetworkFilters            | No*      | None    | Outbound network filters.            |
| route_maps                | BgpRouteMaps                 | No*      | None    | Route maps configuration.            |
| conditional_advertisement | BgpConditionalAdvertisement  | No*      | None    | Conditional advertisement config.    |
| unsuppress_map            | str                          | No*      | None    | Unsuppress map name.                 |

\* `inherit` and filter fields (`filter_list`, `inbound_network_filters`, `outbound_network_filters`, `route_maps`, `conditional_advertisement`, `unsuppress_map`) are mutually exclusive.

### BgpFilterList

Filter list with inbound and outbound references.

| Attribute | Type | Required | Default | Description               |
|-----------|------|----------|---------|---------------------------|
| inbound   | str  | No       | None    | Inbound filter list name. |
| outbound  | str  | No       | None    | Outbound filter list name.|

### BgpNetworkFilters

Network filters with distribute list and prefix list options.

| Attribute       | Type | Required | Default | Description          |
|-----------------|------|----------|---------|----------------------|
| distribute_list | str  | No       | None    | Distribute list name.|
| prefix_list     | str  | No       | None    | Prefix list name.    |

### BgpRouteMaps

Route maps with inbound and outbound references.

| Attribute | Type | Required | Default | Description              |
|-----------|------|----------|---------|--------------------------|
| inbound   | str  | No       | None    | Inbound route map name.  |
| outbound  | str  | No       | None    | Outbound route map name. |

### BgpConditionalAdvertisement

Conditional advertisement with exist and non-exist conditions.

| Attribute | Type                                    | Required | Default | Description          |
|-----------|-----------------------------------------|----------|---------|----------------------|
| exist     | BgpConditionalAdvertisementCondition    | No       | None    | Exist condition.     |
| non_exist | BgpConditionalAdvertisementCondition    | No       | None    | Non-exist condition. |

### BgpConditionalAdvertisementCondition

Condition for conditional advertisement.

| Attribute     | Type | Required | Default | Description          |
|---------------|------|----------|---------|----------------------|
| advertise_map | str  | No       | None    | Advertise map name.  |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a profile (`BgpFilteringProfileCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When `inherit` is set alongside any filter fields in `BgpFilteringProfileMulticast` (mutually exclusive).
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### OneOf Validator in `BgpFilteringProfileMulticast`

- **validate_multicast_type**:
  Ensures that `inherit` and filter fields are mutually exclusive. If `inherit` is set and any of `filter_list`, `inbound_network_filters`, `outbound_network_filters`, `route_maps`, `conditional_advertisement`, or `unsuppress_map` are also set, it raises a `ValueError`. This enforces the oneOf semantics where multicast filtering either inherits from unicast or defines its own independent filters.

### Container Validation in `BgpFilteringProfileCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP Filtering Profile with Unicast Filters

#### Using a Dictionary

```python
from scm.models.network import BgpFilteringProfileCreateModel

profile_data = {
    "name": "filter-profile-1",
    "ipv4": {
        "unicast": {
            "filter_list": {
                "inbound": "as-path-filter-in",
                "outbound": "as-path-filter-out",
            },
            "inbound_network_filters": {
                "prefix_list": "prefix-list-inbound",
            },
            "outbound_network_filters": {
                "distribute_list": "distribute-list-outbound",
            },
            "route_maps": {
                "inbound": "route-map-in",
                "outbound": "route-map-out",
            },
        },
        "multicast": {
            "inherit": True,
        },
    },
    "folder": "Routing",
}

# Validate and create model instance
profile = BgpFilteringProfileCreateModel(**profile_data)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    BgpFilteringProfileCreateModel,
    BgpFilteringProfileIpv4,
    BgpFilter,
    BgpFilteringProfileMulticast,
    BgpFilterList,
    BgpNetworkFilters,
    BgpRouteMaps,
)

# Build unicast filters
unicast = BgpFilter(
    filter_list=BgpFilterList(
        inbound="as-path-filter-in",
        outbound="as-path-filter-out",
    ),
    inbound_network_filters=BgpNetworkFilters(
        prefix_list="prefix-list-inbound",
    ),
    route_maps=BgpRouteMaps(
        inbound="route-map-in",
        outbound="route-map-out",
    ),
)

# Create the profile with multicast inheriting from unicast
profile = BgpFilteringProfileCreateModel(
    name="filter-profile-2",
    ipv4=BgpFilteringProfileIpv4(
        unicast=unicast,
        multicast=BgpFilteringProfileMulticast(inherit=True),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Profile with Independent Multicast Filters

```python
from scm.models.network import (
    BgpFilteringProfileCreateModel,
    BgpFilteringProfileIpv4,
    BgpFilter,
    BgpFilteringProfileMulticast,
    BgpRouteMaps,
    BgpConditionalAdvertisement,
    BgpConditionalAdvertisementCondition,
)

# Multicast with its own filter configuration (not inheriting)
profile = BgpFilteringProfileCreateModel(
    name="filter-profile-multicast",
    ipv4=BgpFilteringProfileIpv4(
        unicast=BgpFilter(
            route_maps=BgpRouteMaps(inbound="unicast-rm-in"),
        ),
        multicast=BgpFilteringProfileMulticast(
            route_maps=BgpRouteMaps(
                inbound="multicast-rm-in",
                outbound="multicast-rm-out",
            ),
            conditional_advertisement=BgpConditionalAdvertisement(
                exist=BgpConditionalAdvertisementCondition(
                    advertise_map="cond-adv-map",
                ),
            ),
        ),
    ),
    folder="Routing",
)
payload = profile.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a BGP Filtering Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing profile
existing = client.bgp_filtering_profile.fetch(name="filter-profile-1", folder="Routing")

# Add an unsuppress map to unicast
existing.ipv4.unicast.unsuppress_map = "my-unsuppress-map"

# Pass modified object to update()
updated = client.bgp_filtering_profile.update(existing)
print(f"Updated profile: {updated.name}")
```
