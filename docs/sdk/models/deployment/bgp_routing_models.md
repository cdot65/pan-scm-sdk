# BGP Routing Models

This page describes the Pydantic models used for BGP routing configuration in the Strata Cloud Manager SDK.

## Overview

The BGP Routing models are a crucial component of the Strata Cloud Manager SDK, enabling programmatic configuration and management of Border Gateway Protocol (BGP) settings in Prisma SD-WAN environments. These models serve as the interface between your application code and the underlying network infrastructure, allowing for precise control over routing behaviors.

The BGP Routing models define the data structures for Border Gateway Protocol (BGP) routing configuration in Prisma SD-WAN. These models handle attributes such as:

- BGP autonomous system numbers
- Router IDs
- BGP peers
- Network advertisements
- Route filtering
- BGP timers and other protocol parameters

By utilizing these models, you can create, update, and manage BGP configurations across your network, ensuring consistent and efficient routing policies.

## Base Models

### BGPRoutingRequest

The base request model for BGP routing configurations.

```python
class BGPRoutingRequest(BaseModel):
    name: str
    folder: str
    description: Optional[str] = None
    local_as_number: int
    router_id: str
    peers: List[BGPPeerRequest]
    networks: Optional[List[BGPNetworkRequest]] = None
    route_maps: Optional[List[BGPRouteMapRequest]] = None
    redistribution: Optional[BGPRedistributionRequest] = None
    timers: Optional[BGPTimerRequest] = None
```

### BGPRoutingResponse

The response model for BGP routing configurations.

```python
class BGPRoutingResponse(BaseModel):
    id: str
    name: str
    folder: str
    description: Optional[str] = None
    local_as_number: int
    router_id: str
    peers: List[BGPPeerResponse]
    networks: Optional[List[BGPNetworkResponse]] = None
    route_maps: Optional[List[BGPRouteMapResponse]] = None
    redistribution: Optional[BGPRedistributionResponse] = None
    timers: Optional[BGPTimerResponse] = None
    creation_time: datetime
    last_modified_time: datetime
```

## BGP Peer Models

Models for BGP peer configurations.

### BGPPeerRequest

```python
class BGPPeerRequest(BaseModel):
    name: str
    peer_as_number: int
    peer_ip_address: str
    description: Optional[str] = None
    connection_options: Optional[BGPConnectionOptions] = None
    route_filtering: Optional[BGPRouteFiltering] = None
    authentication: Optional[BGPAuthentication] = None
```

### BGPPeerResponse

```python
class BGPPeerResponse(BaseModel):
    id: str
    name: str
    peer_as_number: int
    peer_ip_address: str
    description: Optional[str] = None
    connection_options: Optional[BGPConnectionOptions] = None
    route_filtering: Optional[BGPRouteFiltering] = None
    authentication: Optional[BGPAuthentication] = None
    state: Optional[str] = None
    status: Optional[str] = None
    last_state_change: Optional[datetime] = None
```

## BGP Network and Route Map Models

Models for networks advertised via BGP and route maps for policy-based routing.

### BGPNetworkRequest

```python
class BGPNetworkRequest(BaseModel):
    network: str  # CIDR notation
    route_map: Optional[str] = None
```

### BGPNetworkResponse

```python
class BGPNetworkResponse(BaseModel):
    id: str
    network: str
    route_map: Optional[str] = None
```

### BGPRouteMapRequest

```python
class BGPRouteMapRequest(BaseModel):
    name: str
    entries: List[BGPRouteMapEntry]
```

### BGPRouteMapResponse

```python
class BGPRouteMapResponse(BaseModel):
    id: str
    name: str
    entries: List[BGPRouteMapEntry]
```

## Supporting Models

Additional models to support BGP configuration.

### BGPConnectionOptions

```python
class BGPConnectionOptions(BaseModel):
    multihop: Optional[bool] = False
    multihop_ttl: Optional[int] = 1
    connect_retry_time: Optional[int] = 120
    hold_time: Optional[int] = 180
    keepalive_interval: Optional[int] = 60
    passive: Optional[bool] = False
```

### BGPRouteFiltering

```python
class BGPRouteFiltering(BaseModel):
    inbound_route_map: Optional[str] = None
    outbound_route_map: Optional[str] = None
    prefix_list_in: Optional[str] = None
    prefix_list_out: Optional[str] = None
    weight: Optional[int] = None
    maximum_prefixes: Optional[int] = None
```

### BGPAuthentication

```python
class BGPAuthentication(BaseModel):
    auth_type: Literal["MD5", "KEYCHAIN"]
    key_id: Optional[int] = None
    key: Optional[str] = None
    keychain_name: Optional[str] = None
```

### BGPRedistributionRequest

```python
class BGPRedistributionRequest(BaseModel):
    connected: Optional[BGPRedistributionRule] = None
    static: Optional[BGPRedistributionRule] = None
    ospf: Optional[BGPRedistributionRule] = None
```

### BGPRedistributionRule

```python
class BGPRedistributionRule(BaseModel):
    enabled: bool = False
    route_map: Optional[str] = None
    metric: Optional[int] = None
```

### BGPTimerRequest

```python
class BGPTimerRequest(BaseModel):
    keepalive: int = 60
    hold_time: int = 180
    connect_retry: int = 120
```

## Usage Examples

### Creating BGP Routing Configuration

```python
from scm.models.deployment.bgp_routing import BGPRoutingRequest, BGPPeerRequest

# Create BGP peer configuration
peer = BGPPeerRequest(
    name="isp-peer-1",
    peer_as_number=65002,
    peer_ip_address="192.168.1.1",
    description="Primary ISP peering"
)

# Create BGP routing configuration
bgp_config = BGPRoutingRequest(
    name="branch-office-bgp",
    folder="Texas",
    description="BGP configuration for branch office",
    local_as_number=65001,
    router_id="10.0.0.1",
    peers=[peer],
    networks=[{"network": "10.1.0.0/16"}]
)

# Use the model with the SDK
client.bgp_routing.create(bgp_config)
```

### Parsing BGP Configuration Response

```python
from scm.models.deployment.bgp_routing import BGPRoutingResponse

# Parse API response into BGP Routing model
bgp_response = BGPRoutingResponse.parse_obj(api_response_json)

# Access model attributes
print(f"BGP Configuration: {bgp_response.name}")
print(f"Local AS: {bgp_response.local_as_number}")

# Process peers
for peer in bgp_response.peers:
    print(f"Peer: {peer.name} (AS {peer.peer_as_number})")
    print(f"  Status: {peer.status}")
    if peer.route_filtering:
        print(f"  Route Map In: {peer.route_filtering.inbound_route_map}")
```