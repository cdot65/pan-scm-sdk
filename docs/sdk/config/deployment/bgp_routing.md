# BGP Routing Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [BGP Routing Model Attributes](#bgp-routing-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Retrieving BGP Routing Settings](#retrieving-bgp-routing-settings)
    - [Creating BGP Routing Configurations](#creating-bgp-routing-configurations)
    - [Updating BGP Routing Configurations](#updating-bgp-routing-configurations)
    - [Resetting BGP Routing Configurations](#resetting-bgp-routing-configurations)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `BGPRouting` class provides functionality to manage BGP (Border Gateway Protocol) routing settings in Palo Alto Networks' Strata Cloud Manager. BGP routing is a singleton configuration object that controls global routing preferences and behaviors for Service Connections. This class inherits from `BaseObject` and provides methods for retrieving, creating, updating, and resetting the BGP routing configuration.

## Core Methods

| Method     | Description                                  | Parameters             | Return Type               |
|------------|----------------------------------------------|------------------------|---------------------------|
| `get()`    | Retrieves current BGP routing settings       | None                   | `BGPRoutingResponseModel` |
| `create()` | Creates a new BGP routing configuration      | `data: Dict[str, Any]` | `BGPRoutingResponseModel` |
| `update()` | Updates existing BGP routing configuration   | `data: Dict[str, Any]` | `BGPRoutingResponseModel` |
| `delete()` | Resets BGP routing configuration to defaults | None                   | None                      |

## BGP Routing Model Attributes

| Attribute                   | Type                                             | Required | Description                                    |
|----------------------------|--------------------------------------------------|----------|------------------------------------------------|
| `routing_preference`        | Union[DefaultRoutingModel, HotPotatoRoutingModel]| Yes      | The routing preference setting (default or hot potato) |
| `backbone_routing`          | BackboneRoutingEnum                              | Yes      | Controls asymmetric routing options             |
| `accept_route_over_SC`      | bool                                             | Yes      | Whether to accept routes over service connections |
| `outbound_routes_for_services`| List[str]                                      | Yes      | List of outbound routes for services in CIDR format |
| `add_host_route_to_ike_peer`| bool                                             | Yes      | Whether to add host route to IKE peer            |
| `withdraw_static_route`     | bool                                             | Yes      | Whether to withdraw static routes               |

## Exceptions

| Exception                   | HTTP Code | Description                                 |
|----------------------------|-----------|---------------------------------------------|
| `InvalidObjectError`        | 400/500   | Invalid routing configuration or format     |
| `MissingQueryParameterError`| 400       | Empty configuration data provided           |

## Basic Configuration

The BGP Routing service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the BGP Routing service directly through the client
# No need to create a separate BGPRouting instance
bgp_routing = client.bgp_routing
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.deployment import BGPRouting

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize BGPRouting object explicitly
bgp_routing = BGPRouting(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Retrieving BGP Routing Settings

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Get current BGP routing settings
current_settings = client.bgp_routing.get()

# Output current settings
print(f"Backbone routing: {current_settings.backbone_routing}")
print(f"Accept route over SC: {current_settings.accept_route_over_SC}")

# Check routing preference type
if hasattr(current_settings.routing_preference, "default"):
    print("Routing preference: Default")
elif hasattr(current_settings.routing_preference, "hot_potato_routing"):
    print("Routing preference: Hot Potato")

# List outbound routes for services
if current_settings.outbound_routes_for_services:
    print(f"Outbound routes: {', '.join(current_settings.outbound_routes_for_services)}")
else:
    print("No outbound routes configured")
    
print(f"Add host route to IKE peer: {current_settings.add_host_route_to_ike_peer}")
print(f"Withdraw static route: {current_settings.withdraw_static_route}")
```

### Creating BGP Routing Configurations

```python
from scm.client import ScmClient
from scm.models.deployment import BackboneRoutingEnum

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Dictionary approach
bgp_config = {
    "routing_preference": {"hot_potato_routing": {}},  # Use hot potato routing
    "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12"],
    "add_host_route_to_ike_peer": True,
    "withdraw_static_route": False
}

# Create BGP routing configuration
# Note: Since BGP routing is a singleton, this will replace any existing configuration
new_settings = client.bgp_routing.create(bgp_config)
print(f"Created BGP routing settings with backbone routing: {new_settings.backbone_routing}")
```

### Updating BGP Routing Configurations

```python
from scm.client import ScmClient
from scm.models.deployment import (
    BackboneRoutingEnum,
    DefaultRoutingModel,
    HotPotatoRoutingModel
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Method 1: Update using dictionary with direct values
update_config = {
    "routing_preference": {"default": {}},  # Switch to default routing
    "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    "accept_route_over_SC": False,
    "outbound_routes_for_services": ["192.168.0.0/16"],
    "add_host_route_to_ike_peer": False,
    "withdraw_static_route": True
}

updated_settings = client.bgp_routing.update(update_config)
print(f"Updated BGP routing settings successfully")

# Method 2: Update using Pydantic model instances
from scm.models.deployment import BGPRoutingUpdateModel

# Create the update model
update_model = BGPRoutingUpdateModel(
    routing_preference=HotPotatoRoutingModel(),  # Switch back to hot potato routing
    backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
    accept_route_over_SC=True
)

# Convert model to dictionary and update
model_dict = update_model.model_dump(exclude_unset=True)
updated_settings = client.bgp_routing.update(model_dict)
print(f"Updated BGP routing with backbone routing: {updated_settings.backbone_routing}")
```

### Resetting BGP Routing Configurations

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Reset BGP routing configuration to default values
client.bgp_routing.delete()
print("BGP routing settings reset to defaults")

# Verify reset by getting current settings
reset_settings = client.bgp_routing.get()
print(f"Verified settings after reset:")
print(f"Backbone routing: {reset_settings.backbone_routing}")
print(f"Routing preference: Default")
print(f"Accept route over SC: {reset_settings.accept_route_over_SC}")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
   "folders": ["All"],
   "description": "Updated BGP routing configuration",
   "sync": True,
   "timeout": 300  # 5 minute timeout
}

# Commit the changes
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
   MissingQueryParameterError
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Create BGP routing configuration
   routing_config = {
      "routing_preference": {"default": {}},
      "backbone_routing": "invalid-value",  # This will cause a validation error
      "accept_route_over_SC": False,
      "outbound_routes_for_services": ["192.168.0.0/16"],
      "add_host_route_to_ike_peer": False,
      "withdraw_static_route": True
   }

   # Try to create the BGP routing configuration
   new_routing = client.bgp_routing.create(routing_config)

except InvalidObjectError as e:
   print(f"Invalid BGP routing configuration: {e.message}")
   print(f"Error details: {e.details}")
except MissingQueryParameterError as e:
   print(f"Missing required parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.bgp_routing`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)

2. **Routing Preference Configuration**
    - Use either Default or Hot Potato routing, never both
    - Use the appropriate model (DefaultRoutingModel or HotPotatoRoutingModel) 
    - When providing a dictionary, use the correct format ({"default": {}} or {"hot_potato_routing": {}})

3. **Backbone Routing Configuration**
    - Use the BackboneRoutingEnum for backbone_routing values
    - Consider asymmetric routing implications for your network
    - Match backbone routing settings with your network topology

4. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Check job status after commits
    - Handle validation errors before sending data to the API

5. **Outbound Routes Configuration**
    - Use valid CIDR notation for all outbound routes
    - Verify that routes do not overlap unintentionally
    - Keep outbound routes list manageable in size

6. **Change Management**
    - Document BGP routing changes in commit messages
    - Test routing changes in a non-production environment first
    - Plan for routing convergence time when making changes
    - Consider impact on existing connections when modifying routing

## Full Script Examples

Refer to the [bgp_routing_example.py](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/bgp_routing_example.py).

## Related Models

- [BGPRoutingCreateModel](../../models/deployment/bgp_routing_models.md#Overview)
- [BGPRoutingUpdateModel](../../models/deployment/bgp_routing_models.md#Overview)
- [BGPRoutingResponseModel](../../models/deployment/bgp_routing_models.md#Overview)
- [BackboneRoutingEnum](../../models/deployment/bgp_routing_models.md#Overview)