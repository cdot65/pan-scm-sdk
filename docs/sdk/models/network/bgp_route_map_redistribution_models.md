# BGP Route Map Redistribution Models

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Model Attributes](#model-attributes)
4. [Source Protocol Models](#source-protocol-models)
5. [Target Container Models](#target-container-models)
6. [Route Map Entry Models](#route-map-entry-models)
7. [Match Models](#match-models)
8. [Set Models](#set-models)
9. [Exceptions](#exceptions)
10. [Model Validators](#model-validators)
11. [Usage Examples](#usage-examples)

## Overview {#Overview}

The BGP Route Map Redistribution models provide a structured way to represent and validate BGP route map redistribution configuration data for Palo Alto Networks' Strata Cloud Manager. This is the most complex model in the routing profile family, implementing a **2-level oneOf discrimination pattern** that determines which match criteria and set actions are available based on the source and target protocol combination.

### Models

The module provides 31 Pydantic model classes organized into the following categories:

**Main Models (4):**

- `BgpRouteMapRedistributionBaseModel`: Base model with 2-level oneOf source protocol discrimination
- `BgpRouteMapRedistributionCreateModel`: Model for creating new redistributions
- `BgpRouteMapRedistributionUpdateModel`: Model for updating existing redistributions
- `BgpRouteMapRedistributionResponseModel`: Response model for redistribution operations

**Source Protocol Models (3) - Level 1 Discrimination:**

- `BgpRouteMapRedistBgpSource`: BGP as source with targets ospf or rib
- `BgpRouteMapRedistOspfSource`: OSPF as source with targets bgp or rib
- `BgpRouteMapRedistConnectedStaticSource`: Connected/Static as source with targets bgp, ospf, or rib

**Target Container Models (7):**

- `BgpRouteMapRedistBgpToOspf`, `BgpRouteMapRedistBgpToRib`
- `BgpRouteMapRedistOspfToBgp`, `BgpRouteMapRedistOspfToRib`
- `BgpRouteMapRedistConnStaticToBgp`, `BgpRouteMapRedistConnStaticToOspf`, `BgpRouteMapRedistConnStaticToRib`

**Route Map Entry Models (7 crossover variants):**

- `BgpRouteMapRedistBgpToOspfEntry`, `BgpRouteMapRedistBgpToRibEntry`
- `BgpRouteMapRedistOspfToBgpEntry`, `BgpRouteMapRedistOspfToRibEntry`
- `BgpRouteMapRedistConnStaticToBgpEntry`, `BgpRouteMapRedistConnStaticToOspfEntry`, `BgpRouteMapRedistConnStaticToRibEntry`

**Match Models (4):**

- `BgpRouteMapRedistBgpMatch`: Full BGP match criteria (for BGP source)
- `BgpRouteMapRedistBgpMatchIpv4`: IPv4 match criteria for BGP source
- `BgpRouteMapRedistSimpleMatch`: Simple match criteria (for OSPF/connected-static source)
- `BgpRouteMapRedistSimpleMatchIpv4`: IPv4 match criteria for OSPF/connected-static source

**Set Models (6):**

- `BgpRouteMapRedistSetToBgp`: Full BGP set actions (when target is BGP)
- `BgpRouteMapRedistSetToOspf`: OSPF set actions (metric, metric_type, tag)
- `BgpRouteMapRedistSetToRib`: RIB set actions (source_address only)
- `BgpRouteMapRedistSetMetric`: Metric set action
- `BgpRouteMapRedistSetAggregator`: Aggregator set configuration
- `BgpRouteMapRedistSetIpv4`: IPv4 set configuration

## Architecture

### 2-Level OneOf Discrimination Pattern

The BGP route map redistribution model uses a hierarchical oneOf pattern to determine valid configurations:

```
BgpRouteMapRedistributionBaseModel
|
+-- Level 1: Source Protocol (mutually exclusive)
|   +-- bgp (BgpRouteMapRedistBgpSource)
|   |   +-- Level 2: Target (mutually exclusive)
|   |       +-- ospf  -> BgpRouteMapRedistBgpToOspf
|   |       +-- rib   -> BgpRouteMapRedistBgpToRib
|   |
|   +-- ospf (BgpRouteMapRedistOspfSource)
|   |   +-- Level 2: Target (mutually exclusive)
|   |       +-- bgp   -> BgpRouteMapRedistOspfToBgp
|   |       +-- rib   -> BgpRouteMapRedistOspfToRib
|   |
|   +-- connected_static (BgpRouteMapRedistConnectedStaticSource)
|       +-- Level 2: Target (mutually exclusive)
|           +-- bgp   -> BgpRouteMapRedistConnStaticToBgp
|           +-- ospf  -> BgpRouteMapRedistConnStaticToOspf
|           +-- rib   -> BgpRouteMapRedistConnStaticToRib
```

### Source -> Target Crossover Matrix

The source protocol determines the available match criteria, and the target protocol determines the available set actions. This creates 7 unique crossover variants:

| Source           | Target | Match Model             | Set Model                  | Entry Model                          |
|------------------|--------|-------------------------|----------------------------|--------------------------------------|
| BGP              | OSPF   | BgpRouteMapRedistBgpMatch | BgpRouteMapRedistSetToOspf | BgpRouteMapRedistBgpToOspfEntry      |
| BGP              | RIB    | BgpRouteMapRedistBgpMatch | BgpRouteMapRedistSetToRib  | BgpRouteMapRedistBgpToRibEntry       |
| OSPF             | BGP    | BgpRouteMapRedistSimpleMatch | BgpRouteMapRedistSetToBgp | BgpRouteMapRedistOspfToBgpEntry     |
| OSPF             | RIB    | BgpRouteMapRedistSimpleMatch | BgpRouteMapRedistSetToRib | BgpRouteMapRedistOspfToRibEntry     |
| Connected/Static | BGP    | BgpRouteMapRedistSimpleMatch | BgpRouteMapRedistSetToBgp | BgpRouteMapRedistConnStaticToBgpEntry |
| Connected/Static | OSPF   | BgpRouteMapRedistSimpleMatch | BgpRouteMapRedistSetToOspf | BgpRouteMapRedistConnStaticToOspfEntry |
| Connected/Static | RIB    | BgpRouteMapRedistSimpleMatch | BgpRouteMapRedistSetToRib | BgpRouteMapRedistConnStaticToRibEntry |

### Key Design Principles

1. **Match fields depend on the source protocol:** BGP sources have richer match criteria (AS path, communities, origin, etc.), while OSPF and connected/static sources have simpler match criteria (interface, metric, tag, IPv4 address/next-hop).

2. **Set fields depend on the target protocol:** When redistributing to BGP, the full set of BGP attributes is available. When redistributing to OSPF, only metric, metric_type, and tag are available. When redistributing to RIB, only source_address is available.

3. **Source protocols are mutually exclusive (Level 1):** Only one of `bgp`, `ospf`, or `connected_static` can be set.

4. **Target protocols within a source are mutually exclusive (Level 2):** Within each source, only one target can be set.

## Model Attributes

### BgpRouteMapRedistributionBaseModel

This is the base model containing fields for the 2-level oneOf discrimination.

| Attribute         | Type                                     | Required | Default | Description                                                     |
|-------------------|------------------------------------------|----------|---------|-----------------------------------------------------------------|
| name              | str                                      | Yes      | None    | Redistribution name.                                            |
| bgp               | BgpRouteMapRedistBgpSource               | No*      | None    | BGP as source protocol.                                         |
| ospf              | BgpRouteMapRedistOspfSource              | No*      | None    | OSPF as source protocol.                                        |
| connected_static  | BgpRouteMapRedistConnectedStaticSource   | No*      | None    | Connected/Static as source protocol.                            |
| folder            | str                                      | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet           | str                                      | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device            | str                                      | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\* At most one source protocol (`bgp`, `ospf`, or `connected_static`) can be set.

\** Exactly one container (folder/snippet/device) must be provided for create operations

### BgpRouteMapRedistributionCreateModel

Inherits all fields from `BgpRouteMapRedistributionBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### BgpRouteMapRedistributionUpdateModel

Extends `BgpRouteMapRedistributionBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                                |
|-----------|------|----------|---------|------------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route map redistribution      |

### BgpRouteMapRedistributionResponseModel

Extends `BgpRouteMapRedistributionBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                                |
|-----------|------|----------|---------|------------------------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the route map redistribution      |

> **Note:** The `BgpRouteMapRedistributionResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Source Protocol Models

### BgpRouteMapRedistBgpSource

BGP source protocol. Target protocols (ospf, rib) are mutually exclusive.

| Attribute | Type                        | Required | Default | Description                       |
|-----------|-----------------------------|----------|---------|-----------------------------------|
| ospf      | BgpRouteMapRedistBgpToOspf  | No*      | None    | Redistribute BGP routes to OSPF.  |
| rib       | BgpRouteMapRedistBgpToRib   | No*      | None    | Redistribute BGP routes to RIB.   |

\* Only one of `ospf` or `rib` can be set.

### BgpRouteMapRedistOspfSource

OSPF source protocol. Target protocols (bgp, rib) are mutually exclusive.

| Attribute | Type                         | Required | Default | Description                        |
|-----------|------------------------------|----------|---------|------------------------------------|
| bgp       | BgpRouteMapRedistOspfToBgp   | No*      | None    | Redistribute OSPF routes to BGP.   |
| rib       | BgpRouteMapRedistOspfToRib   | No*      | None    | Redistribute OSPF routes to RIB.   |

\* Only one of `bgp` or `rib` can be set.

### BgpRouteMapRedistConnectedStaticSource

Connected/Static source protocol. Target protocols (bgp, ospf, rib) are mutually exclusive.

| Attribute | Type                                  | Required | Default | Description                                       |
|-----------|---------------------------------------|----------|---------|---------------------------------------------------|
| bgp       | BgpRouteMapRedistConnStaticToBgp      | No*      | None    | Redistribute connected/static routes to BGP.      |
| ospf      | BgpRouteMapRedistConnStaticToOspf     | No*      | None    | Redistribute connected/static routes to OSPF.     |
| rib       | BgpRouteMapRedistConnStaticToRib      | No*      | None    | Redistribute connected/static routes to RIB.      |

\* Only one of `bgp`, `ospf`, or `rib` can be set.

## Target Container Models

Each target container holds a list of route map entries specific to the source->target combination.

### BgpRouteMapRedistBgpToOspf / BgpRouteMapRedistBgpToRib

| Attribute | Type                                                    | Required | Default | Description        |
|-----------|---------------------------------------------------------|----------|---------|--------------------|
| route_map | List[BgpRouteMapRedistBgpToOspfEntry] or List[BgpRouteMapRedistBgpToRibEntry] | No | None | Route map entries. |

### BgpRouteMapRedistOspfToBgp / BgpRouteMapRedistOspfToRib

| Attribute | Type                                                      | Required | Default | Description        |
|-----------|-----------------------------------------------------------|----------|---------|--------------------|
| route_map | List[BgpRouteMapRedistOspfToBgpEntry] or List[BgpRouteMapRedistOspfToRibEntry] | No | None | Route map entries. |

### BgpRouteMapRedistConnStaticToBgp / BgpRouteMapRedistConnStaticToOspf / BgpRouteMapRedistConnStaticToRib

| Attribute | Type                                  | Required | Default | Description        |
|-----------|---------------------------------------|----------|---------|--------------------|
| route_map | List[variant-specific Entry model]    | No       | None    | Route map entries. |

## Route Map Entry Models

All 7 entry variants share the same base structure but use different match and set model types:

| Attribute   | Type                     | Required | Default | Description                                  |
|-------------|--------------------------|----------|---------|----------------------------------------------|
| name        | int                      | Yes      | None    | Sequence number (1-65535).                    |
| description | str                      | No       | None    | Entry description.                            |
| action      | str                      | No       | None    | Entry action. Pattern: `^(permit\|deny)$`     |
| match       | (variant-specific Match) | No       | None    | Match criteria (depends on source protocol).  |
| set         | (variant-specific Set)   | No       | None    | Set actions (depends on target protocol).     |

## Match Models

### BgpRouteMapRedistBgpMatch

Full BGP match criteria, used when BGP is the source protocol. Provides richer matching capabilities including AS path, communities, and origin.

| Attribute           | Type                            | Required | Default | Description                                  |
|---------------------|---------------------------------|----------|---------|----------------------------------------------|
| as_path_access_list | str                             | No       | None    | AS path access list name.                    |
| regular_community   | str                             | No       | None    | Regular community to match.                  |
| large_community     | str                             | No       | None    | Large community to match.                    |
| extended_community  | str                             | No       | None    | Extended community to match.                 |
| interface           | str                             | No       | None    | Interface to match.                          |
| tag                 | int                             | No       | None    | Tag value to match.                          |
| local_preference    | int                             | No       | None    | Local preference to match.                   |
| metric              | int                             | No       | None    | Metric to match.                             |
| origin              | str                             | No       | None    | Origin to match.                             |
| peer                | str                             | No       | None    | Peer type to match. Pattern: `^(local\|none)$` |
| ipv4                | BgpRouteMapRedistBgpMatchIpv4   | No       | None    | IPv4 match criteria.                         |

### BgpRouteMapRedistBgpMatchIpv4

IPv4 match criteria for BGP source redistribution. Includes `route_source` which is not available in the simple match variant.

| Attribute    | Type | Required | Default | Description                        |
|--------------|------|----------|---------|------------------------------------|
| address      | str  | No       | None    | IPv4 address prefix list to match. |
| next_hop     | str  | No       | None    | IPv4 next-hop prefix list to match.|
| route_source | str  | No       | None    | IPv4 route source to match.        |

### BgpRouteMapRedistSimpleMatch

Simplified match criteria, used when OSPF or connected/static is the source protocol.

| Attribute | Type                                 | Required | Default | Description           |
|-----------|--------------------------------------|----------|---------|-----------------------|
| interface | str                                  | No       | None    | Interface to match.   |
| metric    | int                                  | No       | None    | Metric to match.      |
| tag       | int                                  | No       | None    | Tag to match.         |
| ipv4      | BgpRouteMapRedistSimpleMatchIpv4     | No       | None    | IPv4 match criteria.  |

### BgpRouteMapRedistSimpleMatchIpv4

IPv4 match criteria for OSPF/connected-static source. Does NOT include `route_source`.

| Attribute | Type | Required | Default | Description                        |
|-----------|------|----------|---------|------------------------------------|
| address   | str  | No       | None    | IPv4 address prefix list to match. |
| next_hop  | str  | No       | None    | IPv4 next-hop prefix list to match.|

## Set Models

### BgpRouteMapRedistSetToBgp

Full BGP set actions, used when the target protocol is BGP. Provides the richest set of configurable attributes.

| Attribute                   | Type                            | Required | Default | Description                         |
|-----------------------------|----------------------------------|----------|---------|-------------------------------------|
| atomic_aggregate            | bool                             | No       | None    | Set atomic aggregate.               |
| local_preference            | int                              | No       | None    | Local preference to set.            |
| tag                         | int                              | No       | None    | Tag to set.                         |
| metric                      | BgpRouteMapRedistSetMetric       | No       | None    | Metric action.                      |
| weight                      | int                              | No       | None    | Weight to set.                      |
| origin                      | str                              | No       | None    | Origin to set. Pattern: `^(none\|egp\|igp\|incomplete)$` |
| remove_regular_community    | str                              | No       | None    | Community to remove.                |
| remove_large_community      | str                              | No       | None    | Large community to remove.          |
| originator_id               | str                              | No       | None    | Originator ID to set.               |
| aggregator                  | BgpRouteMapRedistSetAggregator   | No       | None    | Aggregator config.                  |
| ipv4                        | BgpRouteMapRedistSetIpv4         | No       | None    | IPv4 set config.                    |
| aspath_exclude              | str                              | No       | None    | AS path to exclude.                 |
| aspath_prepend              | str                              | No       | None    | AS path to prepend.                 |
| regular_community           | List[str]                        | No       | None    | Communities to set.                 |
| overwrite_regular_community | bool                             | No       | None    | Overwrite communities.              |
| large_community             | List[str]                        | No       | None    | Large communities to set.           |
| overwrite_large_community   | bool                             | No       | None    | Overwrite large communities.        |

### BgpRouteMapRedistSetToOspf

OSPF set actions, used when the target protocol is OSPF. Limited to metric, metric type, and tag.

| Attribute   | Type                         | Required | Default | Description        |
|-------------|------------------------------|----------|---------|--------------------|
| metric      | BgpRouteMapRedistSetMetric   | No       | None    | Metric action.     |
| metric_type | str                          | No       | None    | OSPF metric type.  |
| tag         | int                          | No       | None    | Tag to set.        |

### BgpRouteMapRedistSetToRib

RIB set actions, used when the target is the routing table. Only source address is configurable.

| Attribute | Type                       | Required | Default | Description             |
|-----------|----------------------------|----------|---------|-------------------------|
| ipv4      | BgpRouteMapRedistSetIpv4   | No       | None    | IPv4 set (source_address).|

### BgpRouteMapRedistSetMetric

Metric set action.

| Attribute | Type | Required | Default | Description                                                                     |
|-----------|------|----------|---------|---------------------------------------------------------------------------------|
| action    | str  | No       | None    | Metric action type. Pattern: `^(set\|add\|substract)$` (note: API uses `substract`) |
| value     | int  | No       | None    | Metric value.                                                                   |

> **Important:** The `substract` spelling is intentional -- it matches the actual API spelling.

### BgpRouteMapRedistSetAggregator

Aggregator set configuration.

| Attribute | Type | Required | Default | Description                          |
|-----------|------|----------|---------|--------------------------------------|
| as\_      | int  | No       | None    | Aggregator AS number. (alias: `as`)  |
| router_id | str  | No       | None    | Aggregator router ID.                |

> **Important:** The Python attribute is `as_` (with trailing underscore) because `as` is a Python reserved keyword. The serialized alias is `as`.

### BgpRouteMapRedistSetIpv4

IPv4 set configuration.

| Attribute      | Type | Required | Default | Description             |
|----------------|------|----------|---------|-------------------------|
| source_address | str  | No       | None    | Source address to set.   |
| next_hop       | str  | No       | None    | Next-hop to set.         |

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a redistribution (`BgpRouteMapRedistributionCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When more than one source protocol (`bgp`, `ospf`, `connected_static`) is set (Level 1 oneOf violation).
- When more than one target protocol is set within a source (Level 2 oneOf violation).
- When an entry sequence number is outside the valid range (1-65535).
- When an entry action is not `permit` or `deny`.
- When a metric action is not `set`, `add`, or `substract`.

## Model Validators

### Level 1 OneOf Validator in `BgpRouteMapRedistributionBaseModel`

- **validate_source_type**:
  Ensures that at most one source protocol is set. If more than one of `bgp`, `ospf`, or `connected_static` is configured, it raises a `ValueError`.

### Level 2 OneOf Validators in Source Protocol Models

- **validate_target_type** (in `BgpRouteMapRedistBgpSource`):
  Ensures that only one of `ospf` or `rib` is set for BGP source.

- **validate_target_type** (in `BgpRouteMapRedistOspfSource`):
  Ensures that only one of `bgp` or `rib` is set for OSPF source.

- **validate_target_type** (in `BgpRouteMapRedistConnectedStaticSource`):
  Ensures that only one of `bgp`, `ospf`, or `rib` is set for connected/static source.

### Container Validation in `BgpRouteMapRedistributionCreateModel`

- **validate_container_type**:
  After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a BGP-to-OSPF Redistribution

```python
from scm.models.network import BgpRouteMapRedistributionCreateModel

redist_data = {
    "name": "bgp-to-ospf-redist",
    "bgp": {
        "ospf": {
            "route_map": [
                {
                    "name": 10,
                    "action": "permit",
                    "match": {
                        "as_path_access_list": "my-as-path-list",
                        "regular_community": "my-community",
                        "ipv4": {
                            "address": "prefix-list-1",
                        },
                    },
                    "set": {
                        "metric": {
                            "action": "set",
                            "value": 100,
                        },
                        "metric_type": "type-2",
                        "tag": 1000,
                    },
                },
                {
                    "name": 100,
                    "action": "deny",
                },
            ],
        },
    },
    "folder": "Routing",
}

redist = BgpRouteMapRedistributionCreateModel(**redist_data)
payload = redist.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating an OSPF-to-BGP Redistribution

```python
from scm.models.network import (
    BgpRouteMapRedistributionCreateModel,
    BgpRouteMapRedistOspfSource,
    BgpRouteMapRedistOspfToBgp,
    BgpRouteMapRedistOspfToBgpEntry,
    BgpRouteMapRedistSimpleMatch,
    BgpRouteMapRedistSimpleMatchIpv4,
    BgpRouteMapRedistSetToBgp,
)

# OSPF -> BGP redistribution with simple match and full BGP set actions
redist = BgpRouteMapRedistributionCreateModel(
    name="ospf-to-bgp-redist",
    ospf=BgpRouteMapRedistOspfSource(
        bgp=BgpRouteMapRedistOspfToBgp(
            route_map=[
                BgpRouteMapRedistOspfToBgpEntry(
                    name=10,
                    action="permit",
                    match=BgpRouteMapRedistSimpleMatch(
                        interface="ethernet1/1",
                        ipv4=BgpRouteMapRedistSimpleMatchIpv4(
                            address="prefix-list-ospf",
                        ),
                    ),
                    set=BgpRouteMapRedistSetToBgp(
                        local_preference=200,
                        weight=100,
                        regular_community=["65000:100"],
                        overwrite_regular_community=True,
                    ),
                ),
            ],
        ),
    ),
    folder="Routing",
)
payload = redist.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Connected/Static-to-BGP Redistribution

```python
from scm.models.network import (
    BgpRouteMapRedistributionCreateModel,
    BgpRouteMapRedistConnectedStaticSource,
    BgpRouteMapRedistConnStaticToBgp,
    BgpRouteMapRedistConnStaticToBgpEntry,
    BgpRouteMapRedistSimpleMatch,
    BgpRouteMapRedistSetToBgp,
    BgpRouteMapRedistSetMetric,
)

# Connected/Static -> BGP redistribution
redist = BgpRouteMapRedistributionCreateModel(
    name="conn-static-to-bgp",
    connected_static=BgpRouteMapRedistConnectedStaticSource(
        bgp=BgpRouteMapRedistConnStaticToBgp(
            route_map=[
                BgpRouteMapRedistConnStaticToBgpEntry(
                    name=10,
                    description="Redistribute connected with metric",
                    action="permit",
                    match=BgpRouteMapRedistSimpleMatch(
                        tag=500,
                    ),
                    set=BgpRouteMapRedistSetToBgp(
                        metric=BgpRouteMapRedistSetMetric(
                            action="set",
                            value=50,
                        ),
                        local_preference=150,
                    ),
                ),
            ],
        ),
    ),
    folder="Routing",
)
payload = redist.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Connected/Static-to-RIB Redistribution

```python
from scm.models.network import (
    BgpRouteMapRedistributionCreateModel,
    BgpRouteMapRedistConnectedStaticSource,
    BgpRouteMapRedistConnStaticToRib,
    BgpRouteMapRedistConnStaticToRibEntry,
    BgpRouteMapRedistSetToRib,
    BgpRouteMapRedistSetIpv4,
)

# Connected/Static -> RIB redistribution (minimal set actions)
redist = BgpRouteMapRedistributionCreateModel(
    name="conn-static-to-rib",
    connected_static=BgpRouteMapRedistConnectedStaticSource(
        rib=BgpRouteMapRedistConnStaticToRib(
            route_map=[
                BgpRouteMapRedistConnStaticToRibEntry(
                    name=10,
                    action="permit",
                    set=BgpRouteMapRedistSetToRib(
                        ipv4=BgpRouteMapRedistSetIpv4(
                            source_address="10.0.0.1",
                        ),
                    ),
                ),
            ],
        ),
    ),
    folder="Routing",
)
payload = redist.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a Redistribution

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing redistribution
existing = client.bgp_route_map_redistribution.fetch(
    name="bgp-to-ospf-redist", folder="Routing"
)

# Modify metric in the first route map entry
existing.bgp.ospf.route_map[0].set.metric.value = 200

# Pass modified object to update()
updated = client.bgp_route_map_redistribution.update(existing)
print(f"Updated redistribution: {updated.name}")
```
