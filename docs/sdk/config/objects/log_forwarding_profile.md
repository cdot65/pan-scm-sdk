# Log Forwarding Profile Configuration Object

[TOC]

## Overview

The `LogForwardingProfile` class facilitates the management of Log Forwarding Profile objects in Palo Alto Networks' Strata Cloud Manager. Log Forwarding Profiles define how logs are handled and forwarded to external systems, allowing you to configure match criteria for different log types and specify where the matching logs should be sent.

The `LogForwardingProfile` class inherits from the `BaseObject` class and provides methods for creating, retrieving, updating, listing, and deleting log forwarding profile configurations.

## Core Methods

| Method   | Description                                           | Parameters                                               | Return Type                             |
|----------|-------------------------------------------------------|----------------------------------------------------------|-----------------------------------------|
| `create` | Creates a new log forwarding profile                  | `data` (Dict[str, Any]): Profile data                    | LogForwardingProfileResponseModel       |
| `get`    | Retrieves a log forwarding profile by ID              | `object_id` (str): Profile ID                            | LogForwardingProfileResponseModel       |
| `update` | Updates an existing log forwarding profile            | `profile` (LogForwardingProfileUpdateModel): Update data | LogForwardingProfileResponseModel       |
| `delete` | Deletes a log forwarding profile                      | `object_id` (str): Profile ID                            | None                                    |
| `list`   | Lists log forwarding profiles with optional filtering | See [list parameters](#list-method-parameters)           | List[LogForwardingProfileResponseModel] |
| `fetch`  | Retrieves a single log forwarding profile by name     | See [fetch parameters](#fetch-method-parameters)         | LogForwardingProfileResponseModel       |

### List Method Parameters

| Parameter          | Type                | Required | Default | Description                                                                                                 |
|--------------------|---------------------|----------|---------|-------------------------------------------------------------------------------------------------------------|
| `folder`           | Optional[str]       | No*      | None    | Folder in which the profiles are defined                                                                    |
| `snippet`          | Optional[str]       | No*      | None    | Snippet in which the profiles are defined                                                                   |
| `device`           | Optional[str]       | No*      | None    | Device in which the profiles are defined                                                                    |
| `exact_match`      | bool                | No       | False   | If True, only return profiles whose container exactly matches                                               |
| `exclude_folders`  | Optional[List[str]] | No       | None    | List of folder names to exclude                                                                             |
| `exclude_snippets` | Optional[List[str]] | No       | None    | List of snippet values to exclude                                                                           |
| `exclude_devices`  | Optional[List[str]] | No       | None    | List of device values to exclude                                                                            |
| `**filters`        | Any                 | No       | None    | Additional filters including `log_type` (str or List[str]), `log_types` (List[str]), and `tags` (List[str]) |

*\* Exactly one of folder, snippet, or device must be provided.*

### Fetch Method Parameters

| Parameter | Type          | Required | Default | Description                             |
|-----------|---------------|----------|---------|-----------------------------------------|
| `name`    | str           | Yes      | -       | The name of the log forwarding profile  |
| `folder`  | Optional[str] | No*      | None    | Folder in which the profile is defined  |
| `snippet` | Optional[str] | No*      | None    | Snippet in which the profile is defined |
| `device`  | Optional[str] | No*      | None    | Device in which the profile is defined  |

*\* Exactly one of folder, snippet, or device must be provided.*

## Log Forwarding Profile Attributes

| Attribute     | Type                | Required      | Description                                                 |
|---------------|---------------------|---------------|-------------------------------------------------------------|
| `name`        | str                 | Yes           | The name of the log forwarding profile (max length: 63)     |
| `description` | str                 | No            | Description of the log forwarding profile (max length: 255) |
| `match_list`  | List[MatchListItem] | No            | List of match profile configurations                        |
| `folder`      | str                 | No*           | The folder in which the resource is defined                 |
| `snippet`     | str                 | No*           | The snippet in which the resource is defined                |
| `device`      | str                 | No*           | The device in which the resource is defined                 |
| `id`          | UUID                | Response only | The UUID of the log forwarding profile (response only)      |

*\* Exactly one of folder, snippet, or device must be provided.*

### MatchListItem Attributes

| Attribute     | Type                                                                                    | Required | Description                                 |
|---------------|-----------------------------------------------------------------------------------------|----------|---------------------------------------------|
| `name`        | str                                                                                     | Yes      | Name of the match profile (max length: 63)  |
| `action_desc` | str                                                                                     | No       | Match profile description (max length: 255) |
| `log_type`    | Literal["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption"] | Yes      | Log type for matching                       |
| `filter`      | str                                                                                     | No       | Filter match criteria (max length: 65535)   |
| `send_http`   | List[str]                                                                               | No       | A list of HTTP server profiles              |
| `send_syslog` | List[str]                                                                               | No       | A list of syslog server profiles            |

## Exceptions

| Exception                    | HTTP Code | Description                                                                |
|------------------------------|-----------|----------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid input data (e.g., invalid max_limit, invalid container parameters) |
| `MissingQueryParameterError` | 400       | Required parameter is missing or empty (e.g., empty folder name)           |
| `InvalidObjectError`         | 500       | Invalid response format from the API                                       |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
# Import the client
from scm.client import Scm

# Create API client instance
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
)

# Access log forwarding profiles directly through the client
# No need to initialize a separate LogForwardingProfile object

# You can customize max_limit for log forwarding profiles when initializing the client
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
    log_forwarding_profile_max_limit=1000  # Default max_limit is 2500 (1-5000)
)
```

</div>

## Usage Examples

### Creating a Log Forwarding Profile

<div class="termy">

<!-- termynal -->

```python
# Create a log forwarding profile with traffic logs
traffic_profile = client.log_forwarding_profile.create({
    "name": "traffic-log-profile",
    "description": "Profile for traffic logs",
    "match_list": [
        {
            "name": "internal-traffic",
            "log_type": "traffic",
            "filter": "addr.src in 192.168.0.0/24",
            "send_http": ["http-profile-1"]
        }
    ],
    "folder": "Shared"
})

