# Remote Networks Models

## Overview {#Overview}

The Remote Networks models provide a structured way to manage remote network connections in Palo Alto Networks' Strata Cloud Manager. These models are integral to the SD-WAN architecture, working in conjunction with Service Connections and BGP Routing configurations to establish secure and efficient connectivity between branch offices and cloud resources.

These models support configuration of remote network sites with options for IPsec tunnels, BGP protocol settings, and Equal-Cost Multi-Path (ECMP) load balancing. By leveraging these models, you can define and manage the connectivity of distributed network locations, ensuring consistent security policies and optimal routing across your organization's infrastructure.

The models handle validation of inputs and outputs when interacting with the SCM API, providing a robust interface for programmatic management of remote network configurations.

### Models

The module provides the following Pydantic models:

- `RemoteNetworkBaseModel`: Base model with fields common to all remote network operations
- `RemoteNetworkCreateModel`: Model for creating new remote networks
- `RemoteNetworkUpdateModel`: Model for updating existing remote networks
- `RemoteNetworkResponseModel`: Response model for remote network operations
- `EcmpTunnelModel`: Model for ECMP tunnel configuration
- `ProtocolModel`: Model for protocol settings (BGP and BGP peer)
- `BgpModel`: Model for BGP configuration
- `BgpPeerModel`: Model for BGP peer configuration
- `EcmpLoadBalancingEnum`: Enum for ECMP load balancing states (enable/disable)
- `PeeringTypeEnum`: Enum for BGP peering types

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Attributes

| Attribute           | Type           | Required  | Default | Description                                                      |
|---------------------|----------------|-----------|---------|------------------------------------------------------------------|
| name                | str            | Yes       | None    | Name of the remote network. Pattern: ^[a-zA-Z0-9_ .-]+$          |
| id                  | UUID           | Yes*      | None    | Unique identifier (*response only)                               |
| region              | str            | Yes       | None    | AWS region for deployment (e.g., us-east-1)                      |
| license_type        | str            | Yes       | None    | License type (defaults to FWAAS-AGGREGATE)                       |
| spn_name            | str            | Yes**     | None    | Service Provider Name (**required for FWAAS)                     |
| subnets             | List[str]      | No        | []      | List of network subnets                                          |
| description         | str            | No        | None    | Description of the remote network                                |
| ecmp_load_balancing | str            | Yes       | None    | ECMP mode (enable/disable)                                       |
| ecmp_tunnels        | List[Tunnel]   | Yes***    | None    | ECMP tunnel configurations (***if ECMP enabled)                  |
| ipsec_tunnel        | str            | Yes***    | None    | IPSec tunnel name (***if ECMP disabled)                          |
| protocol            | Protocol       | No        | None    | BGP protocol configuration                                        |
| folder              | str            | Yes       | None    | Folder where the remote network is defined                        |

\* Only required for response model
\** Required when license_type is FWAAS-AGGREGATE
\*** One of these is required based on ecmp_load_balancing setting

### EcmpTunnelModel Attributes

| Attribute                    | Type            | Required | Default | Description                              |
|------------------------------|-----------------|----------|---------|------------------------------------------|
| name                         | str             | Yes      | None    | Tunnel name (max 63 chars)               |
| ipsec_tunnel                 | str             | Yes      | None    | IPSec tunnel name (max 1023 chars)       |
| local_ip_address             | str             | No       | None    | Local IP address                         |
| peer_ip_address              | str             | No       | None    | Peer IP address                          |
| peer_as                      | str             | No       | None    | Peer Autonomous System number            |
| peering_type                 | PeeringTypeEnum | No       | None    | BGP peering type                         |
| secret                       | str             | No       | None    | Authentication secret                    |
| summarize_mobile_user_routes | bool            | No       | None    | Summarize mobile user routes             |
| do_not_export_routes         | bool            | No       | None    | Do not export routes                     |
| originate_default_route      | bool            | No       | None    | Originate default route                  |

