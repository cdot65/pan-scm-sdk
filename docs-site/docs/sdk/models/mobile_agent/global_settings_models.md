# GlobalProtect Global Settings Models

## Overview

The GlobalProtect Global Settings models provide a structured way to manage the tenant-wide GlobalProtect configuration in Palo Alto Networks' Strata Cloud Manager: the agent version and manual gateway regions. Global settings are a singleton object with only GET and PUT operations. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `GlobalSettingsBaseModel`: Base model with the global settings fields
- `GlobalSettingsUpdateModel`: Model for updating the global settings singleton
- `GlobalSettingsResponseModel`: Response model for global settings operations
- `ManualGateway`: Manual gateway configuration containing the region list
- `ManualGatewayRegion`: A region entry with its locations

Request models use `extra="forbid"`; the response model uses `extra="ignore"`.

:::note
Global settings are a singleton: there is no create model, no `id` field, and no
container (folder/snippet/device) fields.
:::

## Attributes

| Attribute        | Type            | Required | Default | Description                                                          |
|------------------|-----------------|----------|---------|----------------------------------------------------------------------|
| `agent_version`  | `str`           | No       | None    | The GlobalProtect agent version                                      |
| `manual_gateway` | `ManualGateway` | No       | None    | Manual gateway regions (use locations from infrastructure settings)  |

### ManualGatewayRegion Attributes

| Attribute   | Type        | Required | Description                       |
|-------------|-------------|----------|-----------------------------------|
| `name`      | `str`       | No       | The name of the region            |
| `locations` | `List[str]` | No       | The locations within the region   |

## Exceptions

The Global Settings models can raise the following exceptions during validation:

- **ValueError / ValidationError**: Raised when unknown fields are passed to request
  models (`extra="forbid"`), or when field types do not match.

## Usage Examples

### Updating Global Settings

```python
from scm.models.mobile_agent import GlobalSettingsUpdateModel

settings = GlobalSettingsUpdateModel(
    agent_version="6.2.1",
    manual_gateway={
        "region": [
            {
                "name": "americas",
                "locations": ["us-east-1", "us-west-201"],
            }
        ]
    },
)

payload = settings.model_dump(exclude_unset=True)
```

### Partial Updates

All fields are optional, so a partial PUT payload is valid:

```python
settings = GlobalSettingsUpdateModel(agent_version="6.3.0")
payload = settings.model_dump(exclude_unset=True)
# {'agent_version': '6.3.0'}
```

## Related Documentation

- [Global Settings Configuration](../../config/mobile_agent/global_settings.md)
- [Mobile Agent Models Overview](index.md)
