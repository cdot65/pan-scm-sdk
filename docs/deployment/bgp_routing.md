# BGP Routing

The BGP Routing module provides methods to manage BGP routing settings for Service Connections in Palo Alto Networks' Strata Cloud Manager.

## Overview

The BGP Routing module allows you to:

- Retrieve the current BGP routing settings
- Create/update BGP routing settings for your Service Connections
- Reset BGP routing settings to default values

## Usage

First, import the necessary modules and initialize the client:

```python
from scm.api import SCMClient
from scm.auth import SCMAuth
from scm.config.deployment import BGPRouting
from scm.models.deployment import (
    BGPRoutingCreateModel,
    DefaultRoutingPreferenceModel,
    HotPotatoRoutingPreferenceModel,
    BackboneRoutingEnum,
)

# Initialize authentication
auth = SCMAuth(
    client_id="your-client-id",
    client_secret="your-client-secret",
    scope="tsg_id:your-tsg-id",
)

# Initialize API client
client = SCMClient(auth=auth)

# Initialize BGP routing service
bgp_routing = BGPRouting(client)
```

### Get BGP Routing Settings

Retrieve the current BGP routing settings:

```python
current_settings = bgp_routing.get()
print(f"Backbone routing: {current_settings.backbone_routing}")
print(f"Accept route over Service Connection: {current_settings.accept_route_over_SC}")
print(f"Outbound routes for services: {current_settings.outbound_routes_for_services}")
```

### Create BGP Routing Settings

Create BGP routing settings (also works for updating existing settings):

```python
# Using dictionary approach
create_data = {
    "routing_preference": {"default": {}},
    "backbone_routing": "no-asymmetric-routing",
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8", "192.168.0.0/16"],
    "add_host_route_to_ike_peer": False,
    "withdraw_static_route": True
}

created_settings = bgp_routing.create(create_data)
```

Or using Pydantic models:

```python
# Using Pydantic model approach
routing_model = BGPRoutingCreateModel(
    routing_preference=DefaultRoutingPreferenceModel(),
    backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    accept_route_over_SC=True,
    outbound_routes_for_services=["10.0.0.0/8", "192.168.0.0/16"],
    add_host_route_to_ike_peer=False,
    withdraw_static_route=True
)

# Convert model to dict for create method
model_dict = routing_model.model_dump()
created_settings = bgp_routing.create(model_dict)
```

### Update BGP Routing Settings

Update the BGP routing settings:

```python
# Example update payload
update_data = {
    "routing_preference": {"hot_potato_routing": {}},  # Switch to hot potato routing
    "backbone_routing": "asymmetric-routing-with-load-share",
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
    "add_host_route_to_ike_peer": True,
    "withdraw_static_route": False
}

updated_settings = bgp_routing.update(update_data)
```

### Reset to Default Settings

Reset BGP routing settings to default values:

```python
# Reset to defaults
bgp_routing.delete()

# Verify reset
reset_settings = bgp_routing.get()
print(f"Backbone routing after reset: {reset_settings.backbone_routing}")
```

## API Reference

### BGPRouting Class

#### `__init__(self, api_client)`

Initialize a new BGPRouting instance.

**Parameters:**
- `api_client`: The API client instance

#### `get(self) -> BGPRoutingResponseModel`

Get the current BGP routing settings.

**Returns:**
- `BGPRoutingResponseModel`: The current BGP routing configuration

#### `create(self, data: Dict[str, Any]) -> BGPRoutingResponseModel`

Create a new BGP routing configuration. Since BGP routing is a singleton object, this method is functionally equivalent to update() and will replace any existing configuration.

**Parameters:**
- `data`: Dictionary containing the BGP routing configuration

**Returns:**
- `BGPRoutingResponseModel`: The created BGP routing configuration

#### `update(self, data: Dict[str, Any]) -> BGPRoutingResponseModel`

Update the BGP routing settings.

**Parameters:**
- `data`: Dictionary containing the BGP routing configuration

**Returns:**
- `BGPRoutingResponseModel`: The updated BGP routing configuration

#### `delete(self) -> None`

Reset the BGP routing configuration to default values. Since BGP routing is a singleton configuration object, it cannot be truly deleted. This method resets the configuration to default values instead.

### Models

#### BGPRoutingBaseModel

Base model for BGP routing settings containing fields common to all operations.

**Fields:**
- `routing_preference`: Union[DefaultRoutingPreferenceModel, HotPotatoRoutingPreferenceModel]
- `backbone_routing`: BackboneRoutingEnum
- `accept_route_over_SC`: bool
- `outbound_routes_for_services`: List[str]
- `add_host_route_to_ike_peer`: bool
- `withdraw_static_route`: bool

#### BGPRoutingCreateModel

Model for creating BGP routing settings. Used for POST/PUT operations to the BGP routing endpoint.

**Fields:**
Same as BGPRoutingBaseModel.

#### BGPRoutingUpdateModel

Model for updating BGP routing settings. Used for PUT operations to the BGP routing endpoint.

**Fields:**
Same as BGPRoutingBaseModel.

#### BGPRoutingResponseModel

Model for BGP routing API responses. Used to parse GET responses from the BGP routing endpoint.

**Fields:**
Same as BGPRoutingBaseModel.

#### BackboneRoutingEnum

Enum for backbone routing configuration:
- `NO_ASYMMETRIC_ROUTING = "no-asymmetric-routing"`
- `ASYMMETRIC_ROUTING_ONLY = "asymmetric-routing-only"`
- `ASYMMETRIC_ROUTING_WITH_LOAD_SHARE = "asymmetric-routing-with-load-share"`

#### DefaultRoutingPreferenceModel

Model for default routing preference configuration.

**Fields:**
- `default`: Dict[str, Any]

#### HotPotatoRoutingPreferenceModel

Model for hot potato routing preference configuration.

**Fields:**
- `hot_potato_routing`: Dict[str, Any]
