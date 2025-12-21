# Syslog Server Profile Models

## Overview {#Overview}

The Syslog Server Profile models provide a structured way to manage syslog server profile objects in Palo Alto Networks' Strata Cloud Manager. These models support defining configurations for syslog servers that can receive logs from the Strata Cloud Manager. The models handle validation of inputs and outputs when interacting with the SCM API.

### Models

The module provides the following Pydantic models:

- `EscapingModel`: Represents character escaping configuration for syslog messages
- `FormatModel`: Defines format settings for different log types
- `SyslogServerModel`: Represents a server configuration within a syslog server profile
- `SyslogServerProfileBaseModel`: Base model with fields common to all syslog server profile operations
- `SyslogServerProfileCreateModel`: Model for creating new syslog server profiles
- `SyslogServerProfileUpdateModel`: Model for updating existing syslog server profiles
- `SyslogServerProfileResponseModel`: Response model for syslog server profile operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

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
| name | str | Yes | None | Syslog server name |
| server | str | Yes | None | Syslog server address |
| transport | Literal["UDP", "TCP"] | Yes | None | Transport protocol for the syslog server |
| port | int | Yes | None | Syslog server port (1-65535) |
| format | Literal["BSD", "IETF"] | Yes | None | Syslog format |
| facility | Literal["LOG_USER", ...] | Yes | None | Syslog facility |

## SyslogServerProfileBaseModel

The `SyslogServerProfileBaseModel` contains fields common to all syslog server profile CRUD operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | None | The name of the syslog server profile (max length: 31) |
| server | List[SyslogServerModel] | Yes | None | List of server configurations |
| format | Optional[FormatModel] | No | None | Format settings for different log types |
| folder | Optional[str] | No* | None | The folder in which the resource is defined (max length: 64) |
| snippet | Optional[str] | No* | None | The snippet in which the resource is defined (max length: 64) |
| device | Optional[str] | No* | None | The device in which the resource is defined (max length: 64) |

\* Exactly one container type (folder/snippet/device) must be provided for create operations

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

### Creating a Basic Syslog Server Profile with UDP Transport

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
syslog_profile_data = {
    "name": "basic-syslog-profile",
    "server": [
        {
            "name": "primary-syslog",
            "server": "192.168.1.100",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_USER"
        }
    ],
    "folder": "Shared"
}

response = client.syslog_server_profile.create(syslog_profile_data)
print(f"Created syslog profile: {response.name} (ID: {response.id})")
```

### Creating a Profile with TCP Transport and Custom Formatting

```python
# Using dictionary with TCP transport and custom formatting
tcp_profile_data = {
    "name": "advanced-syslog-profile",
    "server": [
        {
            "name": "secure-syslog",
            "server": "logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        }
    ],
    "format": {
        "escaping": {
            "escape_character": "\\",
            "escaped_characters": ",\""
        },
        "traffic": "hostname,$time,$src,$dst,$proto,$sport,$dport",
        "threat": "hostname,$time,$src,$dst,$threatid,$severity",
        "system": "hostname,$time,$severity,$result"
    },
    "device": "My Device"
}

response = client.syslog_server_profile.create(tcp_profile_data)
print(f"Created advanced profile: {response.name}")
```

### Creating a Profile with Multiple Servers

```python
# Using dictionary with multiple servers
multi_server_data = {
    "name": "multi-server-profile",
    "server": [
        {
            "name": "primary",
            "server": "192.168.1.100",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        },
        {
            "name": "backup",
            "server": "192.168.1.101",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL1"
        }
    ],
    "snippet": "My Snippet"
}

response = client.syslog_server_profile.create(multi_server_data)
print(f"Created multi-server profile: {response.name}")
```

### Updating an Existing Syslog Server Profile

```python
# Fetch existing profile
existing = client.syslog_server_profile.fetch(name="basic-syslog-profile", folder="Shared")

# Modify attributes using dot notation
existing.server[0].server = "new-logs.example.com"
existing.server[0].port = 1514

# Add format settings
existing.format = {
    "traffic": "$time,$src,$dst,$proto,$rule,$action",
    "threat": "$time,$src,$dst,$threatid,$severity,$action"
}

# Pass modified object to update()
updated = client.syslog_server_profile.update(existing)
print(f"Updated profile: {updated.name}")
```

## Best Practices

### Server Configuration
- Use TCP transport for critical logs to ensure reliable delivery
- Configure appropriate facility values to distinguish log sources
- Use IETF format for more detailed structured logging
- Set descriptive server names for easier management

### Format Configuration
- Define custom log formats to include only the fields you need
- Use consistent format templates across log types for easier parsing
- Configure escaping for logs containing special characters
- Follow RFC 3164 (BSD) or RFC 5424 (IETF) standards for your syslog messages

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for syslog server profiles
- Organize profiles logically by function or application
