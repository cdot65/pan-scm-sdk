# Deployment Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Bandwidth Allocations](#bandwidth-allocations)
   2. [BGP Routing](#bgp-routing)
   3. [Remote Networks](#remote-networks)
   4. [Service Connections](#service-connections)
6. [Best Practices](#best-practices)
7. [Related Documentation](#related-documentation)

## Overview

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization of deployment configurations. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for deployment configuration resources.

## Model Types

For each deployment configuration, there are corresponding model types:

- **Create Models**: Used when creating new deployment resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing deployment resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing deployment data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related deployment models (`{Object}BaseModel`)

## Common Model Patterns

Deployment models share common patterns:

- Container validation (exactly one of folder/snippet/device)
- UUID validation for identifiers
- Region and zone validation
- Protocol configuration validation
- Authentication settings validation
- Network subnet and routing validation

## Usage Examples

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.models.deployment import (
    BandwidthAllocationCreateModel, 
    BGPRoutingCreateModel, 
    RemoteNetworkCreateModel,
    BackboneRoutingEnum
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a new bandwidth allocation using a model
bandwidth_allocation = BandwidthAllocationCreateModel(
   name="test-region",
   allocated_bandwidth=100,
   spn_name_list=["spn1", "spn2"],
   qos={
      "enabled": True,
      "customized": True,
      "profile": "test-profile",
      "guaranteed_ratio": 0.5
   }
)

# Convert the model to a dictionary for the API call
allocation_dict = bandwidth_allocation.model_dump(exclude_unset=True)
result = client.bandwidth_allocation.create(allocation_dict)

# Create BGP routing configuration using a model
bgp_routing = BGPRoutingCreateModel(
   routing_preference={"default": {}},
   backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
   accept_route_over_SC=False,
   outbound_routes_for_services=["10.0.0.0/8"],
   add_host_route_to_ike_peer=False,
   withdraw_static_route=False
)

# Convert the model to a dictionary for the API call
bgp_dict = bgp_routing.model_dump(exclude_unset=True)
result = client.bgp_routing.create(bgp_dict)

# Create a new remote network using a model
remote_network = RemoteNetworkCreateModel(
   name="branch-office-nyc",
   region="us-east-1",
   spn_name="Service",
   folder="Remote Networks",
   protocol={
      "ipsec": {
         "auth_type": "pre-shared-key",
         "pre_shared_key": "your-pre-shared-key"
      }
   },
   subnets=["10.1.0.0/16"]
)

# Convert the model to a dictionary for the API call
network_dict = remote_network.model_dump(exclude_unset=True)
result = client.remote_networks.create(network_dict)
```

</div>

## Models by Category

### Bandwidth Allocations

- [Bandwidth Allocation Models](bandwidth_allocation_models.md) - Bandwidth allocation models for regions and service node groups

### BGP Routing

- [BGP Routing Models](bgp_routing_models.md) - BGP routing configuration models for global routing preferences

### Remote Networks

- [Remote Networks Models](remote_networks_models.md) - Remote network connection configurations

### Service Connections

- [Service Connections Models](service_connections_models.md) - Service connection configurations for cloud service providers

## Best Practices

1. **Model Validation**
   - Always validate deployment configuration data with models before sending to the API
   - Handle validation errors appropriately for deployment configurations
   - Use model_dump(exclude_unset=True) to avoid sending default values in deployment configurations

2. **BGP Routing Configuration**
   - Understand the implications of different backbone routing options before changing them
   - Use the appropriate routing preference model (Default or Hot Potato) for your use case
   - Validate CIDR notation for outbound routes before submitting to the API
   - Test routing changes in a non-production environment before deploying

3. **Remote Network Configuration**
   - Ensure region and availability zone settings are properly specified
   - Validate that authentication settings are correctly configured
   - Test deployment configurations in a non-production environment first
   - Document remote network configurations and their intended purpose

4. **Network Subnet Handling**
   - Validate IP subnets before creating remote networks
   - Use CIDR notation consistently for network definitions
   - Be aware of overlapping subnet definitions
   - Ensure proper route configuration between networks

5. **Security Considerations**
   - Securely manage pre-shared keys and other authentication credentials
   - Use certificate-based authentication when possible
   - Implement proper access controls for deployment configurations
   - Regularly review and audit deployment settings

## Related Documentation

- [Deployment Configuration](../../config/deployment/index.md) - Working with deployment configurations
- [Bandwidth Allocations Configuration](../../config/deployment/bandwidth_allocations.md) - Bandwidth allocation operations
- [BGP Routing Configuration](../../config/deployment/bgp_routing.md) - BGP routing operations
- [Remote Networks Configuration](../../config/deployment/remote_networks.md) - Remote network operations
- [Service Connections Configuration](../../config/deployment/service_connections.md) - Service connection operations