### ProtocolModel Attributes

| Attribute | Type         | Required | Default | Description                |
|-----------|--------------|----------|---------|----------------------------|
| bgp       | BgpModel     | No       | None    | BGP protocol configuration |
| bgp_peer  | BgpPeerModel | No       | None    | BGP peer configuration     |

### BgpModel Attributes

| Attribute                    | Type            | Required | Default | Description                       |
|------------------------------|-----------------|----------|---------|-----------------------------------|
| enable                       | bool            | No       | None    | Enable BGP                        |
| local_ip_address             | str             | No       | None    | Local IP address for BGP          |
| peer_ip_address              | str             | No       | None    | Peer IP address for BGP           |
| peer_as                      | str             | No       | None    | Peer AS number                    |
| peering_type                 | PeeringTypeEnum | No       | None    | BGP peering type                  |
| secret                       | str             | No       | None    | BGP authentication secret         |
| do_not_export_routes         | bool            | No       | None    | Do not export routes              |
| originate_default_route      | bool            | No       | None    | Originate default route           |
| summarize_mobile_user_routes | bool            | No       | None    | Summarize mobile user routes      |

### BgpPeerModel Attributes

| Attribute        | Type | Required | Default | Description              |
|------------------|------|----------|---------|--------------------------|
| local_ip_address | str  | No       | None    | Local IP address         |
| peer_ip_address  | str  | No       | None    | Peer IP address          |
| secret           | str  | No       | None    | Authentication secret    |

### Enum Classes

#### EcmpLoadBalancingEnum

| Value     | Description                    |
|-----------|--------------------------------|
| `enable`  | Enable ECMP load balancing     |
| `disable` | Disable ECMP load balancing    |

#### PeeringTypeEnum

| Value                           | Description                              |
|---------------------------------|------------------------------------------|
| `exchange-v4-over-v4`           | Exchange IPv4 routes over IPv4           |
| `exchange-v4-v6-over-v4`        | Exchange IPv4 and IPv6 routes over IPv4  |
| `exchange-v4-over-v4-v6-over-v6`| Exchange IPv4 over IPv4, IPv6 over IPv6  |
| `exchange-v6-over-v6`           | Exchange IPv6 routes over IPv6           |

## Exceptions

The Remote Networks models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When ECMP is enabled but ecmp_tunnels is not provided
    - When ECMP is disabled but ipsec_tunnel is not provided
    - When license_type is FWAAS-AGGREGATE but spn_name is not provided
    - When name pattern validation fails
    - When subnet format validation fails
    - When required tunnel attributes are missing
    - When field length limits are exceeded

## Model Validators

### ECMP Configuration Validation

The models enforce consistent configuration based on ECMP mode:

```python
# This will raise a validation error
from scm.models.deployment import RemoteNetworkCreateModel

# Error: ECMP enabled but tunnels not provided
try:
    remote_network = RemoteNetworkCreateModel(
        name="remote-site-1",
        region="us-east-1",
        license_type="FWAAS-AGGREGATE",
        spn_name="us-east-1-spn",
        ecmp_load_balancing="enable",
        # ecmp_tunnels missing
        folder="Remote Networks"
    )
except ValueError as e:
    print(e)  # "When ECMP is enabled, ecmp_tunnels must be provided"

# Error: ECMP disabled but IPsec tunnel not provided
try:
    remote_network = RemoteNetworkCreateModel(
        name="remote-site-1",
        region="us-east-1",
        license_type="FWAAS-AGGREGATE",
        spn_name="us-east-1-spn",
        ecmp_load_balancing="disable",
        # ipsec_tunnel missing
        folder="Remote Networks"
    )
except ValueError as e:
    print(e)  # "When ECMP is disabled, ipsec_tunnel must be provided"
```

### License Type Validation

When using FWAAS-AGGREGATE license type, spn_name is required:

