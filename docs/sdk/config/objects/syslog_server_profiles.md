# Syslog Server Profile Configuration Object

[TOC]

## Overview

The `SyslogServerProfile` class facilitates the management of Syslog Server Profile objects in Palo Alto Networks' Strata Cloud Manager. Syslog Server Profiles define configurations for syslog servers that can receive logs from the Strata Cloud Manager.

The `SyslogServerProfile` class inherits from the `BaseObject` class and provides methods for creating, retrieving, updating, listing, and deleting syslog server profile configurations.

## Core Methods

| Method   | Description                                          | Parameters                                                            | Return Type                            |
|----------|------------------------------------------------------|-----------------------------------------------------------------------|----------------------------------------|
| `create` | Creates a new syslog server profile                  | `data` (Dict[str, Any]): Profile data                                 | SyslogServerProfileResponseModel       |
| `get`    | Retrieves a syslog server profile by ID              | `object_id` (str): Profile ID                                         | SyslogServerProfileResponseModel       |
| `update` | Updates an existing syslog server profile            | `syslog_server_profile` (SyslogServerProfileUpdateModel): Update data | SyslogServerProfileResponseModel       |
| `delete` | Deletes a syslog server profile                      | `object_id` (str): Profile ID                                         | None                                   |
| `list`   | Lists syslog server profiles with optional filtering | See [list parameters](#list-method-parameters)                        | List[SyslogServerProfileResponseModel] |
| `fetch`  | Retrieves a single syslog server profile by name     | See [fetch parameters](#fetch-method-parameters)                      | SyslogServerProfileResponseModel       |

### List Method Parameters

| Parameter          | Type                | Required | Default | Description                                                                   |
|--------------------|---------------------|----------|---------|-------------------------------------------------------------------------------|
| `folder`           | Optional[str]       | No*      | None    | Folder in which the profiles are defined                                      |
| `snippet`          | Optional[str]       | No*      | None    | Snippet in which the profiles are defined                                     |
| `device`           | Optional[str]       | No*      | None    | Device in which the profiles are defined                                      |
| `exact_match`      | bool                | No       | False   | If True, only return profiles whose container exactly matches                 |
| `exclude_folders`  | Optional[List[str]] | No       | None    | List of folder names to exclude                                               |
| `exclude_snippets` | Optional[List[str]] | No       | None    | List of snippet values to exclude                                             |
| `exclude_devices`  | Optional[List[str]] | No       | None    | List of device values to exclude                                              |
| `**filters`        | Any                 | No       | None    | Additional filters including `transport` (List[str]) and `format` (List[str]) |

*\* Exactly one of folder, snippet, or device must be provided.*

### Fetch Method Parameters

| Parameter | Type          | Required | Default | Description                             |
|-----------|---------------|----------|---------|-----------------------------------------|
| `name`    | str           | Yes      | -       | The name of the syslog server profile   |
| `folder`  | Optional[str] | No*      | None    | Folder in which the profile is defined  |
| `snippet` | Optional[str] | No*      | None    | Snippet in which the profile is defined |
| `device`  | Optional[str] | No*      | None    | Device in which the profile is defined  |

*\* Exactly one of folder, snippet, or device must be provided.*

## Syslog Server Profile Attributes

| Attribute | Type                  | Required      | Description                                            |
|-----------|-----------------------|---------------|--------------------------------------------------------|
| `name`    | str                   | Yes           | The name of the syslog server profile (max length: 31) |
| `servers` | Dict[str, Any]        | Yes           | Dictionary of server configurations                    |
| `format`  | Optional[FormatModel] | No            | Format settings for different log types                |
| `folder`  | str                   | No*           | The folder in which the resource is defined            |
| `snippet` | str                   | No*           | The snippet in which the resource is defined           |
| `device`  | str                   | No*           | The device in which the resource is defined            |
| `id`      | UUID                  | Response only | The UUID of the syslog server profile (response only)  |

*\* Exactly one of folder, snippet, or device must be provided.*

### Server Configuration Attributes

| Attribute   | Type                                   | Required | Description                              |
|-------------|----------------------------------------|----------|------------------------------------------|
| `name`      | str                                    | Yes      | Syslog server name                       |
| `server`    | str                                    | Yes      | Syslog server address                    |
| `transport` | Literal["UDP", "TCP"]                  | Yes      | Transport protocol for the syslog server |
| `port`      | int                                    | Yes      | Syslog server port (1-65535)             |
| `format`    | Literal["BSD", "IETF"]                 | Yes      | Syslog format                            |
| `facility`  | Literal["LOG_USER", "LOG_LOCAL0", ...] | Yes      | Syslog facility                          |

## Exceptions

| Exception                    | HTTP Code | Description                                                                |
|------------------------------|-----------|----------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid input data (e.g., invalid max_limit, invalid container parameters) |
| `MissingQueryParameterError` | 400       | Required parameter is missing or empty (e.g., empty folder name)           |
| `InvalidObjectError`         | 500       | Invalid response format from the API                                       |

## Basic Configuration

<div class="termy">

```python
# Import the client
from scm.client import Scm

# Create API client instance
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
)

# Access syslog server profiles directly through the client
# No need to initialize a separate SyslogServerProfile object

# You can customize max_limit for syslog server profiles when initializing the client
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
    syslog_server_profile_max_limit=1000  # Default max_limit is 2500 (1-5000)
)
```

</div>

## Usage Examples

### Creating a Syslog Server Profile

<div class="termy">

```python
# Create a basic syslog server profile with a single UDP server
syslog_profile = client.syslog_server_profile.create({
    "name": "my-syslog-profile",
    "servers": {
        "server1": {
            "name": "server1",
            "server": "192.168.1.100",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_USER"
        }
    },
    "folder": "Prisma Access"
})

# Create a profile with TCP servers
tcp_profile = client.syslog_server_profile.create({
    "name": "tcp-logging-profile",
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
        "traffic": "traffic-format",
        "threat": "threat-format",
        "system": "system-format"
    },
    "folder": "Prisma Access"
})

# Print the created profile ID
print(f"Created profile with ID: {tcp_profile.id}")
```

</div>

### Retrieving a Syslog Server Profile

<div class="termy">

```python
# Get profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
syslog_profile = client.syslog_server_profile.get(profile_id)

# Access profile attributes
print(f"Profile Name: {syslog_profile.name}")
print(f"Number of servers: {len(syslog_profile.servers)}")
for server_name, server_data in syslog_profile.servers.items():
    print(f"  - {server_name}: {server_data['transport']}://{server_data['server']}:{server_data['port']}")

# Fetch profile by name (requires exactly one container parameter)
profile_by_name = client.syslog_server_profile.fetch(
    name="tcp-logging-profile",
    folder="Prisma Access"
)
```

</div>

### Updating a Syslog Server Profile

<div class="termy">

```python
from scm.models.objects import SyslogServerProfileUpdateModel
import uuid

# First, get the current profile
existing_profile = client.syslog_server_profile.get("123e4567-e89b-12d3-a456-426655440000")

# Create an update model with modified servers
update_data = {
    "id": existing_profile.id,
    "name": existing_profile.name,
    "servers": {
        "primary": {
            "name": "primary",
            "server": "new-logs.example.com",  # Updated server address
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
    "folder": "Prisma Access"
}

# Convert to update model
update_model = SyslogServerProfileUpdateModel(**update_data)

# Update the profile
updated_profile = client.syslog_server_profile.update(update_model)
```

</div>

### Listing Syslog Server Profiles

<div class="termy">

```python
# List all profiles in a folder
all_profiles = client.syslog_server_profile.list(folder="Prisma Access")

# List profiles with exact container match
exact_profiles = client.syslog_server_profile.list(
    folder="Prisma Access",
    exact_match=True
)

# List profiles with filtering
udp_only_profiles = client.syslog_server_profile.list(
    folder="Prisma Access",
    transport=["UDP"]  # Only profiles with UDP servers
)

# List profiles with format filtering
ietf_profiles = client.syslog_server_profile.list(
    folder="Prisma Access",
    format=["IETF"]  # Only profiles with IETF format servers
)

# List profiles with exclusions
filtered_profiles = client.syslog_server_profile.list(
    folder="Prisma Access",
    exclude_folders=["Temporary", "Test"]
)

# Print profile information
for profile in filtered_profiles:
    print(f"ID: {profile.id}, Name: {profile.name}")
    for server_name, server_data in profile.servers.items():
        print(f"  Server: {server_name} - {server_data['transport']}://{server_data['server']}:{server_data['port']}")
```

</div>

### Pagination and Max Limit

<div class="termy">

```python
# Create client with custom pagination limit for syslog server profiles
client = Scm(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tsg_id="your-tenant-id",
    syslog_server_profile_max_limit=1000
)

# List profiles with the custom pagination limit
profiles = client.syslog_server_profile.list(folder="Prisma Access")
print(f"Retrieved {len(profiles)} profiles")

# The max_limit is automatically capped at 5000 (the API's maximum)
```

</div>

### Deleting a Syslog Server Profile

<div class="termy">

```python
# Delete a profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.syslog_server_profile.delete(profile_id)
print(f"Profile {profile_id} deleted successfully")
```

</div>

## Error Handling

<div class="termy">

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    # Attempt to list profiles with invalid container parameters
    profiles = client.syslog_server_profile.list()  # No container specified
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"HTTP status: {e.http_status_code}")
    print(f"Details: {e.details}")

try:
    # Attempt to fetch a profile with an empty folder name
    profile = client.syslog_server_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")

try:
    # Attempt to filter by transport with invalid type
    profiles = client.syslog_server_profile.list(
        folder="Prisma Access",
        transport="UDP"  # Should be a list
    )
except InvalidObjectError as e:
    print(f"Invalid filter error: {e.message}")
```

</div>

## Best Practices

### Client Usage

- Use the unified client interface (`client.syslog_server_profile`) for simpler code
- Initialize the client once and reuse across different object types
- Set appropriate max_limit parameters during client initialization

### Container Management

- Always specify exactly one container type (folder, snippet, or device) in operations
- Use consistent container references across operations for the same profiles
- Consider environment-specific folder structures for organization

### Performance

- Set an appropriate `syslog_server_profile_max_limit` when initializing the client
- Use specific filters to reduce the number of results when listing profiles
- Use `exact_match=True` when you know the exact container path
- Consider pagination for large datasets

### Error Handling

- Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
- Implement retry logic for transient network errors
- Log detailed error information for troubleshooting

### Syslog Server Configuration

- Follow RFC 3164 (BSD) or RFC 5424 (IETF) standards for syslog messages
- Consider using TCP transport for critical logs where reliability is important
- Use appropriate syslog facilities to categorize different types of logs
- Configure server redundancy for critical logging

## Related Models

- [Syslog Server Profile Models](../../models/objects/syslog_server_profiles_models.md) - Pydantic models for syslog server profiles