# Create a profile with multiple match items
multi_match_profile = client.log_forwarding_profile.create({
    "name": "security-logs-profile",
    "description": "Profile for security-related logs",
    "match_list": [
        {
            "name": "critical-threats",
            "log_type": "threat",
            "filter": "severity eq critical",
            "send_http": ["security-http-profile"],
            "send_syslog": ["security-syslog-profile"]
        },
        {
            "name": "malware-logs",
            "log_type": "wildfire",
            "filter": "verdict eq malware",
            "send_http": ["malware-http-profile"]
        }
    ],
    "folder": "Shared"
})

# Print the created profile ID
print(f"Created profile with ID: {multi_match_profile.id}")
```

</div>

### Retrieving a Log Forwarding Profile

<div class="termy">

<!-- termynal -->

```python
# Get profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
log_profile = client.log_forwarding_profile.get(profile_id)

# Access profile attributes
print(f"Profile Name: {log_profile.name}")
print(f"Match Items: {len(log_profile.match_list)}")
for match in log_profile.match_list:
    print(f"  - {match.name}: {match.log_type} logs")
    if match.filter:
        print(f"    Filter: {match.filter}")
    if match.send_http:
        print(f"    HTTP Servers: {', '.join(match.send_http)}")
    if match.send_syslog:
        print(f"    Syslog Servers: {', '.join(match.send_syslog)}")

# Fetch profile by name (requires exactly one container parameter)
profile_by_name = client.log_forwarding_profile.fetch(
    name="security-logs-profile",
    folder="Shared"
)
```

</div>

### Updating a Log Forwarding Profile

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import LogForwardingProfileUpdateModel, MatchListItem

# First, get the current profile
existing_profile = client.log_forwarding_profile.get("123e4567-e89b-12d3-a456-426655440000")

# Create an update model with modified fields
update_data = LogForwardingProfileUpdateModel(
    id=existing_profile.id,
    name=existing_profile.name,
    description="Updated description for log forwarding profile",
    match_list=[
        MatchListItem(
            name="updated-match",
            log_type="traffic",
            filter="addr.src in 10.0.0.0/8",
            send_http=["updated-http-profile"]
        ),
        MatchListItem(
            name="new-match",
            log_type="url",
            filter="category eq social-networking",
            send_syslog=["url-syslog-profile"]
        )
    ]
)

# Update the profile
updated_profile = client.log_forwarding_profile.update(update_data)
```

