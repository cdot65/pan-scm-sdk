# GlobalProtect Global Settings Configuration Object

Manages the GlobalProtect global settings singleton (agent version and manual gateways) in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `GlobalSettings` class inherits from `BaseObject` and provides access to the GlobalProtect global settings.

:::note
Global settings are a **singleton** configuration object with only GET and PUT
operations. There is no create, delete, or list-of-many, and no query parameters -
the configuration always exists for the tenant.
:::

### Methods

| Method     | Description                       | Parameters             | Return Type                  |
|------------|-----------------------------------|------------------------|------------------------------|
| `get()`    | Retrieves the global settings     | None                   | `GlobalSettingsResponseModel`|
| `update()` | Updates the global settings       | `data: Dict[str, Any]` | `GlobalSettingsResponseModel`|

:::note
The API returns `200 OK` with an empty body for `update()`; in that case the
validated request payload is returned as the response model.
:::

### Model Attributes

| Attribute        | Type          | Required | Default | Description                                                  |
|------------------|---------------|----------|---------|--------------------------------------------------------------|
| `agent_version`  | str           | No       | None    | The GlobalProtect agent version                              |
| `manual_gateway` | ManualGateway | No       | None    | Manual gateway regions (use locations from infrastructure settings) |

### Exceptions

| Exception                    | HTTP Code | Description                          |
|------------------------------|-----------|--------------------------------------|
| `InvalidObjectError`         | 400       | Invalid settings data or format      |
| `MissingQueryParameterError` | 400       | Empty configuration data on update   |
| `AuthenticationError`        | 401       | Authentication failed                |
| `ServerError`                | 500       | Internal server error                |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

global_settings = client.global_settings
```

## Methods

### Get Global Settings

```python
settings = client.global_settings.get()

print(f"Agent version: {settings.agent_version}")
if settings.manual_gateway and settings.manual_gateway.region:
    for region in settings.manual_gateway.region:
        print(f"Region: {region.name}, Locations: {region.locations}")
```

### Update Global Settings

```python
settings_config = {
    "agent_version": "6.2.1",
    "manual_gateway": {
        "region": [
            {
                "name": "americas",
                "locations": ["us-east-1", "us-west-201"],
            }
        ]
    },
}

updated = client.global_settings.update(settings_config)
print(f"Updated agent version: {updated.agent_version}")
```

## Related Documentation

- [Global Settings Models](../../models/mobile_agent/global_settings_models.md)
- [Mobile Agent Overview](index.md)
