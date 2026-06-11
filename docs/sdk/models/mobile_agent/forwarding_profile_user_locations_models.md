# GlobalProtect Forwarding Profile User Location Models

## Overview

The Forwarding Profile User Location models provide a structured way to manage location matching criteria for GlobalProtect forwarding profiles in Palo Alto Networks' Strata Cloud Manager. A user location matches either by internal host detection or by a list of IP addresses. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `ForwardingProfileUserLocationBaseModel`: Base model with fields common to all operations
- `ForwardingProfileUserLocationCreateModel`: Model for creating new user locations
- `ForwardingProfileUserLocationUpdateModel`: Model for updating existing user locations (adds `id`)
- `ForwardingProfileUserLocationResponseModel`: Response model for user location operations (adds `id`)
- `UserLocationChoice`: Location matching criteria (exactly one option must be set)
- `UserLocationInternalHostDetection`: Internal host detection settings (`ip_address`, `fqdn`)
- `UserLocationIpEntry`: A single IP address entry (`name`)

Request models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model. The response model uses `extra="ignore"` for forward compatibility.

## Attributes

| Attribute     | Type                 | Required | Default | Description                                                                  |
|---------------|----------------------|----------|---------|------------------------------------------------------------------------------|
| `name`        | `str`                | Yes      | None    | Name of the user location. Max length: 64 chars. Pattern: `^[0-9a-zA-Z._-]+$` |
| `choice`      | `UserLocationChoice` | Yes      | None    | Location matching criteria (exactly one option)                              |
| `description` | `str`                | No       | None    | Description of the user location. Max length: 1023 chars                     |
| `id`          | `UUID`               | Yes*     | None    | UUID of the user location                                                    |

\* Present in `UpdateModel` and `ResponseModel` only

### UserLocationChoice

| Attribute                 | Type                                | Required | Description                       |
|---------------------------|-------------------------------------|----------|-----------------------------------|
| `internal_host_detection` | `UserLocationInternalHostDetection` | One of   | Internal host detection settings  |
| `ip_addresses`            | `List[UserLocationIpEntry]`         | One of   | List of IP address entries        |

Exactly one of `internal_host_detection` or `ip_addresses` must be provided.

### UserLocationInternalHostDetection

| Attribute    | Type  | Required | Description                                                       |
|--------------|-------|----------|-------------------------------------------------------------------|
| `ip_address` | `str` | No       | IPv4 address with optional wildcards or CIDR suffix               |
| `fqdn`       | `str` | No       | Fully qualified domain name. Max length: 255 chars                |

### UserLocationIpEntry

| Attribute | Type  | Required | Description                                          |
|-----------|-------|----------|------------------------------------------------------|
| `name`    | `str` | Yes      | IPv4 address with optional wildcards or CIDR suffix  |

## Model Validators

### Choice Validation

The `UserLocationChoice` model enforces that exactly one matching option is provided:

```python
from scm.models.mobile_agent import UserLocationChoice

# This will raise a validation error — both options provided
UserLocationChoice(
    internal_host_detection={"fqdn": "internal.example.com"},
    ip_addresses=[{"name": "10.0.0.0/8"}],
)
```

## Usage Example

```python
from scm.client import Scm
from scm.models.mobile_agent import ForwardingProfileUserLocationCreateModel

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Create a user location using a model
user_location = ForwardingProfileUserLocationCreateModel(
    name="branch-offices",
    choice={
        "ip_addresses": [
            {"name": "10.1.0.0/16"},
            {"name": "10.2.0.0/16"},
        ]
    },
)

# Convert the model to a dictionary for the API call
payload = user_location.model_dump(exclude_unset=True)
result = client.forwarding_profile_user_location.create(payload)
print(f"Created user location: {result.id}")
```

## Related Documentation

- [Forwarding Profile User Locations Configuration](../../config/mobile_agent/forwarding_profile_user_locations.md)
- [Mobile Agent Models](index.md)
