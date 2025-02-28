# HTTP Server Profile Models

HTTP Server Profiles allow you to configure HTTP servers that can receive logs from Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating, updating, and retrieving HTTP server profile configurations.

## Models Overview

The module provides the following Pydantic models:

- `ServerModel`: Represents a server configuration within an HTTP server profile
- `PayloadFormatModel`: Defines the payload format configuration for log types
- `HTTPServerProfileBaseModel`: Base model with fields common to all HTTP server profile operations
- `HTTPServerProfileCreateModel`: Model for creating new HTTP server profiles
- `HTTPServerProfileUpdateModel`: Model for updating existing HTTP server profiles
- `HTTPServerProfileResponseModel`: Response model for HTTP server profile operations

## ServerModel

The `ServerModel` represents a server configuration within an HTTP server profile.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | HTTP server name |
| address | str | Yes | - | HTTP server address |
| protocol | Literal["HTTP", "HTTPS"] | Yes | - | HTTP server protocol |
| port | int | Yes | - | HTTP server port |
| tls_version | Optional[Literal["1.0", "1.1", "1.2", "1.3"]] | No | None | HTTP server TLS version |
| certificate_profile | Optional[str] | No | None | HTTP server certificate profile |
| http_method | Optional[Literal["GET", "POST", "PUT", "DELETE"]] | No | None | HTTP operation to perform |

## PayloadFormatModel

The `PayloadFormatModel` represents the payload format configuration for a specific log type.

This is a flexible model that allows extra fields since the exact fields in the payload format model are not fully specified in the OpenAPI specification.

## HTTPServerProfileBaseModel

The `HTTPServerProfileBaseModel` contains fields common to all HTTP server profile CRUD operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | The name of the HTTP server profile (max length: 63) |
| server | List[ServerModel] | Yes | - | List of server configurations |
| tag_registration | Optional[bool] | No | None | Whether to register tags on match |
| description | Optional[str] | No | None | Description of the HTTP server profile |
| format | Optional[Dict[str, PayloadFormatModel]] | No | None | Format settings for different log types |
| folder | Optional[str] | No | None | The folder in which the resource is defined (max length: 64) |
| snippet | Optional[str] | No | None | The snippet in which the resource is defined (max length: 64) |
| device | Optional[str] | No | None | The device in which the resource is defined (max length: 64) |

## HTTPServerProfileCreateModel

The `HTTPServerProfileCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from HTTPServerProfileBaseModel* |  |  |  |  |

### Container Type Validation

When creating an HTTP server profile, exactly one of the following container types must be provided:
- `folder`: The folder in which the resource is defined
- `snippet`: The snippet in which the resource is defined
- `device`: The device in which the resource is defined

This validation is enforced by the `validate_container_type` model validator.

```python
@model_validator(mode="after")
def validate_container_type(self) -> "HTTPServerProfileCreateModel":
    """Validates that exactly one container type is provided."""
    container_fields = [
        "folder",
        "snippet",
        "device",
    ]
    provided = [
        field for field in container_fields if getattr(self, field) is not None
    ]
    if len(provided) != 1:
        raise ValueError(
            "Exactly one of 'folder', 'snippet', or 'device' must be provided."
        )
    return self
```

## HTTPServerProfileUpdateModel

The `HTTPServerProfileUpdateModel` extends the base model and adds the ID field required for updating existing HTTP server profiles.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the HTTP server profile |
| *All attributes from HTTPServerProfileBaseModel* |  |  |  |  |

## HTTPServerProfileResponseModel

The `HTTPServerProfileResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the HTTP server profile |
| *All attributes from HTTPServerProfileBaseModel* |  |  |  |  |

## Usage Examples

### Creating a Basic HTTP Server Profile

```python
from scm.models.objects.http_server_profiles import (
    HTTPServerProfileCreateModel,
    ServerModel
)

# Define a server configuration
server = ServerModel(
    name="my-http-server",
    address="10.0.0.1",
    protocol="HTTP",
    port=8080
)

# Create an HTTP server profile in a folder
http_profile = HTTPServerProfileCreateModel(
    name="my-http-profile",
    server=[server],
    folder="Prisma Access"
)
```

### Creating an HTTPS Server with TLS Configuration

```python
from scm.models.objects.http_server_profiles import (
    HTTPServerProfileCreateModel,
    ServerModel
)

# Define a server configuration with TLS
server = ServerModel(
    name="secure-server",
    address="secure.example.com",
    protocol="HTTPS",
    port=443,
    tls_version="1.2",
    certificate_profile="default-cert-profile"
)

# Create an HTTP server profile in a device
http_profile = HTTPServerProfileCreateModel(
    name="secure-http-profile",
    server=[server],
    tag_registration=True,
    description="Secure HTTP server profile for logging",
    device="My Device"
)
```

### Updating an Existing HTTP Server Profile

```python
from uuid import UUID
from scm.models.objects.http_server_profiles import (
    HTTPServerProfileUpdateModel,
    ServerModel
)

# Define updated server configurations
server1 = ServerModel(
    name="primary-server",
    address="10.0.0.1",
    protocol="HTTP",
    port=8080
)

server2 = ServerModel(
    name="backup-server",
    address="10.0.0.2",
    protocol="HTTP",
    port=8080
)

# Update an existing HTTP server profile
updated_profile = HTTPServerProfileUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="updated-profile",
    server=[server1, server2],
    description="Updated profile with primary and backup servers",
    folder="Prisma Access"
)
```

## Best Practices

### Server Configuration
- Include at least one server in the `server` list
- Use HTTPS with TLS 1.2 or higher for secure communication
- Configure appropriate certificate profiles when using HTTPS

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for HTTP server profiles

### Validation
- Validate responses using the `HTTPServerProfileResponseModel`
- Handle validation errors appropriately in your application

## Related Models

- [Tag Models](tag_models.md): For working with tags that can be registered by HTTP server profiles
- [Address Models](address_models.md): For defining addresses used in HTTP server configurations