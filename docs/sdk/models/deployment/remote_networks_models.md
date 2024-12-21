# Remote Network Models

## Overview

The Remote Network models provide a structured way to manage remote network configurations in Palo Alto Networks' Strata Cloud Manager.
These models support both ECMP and non-ECMP configurations, BGP peering options, and various licensing types. The models handle
validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute              | Type                  | Required | Default         | Description                                                           |
|------------------------|-----------------------|----------|-----------------|-----------------------------------------------------------------------|
| name                   | str                   | Yes      | None            | Name of remote network. Must start with letter, allows [0-9a-zA-Z._-] |
| region                 | str                   | Yes      | None            | Region where remote network is deployed                               |
| license_type           | str                   | No       | FWAAS-AGGREGATE | License type (new customers use aggregate licensing)                  |
| description            | str                   | No       | None            | Description of remote network. Max length: 1023 chars                 |
| subnets                | List[str]             | No       | None            | List of subnets in remote network                                     |
| spn_name               | str                   | No*      | None            | Required when license_type is FWAAS-AGGREGATE                         |
| ecmp_load_balancing    | EcmpLoadBalancingEnum | No       | disable         | Enable or disable ECMP load balancing                                 |
| ecmp_tunnels           | List[EcmpTunnelModel] | No**     | None            | Required when ecmp_load_balancing is enable. Max 4 tunnels            |
| ipsec_tunnel           | str                   | No**     | None            | Required when ecmp_load_balancing is disable                          |
| secondary_ipsec_tunnel | str                   | No       | None            | Optional secondary IPSec tunnel                                       |
| protocol               | ProtocolModel         | No       | None            | BGP protocol configuration                                            |
| folder                 | str                   | No***    | None            | Folder where network is defined. Max length: 64 chars                 |
| snippet                | str                   | No***    | None            | Snippet where network is defined. Max length: 64 chars                |
| device                 | str                   | No***    | None            | Device where network is defined. Max length: 64 chars                 |
| id                     | UUID                  | Yes****  | None            | UUID of remote network (response only)                                |

\* Required when license_type is FWAAS-AGGREGATE
\** Either ecmp_tunnels (when enabled) or ipsec_tunnel (when disabled) must be provided
\*** Exactly one container type (folder/snippet/device) must be provided for create operations
\**** Only required for response model

## Exceptions

The Remote Network models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
    - When ecmp_tunnels is not provided when ecmp_load_balancing is enabled
    - When ipsec_tunnel is not provided when ecmp_load_balancing is disabled
    - When spn_name is not provided with FWAAS-AGGREGATE license type
    - When multiple container types are specified for create operations
    - When no container type is specified for create operations
    - When name pattern validation fails
    - When container name pattern validation fails

## Model Validators

### Remote Network Logic Validation

The models enforce specific logic based on ECMP and license settings:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
from scm.models.deployment import RemoteNetworkCreateModel

# Error: missing ecmp_tunnels when ECMP enabled
try:
    network = RemoteNetworkCreateModel(
        name="invalid-network",
        region="us-east-1",
        ecmp_load_balancing="enable",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "ecmp_tunnels is required when ecmp_load_balancing is enable"

# Error: missing ipsec_tunnel when ECMP disabled
try:
    network = RemoteNetworkCreateModel(
        name="invalid-network",
        region="us-east-1",
        folder="Texas"
    )
except ValueError as e:
    print(e)  # "ipsec_tunnel is required when ecmp_load_balancing is disable"
```

</div>

### Container Type Validation

For create operations, exactly one container type must be specified:

<div class="termy">

<!-- termynal -->

```python
# This will raise a validation error
try:
    network = RemoteNetworkCreateModel(
        name="invalid-network",
        region="us-east-1",
        ipsec_tunnel="tunnel1",
        folder="Texas",
        device="fw01"  # Can't specify both folder and device
    )
except ValueError as e:
    print(e)  # "Exactly one of 'folder' must be provided."
```

</div>

## Usage Examples

### Creating a Non-ECMP Remote Network

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from scm.config.deployment import RemoteNetwork

network_dict = {
    "name": "branch-office",
    "region": "us-east-1",
    "description": "Branch office network",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "branch-spn",
    "ipsec_tunnel": "tunnel1",
    "subnets": ["192.168.1.0/24"],
    "folder": "Texas"
}

remote_network = RemoteNetwork(api_client)
response = remote_network.create(network_dict)

# Using model directly
from scm.models.deployment import RemoteNetworkCreateModel

network = RemoteNetworkCreateModel(
    name="branch-office",
    region="us-east-1",
    description="Branch office network",
    license_type="FWAAS-AGGREGATE",
    spn_name="branch-spn",
    ipsec_tunnel="tunnel1",
    subnets=["192.168.1.0/24"],
    folder="Texas"
)

payload = network.model_dump(exclude_unset=True)
response = remote_network.create(payload)
```

</div>

### Creating an ECMP Remote Network

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
ecmp_dict = {
    "name": "datacenter",
    "region": "us-west-1",
    "description": "Datacenter network with ECMP",
    "license_type": "FWAAS-AGGREGATE",
    "spn_name": "dc-spn",
    "ecmp_load_balancing": "enable",
    "ecmp_tunnels": [
        {
            "name": "tunnel1",
            "ipsec_tunnel": "ipsec1",
            "peer_as": "65000",
            "peer_ip_address": "10.0.0.1"
        },
        {
            "name": "tunnel2",
            "ipsec_tunnel": "ipsec2",
            "peer_as": "65000",
            "peer_ip_address": "10.0.0.2"
        }
    ],
    "folder": "Texas"
}

response = remote_network.create(ecmp_dict)

# Using model directly
from scm.models.deployment import RemoteNetworkCreateModel, EcmpTunnelModel

ecmp_tunnels = [
    EcmpTunnelModel(
        name="tunnel1",
        ipsec_tunnel="ipsec1",
        peer_as="65000",
        peer_ip_address="10.0.0.1"
    ),
    EcmpTunnelModel(
        name="tunnel2",
        ipsec_tunnel="ipsec2",
        peer_as="65000",
        peer_ip_address="10.0.0.2"
    )
]

network = RemoteNetworkCreateModel(
    name="datacenter",
    region="us-west-1",
    description="Datacenter network with ECMP",
    license_type="FWAAS-AGGREGATE",
    spn_name="dc-spn",
    ecmp_load_balancing="enable",
    ecmp_tunnels=ecmp_tunnels,
    folder="Texas"
)

payload = network.model_dump(exclude_unset=True)
response = remote_network.create(payload)
```

</div>

### Updating a Remote Network

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "branch-office-updated",
    "description": "Updated branch office network",
    "subnets": ["192.168.1.0/24", "192.168.2.0/24"],
    "ipsec_tunnel": "tunnel2"
}

response = remote_network.update(update_dict)

# Using model directly
from scm.models.deployment import RemoteNetworkUpdateModel

update_network = RemoteNetworkUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="branch-office-updated",
    description="Updated branch office network",
    subnets=["192.168.1.0/24", "192.168.2.0/24"],
    ipsec_tunnel="tunnel2"
)

payload = update_network.model_dump(exclude_unset=True)
response = remote_network.update(payload)
```

</div>