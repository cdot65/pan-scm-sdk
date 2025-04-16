# Service Connection Models

## Overview {#Overview}

The Service Connection models are a key component in Palo Alto Networks' Strata Cloud Manager SDK, providing a structured way to manage and configure connections to cloud service providers. These models work in tandem with Remote Networks and BGP Routing configurations to establish secure, optimized connectivity between your on-premises infrastructure and cloud resources.

Service Connection models support defining connectivity to cloud service providers with various parameters including BGP configuration, protocol settings, QoS, and NAT options. By utilizing these models, you can programmatically manage and customize your cloud connectivity, ensuring consistent security policies and efficient routing across hybrid and multi-cloud environments.

The models handle validation of inputs and outputs when interacting with the SCM API, offering a robust interface for creating, updating, and managing service connections. This abstraction layer simplifies the complex task of configuring cloud connectivity, allowing for more streamlined and error-resistant network management.

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

## Exceptions

The Service Connection models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
  - When required fields are missing (name, region, ipsec_tunnel)
  - When name doesn't match the required pattern
  - When invalid subnet formats are provided
  - When invalid values are provided for enums (onboarding_type, no_export_community)
  - When BGP configuration is incomplete or inconsistent
  - When both IPv4 and IPv6 addresses are used inconsistently

## Model Validators

### Name Validation

The name field must match the required pattern:

```python
from scm.models.deployment import ServiceConnectionCreateModel

# This will raise a validation error
try:
    service_connection = ServiceConnectionCreateModel(
        name="invalid@name!",  # Contains invalid characters
        ipsec_tunnel="tunnel1",
        region="us-east-1"
    )
except ValueError as e:
    print(e)  # "String should match pattern '^[0-9a-zA-Z._\\- ]+$'"
```

### Required Fields Validation

Essential fields must be provided:

```python
from scm.models.deployment import ServiceConnectionCreateModel

# This will raise a validation error
try:
    service_connection = ServiceConnectionCreateModel(
        name="valid-name",
        # Missing required field: ipsec_tunnel
        region="us-east-1"
    )
except ValueError as e:
    print(e)  # "Field required"
```

### Subnet Format Validation

Subnets must be in valid CIDR notation:

```python
from scm.models.deployment import ServiceConnectionCreateModel

# This will raise a validation error
try:
    service_connection = ServiceConnectionCreateModel(
        name="valid-name",
        ipsec_tunnel="tunnel1",
        region="us-east-1",
        subnets=["invalid-subnet"]  # Not in CIDR format
    )
except ValueError as e:
    print(e)  # "Invalid subnet format: 'invalid-subnet'"
```

## Usage Examples

### Creating a Basic Service Connection

```python
from scm.client import ScmClient
from scm.models.deployment import ServiceConnectionCreateModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
basic_dict = {
    "name": "aws-service-connection",
    "ipsec_tunnel": "aws-ipsec-tunnel",
    "region": "us-east-1",
    "onboarding_type": "classic",
    "subnets": ["10.0.0.0/24", "192.168.1.0/24"]
}

# Create the service connection using the client
response = client.service_connection.create(basic_dict)
print(f"Created service connection: {response.name}")

# Using model directly
basic_connection = ServiceConnectionCreateModel(
    name="aws-service-connection-2",
    ipsec_tunnel="aws-ipsec-tunnel-2",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24", "192.168.1.0/24"]
)

payload = basic_connection.model_dump(exclude_unset=True)
response = client.service_connection.create(payload)
print(f"Created service connection with ID: {response.id}")
```

### Creating a Service Connection with BGP Configuration

```python
from scm.models.deployment import (
    ServiceConnectionCreateModel,
    BgpPeerModel,
    ProtocolModel,
    BgpProtocolModel
)

# Create BGP peer configuration
bgp_peer = BgpPeerModel(
    local_ip_address="192.168.1.1",
    peer_ip_address="192.168.1.2",
    secret="mysecretkey"  # Authentication key
)

# Create BGP protocol configuration
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
bgp_connection = ServiceConnectionCreateModel(
    name="aws-service-connection-bgp",
    ipsec_tunnel="aws-ipsec-tunnel-bgp",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24"],
    bgp_peer=bgp_peer,
    protocol=protocol,
    source_nat=True
)

payload = bgp_connection.model_dump(exclude_unset=True)
response = client.service_connection.create(payload)
print(f"Created BGP-enabled service connection: {response.name}")
```

### Creating a Service Connection with QoS Configuration

```python
from scm.models.deployment import (
    ServiceConnectionCreateModel,
    QosModel
)

# Create QoS configuration
qos = QosModel(
    enable=True,
    qos_profile="high-priority"
)

# Create the service connection model
qos_connection = ServiceConnectionCreateModel(
    name="aws-service-connection-qos",
    ipsec_tunnel="aws-ipsec-tunnel-qos",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24"],
    qos=qos,
    source_nat=True
)

payload = qos_connection.model_dump(exclude_unset=True)
response = client.service_connection.create(payload)
print(f"Created QoS-enabled service connection: {response.name}")
```

### Creating a Service Connection with No Export Community

```python
from scm.models.deployment import (
    ServiceConnectionCreateModel,
    NoExportCommunity
)

# Create the service connection model with no export community
community_connection = ServiceConnectionCreateModel(
    name="aws-service-connection-community",
    ipsec_tunnel="aws-ipsec-tunnel-community",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24"],
    no_export_community=NoExportCommunity.ENABLED_BOTH  # Enable in both directions
)

payload = community_connection.model_dump(exclude_unset=True)
response = client.service_connection.create(payload)
print(f"Created service connection with no export community: {response.name}")
```

### Updating a Service Connection

```python
from scm.models.deployment import ServiceConnectionUpdateModel
from uuid import UUID

# Create update model
update_connection = ServiceConnectionUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="aws-service-connection-updated",
    ipsec_tunnel="aws-ipsec-tunnel",
    region="us-east-1",
    onboarding_type="classic",
    subnets=["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/24"],  # Added subnet
    source_nat=True  # Enable source NAT
)

# Perform update
payload = update_connection.model_dump(exclude_unset=True)
response = client.service_connection.update(payload)
print(f"Updated service connection subnets: {response.subnets}")
```

### Retrieving and Listing Service Connections

```python
# Get service connection by ID
connection_id = "123e4567-e89b-12d3-a456-426655440000"
connection = client.service_connection.get(connection_id)
print(f"Retrieved service connection: {connection.name}")

# List all service connections
all_connections = client.service_connection.list()
print(f"Found {len(all_connections)} service connections")

# Filter service connections by region
region_connections = client.service_connection.list(region="us-east-1")
print(f"Found {len(region_connections)} connections in us-east-1 region")

# Process connection information
for conn in all_connections:
    print(f"Connection: {conn.name}")
    print(f"Region: {conn.region}")
    print(f"Subnets: {conn.subnets}")
    if conn.bgp_peer:
        print(f"BGP Peer: {conn.bgp_peer.peer_ip_address}")
    if conn.qos and conn.qos.enable:
        print(f"QoS Profile: {conn.qos.qos_profile}")
```
