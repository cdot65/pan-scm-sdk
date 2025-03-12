# Syslog Server Profile Models

Syslog Server Profiles allow you to configure syslog servers that can receive logs from Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating, updating, and retrieving syslog server profile configurations.

## Models Overview

The module provides the following Pydantic models:

- `EscapingModel`: Represents character escaping configuration for syslog messages
- `FormatModel`: Defines format settings for different log types
- `SyslogServerModel`: Represents a server configuration within a syslog server profile
- `SyslogServerProfileBaseModel`: Base model with fields common to all syslog server profile operations
- `SyslogServerProfileCreateModel`: Model for creating new syslog server profiles
- `SyslogServerProfileUpdateModel`: Model for updating existing syslog server profiles
- `SyslogServerProfileResponseModel`: Response model for syslog server profile operations

## EscapingModel

The `EscapingModel` represents character escaping configuration for syslog messages.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| escape_character | Optional[str] | No | None | Escape sequence delimiter (max length: 1) |
| escaped_characters | Optional[str] | No | None | Characters to be escaped without spaces (max length: 255) |

## FormatModel

The `FormatModel` represents format settings for different log types in a syslog server profile.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| escaping | Optional[EscapingModel] | No | None | Character escaping configuration |
| traffic | Optional[str] | No | None | Format for traffic logs |
| threat | Optional[str] | No | None | Format for threat logs |
| wildfire | Optional[str] | No | None | Format for wildfire logs |
| url | Optional[str] | No | None | Format for URL logs |
| data | Optional[str] | No | None | Format for data logs |
| gtp | Optional[str] | No | None | Format for GTP logs |
| sctp | Optional[str] | No | None | Format for SCTP logs |
| tunnel | Optional[str] | No | None | Format for tunnel logs |
| auth | Optional[str] | No | None | Format for authentication logs |
| userid | Optional[str] | No | None | Format for user ID logs |
| iptag | Optional[str] | No | None | Format for IP tag logs |
| decryption | Optional[str] | No | None | Format for decryption logs |
| config | Optional[str] | No | None | Format for configuration logs |
| system | Optional[str] | No | None | Format for system logs |
| globalprotect | Optional[str] | No | None | Format for GlobalProtect logs |
| hip_match | Optional[str] | No | None | Format for HIP match logs |
| correlation | Optional[str] | No | None | Format for correlation logs |

## SyslogServerModel

The `SyslogServerModel` represents a server configuration within a syslog server profile.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | Syslog server name |
| server | str | Yes | - | Syslog server address |
| transport | Literal["UDP", "TCP"] | Yes | - | Transport protocol for the syslog server |
| port | int | Yes | - | Syslog server port (1-65535) |
| format | Literal["BSD", "IETF"] | Yes | - | Syslog format |
| facility | Literal["LOG_USER", "LOG_LOCAL0", "LOG_LOCAL1", "LOG_LOCAL2", "LOG_LOCAL3", "LOG_LOCAL4", "LOG_LOCAL5", "LOG_LOCAL6", "LOG_LOCAL7"] | Yes | - | Syslog facility |

## SyslogServerProfileBaseModel

The `SyslogServerProfileBaseModel` contains fields common to all syslog server profile CRUD operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | The name of the syslog server profile (max length: 31) |
| servers | Dict[str, Any] | Yes | - | Dictionary of server configurations |
| format | Optional[FormatModel] | No | None | Format settings for different log types |
| folder | Optional[str] | No | None | The folder in which the resource is defined (max length: 64) |
| snippet | Optional[str] | No | None | The snippet in which the resource is defined (max length: 64) |
| device | Optional[str] | No | None | The device in which the resource is defined (max length: 64) |

## SyslogServerProfileCreateModel

The `SyslogServerProfileCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from SyslogServerProfileBaseModel* |  |  |  |  |

### Container Type Validation

When creating a syslog server profile, exactly one of the following container types must be provided:
- `folder`: The folder in which the resource is defined
- `snippet`: The snippet in which the resource is defined
- `device`: The device in which the resource is defined

This validation is enforced by the `validate_container_type` model validator.

```python
@model_validator(mode="after")
def validate_container_type(self) -> "SyslogServerProfileCreateModel":
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

