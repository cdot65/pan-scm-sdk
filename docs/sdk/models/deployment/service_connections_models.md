# Service Connection Models

## Overview

The Service Connection models provide a structured way to manage service connections in Palo Alto Networks' Strata Cloud Manager.
These models support defining connectivity to cloud service providers with various parameters including BGP configuration,
protocol settings, QoS, and NAT options. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute                | Type                | Required | Default            | Description                                                          |
|--------------------------|---------------------|----------|---------------------|---------------------------------------------------------------------|
| name                     | str                 | Yes      | None               | Name of the service connection. Max 63 chars, must match pattern: `^[0-9a-zA-Z._\- ]+$` |
| id                       | UUID                | Yes***   | None               | UUID of the service connection (response & update only)              |
| folder                   | str                 | Yes      | Service Connections | The folder containing the service connection                         |
| ipsec_tunnel             | str                 | Yes      | None               | IPsec tunnel for the service connection                             |
| onboarding_type          | OnboardingType      | Yes      | classic            | Onboarding type for the service connection                          |
| region                   | str                 | Yes      | None               | Region for the service connection                                   |
| backup_SC                | str                 | No       | None               | Backup service connection                                            |
| bgp_peer                 | BgpPeerModel        | No       | None               | BGP peer configuration                                               |
| nat_pool                 | str                 | No       | None               | NAT pool for the service connection                                 |
| no_export_community      | NoExportCommunity   | No       | None               | No export community configuration                                   |
| protocol                 | ProtocolModel       | No       | None               | Protocol configuration                                               |
| qos                      | QosModel            | No       | None               | QoS configuration                                                    |
| secondary_ipsec_tunnel   | str                 | No       | None               | Secondary IPsec tunnel                                               |
| source_nat               | bool                | No       | None               | Enable source NAT                                                    |
| subnets                  | List[str]           | No       | None               | Subnets for the service connection                                  |

\*** Only required for update and response models

## Model Structures

### OnboardingType Enum

Defines the types of onboarding for service connections:

| Value       | Description                     |
|-------------|---------------------------------|
| CLASSIC     | Classic onboarding               |

### NoExportCommunity Enum

Defines the no export community options for service connections:

| Value        | Description                     |
|--------------|---------------------------------|
| DISABLED     | No export community disabled     |
| ENABLED_IN   | No export community enabled for inbound |
| ENABLED_OUT  | No export community enabled for outbound |
| ENABLED_BOTH | No export community enabled for both directions |

### BgpPeerModel

Contains the BGP peer configuration for service connections:

| Attribute         | Type   | Required | Description                          |
|-------------------|--------|----------|--------------------------------------|
| local_ip_address  | str    | No       | Local IPv4 address for BGP peering   |
| local_ipv6_address| str    | No       | Local IPv6 address for BGP peering   |
| peer_ip_address   | str    | No       | Peer IPv4 address for BGP peering    |
| peer_ipv6_address | str    | No       | Peer IPv6 address for BGP peering    |
| secret            | str    | No       | BGP authentication secret            |

### BgpProtocolModel

Contains the BGP protocol configuration for service connections:

| Attribute                  | Type  | Required | Description                        |
|----------------------------|-------|----------|------------------------------------|
| do_not_export_routes       | bool  | No       | Do not export routes option        |
| enable                     | bool  | No       | Enable BGP                         |
| fast_failover              | bool  | No       | Enable fast failover               |
| local_ip_address           | str   | No       | Local IPv4 address for BGP peering |
| originate_default_route    | bool  | No       | Originate default route            |
| peer_as                    | str   | No       | BGP peer AS number                 |
| peer_ip_address            | str   | No       | Peer IPv4 address for BGP peering  |
| secret                     | str   | No       | BGP authentication secret          |
| summarize_mobile_user_routes| bool | No       | Summarize mobile user routes       |

### ProtocolModel

Contains the protocol configuration for service connections:

| Attribute | Type             | Required | Description                |
|-----------|------------------|----------|----------------------------|
| bgp       | BgpProtocolModel | No       | BGP protocol configuration |

### QosModel

Contains the QoS configuration for service connections:

