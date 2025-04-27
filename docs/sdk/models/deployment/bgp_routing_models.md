# BGP Routing Models

## Overview {#Overview}

The BGP Routing models provide a structured way to manage BGP (Border Gateway Protocol) routing configurations in Palo Alto Networks' Strata Cloud Manager. These models define the structure, validation rules, and behavior for BGP routing settings, which control global routing preferences and behaviors for Service Connections.

BGP routing in Strata Cloud Manager is implemented as a singleton object, meaning there is only one global BGP routing configuration per tenant. The models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute                   | Type                                             | Required     | Default         | Description                                             |
|----------------------------|--------------------------------------------------|--------------|----------------|---------------------------------------------------------|
| `routing_preference`        | Union[DefaultRoutingModel, HotPotatoRoutingModel]| Yes*         | None           | The routing preference setting (default or hot potato)   |
| `backbone_routing`          | BackboneRoutingEnum                              | Yes*         | None           | Controls asymmetric routing options                      |
| `accept_route_over_SC`      | bool                                             | Yes*         | False          | Whether to accept routes over service connections        |
| `outbound_routes_for_services`| List[str]                                      | Yes*         | []             | List of outbound routes for services in CIDR format      |
| `add_host_route_to_ike_peer`| bool                                             | Yes*         | False          | Whether to add host route to IKE peer                    |
| `withdraw_static_route`     | bool                                             | Yes*         | False          | Whether to withdraw static routes                        |

\* Required for CreateModel, optional for UpdateModel, required for ResponseModel

## Enums and Sub-Models

### BackboneRoutingEnum

The `BackboneRoutingEnum` defines the possible backbone routing options:

| Value                            | Description                                      |
|---------------------------------|--------------------------------------------------|
| `NO_ASYMMETRIC_ROUTING`         | No asymmetric routing allowed                    |
| `ASYMMETRIC_ROUTING_ONLY`       | Only asymmetric routing allowed                  |
| `ASYMMETRIC_ROUTING_WITH_LOAD_SHARE` | Asymmetric routing with load sharing enabled |

### DefaultRoutingModel

Model for default routing preference configuration:

```python
class DefaultRoutingModel(BaseModel):
    default: Dict[str, Any] = Field(
        default_factory=dict,
        description="Default routing configuration",
    )
```

### HotPotatoRoutingModel

Model for hot potato routing preference configuration:

```python
class HotPotatoRoutingModel(BaseModel):
    hot_potato_routing: Dict[str, Any] = Field(
        default_factory=dict,
        description="Hot potato routing configuration",
    )
```

## Exceptions

The BGP Routing models can raise the following exceptions during validation:

- **ValueError**: Raised in several scenarios:
  - When routing_preference is not a valid type
  - When no fields are specified for an update
  - When outbound_routes_for_services contains invalid entries
  - When backbone_routing is not a valid enum value

## Model Validators

### Routing Preference Type Validation

The models enforce that routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel:

```python
# This will raise a validation error
from scm.models.deployment import BGPRoutingCreateModel

# Error: invalid routing_preference type
try:
    routing_config = BGPRoutingCreateModel(
        routing_preference="invalid-type",  # Not a valid routing preference type
        backbone_routing="no-asymmetric-routing",
        accept_route_over_SC=False
    )
except ValueError as e:
    print(e)  # "routing_preference must be either DefaultRoutingModel or HotPotatoRoutingModel"
```

### Update Model Validation

For update operations, at least one field must be specified:

```python
# This will raise a validation error
from scm.models.deployment import BGPRoutingUpdateModel

# Error: no fields specified for update
try:
    update_config = BGPRoutingUpdateModel()
except ValueError as e:
    print(e)  # "At least one field must be specified for update"
```

### Outbound Routes Validation

The outbound_routes_for_services field is validated to ensure proper formatting:

```python
# This will handle various input formats
from scm.models.deployment import BGPRoutingCreateModel
from scm.models.deployment import BackboneRoutingEnum

# Convert single string to list
config1 = BGPRoutingCreateModel(
    routing_preference={"default": {}},
    backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    outbound_routes_for_services="192.168.0.0/24"  # Will be converted to ["192.168.0.0/24"]
)
print(config1.outbound_routes_for_services)  # ["192.168.0.0/24"]

# Handle empty list
config2 = BGPRoutingCreateModel(
    routing_preference={"default": {}},
    backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    outbound_routes_for_services=[]  # Empty list is allowed
)
print(config2.outbound_routes_for_services)  # []

# Error: invalid type
try:
    config3 = BGPRoutingCreateModel(
        routing_preference={"default": {}},
        backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
        outbound_routes_for_services=123  # Not a list or string
    )
except ValueError as e:
    print(e)  # "outbound_routes_for_services must be a list of strings"
```

