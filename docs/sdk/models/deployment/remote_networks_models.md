# Remote Networks Models

## Overview {#Overview}

The Remote Networks models provide a structured way to manage remote network connections in Palo Alto Networks' Strata Cloud Manager. These models are integral to the SD-WAN architecture, working in conjunction with Service Connections and BGP Routing configurations to establish secure and efficient connectivity between branch offices and cloud resources.

These models support configuration of remote network sites with options for IPsec tunnels, BGP protocol settings, and Equal-Cost Multi-Path (ECMP) load balancing. By leveraging these models, you can define and manage the connectivity of distributed network locations, ensuring consistent security policies and optimal routing across your organization's infrastructure.

The models handle validation of inputs and outputs when interacting with the SCM API, providing a robust interface for programmatic management of remote network configurations.

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

### Tunnel Model Attributes

| Attribute       | Type     | Required | Default | Description                          |
|-----------------|----------|----------|---------|--------------------------------------|
| name            | str      | Yes      | None    | Tunnel name                          |
| ipsec_tunnel    | str      | Yes      | None    | IPSec tunnel name                    |
| local_ip_address| str      | Yes      | None    | Local IP address                     |
| peer_ip_address | str      | Yes      | None    | Peer IP address                      |
| peer_as         | str      | Yes      | None    | Peer Autonomous System number        |

### Protocol Model Attributes

| Attribute           | Type    | Required | Default | Description                       |
|---------------------|---------|----------|---------|-----------------------------------|
| bgp                 | BGP     | No       | None    | BGP protocol configuration        |

### BGP Model Attributes

| Attribute           | Type    | Required | Default | Description                       |
|---------------------|---------|----------|---------|-----------------------------------|
| enable              | bool    | No       | None    | Enable BGP                        |
| local_ip_address    | str     | No       | None    | Local IP address for BGP          |
| peer_ip_address     | str     | No       | None    | Peer IP address for BGP           |
| peer_as             | str     | No       | None    | Peer AS number                    |
| local_as            | str     | No       | None    | Local AS number                   |
| secret              | str     | No       | None    | BGP authentication secret         |

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

<div class="termy">

<!-- termynal -->

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

</div>

### License Type Validation

When using FWAAS-AGGREGATE license type, spn_name is required:

<div class="termy">

<!-- termynal -->

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

</div>

### Subnet Format Validation

Subnets must follow proper CIDR notation:

<div class="termy">

<!-- termynal -->

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

</div>

## Usage Examples

### Creating a Standard Remote Network

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.deployment import RemoteNetworks

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

remote_networks = RemoteNetworks(api_client)
response = remote_networks.create(standard_config)

# Using model directly
from scm.models.deployment import RemoteNetworkCreateModel

standard_network = RemoteNetworkCreateModel(
    name="branch-office-1",
    region="us-east-1",
    license_type="FWAAS-AGGREGATE",
    spn_name="us-east-1-spn",
    folder="Remote Networks",
    description="Branch office VPN connection",
    subnets=["10.0.0.0/24", "10.0.1.0/24"],
    ecmp_load_balancing="disable",
    ipsec_tunnel="branch-1-tunnel"
)

payload = standard_network.model_dump(exclude_unset=True)
response = remote_networks.create(payload)
```

</div>

### Creating an ECMP-Enabled Remote Network

<div class="termy">

<!-- termynal -->

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

response = remote_networks.create(ecmp_config)

# Using model directly
from scm.models.deployment import RemoteNetworkCreateModel, Tunnel

ecmp_tunnels = [
    Tunnel(
        name="tunnel-1",
        ipsec_tunnel="branch-2-tunnel-1",
        local_ip_address="10.0.1.1",
        peer_as="65515",
        peer_ip_address="10.0.1.2"
    ),
    Tunnel(
        name="tunnel-2",
        ipsec_tunnel="branch-2-tunnel-2",
        local_ip_address="10.0.2.1",
        peer_as="65515",
        peer_ip_address="10.0.2.2"
    )
]

ecmp_network = RemoteNetworkCreateModel(
    name="branch-office-2",
    region="us-west-2",
    license_type="FWAAS-AGGREGATE",
    spn_name="us-west-2-spn",
    folder="Remote Networks",
    description="Branch office with ECMP",
    subnets=["172.16.0.0/24", "172.16.1.0/24"],
    ecmp_load_balancing="enable",
    ecmp_tunnels=ecmp_tunnels
)

payload = ecmp_network.model_dump(exclude_unset=True)
response = remote_networks.create(payload)
```

</div>

### Creating a Remote Network with BGP Protocol

<div class="termy">

<!-- termynal -->

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
            "local_as": "65001",
            "secret": "bgp-auth-key"
        }
    }
}

response = remote_networks.create(bgp_config)

# Using model directly
from scm.models.deployment import RemoteNetworkCreateModel, Protocol, BGP

bgp = BGP(
    enable=True,
    local_ip_address="10.1.1.1",
    peer_ip_address="10.1.1.2",
    peer_as="65000",
    local_as="65001",
    secret="bgp-auth-key"
)

protocol = Protocol(bgp=bgp)

bgp_network = RemoteNetworkCreateModel(
    name="branch-office-3",
    region="eu-west-1",
    license_type="FWAAS-AGGREGATE",
    spn_name="eu-west-1-spn",
    folder="Remote Networks",
    description="Branch office with BGP",
    subnets=["192.168.1.0/24"],
    ecmp_load_balancing="disable",
    ipsec_tunnel="branch-3-tunnel",
    protocol=protocol
)

payload = bgp_network.model_dump(exclude_unset=True)
response = remote_networks.create(payload)
```

</div>

### Updating a Remote Network

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "name": "branch-office-1",
    "description": "Updated branch office configuration",
    "subnets": ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"],  # Added a new subnet
    "protocol": {
        "bgp": {
            "enable": True,
            "peer_as": "65515",
            "peer_ip_address": "10.0.0.1",
            "local_ip_address": "10.0.0.2"
        }
    }
}

response = remote_networks.update(update_dict)

# Using model directly
from scm.models.deployment import RemoteNetworkUpdateModel, Protocol, BGP

protocol = Protocol(
    bgp=BGP(
        enable=True,
        peer_as="65515",
        peer_ip_address="10.0.0.1",
        local_ip_address="10.0.0.2"
    )
)

update_network = RemoteNetworkUpdateModel(
    name="branch-office-1",
    description="Updated branch office configuration",
    subnets=["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"],
    protocol=protocol
)

payload = update_network.model_dump(exclude_unset=True)
response = remote_networks.update(payload)
```

</div>
