# Log Forwarding Profile Models

## Overview {#Overview}

Log Forwarding Profiles allow you to configure how logs are handled and forwarded to external systems in Palo Alto Networks' Strata Cloud Manager. These models define the structure for creating, updating, and retrieving log forwarding profile configurations.

### Models

The module provides the following Pydantic models:

- `MatchListItem`: Represents a match profile configuration within a log forwarding profile
- `LogForwardingProfileBaseModel`: Base model with fields common to all log forwarding profile operations
- `LogForwardingProfileCreateModel`: Model for creating new log forwarding profiles
- `LogForwardingProfileUpdateModel`: Model for updating existing log forwarding profiles
- `LogForwardingProfileResponseModel`: Response model for log forwarding profile operations

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## MatchListItem

The `MatchListItem` represents a match profile configuration within a log forwarding profile. It defines the criteria for matching specific log types and where to send the matching logs.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | Name of the match profile (max length: 63) |
| action_desc | Optional[str] | No | None | Match profile description (max length: 255) |
| log_type | Literal["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption", "dns-security"] | Yes | - | Log type for matching |
| filter | Optional[str] | No | None | Filter match criteria (max length: 65535) |
| send_http | Optional[List[str]] | No | None | A list of HTTP server profiles |
| send_syslog | Optional[List[str]] | No | None | A list of syslog server profiles |
| send_to_panorama | Optional[bool] | No | None | Flag to send logs to Panorama |
| quarantine | Optional[bool] | No | False | Flag to quarantine matching logs |

## LogForwardingProfileBaseModel

The `LogForwardingProfileBaseModel` contains fields common to all log forwarding profile CRUD operations.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| name | str | Yes | - | The name of the log forwarding profile (max length: 63) |
| description | Optional[str] | No | None | Log forwarding profile description (max length: 255) |
| match_list | Optional[List[MatchListItem]] | No | None | List of match profile configurations |
| enhanced_application_logging | Optional[bool] | No | None | Flag for enhanced application logging |
| folder | Optional[str] | No | None | The folder in which the resource is defined (max length: 64) |
| snippet | Optional[str] | No | None | The snippet in which the resource is defined (max length: 64) |
| device | Optional[str] | No | None | The device in which the resource is defined (max length: 64) |

## LogForwardingProfileCreateModel

The `LogForwardingProfileCreateModel` extends the base model and includes validation to ensure that exactly one container type is provided.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| *All attributes from LogForwardingProfileBaseModel* |  |  |  |  |

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

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | UUID | Yes | - | The UUID of the log forwarding profile |
| *All attributes from LogForwardingProfileBaseModel* |  |  |  |  |

## LogForwardingProfileResponseModel

The `LogForwardingProfileResponseModel` extends the base model and includes the ID field returned in API responses.

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| id | Optional[UUID] | No | None | The UUID of the log forwarding profile (not required for predefined snippets) |
| *All attributes from LogForwardingProfileBaseModel* |  |  |  |  |

### ID Validation for Non-Predefined Profiles

The response model includes a validator to ensure that non-predefined profiles have an ID:

```python
@model_validator(mode="after")
def validate_id_for_non_predefined(self) -> "LogForwardingProfileResponseModel":
    """Validates that non-predefined profiles have an ID."""
    # Skip validation if snippet is "predefined-snippet"
    if self.snippet == "predefined-snippet":
        return self

    # For normal profiles in folders, ensure ID is present
    if not self.id and self.snippet != "predefined-snippet" and self.folder is not None:
        raise ValueError("ID is required for non-predefined profiles")

    return self
```

## Usage Examples

### Creating a Log Forwarding Profile

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Using dictionary
profile = {
    "name": "my-log-profile",
    "description": "Log forwarding profile for traffic and threat logs",
    "match_list": [
        {
            "name": "traffic-logs",
            "log_type": "traffic",
            "filter": "addr.src in 192.168.0.0/24",
            "send_http": ["http-profile-1"]
        },
        {
            "name": "threat-logs",
            "log_type": "threat",
            "filter": "severity eq critical",
            "send_syslog": ["syslog-profile-1"]
        }
    ],
    "folder": "Shared"
}

response = client.log_forwarding_profile.create(profile)
```

### Creating a Log Forwarding Profile in a Snippet

```python
# Using dictionary
profile = {
    "name": "url-log-profile",
    "description": "Log forwarding profile for URL logs",
    "match_list": [
        {
            "name": "url-logs",
            "log_type": "url",
            "filter": "category eq social-networking",
            "send_http": ["http-profile-2"]
        }
    ],
    "snippet": "My Snippet"
}

response = client.log_forwarding_profile.create(profile)
```

### Updating an Existing Log Forwarding Profile

```python
# Fetch existing log forwarding profile
existing = client.log_forwarding_profile.fetch(
    name="my-log-profile",
    folder="Shared"
)

# Modify attributes using dot notation
existing.description = "Updated log forwarding profile"
existing.enhanced_application_logging = True

# Add a new match item
if existing.match_list is None:
    existing.match_list = []

existing.match_list.append({
    "name": "updated-match",
    "log_type": "wildfire",
    "filter": "file_type eq pdf",
    "send_http": ["updated-http-profile"],
    "send_syslog": ["updated-syslog-profile"],
    "send_to_panorama": True,
    "quarantine": True
})

# Pass modified object to update()
updated = client.log_forwarding_profile.update(existing)
```

## Best Practices

### Match List Configuration
- Use specific filters to target only the logs you need
- Configure appropriate log destinations (HTTP servers or syslog servers)
- Consider using both HTTP and syslog servers for critical logs
- Set descriptive names and action descriptions for better management
- Enable quarantine for suspicious events that require investigation
- Use send_to_panorama for logs that should be centrally stored

### Container Management
- Always specify exactly one container type (folder, snippet, or device)
- Use consistent naming conventions for log forwarding profiles
- Organize profiles logically by function or application
