# Log Forwarding Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Log Forwarding Profile Attributes](#log-forwarding-profile-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating a Log Forwarding Profile](#creating-a-log-forwarding-profile)
    - [Retrieving a Log Forwarding Profile](#retrieving-a-log-forwarding-profile)
    - [Updating a Log Forwarding Profile](#updating-a-log-forwarding-profile)
    - [Listing Log Forwarding Profiles](#listing-log-forwarding-profiles)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting a Log Forwarding Profile](#deleting-a-log-forwarding-profile)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Example Script](#example-script)
10. [Related Models](#related-models)

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

| Attribute                      | Type                | Required      | Default | Description                                                 |
|--------------------------------|---------------------|---------------|---------|-------------------------------------------------------------|
| `name`                         | str                 | Yes           | None    | The name of the log forwarding profile (max length: 63)     |
| `description`                  | str                 | No            | None    | Description of the log forwarding profile (max length: 255) |
| `match_list`                   | List[MatchListItem] | No            | None    | List of match profile configurations                        |
| `enhanced_application_logging` | bool                | No            | None    | Flag for enhanced application logging                       |
| `folder`                       | str                 | No*           | None    | The folder in which the resource is defined                 |
| `snippet`                      | str                 | No*           | None    | The snippet in which the resource is defined                |
| `device`                       | str                 | No*           | None    | The device in which the resource is defined                 |
| `id`                           | UUID                | Response only | None    | The UUID of the log forwarding profile (response only)      |

*\* Exactly one of folder, snippet, or device must be provided.*

### MatchListItem Attributes

| Attribute          | Type                                                                                                  | Required | Default | Description                                 |
|--------------------|-------------------------------------------------------------------------------------------------------|----------|---------|---------------------------------------------|
| `name`             | str                                                                                                   | Yes      | None    | Name of the match profile (max length: 63)  |
| `action_desc`      | str                                                                                                   | No       | None    | Match profile description (max length: 255) |
| `log_type`         | Literal["traffic", "threat", "wildfire", "url", "data", "tunnel", "auth", "decryption", "dns-security"] | Yes      | None    | Log type for matching                       |
| `filter`           | str                                                                                                   | No       | None    | Filter match criteria (max length: 65535)   |
| `send_http`        | List[str]                                                                                             | No       | None    | A list of HTTP server profiles              |
| `send_syslog`      | List[str]                                                                                             | No       | None    | A list of syslog server profiles            |
| `send_to_panorama` | bool                                                                                                  | No       | None    | Flag to send logs to Panorama               |
| `quarantine`       | bool                                                                                                  | No       | False   | Flag to quarantine matching logs            |

## Exceptions

| Exception                    | HTTP Code | Description                                                                |
|------------------------------|-----------|----------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid input data (e.g., invalid max_limit, invalid container parameters) |
| `MissingQueryParameterError` | 400       | Required parameter is missing or empty (e.g., empty folder name)           |
| `InvalidObjectError`         | 500       | Invalid response format from the API                                       |

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client using the unified client approach
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the log_forwarding_profile module directly through the client
# client.log_forwarding_profile is automatically initialized for you
```

You can also use the traditional approach if preferred:

```python
from scm.client import Scm
from scm.config.objects import LogForwardingProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize LogForwardingProfile object
log_forwarding_profiles = LogForwardingProfile(client)
```

## Usage Examples

### Creating a Log Forwarding Profile

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

### Retrieving a Log Forwarding Profile

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

### Updating a Log Forwarding Profile

```python
# Fetch existing log forwarding profile
existing_profile = client.log_forwarding_profile.fetch(
    name="security-logs-profile",
    folder="Shared"
)

# Modify attributes using dot notation
existing_profile.description = "Updated description for log forwarding profile"

# Add a new match item to the existing match_list
if existing_profile.match_list is None:
    existing_profile.match_list = []

existing_profile.match_list.append({
    "name": "new-match",
    "log_type": "url",
    "filter": "category eq social-networking",
    "send_syslog": ["url-syslog-profile"]
})

# Perform update
updated_profile = client.log_forwarding_profile.update(existing_profile)
print(f"Updated profile: {updated_profile.name}")
```

### Listing Log Forwarding Profiles

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

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved.

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Configure max_limit on the log_forwarding_profile service
client.log_forwarding_profile.max_limit = 1000

# List all log forwarding profiles - auto-paginates through results
all_profiles = client.log_forwarding_profile.list(folder="Shared")

# The list() method will retrieve up to 1000 objects per API call (max 5000)
# and auto-paginate through all available objects.
print(f"Retrieved {len(all_profiles)} profiles")
```

### Deleting a Log Forwarding Profile

```python
# Delete a profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.log_forwarding_profile.delete(profile_id)
print(f"Profile {profile_id} deleted successfully")
```

## Error Handling

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
