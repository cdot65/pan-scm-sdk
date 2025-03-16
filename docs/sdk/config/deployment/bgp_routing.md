# BGP Routing

The BGP Routing module allows you to configure BGP (Border Gateway Protocol) routing for Prisma SD-WAN service connections and remote networks. This module supports standard BGP configurations including autonomous system numbers, peers, route preferences, and filtering.

## Class Overview

The `BGPRouting` class provides functionality to create, update, delete, and fetch BGP routing configurations in Strata Cloud Manager.

```python
from scm.config.deployment import BGPRouting
from scm.client import Scm

# Initialize the client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize the BGP routing service
bgp_routing = BGPRouting(client)

# Alternatively, use the unified client pattern
# Access BGP routing directly through the client
bgp_config = client.bgp_routing
```

## Methods

### List BGP Routing Configurations

Retrieve a list of all BGP routing configurations in the specified folder.

```python
# List BGP routing configurations
bgp_configs = client.bgp_routing.list(folder="Texas")

# Process the BGP configurations
for config in bgp_configs:
    print(f"BGP Config: {config.name}")
    print(f"  AS Number: {config.local_as_number}")
    print(f"  Peers: {len(config.peers)}")
```

### Fetch a BGP Routing Configuration

Retrieve a specific BGP routing configuration by name.

```python
# Fetch specific BGP config by name
bgp_config = client.bgp_routing.fetch(
    name="isp-connection-1-bgp",
    folder="Texas"
)

print(f"BGP Config: {bgp_config.name}")
print(f"Local AS: {bgp_config.local_as_number}")
print(f"Peers: {[peer.name for peer in bgp_config.peers]}")
```

### Create a BGP Routing Configuration

Create a new BGP routing configuration.

```python
# Create a new BGP routing configuration
new_bgp_config = client.bgp_routing.create({
    "name": "branch-office-bgp",
    "folder": "Texas",
    "local_as_number": 65001,
    "router_id": "10.0.0.1",
    "peers": [
        {
            "name": "isp-peer-1",
            "peer_as_number": 65002,
            "peer_ip_address": "192.168.1.1"
        },
        {
            "name": "isp-peer-2",
            "peer_as_number": 65003,
            "peer_ip_address": "192.168.2.1"
        }
    ],
    "networks": [
        {
            "network": "10.1.0.0/16",
            "route_map": "outbound-policy"
        }
    ]
})

print(f"Created BGP configuration: {new_bgp_config.name} with ID: {new_bgp_config.id}")
```

### Update a BGP Routing Configuration

Update an existing BGP routing configuration.

```python
# Fetch the configuration first
bgp_config = client.bgp_routing.fetch(
    name="branch-office-bgp",
    folder="Texas"
)

# Modify the configuration
bgp_config.description = "Updated BGP configuration for branch office"
bgp_config.local_as_number = 65005  # Update AS number

# Add a new peer
bgp_config.peers.append({
    "name": "backup-isp-peer",
    "peer_as_number": 65100,
    "peer_ip_address": "192.168.3.1"
})

# Update the configuration
updated_bgp = client.bgp_routing.update(bgp_config)
print(f"Updated BGP configuration: {updated_bgp.name}")
print(f"New peer count: {len(updated_bgp.peers)}")
```

### Delete a BGP Routing Configuration

Delete a BGP routing configuration.

```python
# Delete by ID
client.bgp_routing.delete("123456789")

# Or by providing a model
client.bgp_routing.delete(bgp_config)

print("BGP configuration deleted successfully")
```

## Integrating with Service Connections

BGP routing configurations can be associated with service connections to enable dynamic routing between your network and service providers.

```python
# First, fetch your service connection
service_conn = client.service_connection.fetch(
    name="aws-connection",
    folder="Texas"
)

# Then, fetch your BGP configuration
bgp_config = client.bgp_routing.fetch(
    name="aws-bgp",
    folder="Texas"
)

# Associate BGP with service connection
service_conn.routing = {
    "bgp": {
        "id": bgp_config.id,
        "enabled": True
    }
}

# Update the service connection
updated_conn = client.service_connection.update(service_conn)
print(f"Updated service connection with BGP routing: {updated_conn.name}")
```

## Error Handling

Handle potential errors when working with BGP routing configurations:

```python
from scm.exceptions import ScmApiError, ResourceNotFoundError

try:
    bgp_config = client.bgp_routing.fetch(
        name="non-existent-bgp",
        folder="Texas"
    )
except ResourceNotFoundError:
    print("BGP configuration not found")
except ScmApiError as e:
    print(f"API Error: {e}")
```