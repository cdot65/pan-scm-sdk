# HTTP Server Profile Models

## Overview {#Overview}

HTTP Server Profiles allow you to configure HTTP servers that can receive logs from Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating, updating, and retrieving HTTP server profile configurations.

### Models

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
| username | Optional[str] | No | None | Username for HTTP server authentication |
| password | Optional[str] | No | None | Password for HTTP server authentication |

## PayloadFormatModel

The `PayloadFormatModel` represents the payload format configuration for a specific log type.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | Optional[str] | No | "Default" | The name of the payload format |
| url_format | Optional[str] | No | None | The URL path of the HTTP server |
| headers | Optional[List[Dict[str, str]]] | No | None | List of HTTP headers to include in the request |
| params | Optional[List[Dict[str, str]]] | No | None | List of HTTP parameters to include in the request |
| payload | Optional[str] | No | None | The log payload format containing log field values |

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
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
http_profile = {
    "name": "my-http-profile",
    "server": [
        {
            "name": "my-http-server",
            "address": "10.0.0.1",
            "protocol": "HTTP",
            "port": 8080
        }
    ],
    "folder": "Prisma Access"
}

response = client.http_server_profile.create(http_profile)
```

### Creating an HTTPS Server with TLS Configuration

```python
# Using dictionary with TLS configuration
https_profile = {
    "name": "secure-http-profile",
    "description": "Secure HTTP server profile for logging",
    "server": [
        {
            "name": "secure-server",
            "address": "secure.example.com",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "certificate_profile": "default-cert-profile"
        }
    ],
    "tag_registration": True,
    "folder": "Prisma Access"
}

response = client.http_server_profile.create(https_profile)
```

### Updating an Existing HTTP Server Profile

```python
# Fetch existing HTTP server profile
existing = client.http_server_profile.fetch(
    name="my-http-profile",
    folder="Prisma Access"
)

# Modify attributes using dot notation
existing.description = "Updated profile with primary and backup servers"

# Add a backup server
existing.server.append({
    "name": "backup-server",
    "address": "10.0.0.2",
    "protocol": "HTTP",
    "port": 8080
})

# Pass modified object to update()
updated = client.http_server_profile.update(existing)
```

## Best Practices

### Server Configuration
- Include at least one server in the `server` list
- Use HTTPS with TLS 1.2 or higher for secure communication
- Configure appropriate certificate profiles when using HTTPS
- Set authentication credentials when required by your HTTP servers

### Format Configuration
- Define specific format settings for each log type when needed
- Include any necessary HTTP headers and parameters
- Design payload formats to match your log analysis system requirements

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for HTTP server profiles
- Organize profiles logically by function or application

## Related Models

- [Tag Models](tag_models.md): For working with tags that can be registered by HTTP server profiles
- [Address Models](address_models.md): For defining addresses used in HTTP server configurations
