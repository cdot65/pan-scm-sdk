# BGP Route Map Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Route Map models provide a structured way to represent and validate BGP route map configuration data for Palo Alto Networks' Strata Cloud Manager. Route maps are ordered lists of entries, each with a sequence number, action (permit/deny), match criteria, and set actions. They are used to control BGP route advertisement, filtering, and attribute modification.

### Models

The module provides the following Pydantic models:

- `BgpRouteMapBaseModel`: Base model with fields common to all BGP route map operations
- `BgpRouteMapCreateModel`: Model for creating new BGP route maps
- `BgpRouteMapUpdateModel`: Model for updating existing BGP route maps
- `BgpRouteMapResponseModel`: Response model for BGP route map operations
- `BgpRouteMapEntry`: A single entry in a route map (sequence number + match/set)
- `BgpRouteMapMatch`: Match criteria for a route map entry
- `BgpRouteMapMatchIpv4`: IPv4-specific match criteria
- `BgpRouteMapSet`: Set actions for a route map entry
- `BgpRouteMapSetMetric`: Metric set action
- `BgpRouteMapSetAggregator`: Aggregator set configuration
- `BgpRouteMapSetIpv4`: IPv4-specific set configuration

The `BgpRouteMapBaseModel` and `BgpRouteMapCreateModel` / `BgpRouteMapUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The `BgpRouteMapResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

### API Quirks

- **Metric action typo:** The API uses `substract` (not `subtract`) as a valid metric action value. The SDK preserves this exact spelling to maintain API compatibility.
- **Aggregator `as` field:** The `as` field in `BgpRouteMapSetAggregator` uses the Python attribute name `as_` (with trailing underscore) to avoid conflict with the Python keyword `as`. The serialized alias is `as`.

## Model Attributes

### BgpRouteMapBaseModel

This is the base model containing fields common to all BGP route map operations.

| Attribute | Type                    | Required | Default | Description                                                     |
|-----------|-------------------------|----------|---------|-----------------------------------------------------------------|
| name      | str                     | Yes      | None    | Route map name.                                                 |
| route_map | List[BgpRouteMapEntry]  | No       | None    | List of route map entries.                                      |
| folder    | str                     | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet   | str                     | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device    | str                     | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpRouteMapCreateModel

Inherits all fields from `BgpRouteMapBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpRouteMapUpdateModel

Extends `BgpRouteMapBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                  |
|-----------|------|----------|---------|----------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP route map   |

### BgpRouteMapResponseModel

Extends `BgpRouteMapBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                  |
|-----------|------|----------|---------|----------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the BGP route map   |

> **Note:** The `BgpRouteMapResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### BgpRouteMapEntry

A single entry in a BGP route map with a sequence number, action, match criteria, and set actions.

| Attribute   | Type            | Required | Default | Description                                                |
|-------------|-----------------|----------|---------|------------------------------------------------------------|
| name        | int             | Yes      | None    | Sequence number for the route map entry (1-65535).         |
| description | str             | No       | None    | Entry description.                                         |
| action      | str             | No       | None    | Entry action. Pattern: `^(permit\|deny)$`                  |
| match       | BgpRouteMapMatch | No       | None    | Match criteria.                                           |
| set         | BgpRouteMapSet  | No       | None    | Set actions.                                               |

### BgpRouteMapMatch

Match criteria for a BGP route map entry.

| Attribute            | Type                | Required | Default | Description                                          |
|----------------------|---------------------|----------|---------|------------------------------------------------------|
| as_path_access_list  | str                 | No       | None    | AS path access list name.                            |
| interface            | str                 | No       | None    | Interface name to match.                             |
| regular_community    | str                 | No       | None    | Regular community to match.                          |
| origin               | str                 | No       | None    | Origin to match.                                     |
| large_community      | str                 | No       | None    | Large community to match.                            |
| tag                  | int                 | No       | None    | Tag value to match.                                  |
| extended_community   | str                 | No       | None    | Extended community to match.                         |
| local_preference     | int                 | No       | None    | Local preference to match.                           |
| metric               | int                 | No       | None    | Metric value to match.                               |
| peer                 | str                 | No       | None    | Peer type to match. Pattern: `^(local\|none)$`       |
| ipv4                 | BgpRouteMapMatchIpv4 | No      | None    | IPv4 match criteria.                                 |

### BgpRouteMapMatchIpv4

IPv4-specific match criteria.

| Attribute    | Type | Required | Default | Description                        |
|--------------|------|----------|---------|------------------------------------|
| address      | str  | No       | None    | IPv4 address prefix list to match. |
| next_hop     | str  | No       | None    | IPv4 next-hop prefix list to match.|
| route_source | str  | No       | None    | IPv4 route source to match.        |

### BgpRouteMapSet

Set actions for a BGP route map entry.

| Attribute                   | Type                     | Required | Default | Description                         |
|-----------------------------|--------------------------|----------|---------|-------------------------------------|
| atomic_aggregate            | bool                     | No       | None    | Set atomic aggregate.               |
| local_preference            | int                      | No       | None    | Local preference value to set.      |
| tag                         | int                      | No       | None    | Tag value to set.                   |
| metric                      | BgpRouteMapSetMetric     | No       | None    | Metric action.                      |
| weight                      | int                      | No       | None    | Weight value to set.                |
| origin                      | str                      | No       | None    | Origin to set. Pattern: `^(none\|egp\|igp\|incomplete)$` |
| remove_regular_community    | str                      | No       | None    | Regular community to remove.        |
| remove_large_community      | str                      | No       | None    | Large community to remove.          |
| originator_id               | str                      | No       | None    | Originator ID to set.               |
| aggregator                  | BgpRouteMapSetAggregator | No       | None    | Aggregator configuration.           |
| ipv4                        | BgpRouteMapSetIpv4       | No       | None    | IPv4 set configuration.             |
| aspath_exclude              | str                      | No       | None    | AS path to exclude.                 |
| aspath_prepend              | str                      | No       | None    | AS path to prepend.                 |
| regular_community           | List[str]                | No       | None    | Regular communities to set.         |
| overwrite_regular_community | bool                     | No       | None    | Overwrite existing regular communities. |
| large_community             | List[str]                | No       | None    | Large communities to set.           |
| overwrite_large_community   | bool                     | No       | None    | Overwrite existing large communities. |

