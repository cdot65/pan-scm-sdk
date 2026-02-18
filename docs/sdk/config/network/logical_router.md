# Logical Router Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Logical Router Model Attributes](#logical-router-model-attributes)
4. [VRF Configuration](#vrf-configuration)
5. [Static Routes](#static-routes)
6. [BGP Configuration](#bgp-configuration)
7. [OSPF Configuration](#ospf-configuration)
8. [ECMP Configuration](#ecmp-configuration)
9. [Exceptions](#exceptions)
10. [Basic Configuration](#basic-configuration)
11. [Usage Examples](#usage-examples)
    - [Creating Logical Routers](#creating-logical-routers)
    - [Retrieving Logical Routers](#retrieving-logical-routers)
    - [Updating Logical Routers](#updating-logical-routers)
    - [Listing Logical Routers](#listing-logical-routers)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting Logical Routers](#deleting-logical-routers)
12. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
13. [Error Handling](#error-handling)
14. [Best Practices](#best-practices)
15. [Related Models](#related-models)

## Overview

The `LogicalRouter` class manages logical router objects in Palo Alto Networks' Strata Cloud Manager. It extends from `BaseObject` and offers methods to create, retrieve, update, list, fetch, and delete logical routers. Logical routers serve as the routing backbone for SCM-managed devices, replacing the legacy Virtual Router for ARE-enabled devices. All routing configuration -- static routes, BGP, OSPF, ECMP, and RIP -- is organized within VRF (Virtual Routing and Forwarding) objects attached to the router. The underlying Pydantic model hierarchy comprises 93 model classes to represent the full depth of the routing configuration.

## Core Methods

| Method     | Description                                                     | Parameters                                                                                                                       | Return Type                          |
|------------|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `create()` | Creates a new logical router                                    | `data: Dict[str, Any]`                                                                                                           | `LogicalRouterResponseModel`         |
| `get()`    | Retrieves a logical router by its unique ID                     | `object_id: str`                                                                                                                 | `LogicalRouterResponseModel`         |
| `update()` | Updates an existing logical router                              | `router: LogicalRouterUpdateModel`                                                                                               | `LogicalRouterResponseModel`         |
| `list()`   | Lists logical routers with optional filtering                   | `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`, `exact_match: bool = False`, plus additional filters | `List[LogicalRouterResponseModel]`   |
| `fetch()`  | Fetches a single logical router by name within a container      | `name: str`, `folder: Optional[str]`, `snippet: Optional[str]`, `device: Optional[str]`                                          | `LogicalRouterResponseModel`         |
| `delete()` | Deletes a logical router by its ID                              | `object_id: str`                                                                                                                 | `None`                               |

## Logical Router Model Attributes

| Attribute       | Type                   | Required | Default | Description                                                 |
|-----------------|------------------------|----------|---------|-------------------------------------------------------------|
| `name`          | str                    | Yes      | None    | The name of the logical router                              |
| `id`            | UUID                   | Yes*     | None    | Unique identifier (*response/update only)                   |
| `routing_stack` | RoutingStackEnum       | No       | None    | Routing stack type: `"legacy"` or `"advanced"`              |
| `vrf`           | List[VrfConfig]        | No       | None    | List of VRF configurations                                  |
| `folder`        | str                    | No**     | None    | Folder location. Max 64 chars                               |
| `snippet`       | str                    | No**     | None    | Snippet location. Max 64 chars                              |
| `device`        | str                    | No**     | None    | Device location. Max 64 chars                               |

\* Only required for update and response models
\** Exactly one container (folder/snippet/device) must be provided for create operations

## VRF Configuration

The `vrf` attribute contains a list of VRF objects. Each VRF is the central organizing unit for all routing configuration within a logical router.

### VrfConfig

| Attribute        | Type               | Required | Description                                    |
|------------------|--------------------|----------|------------------------------------------------|
| `name`           | str                | Yes      | VRF name                                       |
| `interface`      | List[str]          | No       | Interfaces assigned to this VRF                |
| `global_vrid`    | int                | No       | Global VRID                                    |
| `zone_name`      | str                | No       | Zone name                                      |
| `sdwan_type`     | str                | No       | SD-WAN type                                    |
| `admin_dists`    | AdminDists         | No       | Administrative distance settings               |
| `vr_admin_dists` | VrAdminDists       | No       | VR administrative distance settings            |
| `rib_filter`     | RibFilter          | No       | RIB filter configuration (IPv4/IPv6)           |
| `routing_table`  | RoutingTable       | No       | Routing table with static routes               |
| `ospf`           | OspfConfig         | No       | OSPF routing protocol configuration            |
| `ospfv3`         | Dict[str, Any]     | No       | OSPFv3 routing protocol configuration          |
| `ecmp`           | EcmpConfig         | No       | ECMP configuration                             |
| `multicast`      | Dict[str, Any]     | No       | Multicast configuration                        |
| `rip`            | RipConfig          | No       | RIP routing protocol configuration             |
| `bgp`            | BgpConfig          | No       | BGP routing protocol configuration             |

### AdminDists

| Attribute      | Type | Required | Description                          |
|----------------|------|----------|--------------------------------------|
| `static`       | int  | No       | Static route admin distance          |
| `static_ipv6`  | int  | No       | Static IPv6 route admin distance     |
| `ospf_inter`   | int  | No       | OSPF inter-area admin distance       |
| `ospf_intra`   | int  | No       | OSPF intra-area admin distance       |
| `ospf_ext`     | int  | No       | OSPF external admin distance         |
| `ospfv3_inter` | int  | No       | OSPFv3 inter-area admin distance     |
| `ospfv3_intra` | int  | No       | OSPFv3 intra-area admin distance     |
| `ospfv3_ext`   | int  | No       | OSPFv3 external admin distance       |
| `bgp_internal` | int  | No       | BGP internal admin distance          |
| `bgp_external` | int  | No       | BGP external admin distance          |
| `bgp_local`    | int  | No       | BGP local admin distance             |
| `rip`          | int  | No       | RIP admin distance                   |

## Static Routes

Static routes live inside a VRF's `routing_table` attribute, which contains separate `ip` (IPv4) and `ipv6` sections, each holding a list of static route objects.

### IPv4StaticRoute

| Attribute      | Type           | Required | Description                                       |
|----------------|----------------|----------|---------------------------------------------------|
| `name`         | str            | Yes      | Static route name                                 |
| `destination`  | str            | No       | Destination network (CIDR notation)               |
| `interface`    | str            | No       | Egress interface                                  |
| `nexthop`      | IPv4Nexthop    | No       | Nexthop configuration (oneOf: ip_address, fqdn, next_lr, next_vr, tunnel, discard, receive) |
| `route_table`  | IPv4RouteTable | No       | Route table selection (unicast, multicast, both, no_install) |
| `admin_dist`   | int            | No       | Administrative distance                           |
| `metric`       | int            | No       | Route metric                                      |
| `bfd`          | BfdProfile     | No       | BFD profile reference                             |
| `path_monitor` | PathMonitor    | No       | Path monitor configuration                        |

### IPv6StaticRoute

| Attribute      | Type           | Required | Description                                       |
|----------------|----------------|----------|---------------------------------------------------|
| `name`         | str            | Yes      | Static route name                                 |
| `destination`  | str            | No       | Destination network (IPv6 CIDR notation)          |
| `interface`    | str            | No       | Egress interface                                  |
| `nexthop`      | IPv6Nexthop    | No       | Nexthop configuration (oneOf: ipv6_address, fqdn, next_lr, next_vr, tunnel, discard, receive) |
| `route_table`  | IPv6RouteTable | No       | Route table selection (unicast, multicast, both, no_install) |
| `admin_dist`   | int            | No       | Administrative distance                           |
| `metric`       | int            | No       | Route metric                                      |
| `bfd`          | BfdProfile     | No       | BFD profile reference                             |
| `path_monitor` | PathMonitor    | No       | Path monitor configuration                        |

## BGP Configuration

The `bgp` attribute within a VRF provides full BGP routing protocol support including peer groups, redistribution, and policy configuration.

### BgpConfig

| Attribute                          | Type                  | Required | Description                               |
|------------------------------------|-----------------------|----------|-------------------------------------------|
| `enable`                           | bool                  | No       | Enable BGP                                |
| `router_id`                        | str                   | No       | BGP router ID                             |
| `local_as`                         | str                   | No       | Local AS number                           |
| `confederation_member_as`          | str                   | No       | Confederation member AS                   |
| `install_route`                    | bool                  | No       | Install routes into the routing table     |
| `enforce_first_as`                 | bool                  | No       | Enforce first AS in AS path               |
| `fast_external_failover`           | bool                  | No       | Enable fast external failover             |
| `ecmp_multi_as`                    | bool                  | No       | ECMP multi-AS support                     |
| `default_local_preference`         | int                   | No       | Default local preference value            |
| `reject_default_route`             | bool                  | No       | Reject default route                      |
| `allow_redist_default_route`       | bool                  | No       | Allow redistribution of default route     |
| `med`                              | BgpMed                | No       | MED configuration                         |
| `graceful_restart`                 | BgpGracefulRestart    | No       | Graceful restart configuration            |
| `global_bfd`                       | BfdProfile            | No       | Global BFD profile                        |
| `peer_group`                       | List[BgpPeerGroup]    | No       | BGP peer groups                           |
| `aggregate_routes`                 | List[BgpAggregateRoute]| No      | Aggregate route entries                   |
| `redistribution_profile`           | BgpRedistProfile      | No       | Redistribution profile                    |
| `advertise_network`                | BgpAdvertiseNetwork   | No       | Networks to advertise                     |
| `policy`                           | BgpPolicy             | No       | BGP policy configuration                  |
| `redist_rules`                     | List[BgpRedistRule]   | No       | Redistribution rules                      |

### BgpPeerGroup

| Attribute                      | Type                           | Required | Description                              |
|--------------------------------|--------------------------------|----------|------------------------------------------|
| `name`                         | str                            | Yes      | Peer group name                          |
| `enable`                       | bool                           | No       | Enable peer group                        |
| `type`                         | BgpPeerGroupType               | No       | Peer group type (ibgp, ebgp, ebgp_confed, ibgp_confed) |
| `address_family`               | BgpPeerGroupAddressFamily      | No       | Address family configuration             |
| `filtering_profile`            | BgpPeerGroupFilteringProfile   | No       | Filtering profile configuration          |
| `connection_options`           | BgpPeerGroupConnectionOptions  | No       | Connection options                       |
| `peer`                         | List[BgpPeer]                  | No       | Peers in this group                      |

## OSPF Configuration

The `ospf` attribute within a VRF provides OSPF routing protocol support with areas, interfaces, authentication, and graceful restart.

### OspfConfig

| Attribute                      | Type                   | Required | Description                               |
|--------------------------------|------------------------|----------|-------------------------------------------|
| `router_id`                    | str                    | No       | OSPF router ID                            |
| `enable`                       | bool                   | No       | Enable OSPF                               |
| `rfc1583`                      | bool                   | No       | RFC 1583 compatibility                    |
| `reject_default_route`         | bool                   | No       | Reject default route                      |
| `allow_redist_default_route`   | bool                   | No       | Allow redistribution of default route     |
| `spf_timer`                    | str                    | No       | SPF timer profile                         |
| `global_if_timer`              | str                    | No       | Global interface timer profile            |
| `redistribution_profile`       | str                    | No       | Redistribution profile name               |
| `global_bfd`                   | BfdProfile             | No       | Global BFD profile                        |
| `flood_prevention`             | OspfFloodPrevention    | No       | Flood prevention configuration            |
| `vr_timers`                    | OspfVrTimers           | No       | VR timer settings                         |
| `auth_profile`                 | List[OspfAuthProfile]  | No       | Authentication profiles                   |
| `area`                         | List[OspfArea]         | No       | OSPF areas                                |
| `export_rules`                 | List[OspfExportRule]   | No       | Export rules                              |
| `graceful_restart`             | OspfGracefulRestart    | No       | Graceful restart configuration            |

### OspfArea

| Attribute        | Type                   | Required | Description                                          |
|------------------|------------------------|----------|------------------------------------------------------|
| `name`           | str                    | Yes      | Area ID (e.g., "0.0.0.0" for backbone)               |
| `authentication` | str                    | No       | Authentication profile name                          |
| `type`           | OspfAreaType           | No       | Area type (normal, stub, or nssa)                    |
| `range`          | List[OspfAreaRange]    | No       | Area ranges                                          |
| `vr_range`       | List[OspfAreaVrRange]  | No       | VR area ranges                                       |
| `interface`      | List[OspfInterface]    | No       | OSPF interfaces in this area                         |
| `virtual_link`   | List[OspfVirtualLink]  | No       | OSPF virtual links                                   |

## ECMP Configuration

The `ecmp` attribute within a VRF configures Equal-Cost Multi-Path routing with algorithm selection and path limits.

### EcmpConfig

| Attribute            | Type          | Required | Description                              |
|----------------------|---------------|----------|------------------------------------------|
| `enable`             | bool          | No       | Enable ECMP                              |
| `algorithm`          | EcmpAlgorithm | No       | ECMP algorithm (ip_modulo, ip_hash, weighted_round_robin, balanced_round_robin) |
| `max_path`           | int           | No       | Maximum number of ECMP paths             |
| `symmetric_return`   | bool          | No       | Enable symmetric return                  |
| `strict_source_path` | bool          | No       | Enable strict source path                |

### EcmpAlgorithm

Only one algorithm can be selected at a time (oneOf):

| Attribute                | Type                   | Description                              |
|--------------------------|------------------------|------------------------------------------|
| `ip_modulo`              | Dict[str, Any]         | IP modulo algorithm (empty object)       |
| `ip_hash`                | EcmpIpHash             | IP hash with src_only, use_port, hash_seed |
| `weighted_round_robin`   | EcmpWeightedRoundRobin | Weighted round-robin with interface weights |
| `balanced_round_robin`   | Dict[str, Any]         | Balanced round-robin algorithm (empty object) |

## Exceptions

| Exception                    | HTTP Code | Description                                                                   |
|------------------------------|-----------|-------------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Thrown when provided data or parameters are invalid                           |
| `MissingQueryParameterError` | 400       | Thrown when required query parameters (e.g., `name` or `folder`) are missing  |
| `NameNotUniqueError`         | 409       | Logical router name already exists                                            |
| `ObjectNotPresentError`      | 404       | Logical router not found                                                      |
| `ReferenceNotZeroError`      | 409       | Logical router still referenced by other objects                              |
| `AuthenticationError`        | 401       | Authentication failed                                                         |
| `ServerError`                | 500       | Internal server error                                                         |

## Basic Configuration

The Logical Router service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Access the Logical Router service directly through the client
logical_routers = client.logical_router
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.network import LogicalRouter

# Initialize client
client = Scm(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Initialize LogicalRouter object explicitly
logical_routers = LogicalRouter(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Logical Routers

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a basic logical router with a VRF and static routes
router_data = {
   "name": "branch-router-01",
   "routing_stack": "advanced",
   "vrf": [
      {
         "name": "vrf-production",
         "interface": ["ethernet1/1", "ethernet1/2"],
         "routing_table": {
            "ip": {
               "static_route": [
                  {
                     "name": "default-route",
                     "destination": "0.0.0.0/0",
                     "nexthop": {
                        "ip_address": "10.0.0.1"
                     },
                     "metric": 10
                  },
                  {
                     "name": "internal-subnet",
                     "destination": "192.168.0.0/16",
                     "nexthop": {
                        "ip_address": "10.0.0.2"
                     },
                     "admin_dist": 15
                  }
               ]
            }
         }
      }
   ],
   "folder": "Texas"
}

new_router = client.logical_router.create(router_data)
print(f"Created logical router with ID: {new_router.id}")

# Create a logical router with BGP configuration
bgp_router_data = {
   "name": "core-router-01",
   "routing_stack": "advanced",
   "vrf": [
      {
         "name": "vrf-transit",
         "interface": ["ethernet1/3", "ethernet1/4"],
         "bgp": {
            "enable": True,
            "router_id": "10.255.0.1",
            "local_as": "65001",
            "peer_group": [
               {
                  "name": "upstream-peers",
                  "enable": True,
                  "type": {
                     "ebgp": {}
                  },
                  "peer": [
                     {
                        "name": "isp-peer-1",
                        "enable": True,
                        "peer_as": "64512",
                        "peer_address": {
                           "ip": "203.0.113.1"
                        },
                        "local_address": {
                           "interface": "ethernet1/3",
                           "ip": "203.0.113.2"
                        }
                     }
                  ]
               }
            ]
         }
      }
   ],
   "folder": "Texas"
}

bgp_router = client.logical_router.create(bgp_router_data)
print(f"Created BGP router with ID: {bgp_router.id}")

# Create a logical router with OSPF configuration
ospf_router_data = {
   "name": "campus-router-01",
   "routing_stack": "advanced",
   "vrf": [
      {
         "name": "vrf-campus",
         "interface": ["ethernet1/1", "ethernet1/2"],
         "ospf": {
            "enable": True,
            "router_id": "10.255.0.2",
            "area": [
               {
                  "name": "0.0.0.0",
                  "type": {
                     "normal": {}
                  },
                  "interface": [
                     {
                        "name": "ethernet1/1",
                        "enable": True,
                        "metric": 10,
                        "link_type": {
                           "broadcast": {}
                        }
                     },
                     {
                        "name": "ethernet1/2",
                        "enable": True,
                        "passive": True
                     }
                  ]
               }
            ],
            "graceful_restart": {
               "enable": True,
               "grace_period": 120
            }
         }
      }
   ],
   "folder": "Texas"
}

ospf_router = client.logical_router.create(ospf_router_data)
print(f"Created OSPF router with ID: {ospf_router.id}")
```

### Retrieving Logical Routers

```python
# Fetch by name and folder
router = client.logical_router.fetch(
   name="branch-router-01",
   folder="Texas"
)
print(f"Found router: {router.name}")
print(f"  Routing stack: {router.routing_stack}")
if router.vrf:
   for vrf in router.vrf:
      print(f"  VRF: {vrf.name}")
      if vrf.interface:
         print(f"    Interfaces: {', '.join(vrf.interface)}")

# Get by ID
router_by_id = client.logical_router.get(router.id)
print(f"Retrieved router: {router_by_id.name}")
```

### Updating Logical Routers

```python
# Fetch existing router
existing_router = client.logical_router.fetch(
   name="branch-router-01",
   folder="Texas"
)

# Add ECMP configuration to the first VRF
if existing_router.vrf:
   existing_router.vrf[0].ecmp = {
      "enable": True,
      "algorithm": {
         "ip_hash": {
            "src_only": False,
            "use_port": True,
            "hash_seed": 42
         }
      },
      "max_path": 4,
      "symmetric_return": True
   }

# Perform update
updated_router = client.logical_router.update(existing_router)
print(f"Updated router: {updated_router.name}")

# Update a router to add a BGP peer group
router_with_bgp = client.logical_router.fetch(
   name="core-router-01",
   folder="Texas"
)

# Add a second peer to the existing peer group
if router_with_bgp.vrf and router_with_bgp.vrf[0].bgp:
   bgp = router_with_bgp.vrf[0].bgp
   if bgp.peer_group:
      bgp.peer_group[0].peer.append({
         "name": "isp-peer-2",
         "enable": True,
         "peer_as": "64513",
         "peer_address": {
            "ip": "198.51.100.1"
         },
         "local_address": {
            "interface": "ethernet1/4",
            "ip": "198.51.100.2"
         }
      })

updated_bgp_router = client.logical_router.update(router_with_bgp)
print(f"Updated BGP router with additional peer")

# Add OSPF stub area to a router
router_with_ospf = client.logical_router.fetch(
   name="campus-router-01",
   folder="Texas"
)

if router_with_ospf.vrf and router_with_ospf.vrf[0].ospf:
   router_with_ospf.vrf[0].ospf.area.append({
      "name": "0.0.0.1",
      "type": {
         "stub": {
            "accept_summary": True,
            "default_route": {
               "advertise": {}
            }
         }
      },
      "interface": [
         {
            "name": "ethernet1/5",
            "enable": True,
            "metric": 20
         }
      ]
   })

updated_ospf_router = client.logical_router.update(router_with_ospf)
print(f"Updated OSPF router with stub area")
```

### Listing Logical Routers

```python
# List all logical routers in a folder
routers = client.logical_router.list(
   folder="Texas"
)

# Process results
for router in routers:
   print(f"Name: {router.name}")
   if router.routing_stack:
      print(f"  Routing Stack: {router.routing_stack.value}")
   if router.vrf:
      for vrf in router.vrf:
         print(f"  VRF: {vrf.name}")
         if vrf.bgp and vrf.bgp.enable:
            print(f"    BGP: AS {vrf.bgp.local_as}")
         if vrf.ospf and vrf.ospf.enable:
            print(f"    OSPF: Router ID {vrf.ospf.router_id}")
         if vrf.ecmp and vrf.ecmp.enable:
            print(f"    ECMP: max_path={vrf.ecmp.max_path}")

# List with routing_stack filter
advanced_routers = client.logical_router.list(
   folder="Texas",
   routing_stack=["advanced"]
)

for router in advanced_routers:
   print(f"Advanced router: {router.name}")
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters,
you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices` parameters to control
which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return routers defined exactly in 'Texas'
exact_routers = client.logical_router.list(
   folder='Texas',
   exact_match=True
)

for router in exact_routers:
   print(f"Exact match: {router.name} in {router.folder}")

# Exclude all routers from the 'All' folder
no_all_routers = client.logical_router.list(
   folder='Texas',
   exclude_folders=['All']
)

for router in no_all_routers:
   assert router.folder != 'All'
   print(f"Filtered out 'All': {router.name}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

**Example:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Configure max_limit using the property setter
client.logical_router.max_limit = 4000

# List all routers - auto-paginates through results
all_routers = client.logical_router.list(folder='Texas')
```

### Deleting Logical Routers

```python
# Delete by ID
router_id = "123e4567-e89b-12d3-a456-426655440000"
client.logical_router.delete(router_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["Texas"],
   "description": "Updated logical router configurations",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
   print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   NameNotUniqueError,
   ObjectNotPresentError,
   ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create logical router configuration
   router_config = {
      "name": "test-router",
      "routing_stack": "advanced",
      "vrf": [
         {
            "name": "vrf-default",
            "interface": ["ethernet1/1"],
            "routing_table": {
               "ip": {
                  "static_route": [
                     {
                        "name": "default-route",
                        "destination": "0.0.0.0/0",
                        "nexthop": {
                           "ip_address": "10.0.0.1"
                        },
                        "metric": 10
                     }
                  ]
               }
            }
         }
      ],
      "folder": "Texas"
   }

   # Create the router using the unified client interface
   new_router = client.logical_router.create(router_config)

   # Commit changes directly from the client
   result = client.commit(
      folders=["Texas"],
      description="Added test logical router",
      sync=True
   )

   # Check job status directly from the client
   status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
   print(f"Invalid router data: {e.message}")
except NameNotUniqueError as e:
   print(f"Router name already exists: {e.message}")
except ObjectNotPresentError as e:
   print(f"Router not found: {e.message}")
except ReferenceNotZeroError as e:
   print(f"Router still in use: {e.message}")
except MissingQueryParameterError as e:
   print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
   - Use the unified client interface (`client.logical_router`) for streamlined code
   - Create a single client instance and reuse it across your application
   - Perform commit operations directly on the client object (`client.commit()`)

2. **VRF Design**
   - Use separate VRFs to segment routing domains (e.g., production, management, guest)
   - Assign interfaces to VRFs before configuring routing protocols
   - Use descriptive VRF names that indicate their purpose
   - Configure administrative distances to control route preference between protocols

3. **Routing Protocol Configuration**
   - Enable only the routing protocols you need within each VRF
   - For BGP, always set `router_id` and `local_as` explicitly
   - For OSPF, assign the backbone area (`0.0.0.0`) first, then add stub or NSSA areas
   - Use ECMP to distribute traffic across multiple paths for high availability
   - Configure graceful restart for both BGP and OSPF to minimize disruption during failovers

4. **Static Routes**
   - Use static routes for simple default routing and well-known destinations
   - Set appropriate administrative distances when mixing static routes with dynamic protocols
   - Configure path monitoring on critical static routes to detect next-hop failures
   - Use BFD profiles for fast failure detection on static route next-hops

5. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names across operations
   - Validate container existence before operations

6. **Error Handling**
   - Implement comprehensive error handling for all operations
   - Check job status after commits
   - Handle specific exceptions before generic ones
   - Log error details for troubleshooting

7. **Performance**
   - Use appropriate pagination for list operations
   - Cache frequently accessed router configurations
   - Implement proper retry mechanisms
   - Use the `routing_stack` filter on `list()` to narrow results

## Related Models

- [LogicalRouterBaseModel](../../models/network/logical_router_models.md#Overview)
- [LogicalRouterCreateModel](../../models/network/logical_router_models.md#Overview)
- [LogicalRouterUpdateModel](../../models/network/logical_router_models.md#Overview)
- [LogicalRouterResponseModel](../../models/network/logical_router_models.md#Overview)
- [VrfConfig](../../models/network/logical_router_models.md#Overview)
- [BgpConfig](../../models/network/logical_router_models.md#Overview)
- [OspfConfig](../../models/network/logical_router_models.md#Overview)
- [EcmpConfig](../../models/network/logical_router_models.md#Overview)
