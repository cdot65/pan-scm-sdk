# Logical Router Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Supporting Models](#supporting-models)
4. [Exceptions](#exceptions)
5. [Model Validators](#model-validators)
6. [Usage Examples](#usage-examples)

## Overview {#Overview}

The Logical Router models provide a structured way to represent and validate logical router configuration data for Palo Alto Networks' Strata Cloud Manager. These models ensure data integrity when creating and updating logical routers, enforcing proper VRF configuration, routing protocol settings (BGP, OSPF, ECMP, RIP), static route nexthop types, administrative distances, container specifications, and field validations. With 93 model classes and 20 `model_validator` implementations, this is the most complex model hierarchy in the SDK.

### Models

The module provides the following Pydantic models, organized by functional group:

**Top-Level Models (4)**

- `LogicalRouterBaseModel`: Base model with fields common to all logical router operations
- `LogicalRouterCreateModel`: Model for creating new logical routers
- `LogicalRouterUpdateModel`: Model for updating existing logical routers
- `LogicalRouterResponseModel`: Response model for logical router operations
- `RoutingStackEnum`: Enum for routing stack type (`legacy` or `advanced`)

**VRF & Administrative Distances (4)**

- `VrfConfig`: VRF (Virtual Routing and Forwarding) configuration
- `AdminDists`: Administrative distance settings for a logical router
- `VrAdminDists`: VR-level administrative distance settings

**RIB Filter Models (4)**

- `RibFilter`: Top-level RIB filter configuration (IPv4/IPv6)
- `RibFilterIpv4`: IPv4 RIB filter by protocol (static, BGP, OSPF, RIP)
- `RibFilterIpv6`: IPv6 RIB filter by protocol (static, BGP, OSPFv3)
- `RibFilterProtocol`: Individual RIB filter protocol entry with route map

**BFD / Path Monitor Models (3)**

- `BfdProfile`: BFD profile reference
- `PathMonitor`: Path monitor configuration for static routes
- `MonitorDestination`: Path monitor destination entry

**Static Route Models (8)**

- `RoutingTable`, `RoutingTableIp`, `RoutingTableIpv6`: Routing table hierarchy
- `IPv4StaticRoute`: IPv4 static route configuration
- `IPv4Nexthop`: IPv4 nexthop (oneOf: 8 types)
- `IPv4RouteTable`: IPv4 route table selection (oneOf: 4 types)
- `IPv6StaticRoute`: IPv6 static route configuration
- `IPv6Nexthop`: IPv6 nexthop (oneOf: 7 types)
- `IPv6RouteTable`: IPv6 route table selection (oneOf: 4 types)

**OSPF Models (19)**

- `OspfConfig`: Top-level OSPF configuration
- `OspfArea`, `OspfAreaType`, `OspfNormalArea`, `OspfStubArea`, `OspfNssaArea`
- `OspfStubDefaultRoute`, `OspfNssaDefaultRoute`, `OspfNssaExtRange`
- `OspfAreaRange`, `OspfAreaVrRange`
- `OspfInterface`, `OspfInterfaceVrTiming`, `OspfLinkType`
- `OspfVirtualLink`, `OspfVirtualLinkVrTiming`
- `OspfAuthProfile`, `OspfMd5Key`
- `OspfExportRule`, `OspfFloodPrevention`, `OspfFloodPreventionEntry`
- `OspfVrTimers`, `OspfGracefulRestart`, `OspfP2mpNeighbor`

**ECMP Models (5)**

- `EcmpConfig`: Top-level ECMP configuration
- `EcmpAlgorithm`: Algorithm selection (oneOf: 4 types)
- `EcmpIpHash`: IP hash algorithm settings
- `EcmpWeightedRoundRobin`: Weighted round-robin configuration
- `EcmpWeightedInterface`: Weighted interface entry

**RIP Models (3)**

- `RipConfig`: Top-level RIP configuration
- `RipInterface`: RIP interface configuration
- `RipDistributeList`: RIP distribute list configuration

**BGP Models (30+)**

- `BgpConfig`: Top-level BGP configuration
- `BgpPeerGroup`, `BgpPeerGroupType`, `BgpPeerGroupConnectionOptions`, `BgpPeerGroupAddressFamily`, `BgpPeerGroupFilteringProfile`
- `BgpPeer`, `BgpPeerAddress`, `BgpPeerLocalAddress`, `BgpPeerSubsequentAfi`, `BgpPeerConnectionOptions`, `BgpPeerIncomingBgpConnection`, `BgpPeerOutgoingBgpConnection`, `BgpPeerBfd`, `BgpPeerInherit`
- `BgpAggregateRoute`, `BgpAggregateRouteType`
- `BgpRedistProfile`, `BgpRedistRule`
- `BgpAdvertiseNetwork`, `BgpAdvertiseNetworkFamily`, `BgpAdvertiseNetworkEntry`
- `BgpPolicy`, `BgpPolicyImportExport`, `BgpPolicyRule`, `BgpPolicyAction`, `BgpPolicyActionAllow`
- `BgpPolicyMatch`, `BgpPolicyMatchAddressPrefix`, `BgpPolicyMatchAsPath`, `BgpPolicyMatchCommunity`
- `BgpPolicyUpdate`, `BgpPolicyUpdateAsPath`, `BgpPolicyUpdateCommunity`
- `BgpMed`, `BgpAggregate`, `BgpGracefulRestart`

The `LogicalRouterBaseModel` and `LogicalRouterCreateModel` / `LogicalRouterUpdateModel` use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. All sub-models also use `extra="forbid"`. The `LogicalRouterResponseModel` uses `extra="ignore"` to provide resilience against unexpected fields returned by the API.

## Model Attributes

### LogicalRouterBaseModel

This is the base model containing fields common to all logical router operations.

| Attribute     | Type                  | Required | Default | Description                                                     |
|---------------|-----------------------|----------|---------|-----------------------------------------------------------------|
| name          | str                   | Yes      | None    | Name of the logical router.                                     |
| routing_stack | RoutingStackEnum      | No       | None    | Routing stack type: `legacy` or `advanced`.                     |
| vrf           | List[VrfConfig]       | No       | None    | List of VRF configurations.                                     |
| folder        | str                   | No**     | None    | Folder location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |
| snippet       | str                   | No**     | None    | Snippet location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars. |
| device        | str                   | No**     | None    | Device location. Pattern: `^[a-zA-Z\d\-_. ]+$`. Max 64 chars.  |

\** Exactly one container (folder/snippet/device) must be provided for create operations

### LogicalRouterCreateModel

Inherits all fields from `LogicalRouterBaseModel` and enforces that **exactly one** of `folder`, `snippet`, or `device` is provided during creation.

### LogicalRouterUpdateModel

Extends `LogicalRouterBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                  |
|-----------|------|----------|---------|----------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the logical router. |

### LogicalRouterResponseModel

Extends `LogicalRouterBaseModel` by adding:

| Attribute | Type | Required | Default | Description                                  |
|-----------|------|----------|---------|----------------------------------------------|
| id        | UUID | Yes      | None    | The unique identifier of the logical router. |

> **Note:** The `LogicalRouterResponseModel` uses `extra="ignore"` instead of `extra="forbid"`. This means it will silently ignore any extra fields returned by the API that are not defined in the model, providing resilience against API changes.

## Supporting Models

### VrfConfig

This model defines VRF (Virtual Routing and Forwarding) configuration. Each logical router contains a list of VRFs, which serve as the primary container for all routing configuration.

| Attribute      | Type                | Required | Default | Description                         |
|----------------|---------------------|----------|---------|-------------------------------------|
| name           | str                 | Yes      | None    | VRF name.                           |
| interface      | List[str]           | No       | None    | Interfaces assigned to this VRF.    |
| global_vrid    | int                 | No       | None    | Global VRID.                        |
| zone_name      | str                 | No       | None    | Zone name.                          |
| sdwan_type     | str                 | No       | None    | SD-WAN type.                        |
| admin_dists    | AdminDists          | No       | None    | Administrative distance settings.   |
| vr_admin_dists | VrAdminDists        | No       | None    | VR administrative distances.        |
| rib_filter     | RibFilter           | No       | None    | RIB filter configuration.           |
| routing_table  | RoutingTable        | No       | None    | Routing table with static routes.   |
| ospf           | OspfConfig          | No       | None    | OSPF configuration.                 |
| ospfv3         | Dict[str, Any]      | No       | None    | OSPFv3 configuration (raw dict).    |
| ecmp           | EcmpConfig          | No       | None    | ECMP configuration.                 |
| multicast      | Dict[str, Any]      | No       | None    | Multicast configuration (raw dict). |
| rip            | RipConfig           | No       | None    | RIP configuration.                  |
| bgp            | BgpConfig           | No       | None    | BGP configuration.                  |

### AdminDists

Administrative distance settings for a logical router.

| Attribute   | Type | Required | Default | Description                      |
|-------------|------|----------|---------|----------------------------------|
| static      | int  | No       | None    | Static route admin distance.     |
| static_ipv6 | int  | No       | None    | Static IPv6 route admin distance.|
| ospf_inter  | int  | No       | None    | OSPF inter-area admin distance.  |
| ospf_intra  | int  | No       | None    | OSPF intra-area admin distance.  |
| ospf_ext    | int  | No       | None    | OSPF external admin distance.    |
| ospfv3_inter| int  | No       | None    | OSPFv3 inter-area admin distance.|
| ospfv3_intra| int  | No       | None    | OSPFv3 intra-area admin distance.|
| ospfv3_ext  | int  | No       | None    | OSPFv3 external admin distance.  |
| bgp_internal| int  | No       | None    | BGP internal admin distance.     |
| bgp_external| int  | No       | None    | BGP external admin distance.     |
| bgp_local   | int  | No       | None    | BGP local admin distance.        |
| rip         | int  | No       | None    | RIP admin distance.              |

### VrAdminDists

VR-level administrative distance settings.

| Attribute   | Type | Required | Default | Description                      |
|-------------|------|----------|---------|----------------------------------|
| static      | int  | No       | None    | Static route admin distance.     |
| static_ipv6 | int  | No       | None    | Static IPv6 route admin distance.|
| ospf_int    | int  | No       | None    | OSPF internal admin distance.    |
| ospf_ext    | int  | No       | None    | OSPF external admin distance.    |
| ospfv3_int  | int  | No       | None    | OSPFv3 internal admin distance.  |
| ospfv3_ext  | int  | No       | None    | OSPFv3 external admin distance.  |
| ibgp        | int  | No       | None    | iBGP admin distance.             |
| ebgp        | int  | No       | None    | eBGP admin distance.             |
| rip         | int  | No       | None    | RIP admin distance.              |

### RIB Filter Models

The `RibFilter` model provides protocol-based route filtering for IPv4 and IPv6 address families.

| Model            | Fields                              | Description                              |
|------------------|-------------------------------------|------------------------------------------|
| RibFilter        | ipv4, ipv6                          | Top-level RIB filter container.          |
| RibFilterIpv4    | static, bgp, ospf, rip              | IPv4 RIB filters per routing protocol.   |
| RibFilterIpv6    | static, bgp, ospfv3                 | IPv6 RIB filters per routing protocol.   |
| RibFilterProtocol| route_map                           | Protocol entry referencing a route map.  |

### Static Route Models

Static routes are organized under `RoutingTable` > `RoutingTableIp` / `RoutingTableIpv6` > `IPv4StaticRoute` / `IPv6StaticRoute`.

#### IPv4StaticRoute

| Attribute    | Type            | Required | Default | Description                      |
|--------------|-----------------|----------|---------|----------------------------------|
| name         | str             | Yes      | None    | Static route name.               |
| destination  | str             | No       | None    | Destination network (CIDR).      |
| interface    | str             | No       | None    | Egress interface.                |
| nexthop      | IPv4Nexthop     | No       | None    | Nexthop configuration.           |
| route_table  | IPv4RouteTable  | No       | None    | Route table selection.           |
| admin_dist   | int             | No       | None    | Administrative distance.         |
| metric       | int             | No       | None    | Route metric.                    |
| bfd          | BfdProfile      | No       | None    | BFD profile reference.           |
| path_monitor | PathMonitor     | No       | None    | Path monitor configuration.      |

#### IPv4Nexthop (oneOf)

At most one of the following nexthop types may be set:

| Attribute    | Type           | Description                    |
|--------------|----------------|--------------------------------|
| receive      | Dict[str, Any] | Receive (drop into local host).|
| discard      | Dict[str, Any] | Discard (silently drop).       |
| ip_address   | str            | IPv4 address nexthop.          |
| ipv6_address | str            | IPv6 address nexthop.          |
| fqdn         | str            | FQDN nexthop.                  |
| next_lr      | str            | Next logical router.           |
| next_vr      | str            | Next virtual router.           |
| tunnel       | str            | Tunnel nexthop.                |

#### IPv4RouteTable (oneOf)

At most one route table type may be set: `unicast`, `multicast`, `both`, or `no_install`.

#### IPv6StaticRoute

Same structure as `IPv4StaticRoute`, with the addition of:

| Attribute | Type           | Required | Default | Description       |
|-----------|----------------|----------|---------|-------------------|
| option    | Dict[str, Any] | No       | None    | Route option.     |

#### IPv6Nexthop (oneOf)

Same as `IPv4Nexthop` but without `ip_address` (7 nexthop types instead of 8).

#### PathMonitor

| Attribute            | Type                    | Required | Default | Description                    |
|----------------------|-------------------------|----------|---------|--------------------------------|
| enable               | bool                    | No       | None    | Enable path monitoring.        |
| failure_condition    | str                     | No       | None    | Failure condition: `any`/`all`.|
| hold_time            | int                     | No       | None    | Hold time.                     |
| monitor_destinations | List[MonitorDestination]| No       | None    | List of monitor destinations.  |

### OSPF Models

OSPF configuration is organized hierarchically: `OspfConfig` > `OspfArea` > `OspfInterface` / `OspfVirtualLink`.

#### OspfConfig

| Attribute                  | Type                    | Required | Default | Description                         |
|----------------------------|-------------------------|----------|---------|-------------------------------------|
| router_id                  | str                     | No       | None    | OSPF router ID.                     |
| enable                     | bool                    | No       | None    | Enable OSPF.                        |
| rfc1583                    | bool                    | No       | None    | RFC 1583 compatibility.             |
| reject_default_route       | bool                    | No       | None    | Reject default route.               |
| allow_redist_default_route | bool                    | No       | None    | Allow redistribution of default.    |
| spf_timer                  | str                     | No       | None    | SPF timer profile.                  |
| global_if_timer            | str                     | No       | None    | Global interface timer profile.     |
| redistribution_profile     | str                     | No       | None    | Redistribution profile name.        |
| global_bfd                 | BfdProfile              | No       | None    | Global BFD profile.                 |
| flood_prevention           | OspfFloodPrevention     | No       | None    | Flood prevention configuration.     |
| vr_timers                  | OspfVrTimers            | No       | None    | VR timer settings.                  |
| auth_profile               | List[OspfAuthProfile]   | No       | None    | Authentication profiles.            |
| area                       | List[OspfArea]          | No       | None    | OSPF areas.                         |
| export_rules               | List[OspfExportRule]    | No       | None    | Export rules.                       |
| graceful_restart           | OspfGracefulRestart     | No       | None    | Graceful restart configuration.     |

#### OspfArea

| Attribute    | Type                   | Required | Default | Description                 |
|--------------|------------------------|----------|---------|-----------------------------|
| name         | str                    | Yes      | None    | Area ID.                    |
| authentication | str                  | No       | None    | Authentication profile.     |
| type         | OspfAreaType           | No       | None    | Area type (normal/stub/nssa).|
| range        | List[OspfAreaRange]    | No       | None    | Area ranges.                |
| vr_range     | List[OspfAreaVrRange]  | No       | None    | VR area ranges.             |
| interface    | List[OspfInterface]    | No       | None    | OSPF interfaces.            |
| virtual_link | List[OspfVirtualLink]  | No       | None    | OSPF virtual links.         |

#### OspfAreaType (oneOf)

At most one area type may be set: `normal` (OspfNormalArea), `stub` (OspfStubArea), or `nssa` (OspfNssaArea).

#### OspfAuthProfile (oneOf)

| Attribute | Type            | Required | Description                      |
|-----------|-----------------|----------|----------------------------------|
| name      | str             | Yes      | Auth profile name.               |
| password  | str             | No*      | Simple password authentication.  |
| md5       | List[OspfMd5Key]| No*      | MD5 authentication keys.         |

\* `password` and `md5` are mutually exclusive.

#### OspfLinkType (oneOf)

At most one link type may be set: `broadcast`, `p2p`, or `p2mp`.

### ECMP Models

ECMP (Equal-Cost Multi-Path) configuration controls load balancing across multiple equal-cost paths.

#### EcmpConfig

| Attribute          | Type          | Required | Default | Description                    |
|--------------------|---------------|----------|---------|--------------------------------|
| enable             | bool          | No       | None    | Enable ECMP.                   |
| algorithm          | EcmpAlgorithm | No       | None    | ECMP algorithm selection.      |
| max_path           | int           | No       | None    | Maximum number of ECMP paths.  |
| symmetric_return   | bool          | No       | None    | Enable symmetric return.       |
| strict_source_path | bool          | No       | None    | Enable strict source path.     |

#### EcmpAlgorithm (oneOf)

At most one algorithm may be set:

| Attribute              | Type                   | Description                    |
|------------------------|------------------------|--------------------------------|
| ip_modulo              | Dict[str, Any]         | IP modulo algorithm.           |
| ip_hash                | EcmpIpHash             | IP hash algorithm.             |
| weighted_round_robin   | EcmpWeightedRoundRobin | Weighted round-robin.          |
| balanced_round_robin   | Dict[str, Any]         | Balanced round-robin.          |

### RIP Models

#### RipConfig

| Attribute                       | Type                | Required | Default | Description                          |
|---------------------------------|---------------------|----------|---------|--------------------------------------|
| enable                          | bool                | No       | None    | Enable RIP.                          |
| default_information_originate   | bool                | No       | None    | Originate default information.       |
| global_timer                    | str                 | No       | None    | Global timer profile.               |
| auth_profile                    | str                 | No       | None    | Authentication profile name.        |
| redistribution_profile          | str                 | No       | None    | Redistribution profile name.        |
| global_bfd                      | BfdProfile          | No       | None    | Global BFD profile.                 |
| global_inbound_distribute_list  | RipDistributeList   | No       | None    | Global inbound distribute list.     |
| global_outbound_distribute_list | RipDistributeList   | No       | None    | Global outbound distribute list.    |
| interface                       | List[RipInterface]  | No       | None    | RIP interfaces.                     |

#### RipInterface

| Attribute                          | Type              | Required | Default | Description                                                  |
|------------------------------------|-------------------|----------|---------|--------------------------------------------------------------|
| name                               | str               | Yes      | None    | Interface name.                                              |
| enable                             | bool              | No       | None    | Enable RIP on interface.                                     |
| mode                               | str               | No       | None    | RIP mode: `active`, `passive`, or `send-only`.               |
| split_horizon                      | str               | No       | None    | Split horizon mode.                                          |
| authentication                     | str               | No       | None    | Authentication profile name.                                 |
| bfd                                | BfdProfile        | No       | None    | BFD profile.                                                 |
| interface_inbound_distribute_list  | RipDistributeList | No       | None    | Inbound distribute list.                                     |
| interface_outbound_distribute_list | RipDistributeList | No       | None    | Outbound distribute list.                                    |

### BGP Models

BGP configuration is the most deeply nested section, organized as: `BgpConfig` > `BgpPeerGroup` > `BgpPeer`, with separate sub-trees for policies, aggregate routes, redistribution, and network advertisements.

#### BgpConfig

| Attribute                       | Type                     | Required | Default | Description                               |
|---------------------------------|--------------------------|----------|---------|-------------------------------------------|
| enable                          | bool                     | No       | None    | Enable BGP.                               |
| router_id                       | str                      | No       | None    | BGP router ID.                            |
| local_as                        | str                      | No       | None    | Local AS number (ASPLAIN format).         |
| confederation_member_as         | str                      | No       | None    | Confederation member AS.                  |
| install_route                   | bool                     | No       | None    | Install routes.                           |
| enforce_first_as                | bool                     | No       | None    | Enforce first AS.                         |
| fast_external_failover          | bool                     | No       | None    | Fast external failover.                   |
| ecmp_multi_as                   | bool                     | No       | None    | ECMP multi-AS.                            |
| default_local_preference        | int                      | No       | None    | Default local preference.                 |
| graceful_shutdown               | bool                     | No       | None    | Graceful shutdown.                        |
| always_advertise_network_route  | bool                     | No       | None    | Always advertise network route.           |
| reject_default_route            | bool                     | No       | None    | Reject default route.                     |
| allow_redist_default_route      | bool                     | No       | None    | Allow redistribution of default route.    |
| as_format                       | str                      | No       | None    | AS number format.                         |
| med                             | BgpMed                   | No       | None    | MED configuration.                        |
| aggregate                       | BgpAggregate             | No       | None    | Aggregate configuration.                  |
| graceful_restart                | BgpGracefulRestart       | No       | None    | Graceful restart configuration.           |
| global_bfd                      | BfdProfile               | No       | None    | Global BFD profile.                       |
| peer_group                      | List[BgpPeerGroup]       | No       | None    | Peer groups.                              |
| aggregate_routes                | List[BgpAggregateRoute]  | No       | None    | Aggregate routes.                         |
| redistribution_profile          | BgpRedistProfile         | No       | None    | Redistribution profile.                   |
| advertise_network               | BgpAdvertiseNetwork      | No       | None    | Advertise network configuration.          |
| policy                          | BgpPolicy                | No       | None    | BGP policy configuration.                 |
| redist_rules                    | List[BgpRedistRule]      | No       | None    | Redistribution rules.                     |

#### BgpPeerGroup

| Attribute                   | Type                           | Required | Default | Description                       |
|-----------------------------|--------------------------------|----------|---------|-----------------------------------|
| name                        | str                            | Yes      | None    | Peer group name.                  |
| enable                      | bool                           | No       | None    | Enable peer group.                |
| aggregated_confed_as_path   | bool                           | No       | None    | Aggregated confederation AS path. |
| soft_reset_with_stored_info | bool                           | No       | None    | Soft reset with stored info.      |
| type                        | BgpPeerGroupType               | No       | None    | Peer group type.                  |
| address_family              | BgpPeerGroupAddressFamily      | No       | None    | Address family configuration.     |
| filtering_profile           | BgpPeerGroupFilteringProfile   | No       | None    | Filtering profile configuration.  |
| connection_options          | BgpPeerGroupConnectionOptions  | No       | None    | Connection options.               |
| peer                        | List[BgpPeer]                  | No       | None    | Peers in this group.              |

#### BgpPeerGroupType (oneOf)

At most one peer group type may be set: `ibgp`, `ebgp_confed`, `ibgp_confed`, or `ebgp`.

#### BgpPeerAddress (oneOf)

`ip` and `fqdn` are mutually exclusive for specifying the peer address.

#### BgpPeerInherit (oneOf)

`ipv4` and `no` are mutually exclusive for inherit configuration.

#### BgpAggregateRouteType (oneOf)

`ipv4` and `ipv6` are mutually exclusive for aggregate route types.

#### BgpPolicy

| Attribute                 | Type                  | Required | Default | Description                                  |
|---------------------------|-----------------------|----------|---------|----------------------------------------------|
| import_ (alias: `import`) | BgpPolicyImportExport | No       | None    | Import policy rules.                         |
| export                    | BgpPolicyImportExport | No       | None    | Export policy rules.                         |
| conditional_advertisement | Dict[str, Any]        | No       | None    | Conditional advertisement config (raw dict). |
| aggregation               | Dict[str, Any]        | No       | None    | Aggregation policy config (raw dict).        |

#### BgpPolicyAction (oneOf)

`deny` and `allow` are mutually exclusive. The `allow` variant accepts an optional `BgpPolicyUpdate` with route attribute modifications.

#### BgpPolicyUpdateAsPath (oneOf)

At most one AS path action may be set: `none`, `remove`, `prepend`, or `remove_and_prepend`.

#### BgpPolicyUpdateCommunity (oneOf)

At most one community action may be set: `none`, `remove_all`, `remove_regex`, `append`, or `overwrite`. This model is used for both `community` and `extended_community` update fields.

### Fields Using Dict[str, Any]

Several deeply nested or less commonly used configurations are represented as raw dictionaries rather than fully typed models:

| Field Location                    | Description                                           |
|-----------------------------------|-------------------------------------------------------|
| `VrfConfig.ospfv3`               | OSPFv3 configuration.                                 |
| `VrfConfig.multicast`            | Multicast routing configuration.                      |
| `BgpPolicy.conditional_advertisement` | BGP conditional advertisement rules.             |
| `BgpPolicy.aggregation`          | BGP aggregation policy.                               |

These fields accept arbitrary nested structures. Fully typed models may be added in a future SDK release.

## Exceptions

The models perform strict validation and will raise `ValueError` in scenarios such as:

- When creating a logical router (`LogicalRouterCreateModel`), if not exactly one container (`folder`, `snippet`, or `device`) is provided.
- When more than one nexthop type is set on `IPv4Nexthop` or `IPv6Nexthop` (at most one is allowed).
- When more than one route table type is set on `IPv4RouteTable` or `IPv6RouteTable`.
- When more than one OSPF area type is set on `OspfAreaType` (normal, stub, or nssa).
- When mutually exclusive OSPF fields are both set (e.g., `password` and `md5` on `OspfAuthProfile`).
- When more than one ECMP algorithm is set on `EcmpAlgorithm`.
- When mutually exclusive BGP fields are both set (e.g., `ip` and `fqdn` on `BgpPeerAddress`).
- When more than one BGP peer group type is set on `BgpPeerGroupType`.
- When more than one BGP policy action is set on `BgpPolicyAction` (deny or allow).
- When more than one AS path action or community action is set on `BgpPolicyUpdateAsPath` or `BgpPolicyUpdateCommunity`.
- When container identifiers (folder, snippet, device) do not match the required pattern or exceed the maximum length.

## Model Validators

The Logical Router models contain 20 `model_validator` implementations, all operating in `mode="after"` to enforce oneOf-style mutual exclusivity constraints.

### Nexthop Validators

- **`IPv4Nexthop.validate_nexthop_type`**: Ensures at most one of the 8 nexthop types is set: `receive`, `discard`, `ip_address`, `ipv6_address`, `fqdn`, `next_lr`, `next_vr`, or `tunnel`.

- **`IPv6Nexthop.validate_nexthop_type`**: Ensures at most one of the 7 nexthop types is set: `receive`, `discard`, `ipv6_address`, `fqdn`, `next_lr`, `next_vr`, or `tunnel`.

### Route Table Validators

- **`IPv4RouteTable.validate_route_table`**: Ensures at most one route table type is set: `unicast`, `multicast`, `both`, or `no_install`.

- **`IPv6RouteTable.validate_route_table`**: Same constraint as IPv4 route table.

### OSPF Validators

- **`OspfAuthProfile.validate_auth_type`**: Ensures `password` and `md5` are mutually exclusive.

- **`OspfLinkType.validate_link_type`**: Ensures at most one link type is set: `broadcast`, `p2p`, or `p2mp`.

- **`OspfAreaVrRange.validate_action`**: Ensures `advertise` and `suppress` are mutually exclusive.

- **`OspfStubDefaultRoute.validate_default_route`**: Ensures `disable` and `advertise` are mutually exclusive.

- **`OspfNssaDefaultRoute.validate_default_route`**: Ensures `disable` and `advertise` are mutually exclusive.

- **`OspfNssaExtRange.validate_action`**: Ensures `advertise` and `suppress` are mutually exclusive.

- **`OspfAreaType.validate_area_type`**: Ensures at most one area type is set: `normal`, `stub`, or `nssa`.

### ECMP Validators

- **`EcmpAlgorithm.validate_algorithm`**: Ensures at most one ECMP algorithm is set: `ip_modulo`, `ip_hash`, `weighted_round_robin`, or `balanced_round_robin`.

### BGP Validators

- **`BgpPeerAddress.validate_peer_address`**: Ensures `ip` and `fqdn` are mutually exclusive.

- **`BgpPeerInherit.validate_inherit`**: Ensures `ipv4` and `no` are mutually exclusive.

- **`BgpPeerGroupType.validate_type`**: Ensures at most one peer group type is set: `ibgp`, `ebgp_confed`, `ibgp_confed`, or `ebgp`.

- **`BgpAggregateRouteType.validate_type`**: Ensures `ipv4` and `ipv6` are mutually exclusive.

- **`BgpPolicyUpdateAsPath.validate_as_path_action`**: Ensures at most one AS path action is set: `none`, `remove`, `prepend`, or `remove_and_prepend`.

- **`BgpPolicyUpdateCommunity.validate_community_action`**: Ensures at most one community action is set: `none`, `remove_all`, `remove_regex`, `append`, or `overwrite`.

- **`BgpPolicyAction.validate_action`**: Ensures `deny` and `allow` are mutually exclusive.

### Container Validation in `LogicalRouterCreateModel`

- **`validate_container_type`**: After model initialization, this validator checks that exactly one of the container fields (`folder`, `snippet`, or `device`) is provided. If not, it raises a `ValueError`.

## Usage Examples

### Creating a Logical Router

#### Using a Dictionary

```python
from scm.models.network import LogicalRouterCreateModel

router_data = {
    "name": "LR1",
    "routing_stack": "advanced",
    "vrf": [
        {
            "name": "default",
            "interface": ["ethernet1/1", "ethernet1/2"],
            "routing_table": {
                "ip": {
                    "static_route": [
                        {
                            "name": "default-route",
                            "destination": "0.0.0.0/0",
                            "nexthop": {"ip_address": "10.0.0.1"},
                            "metric": 10,
                            "admin_dist": 10,
                        }
                    ]
                }
            },
        }
    ],
    "folder": "Texas",
}

# Validate and create model instance
router = LogicalRouterCreateModel(**router_data)
payload = router.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

#### Using the Model Directly

```python
from scm.models.network import LogicalRouterCreateModel
from scm.models.network.logical_router import (
    VrfConfig,
    RoutingTable,
    RoutingTableIp,
    IPv4StaticRoute,
    IPv4Nexthop,
    BfdProfile,
    PathMonitor,
    MonitorDestination,
)

# Create a static route with BFD and path monitoring
static_route = IPv4StaticRoute(
    name="default-route",
    destination="0.0.0.0/0",
    nexthop=IPv4Nexthop(ip_address="10.0.0.1"),
    metric=10,
    bfd=BfdProfile(profile="bfd-default"),
    path_monitor=PathMonitor(
        enable=True,
        failure_condition="any",
        monitor_destinations=[
            MonitorDestination(
                name="monitor-1",
                enable=True,
                source="10.0.0.2",
                destination="8.8.8.8",
            )
        ],
    ),
)

# Build the VRF configuration
vrf = VrfConfig(
    name="default",
    interface=["ethernet1/1", "ethernet1/2"],
    routing_table=RoutingTable(
        ip=RoutingTableIp(static_route=[static_route])
    ),
)

# Create logical router
router = LogicalRouterCreateModel(
    name="LR1",
    routing_stack="advanced",
    vrf=[vrf],
    folder="Texas",
)
payload = router.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Updating a Logical Router

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Fetch existing router
existing = client.logical_router.fetch(name="LR1", folder="Texas")

# Add a new VRF with BGP configuration
existing.vrf.append({
    "name": "vrf-production",
    "interface": ["ethernet1/3"],
    "bgp": {
        "enable": True,
        "router_id": "10.0.0.1",
        "local_as": "65001",
        "peer_group": [
            {
                "name": "upstream",
                "enable": True,
                "type": {"ebgp": {}},
                "peer": [
                    {
                        "name": "isp-peer",
                        "enable": True,
                        "peer_as": "65002",
                        "peer_address": {"ip": "192.168.1.1"},
                    }
                ],
            }
        ],
    },
})

# Pass modified object to update()
updated = client.logical_router.update(existing)
print(f"Updated logical router: {updated.name}")
```

### Creating a Logical Router with OSPF

```python
from scm.models.network import LogicalRouterCreateModel
from scm.models.network.logical_router import (
    VrfConfig,
    OspfConfig,
    OspfArea,
    OspfAreaType,
    OspfNormalArea,
    OspfInterface,
    OspfLinkType,
    OspfGracefulRestart,
    BfdProfile,
)

# Build OSPF area with interfaces
area = OspfArea(
    name="0.0.0.0",
    type=OspfAreaType(normal=OspfNormalArea()),
    interface=[
        OspfInterface(
            name="ethernet1/1",
            enable=True,
            passive=False,
            metric=10,
            link_type=OspfLinkType(broadcast={}),
            bfd=BfdProfile(profile="bfd-default"),
        ),
    ],
)

# Build OSPF configuration
ospf = OspfConfig(
    router_id="10.0.0.1",
    enable=True,
    area=[area],
    graceful_restart=OspfGracefulRestart(
        enable=True,
        grace_period=120,
    ),
)

# Create the router
router = LogicalRouterCreateModel(
    name="LR-OSPF",
    routing_stack="advanced",
    vrf=[
        VrfConfig(
            name="default",
            interface=["ethernet1/1"],
            ospf=ospf,
        )
    ],
    folder="Texas",
)
payload = router.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```

### Creating a Logical Router with ECMP

```python
from scm.models.network import LogicalRouterCreateModel
from scm.models.network.logical_router import (
    VrfConfig,
    EcmpConfig,
    EcmpAlgorithm,
    EcmpIpHash,
)

router = LogicalRouterCreateModel(
    name="LR-ECMP",
    routing_stack="advanced",
    vrf=[
        VrfConfig(
            name="default",
            interface=["ethernet1/1", "ethernet1/2"],
            ecmp=EcmpConfig(
                enable=True,
                max_path=4,
                symmetric_return=True,
                algorithm=EcmpAlgorithm(
                    ip_hash=EcmpIpHash(
                        src_only=False,
                        use_port=True,
                        hash_seed=12345,
                    )
                ),
            ),
        )
    ],
    folder="Texas",
)
payload = router.model_dump(exclude_unset=True, by_alias=True)
print(payload)
```