### BgpRouteMapSetMetric

Metric set action for BGP route map entries.

| Attribute | Type | Required | Default | Description                                                                     |
|-----------|------|----------|---------|---------------------------------------------------------------------------------|
| action    | str  | No       | None    | Metric action type. Pattern: `^(set\|add\|substract)$` (note: API uses `substract`) |
| value     | int  | No       | None    | Metric value.                                                                   |

> **Important:** The `substract` spelling is intentional -- it matches the actual API spelling. Using `subtract` will result in a validation error.

### BgpRouteMapSetAggregator

Aggregator set configuration.

| Attribute | Type | Required | Default | Description                                        |
|-----------|------|----------|---------|----------------------------------------------------|
| as\_      | int  | No       | None    | Aggregator AS number. (alias: `as`)                |
| router_id | str  | No       | None    | Aggregator router ID.                              |

> **Important:** The Python attribute is `as_` (with trailing underscore) because `as` is a Python reserved keyword. When serializing, the field alias `as` is used.

### BgpRouteMapSetIpv4

IPv4-specific set configuration.

| Attribute      | Type | Required | Default | Description             |
|----------------|------|----------|---------|-------------------------|
| source_address | str  | No       | None    | Source address to set.   |
| next_hop       | str  | No       | None    | Next-hop address to set. |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a route map (`BgpRouteMapCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When an entry sequence number is outside the valid range (1-65535).
- When an entry action is not `permit` or `deny`.
- When an origin value is not one of `none`, `egp`, `igp`, or `incomplete`.
- When a metric action is not `set`, `add`, or `substract`.
- When a peer value is not `local` or `none`.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

### Container Validation in `BgpRouteMapCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP Route Map

#### Using a Dictionary

```python
from scm.models.network import BgpRouteMapCreateModel

route_map_data = {
    "name": "route-map-1",
    "route_map": [
        {
            "name": 10,
            "description": "Match and set local preference",
            "action": "permit",
            "match": {
                "as_path_access_list": "as-path-list-1",
                "ipv4": {
                    "address": "prefix-list-inbound",
                },
            },
            "set": {
                "local_preference": 200,
                "weight": 100,
            },
        },
        {
            "name": 20,
            "action": "permit",
            "set": {
                "metric": {
                    "action": "set",
                    "value": 50,
                },
            },
        },
        {
            "name": 100,
            "action": "deny",
        },
    ],
    "folder": "Routing",
}

# Validate and create model instance
route_map = BgpRouteMapCreateModel(**route_map_data)
payload = route_map.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import (
    BgpRouteMapCreateModel,
    BgpRouteMapEntry,
    BgpRouteMapMatch,
    BgpRouteMapMatchIpv4,
    BgpRouteMapSet,
    BgpRouteMapSetMetric,
    BgpRouteMapSetAggregator,
)

# Build route map entries
entries = [
    BgpRouteMapEntry(
        name=10,
        description="Set communities",
        action="permit",
        match=BgpRouteMapMatch(
            ipv4=BgpRouteMapMatchIpv4(address="prefix-list-1"),
        ),
        set=BgpRouteMapSet(
            local_preference=200,
            regular_community=["65000:100", "65000:200"],
            overwrite_regular_community=True,
        ),
    ),
    BgpRouteMapEntry(
        name=20,
        action="permit",
        set=BgpRouteMapSet(
            metric=BgpRouteMapSetMetric(action="add", value=10),
            aspath_prepend="65001 65001",
        ),
    ),
    BgpRouteMapEntry(
        name=30,
        action="permit",
        set=BgpRouteMapSet(
            aggregator=BgpRouteMapSetAggregator(as_=65000, router_id="1.1.1.1"),
            atomic_aggregate=True,
        ),
    ),
]

# Create the route map
route_map = BgpRouteMapCreateModel(
    name="route-map-2",
    route_map=entries,
    folder="Routing",
)
payload = route_map.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a BGP Route Map

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing route map
existing = client.bgp_route_map.fetch(name="route-map-1", folder="Routing")

# Modify the local preference in entry 10
for entry in existing.route_map:
    if entry.name == 10:
        entry.set.local_preference = 300

# Pass modified object to update()
updated = client.bgp_route_map.update(existing)
print(f"Updated route map: {updated.name}")
```

### Using Metric Subtract (API Typo)

```python
from scm.models.network import (
    BgpRouteMapCreateModel,
    BgpRouteMapEntry,
    BgpRouteMapSet,
    BgpRouteMapSetMetric,
)

# Note: use 'substract' (not 'subtract') to match the API spelling
route_map = BgpRouteMapCreateModel(
    name="route-map-metric-sub",
    route_map=[
        BgpRouteMapEntry(
            name=10,
            action="permit",
            set=BgpRouteMapSet(
                metric=BgpRouteMapSetMetric(
                    action="substract",  # API typo preserved
                    value=20,
                ),
            ),
        ),
    ],
    folder="Routing",
)
payload = route_map.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