| Attribute   | Type  | Required | Description     |
|-------------|-------|----------|-----------------|
| enable      | bool  | No       | Enable QoS      |
| qos_profile | str   | No       | QoS profile name|

## Usage Examples

### Creating a Service Connection

<div class="termy">

<!-- termynal -->

```python
# Using direct dictionary
from scm.config.deployment import ServiceConnection

service_connection_dict = {
    "name": "aws-service-connection",
    "ipsec_tunnel": "aws-ipsec-tunnel",
    "region": "us-east-1",
    "onboarding_type": "classic",
    "subnets": ["10.0.0.0/24", "192.168.1.0/24"],
    "bgp_peer": {
        "local_ip_address": "192.168.1.1",
        "peer_ip_address": "192.168.1.2",
    },
    "protocol": {
        "bgp": {
            "enable": True,
            "peer_as": "65000",
        }
    },
    "source_nat": True
}

service_connection = ServiceConnection(api_client)
response = service_connection.create(service_connection_dict)

# Using model directly
from scm.models.deployment import ServiceConnectionCreateModel

service_connection_obj = ServiceConnectionCreateModel(
    name="aws-service-connection",
    ipsec_tunnel="aws-ipsec-tunnel",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24", "192.168.1.0/24"],
    bgp_peer={
        "local_ip_address": "192.168.1.1",
        "peer_ip_address": "192.168.1.2",
    },
    protocol={
        "bgp": {
            "enable": True,
            "peer_as": "65000",
        }
    },
    source_nat=True
)

payload = service_connection_obj.model_dump(exclude_unset=True, by_alias=True)
response = service_connection.create(payload)
```

</div>

### Updating a Service Connection

<div class="termy">

<!-- termynal -->

```python
# Using dictionary
from uuid import UUID

update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "aws-service-connection-updated",
    "ipsec_tunnel": "aws-ipsec-tunnel",
    "region": "us-east-1",
    "onboarding_type": "classic",
    "subnets": ["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/24"],
    "source_nat": False
}

response = service_connection.update(update_dict)

# Using model directly
from scm.models.deployment import ServiceConnectionUpdateModel

update_obj = ServiceConnectionUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="aws-service-connection-updated",
    ipsec_tunnel="aws-ipsec-tunnel",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/24"],
    source_nat=False
)

payload = update_obj.model_dump(exclude_unset=True, by_alias=True)
response = service_connection.update(payload)
```

</div>

### Configuring BGP with Authentication

<div class="termy">

<!-- termynal -->

```python
# Creating a service connection with BGP authentication
from scm.models.deployment import ServiceConnectionCreateModel, BgpPeerModel, ProtocolModel, BgpProtocolModel

# Create BGP peer model
bgp_peer = BgpPeerModel(
    local_ip_address="192.168.1.1",
    peer_ip_address="192.168.1.2",
    secret="mysecretkey"  # Authentication key
)

# Create BGP protocol model
bgp_protocol = BgpProtocolModel(
    enable=True,
    peer_as="65000",
    fast_failover=True,
    originate_default_route=True,
    secret="mysecretkey"  # Authentication key should match
)

# Create protocol model
protocol = ProtocolModel(
    bgp=bgp_protocol
)

# Create the service connection model
service_connection_obj = ServiceConnectionCreateModel(
    name="aws-service-connection-bgp",
    ipsec_tunnel="aws-ipsec-tunnel-bgp",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24"],
    bgp_peer=bgp_peer,
    protocol=protocol,
    source_nat=True
)

payload = service_connection_obj.model_dump(exclude_unset=True, by_alias=True)
response = service_connection.create(payload)
```

</div>

### QoS Configuration

<div class="termy">

<!-- termynal -->

```python
# Creating a service connection with QoS
from scm.models.deployment import ServiceConnectionCreateModel, QosModel

# Create QoS model
qos = QosModel(
    enable=True,
    qos_profile="high-priority"
)

# Create the service connection model
service_connection_obj = ServiceConnectionCreateModel(
    name="aws-service-connection-qos",
    ipsec_tunnel="aws-ipsec-tunnel-qos",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24"],
    qos=qos,
    source_nat=True
)

payload = service_connection_obj.model_dump(exclude_unset=True, by_alias=True)
response = service_connection.create(payload)
```

</div>