```python
# This will raise a validation error
try:
    remote_network = RemoteNetworkCreateModel(
        name="remote-site-1",
        region="us-east-1",
        license_type="FWAAS-AGGREGATE",
        # spn_name missing
        ecmp_load_balancing="disable",
        ipsec_tunnel="tunnel1",
        folder="Remote Networks"
    )
except ValueError as e:
    print(e)  # "When license_type is FWAAS-AGGREGATE, spn_name must be provided"
```

### Subnet Format Validation

Subnets must follow proper CIDR notation:

```python
# This will raise a validation error
try:
    remote_network = RemoteNetworkCreateModel(
        name="remote-site-1",
        region="us-east-1",
        license_type="FWAAS-AGGREGATE",
        spn_name="us-east-1-spn",
        ecmp_load_balancing="disable",
        ipsec_tunnel="tunnel1",
        subnets=["invalid-subnet"],  # Should be CIDR notation like 192.168.1.0/24
        folder="Remote Networks"
    )
except ValueError as e:
    print(e)  # "Subnet must be in CIDR notation (e.g., 192.168.1.0/24)"
```

## Usage Examples

### Creating a Standard Remote Network

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
standard_config = {
    "name": "branch-office-1",
    "region": "us-east-1",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-east-1-spn",
    "folder": "Remote Networks",
    "description": "Branch office VPN connection",
    "subnets": ["10.0.0.0/24", "10.0.1.0/24"],
    "ecmp_load_balancing": "disable",
    "ipsec_tunnel": "branch-1-tunnel"
}

response = client.remote_network.create(standard_config)
print(f"Created remote network: {response.name} with ID: {response.id}")
```

### Creating an ECMP-Enabled Remote Network

```python
# Using dictionary
ecmp_config = {
    "name": "branch-office-2",
    "region": "us-west-2",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "us-west-2-spn",
    "folder": "Remote Networks",
    "description": "Branch office with ECMP",
    "subnets": ["172.16.0.0/24", "172.16.1.0/24"],
    "ecmp_load_balancing": "enable",
    "ecmp_tunnels": [
        {
            "name": "tunnel-1",
            "ipsec_tunnel": "branch-2-tunnel-1",
            "local_ip_address": "10.0.1.1",
            "peer_as": "65515",
            "peer_ip_address": "10.0.1.2"
        },
        {
            "name": "tunnel-2",
            "ipsec_tunnel": "branch-2-tunnel-2",
            "local_ip_address": "10.0.2.1",
            "peer_as": "65515",
            "peer_ip_address": "10.0.2.2"
        }
    ]
}

response = client.remote_network.create(ecmp_config)
print(f"Created ECMP remote network: {response.name}")
```

### Creating a Remote Network with BGP Protocol

```python
# Using dictionary
bgp_config = {
    "name": "branch-office-3",
    "region": "eu-west-1",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "eu-west-1-spn",
    "folder": "Remote Networks",
    "description": "Branch office with BGP",
    "subnets": ["192.168.1.0/24"],
    "ecmp_load_balancing": "disable",
    "ipsec_tunnel": "branch-3-tunnel",
    "protocol": {
        "bgp": {
            "enable": True,
            "local_ip_address": "10.1.1.1",
            "peer_ip_address": "10.1.1.2",
            "peer_as": "65000",
            "secret": "bgp-auth-key"
        }
    }
}

response = client.remote_network.create(bgp_config)
print(f"Created BGP remote network: {response.name}")
```

### Updating a Remote Network

```python
# Fetch existing remote network
existing = client.remote_network.fetch(
    name="branch-office-1",
    folder="Remote Networks"
)

# Modify attributes using dot notation
existing.description = "Updated branch office configuration"
existing.subnets = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]

# Add BGP configuration
existing.protocol = {
    "bgp": {
        "enable": True,
        "peer_as": "65515",
        "peer_ip_address": "10.0.0.1",
        "local_ip_address": "10.0.0.2"
    }
}

# Pass modified object to update()
updated = client.remote_network.update(existing)
print(f"Updated remote network: {updated.name}")
```