## SyslogServerProfileUpdateModel

The `SyslogServerProfileUpdateModel` extends the base model and adds the ID field required for updating existing syslog server profiles.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the syslog server profile |
| *All attributes from SyslogServerProfileBaseModel* |  |  |  |  |

## SyslogServerProfileResponseModel

The `SyslogServerProfileResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the syslog server profile |
| *All attributes from SyslogServerProfileBaseModel* |  |  |  |  |

## Usage Examples

### Creating a Basic Syslog Server Profile

```python
from scm.models.objects.syslog_server_profiles import (
    SyslogServerProfileCreateModel,
    FormatModel
)

# Create a simple syslog server profile
profile_data = {
    "name": "basic-syslog-profile",
    "servers": {
        "primary": {
            "name": "primary",
            "server": "192.168.1.100",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_USER"
        }
    },
    "folder": "Shared"
}

# Use the data with the Pydantic model
syslog_profile = SyslogServerProfileCreateModel(**profile_data)
```

### Creating a Profile with Multiple Servers and Formatting

```python
from scm.models.objects.syslog_server_profiles import (
    SyslogServerProfileCreateModel,
    FormatModel,
    EscapingModel
)

# Define format settings with escaping
format_config = FormatModel(
    escaping=EscapingModel(
        escape_character="\\",
        escaped_characters=",\""
    ),
    traffic="hostname,$time,$src,$dst,$proto,$sport,$dport",
    threat="hostname,$time,$src,$dst,$threatid,$severity",
    system="hostname,$time,$severity,$result"
)

# Create a profile with multiple servers and formatting
profile_data = {
    "name": "advanced-syslog-profile",
    "servers": {
        "primary": {
            "name": "primary",
            "server": "logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        },
        "backup": {
            "name": "backup",
            "server": "backup-logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL1"
        }
    },
    "format": {
        "traffic": "hostname,$time,$src,$dst,$proto,$sport,$dport",
        "threat": "hostname,$time,$src,$dst,$threatid,$severity",
        "system": "hostname,$time,$severity,$result",
        "escaping": {
            "escape_character": "\\",
            "escaped_characters": ",\""
        }
    },
    "folder": "Shared"
}

# Use the data with the Pydantic model
syslog_profile = SyslogServerProfileCreateModel(**profile_data)
```

### Updating an Existing Syslog Server Profile

```python
from uuid import UUID
from scm.models.objects.syslog_server_profiles import (
    SyslogServerProfileUpdateModel
)

# Update an existing syslog server profile
update_data = {
    "id": UUID("123e4567-e89b-12d3-a456-426655440000"),
    "name": "updated-syslog-profile",
    "servers": {
        "primary": {
            "name": "primary",
            "server": "new-logs.example.com",  # Updated server address
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        }
    },
    "folder": "Shared"
}

# Create update model
update_profile = SyslogServerProfileUpdateModel(**update_data)
```

## Best Practices

### Server Configuration
- Include at least one server in the `servers` dictionary
- Use TCP transport for critical logs where reliability is important
- Follow standard syslog configuration practices (port 514 for UDP, 1514 for TCP)
- Use appropriate syslog facilities based on the log type

### Format Configuration
- Follow RFC 3164 (BSD) or RFC 5424 (IETF) standards for your syslog messages
- Use escaping configuration when your logs contain special characters that need escaping
- Use different format templates for different log types for easier parsing

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for syslog server profiles

### Validation
- Validate responses using the `SyslogServerProfileResponseModel`
- Handle validation errors appropriately in your application
- Ensure server port numbers are within the valid range (1-65535)

## Related Models

- [Log Forwarding Profile Models](log_forwarding_profile_models.md): For configuring log forwarding with syslog servers
- [HTTP Server Profiles Models](http_server_profiles_models.md): For configuring HTTP-based logging