## Usage Examples

### Creating BGP Routing Configuration

```python
# Using dictionary approach
from scm.client import ScmClient
from scm.models.deployment import BackboneRoutingEnum

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create with direct dictionary (automatically converted to models)
bgp_config = {
    "routing_preference": {"default": {}},
    "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    "accept_route_over_SC": False,
    "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12"],
    "add_host_route_to_ike_peer": False,
    "withdraw_static_route": False
}

result = client.bgp_routing.create(bgp_config)

# Using Pydantic models directly
from scm.models.deployment import (
    BGPRoutingCreateModel,
    DefaultRoutingModel,
    HotPotatoRoutingModel
)

# Create with Pydantic model (explicit instantiation)
bgp_model = BGPRoutingCreateModel(
    routing_preference=DefaultRoutingModel(),
    backbone_routing=BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    accept_route_over_SC=False,
    outbound_routes_for_services=["10.0.0.0/8"],
    add_host_route_to_ike_peer=False,
    withdraw_static_route=False
)

# Convert to dictionary for API call
model_dict = bgp_model.model_dump(exclude_unset=True)
result = client.bgp_routing.create(model_dict)
```

### Creating with Hot Potato Routing

```python
# Using Hot Potato routing preference
from scm.models.deployment import (
    BGPRoutingCreateModel,
    HotPotatoRoutingModel,
    BackboneRoutingEnum
)

# Create with Hot Potato routing
hot_potato_model = BGPRoutingCreateModel(
    routing_preference=HotPotatoRoutingModel(),
    backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
    accept_route_over_SC=True,
    outbound_routes_for_services=["192.168.0.0/16", "10.0.0.0/8"],
    add_host_route_to_ike_peer=True,
    withdraw_static_route=False
)

payload = hot_potato_model.model_dump(exclude_unset=True)
result = client.bgp_routing.create(payload)
```

### Updating BGP Routing Configuration

```python
# Partial updates with only specified fields
from scm.models.deployment import BGPRoutingUpdateModel, BackboneRoutingEnum

# Update only specific fields
update_model = BGPRoutingUpdateModel(
    backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
    accept_route_over_SC=True
)

# Convert to dictionary, excluding unset fields
payload = update_model.model_dump(exclude_unset=True)
result = client.bgp_routing.update(payload)

# Dictionary approach for partial update
partial_update = {
    "outbound_routes_for_services": ["172.16.0.0/12", "192.168.0.0/16"],
    "add_host_route_to_ike_peer": True
}

result = client.bgp_routing.update(partial_update)
```

### Handling Response Models

```python
# Working with response models
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get current BGP routing configuration
response = client.bgp_routing.get()

# Determine routing preference type
if hasattr(response.routing_preference, "default"):
    print("Using Default routing")
elif hasattr(response.routing_preference, "hot_potato_routing"):
    print("Using Hot Potato routing")

# Check backbone routing configuration
if response.backbone_routing == "no-asymmetric-routing":
    print("No asymmetric routing allowed")
elif response.backbone_routing == "asymmetric-routing-only":
    print("Only asymmetric routing allowed")
elif response.backbone_routing == "asymmetric-routing-with-load-share":
    print("Asymmetric routing with load sharing enabled")

# Check if accepting routes over Service Connections
if response.accept_route_over_SC:
    print("Accepting routes over Service Connections")
else:
    print("Not accepting routes over Service Connections")

# Display outbound routes
if response.outbound_routes_for_services:
    print("Outbound routes:")
    for route in response.outbound_routes_for_services:
        print(f"  - {route}")
else:
    print("No outbound routes configured")

# Check other settings
print(f"Add host route to IKE peer: {response.add_host_route_to_ike_peer}")
print(f"Withdraw static route: {response.withdraw_static_route}")
```

## Field Serialization

The BGP Routing models include a custom serializer for the `routing_preference` field to ensure it's properly serialized for API requests:

```python
@field_serializer('routing_preference')
def serialize_routing_preference(self, value: Optional[Union[DefaultRoutingModel, HotPotatoRoutingModel]]) -> Optional[Dict[str, Any]]:
    """Serialize routing_preference to correct format for API requests."""
    if value is None:
        return None

    if isinstance(value, DefaultRoutingModel):
        return {"default": {}}
    elif isinstance(value, HotPotatoRoutingModel):
        return {"hot_potato_routing": {}}

    return None
```

This serializer ensures that the models are correctly converted to the format expected by the API, regardless of how they were created or modified in your code.
