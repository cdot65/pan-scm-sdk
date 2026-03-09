# BGP Routing Configuration Object

Manages BGP routing singleton configuration for controlling global routing preferences in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `BGPRouting` class inherits from `BaseObject` and provides methods for retrieving, creating, updating, and resetting the BGP routing configuration. BGP routing is a singleton configuration object that controls global routing preferences and behaviors for Service Connections.

### Methods

| Method     | Description                                  | Parameters             | Return Type               |
|------------|----------------------------------------------|------------------------|---------------------------|
| `get()`    | Retrieves current BGP routing settings       | None                   | `BGPRoutingResponseModel` |
| `create()` | Creates a new BGP routing configuration      | `data: Dict[str, Any]` | `BGPRoutingResponseModel` |
| `update()` | Updates existing BGP routing configuration   | `data: Dict[str, Any]` | `BGPRoutingResponseModel` |
| `delete()` | Resets BGP routing configuration to defaults | None                   | None                      |

### Model Attributes

| Attribute                      | Type                                              | Required | Default | Description                                       |
|--------------------------------|---------------------------------------------------|----------|---------|---------------------------------------------------|
| `routing_preference`           | Union[DefaultRoutingModel, HotPotatoRoutingModel] | No       | None    | Routing preference (default or hot potato)        |
| `backbone_routing`             | BackboneRoutingEnum                               | No       | None    | Controls asymmetric routing options               |
| `accept_route_over_SC`         | bool                                              | No       | None    | Whether to accept routes over service connections |
| `outbound_routes_for_services` | List[str]                                         | No       | []      | Outbound routes for services in CIDR format       |
| `add_host_route_to_ike_peer`   | bool                                              | No       | None    | Whether to add host route to IKE peer             |
| `withdraw_static_route`        | bool                                              | No       | None    | Whether to withdraw static routes                 |

!!! note
    All fields are optional. For update operations, at least one field must be specified.

### Exceptions

| Exception                    | HTTP Code | Description                             |
|------------------------------|-----------|-----------------------------------------|
| `InvalidObjectError`         | 400/500   | Invalid routing configuration or format |
| `MissingQueryParameterError` | 400       | Empty configuration data provided       |

### Basic Configuration

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

bgp_routing = client.bgp_routing
```

## Methods

### Get BGP Routing Settings

```python
current_settings = client.bgp_routing.get()

print(f"Backbone routing: {current_settings.backbone_routing}")
print(f"Accept route over SC: {current_settings.accept_route_over_SC}")

if hasattr(current_settings.routing_preference, "default"):
    print("Routing preference: Default")
elif hasattr(current_settings.routing_preference, "hot_potato_routing"):
    print("Routing preference: Hot Potato")

if current_settings.outbound_routes_for_services:
    print(f"Outbound routes: {', '.join(current_settings.outbound_routes_for_services)}")
```

### Create a BGP Routing Configuration

```python
from scm.models.deployment import BackboneRoutingEnum

# Since BGP routing is a singleton, this replaces any existing configuration
bgp_config = {
    "routing_preference": {"hot_potato_routing": {}},
    "backbone_routing": BackboneRoutingEnum.ASYMMETRIC_ROUTING_WITH_LOAD_SHARE,
    "accept_route_over_SC": True,
    "outbound_routes_for_services": ["10.0.0.0/8", "172.16.0.0/12"],
    "add_host_route_to_ike_peer": True,
    "withdraw_static_route": False
}
new_settings = client.bgp_routing.create(bgp_config)
```

### Update a BGP Routing Configuration

```python
from scm.models.deployment import BackboneRoutingEnum

# Update using dictionary
update_config = {
    "routing_preference": {"default": {}},
    "backbone_routing": BackboneRoutingEnum.NO_ASYMMETRIC_ROUTING,
    "accept_route_over_SC": False,
    "outbound_routes_for_services": ["192.168.0.0/16"],
    "add_host_route_to_ike_peer": False,
    "withdraw_static_route": True
}
updated_settings = client.bgp_routing.update(update_config)

# Update using Pydantic model
from scm.models.deployment import BGPRoutingUpdateModel, HotPotatoRoutingModel

update_model = BGPRoutingUpdateModel(
    routing_preference=HotPotatoRoutingModel(),
    backbone_routing=BackboneRoutingEnum.ASYMMETRIC_ROUTING_ONLY,
    accept_route_over_SC=True
)
model_dict = update_model.model_dump(exclude_unset=True)
updated_settings = client.bgp_routing.update(model_dict)
```

### Delete (Reset) BGP Routing Configuration

```python
# Reset BGP routing configuration to default values
client.bgp_routing.delete()

# Verify reset
reset_settings = client.bgp_routing.get()
print(f"Backbone routing: {reset_settings.backbone_routing}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["All"],
    description="Updated BGP routing configuration",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError
)

try:
    routing_config = {
        "routing_preference": {"default": {}},
        "backbone_routing": "invalid-value",
        "accept_route_over_SC": False
    }
    new_routing = client.bgp_routing.create(routing_config)

except InvalidObjectError as e:
    print(f"Invalid BGP routing configuration: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

## Related Topics

- [BGP Routing Models](../../models/deployment/bgp_routing_models.md#Overview)
- [Deployment Overview](index.md)
- [API Client](../../client.md)
