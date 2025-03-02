# Deployment Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Remote Networks](#remote-networks)
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
from scm.models.deployment import RemoteNetworkCreateModel, RemoteNetworkUpdateModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

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

# Update an existing remote network using a model
update_network = RemoteNetworkUpdateModel(
   id=result.id,
   name="branch-office-nyc-updated",
   description="Updated NYC branch office",
   subnets=["10.1.0.0/16", "10.2.0.0/16"],
   folder="Remote Networks"
)

update_dict = update_network.model_dump(exclude_unset=True)
updated_result = client.remote_networks.update(update_dict)
```

</div>

## Models by Category

### Remote Networks

- [Remote Networks Models](remote_networks_models.md) - Remote network connection configurations

## Best Practices

1. **Model Validation**
   - Always validate deployment configuration data with models before sending to the API
   - Handle validation errors appropriately for deployment configurations
   - Use model_dump(exclude_unset=True) to avoid sending default values in deployment configurations

2. **Remote Network Configuration**
   - Ensure region and availability zone settings are properly specified
   - Validate that authentication settings are correctly configured
   - Test deployment configurations in a non-production environment first
   - Document remote network configurations and their intended purpose

3. **Network Subnet Handling**
   - Validate IP subnets before creating remote networks
   - Use CIDR notation consistently for network definitions
   - Be aware of overlapping subnet definitions
   - Ensure proper route configuration between networks

4. **Security Considerations**
   - Securely manage pre-shared keys and other authentication credentials
   - Use certificate-based authentication when possible
   - Implement proper access controls for deployment configurations
   - Regularly review and audit deployment settings

## Related Documentation

- [Deployment Configuration](../../config/deployment/index.md) - Working with deployment configurations
- [Remote Networks Configuration](../../config/deployment/remote_networks.md) - Remote network operations