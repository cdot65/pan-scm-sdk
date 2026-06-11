# GlobalProtect Forwarding Profile Source Application Models

## Overview

The Forwarding Profile Source Application models provide a structured way to manage source application lists for GlobalProtect forwarding profiles in Palo Alto Networks' Strata Cloud Manager. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `ForwardingProfileSourceApplicationBaseModel`: Base model with fields common to all operations
- `ForwardingProfileSourceApplicationCreateModel`: Model for creating new source applications
- `ForwardingProfileSourceApplicationUpdateModel`: Model for updating existing source applications (adds `id`)
- `ForwardingProfileSourceApplicationResponseModel`: Response model for source application operations (adds `id`)

Request models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The response model uses `extra="ignore"` for forward compatibility.

## Attributes

| Attribute      | Type        | Required | Default | Description                                                                  |
|----------------|-------------|----------|---------|------------------------------------------------------------------------------|
| `name`         | `str`       | Yes      | None    | Name of the source application. Max length: 64 chars. Pattern: `^[0-9a-zA-Z._-]+$` |
| `applications` | `List[str]` | Yes      | None    | List of applications                                                          |
| `description`  | `str`       | No       | None    | Description of the source application. Max length: 1023 chars                 |
| `id`           | `UUID`      | Yes*     | None    | UUID of the source application                                                |

\* Present in `UpdateModel` and `ResponseModel` only

## Usage Example

```python
from scm.client import Scm
from scm.models.mobile_agent import ForwardingProfileSourceApplicationCreateModel

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a source application using a model
source_application = ForwardingProfileSourceApplicationCreateModel(
    name="saas-apps",
    description="SaaS applications forwarded via proxy",
    applications=["office365-enterprise-access", "slack", "zoom"],
)

# Convert the model to a dictionary for the API call
payload = source_application.model_dump(exclude_unset=True)
result = client.forwarding_profile_source_application.create(payload)
print(f"Created source application: {result.id}")
```

## Related Documentation

- [Forwarding Profile Source Applications Configuration](../../config/mobile_agent/forwarding_profile_source_applications.md)
- [Mobile Agent Models](index.md)