</div>

### Listing Log Forwarding Profiles

<div class="termy">

<!-- termynal -->

```python
# List all profiles in a folder
all_profiles = client.log_forwarding_profile.list(folder="Shared")

# List profiles with exact container match
exact_profiles = client.log_forwarding_profile.list(
    folder="Shared",
    exact_match=True
)

# List profiles handling traffic logs
traffic_profiles = client.log_forwarding_profile.list(
    folder="Shared",
    log_type="traffic"
)

# List profiles handling multiple log types
security_profiles = client.log_forwarding_profile.list(
    folder="Shared",
    log_types=["threat", "wildfire"]
)

# List profiles with exclusions
filtered_profiles = client.log_forwarding_profile.list(
    folder="Shared",
    exclude_folders=["Temporary", "Test"]
)

# Print profile information
for profile in filtered_profiles:
    print(f"ID: {profile.id}, Name: {profile.name}")
    if profile.match_list:
        print(f"  Log Types: {', '.join([match.log_type for match in profile.match_list])}")
```

</div>

### Pagination and Max Limit

<div class="termy">

<!-- termynal -->

```python
# Create client with custom pagination limit for log forwarding profiles
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
    log_forwarding_profile_max_limit=1000
)

# List profiles with the custom pagination limit
profiles = client.log_forwarding_profile.list(folder="Shared")
print(f"Retrieved {len(profiles)} profiles")

# The max_limit is automatically capped at 5000 (the API's maximum)
```

</div>

### Deleting a Log Forwarding Profile

<div class="termy">

<!-- termynal -->

```python
# Delete a profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.log_forwarding_profile.delete(profile_id)
print(f"Profile {profile_id} deleted successfully")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    # Attempt to list profiles with invalid container parameters
    profiles = client.log_forwarding_profile.list()  # No container specified
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"HTTP status: {e.http_status_code}")
    print(f"Details: {e.details}")

try:
    # Attempt to fetch a profile with an empty folder name
    profile = client.log_forwarding_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")

try:
    # Attempt to filter by log_type with invalid type
    profiles = client.log_forwarding_profile.list(
        folder="Shared",
        log_type=123  # Should be string or list
    )
except InvalidObjectError as e:
    print(f"Invalid filter error: {e.message}")
```

</div>

## Best Practices

### Client Usage

- Use the unified client interface (`client.log_forwarding_profile`) for simpler code
- Initialize the client once and reuse across different object types
- Set appropriate max_limit parameters during client initialization

### Match List Configuration

- Use specific filters to target only the logs you need
- Provide clear, descriptive names for match list items
- Consider using both HTTP and syslog servers for critical log types
- Configure filters that minimize the volume of logs while capturing important events

### Container Management

- Always specify exactly one container type (folder, snippet, or device) in operations
- Use consistent container references across operations for the same profiles
- Organize profiles logically by function or application

### Performance

- Set an appropriate `log_forwarding_profile_max_limit` when initializing the client
- Use specific filters to reduce the number of results when listing profiles
- Use `exact_match=True` when you know the exact container path
- Consider the impact of complex filter expressions on performance

### Error Handling

- Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
- Implement retry logic for transient network errors
- Log detailed error information for troubleshooting
- Validate references to HTTP and syslog servers before creating or updating profiles

## Example Script

See a complete example script for log forwarding profiles in the [examples directory](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/log_forwarding_profile.py).

## Related Models

- [Log Forwarding Profile Models](../../models/objects/log_forwarding_profile_models.md) - Pydantic models for log forwarding profiles
- [HTTP Server Profiles](http_server_profiles.md) - Documentation for HTTP server profiles used as log destinations