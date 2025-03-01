# Log Forwarding Profile Models

Log Forwarding Profiles allow you to configure how logs are handled and forwarded to external systems in Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating, updating, and retrieving log forwarding profile configurations.

## Models Overview

The module provides the following Pydantic models:

- `MatchListItem`: Represents a match profile configuration within a log forwarding profile
- `LogForwardingProfileBaseModel`: Base model with fields common to all log forwarding profile operations
- `LogForwardingProfileCreateModel`: Model for creating new log forwarding profiles
- `LogForwardingProfileUpdateModel`: Model for updating existing log forwarding profiles
- `LogForwardingProfileResponseModel`: Response model for log forwarding profile operations

## MatchListItem

The `MatchListItem` represents a match profile configuration within a log forwarding profile. It defines the criteria for matching specific log types and where to send the matching logs.

| Attribute   | Type                                                                                    | Required | Default | Description                                 |
|-------------|-----------------------------------------------------------------------------------------|----------|---------|---------------------------------------------|
| name        | str                                                                                     | Yes      | -       | Name of the match profile (max length: 63)  |
| action_desc | Optional[str]                                                                           | No       | None    | Match profile description (max length: 255) |
| log_type    | Literal["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption"] | Yes      | -       | Log type for matching                       |
| filter      | Optional[str]                                                                           | No       | None    | Filter match criteria (max length: 65535)   |
| send_http   | Optional[List[str]]                                                                     | No       | None    | A list of HTTP server profiles              |
| send_syslog | Optional[List[str]]                                                                     | No       | None    | A list of syslog server profiles            |

## LogForwardingProfileBaseModel

The `LogForwardingProfileBaseModel` contains fields common to all log forwarding profile CRUD operations.

| Attribute   | Type                          | Required | Default | Description                                                   |
|-------------|-------------------------------|----------|---------|---------------------------------------------------------------|
| name        | str                           | Yes      | -       | The name of the log forwarding profile (max length: 63)       |
| description | Optional[str]                 | No       | None    | Log forwarding profile description (max length: 255)          |
| match_list  | Optional[List[MatchListItem]] | No       | None    | List of match profile configurations                          |
| folder      | Optional[str]                 | No       | None    | The folder in which the resource is defined (max length: 64)  |
| snippet     | Optional[str]                 | No       | None    | The snippet in which the resource is defined (max length: 64) |
| device      | Optional[str]                 | No       | None    | The device in which the resource is defined (max length: 64)  |

## LogForwardingProfileCreateModel

The `LogForwardingProfileCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute                                           | Type | Required | Default | Description |
|-----------------------------------------------------|------|----------|---------|-------------|
| *All attributes from LogForwardingProfileBaseModel* |      |          |         |             |

### Container Type Validation

When creating a log forwarding profile, exactly one of the following container types must be provided:
- `folder`: The folder in which the resource is defined
- `snippet`: The snippet in which the resource is defined
- `device`: The device in which the resource is defined

This validation is enforced by the `validate_container_type` model validator.

```python
@model_validator(mode="after")
def validate_container_type(self) -> "LogForwardingProfileCreateModel":
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

## LogForwardingProfileUpdateModel

The `LogForwardingProfileUpdateModel` extends the base model and adds the ID field required for updating existing log forwarding profiles.

| Attribute                                           | Type | Required | Default | Description                            |
|-----------------------------------------------------|------|----------|---------|----------------------------------------|
| id                                                  | UUID | Yes      | -       | The UUID of the log forwarding profile |
| *All attributes from LogForwardingProfileBaseModel* |      |          |         |                                        |

## LogForwardingProfileResponseModel

The `LogForwardingProfileResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute                                           | Type | Required | Default | Description                            |
|-----------------------------------------------------|------|----------|---------|----------------------------------------|
| id                                                  | UUID | Yes      | -       | The UUID of the log forwarding profile |
| *All attributes from LogForwardingProfileBaseModel* |      |          |         |                                        |

## Usage Examples

### Creating a Log Forwarding Profile

```python
from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileCreateModel,
    MatchListItem
)

# Define a match list item for traffic logs
traffic_match = MatchListItem(
    name="traffic-logs",
    log_type="traffic",
    filter="addr.src in 192.168.0.0/24",
    send_http=["http-profile-1"]
)

# Define a match list item for threat logs
threat_match = MatchListItem(
    name="threat-logs",
    log_type="threat",
    filter="severity eq critical",
    send_syslog=["syslog-profile-1"]
)

# Create a log forwarding profile in a folder
profile = LogForwardingProfileCreateModel(
    name="my-log-profile",
    description="Log forwarding profile for traffic and threat logs",
    match_list=[traffic_match, threat_match],
    folder="Shared"
)
```

### Creating a Log Forwarding Profile in a Snippet

```python
from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileCreateModel,
    MatchListItem
)

# Define a match list item for URL logs
url_match = MatchListItem(
    name="url-logs",
    log_type="url",
    filter="category eq social-networking",
    send_http=["http-profile-2"]
)

# Create a log forwarding profile in a snippet
profile = LogForwardingProfileCreateModel(
    name="url-log-profile",
    description="Log forwarding profile for URL logs",
    match_list=[url_match],
    snippet="My Snippet"
)
```

### Updating an Existing Log Forwarding Profile

```python
from uuid import UUID
from scm.models.objects.log_forwarding_profile import (
    LogForwardingProfileUpdateModel,
    MatchListItem
)

# Define updated match list items
updated_match = MatchListItem(
    name="updated-match",
    log_type="wildfire",
    filter="file_type eq pdf",
    send_http=["updated-http-profile"],
    send_syslog=["updated-syslog-profile"]
)

# Update an existing log forwarding profile
updated_profile = LogForwardingProfileUpdateModel(
    id=UUID("123e4567-e89b-12d3-a456-426655440000"),
    name="updated-profile",
    description="Updated log forwarding profile",
    match_list=[updated_match],
)
```

## Best Practices

### Match List Configuration
- Use specific filters to target only the logs you need
- Configure appropriate log destinations (HTTP servers or syslog servers)
- Consider using both HTTP and syslog servers for critical logs
- Set descriptive names and action descriptions for better management

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for log forwarding profiles
- Organize profiles logically by function or application

### Validation
- Validate responses using the `LogForwardingProfileResponseModel`
- Handle validation errors appropriately in your application
- Verify that referenced HTTP or syslog servers exist before creating profiles

## Related Models

- [HTTP Server Profiles Models](http_server_profiles_models.md): For defining HTTP servers used as log destinations