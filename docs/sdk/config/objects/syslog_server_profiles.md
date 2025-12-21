# Syslog Server Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Syslog Server Profile Attributes](#syslog-server-profile-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Syslog Server Profiles](#creating-a-syslog-server-profile)
    - [Retrieving Syslog Server Profiles](#retrieving-a-syslog-server-profile)
    - [Updating Syslog Server Profiles](#updating-a-syslog-server-profile)
    - [Listing Syslog Server Profiles](#listing-syslog-server-profiles)
    - [Filtering Responses](#filtering-responses)
    - [Controlling Pagination with max_limit](#pagination-and-max-limit)
    - [Deleting Syslog Server Profiles](#deleting-a-syslog-server-profile)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#example-script)
11. [Related Models](#related-models)

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

| Attribute | Type                     | Required | Default | Description                                            |
|-----------|--------------------------|----------|---------|--------------------------------------------------------|
| `name`    | str                      | Yes      | None    | The name of the syslog server profile (max length: 31) |
| `server`  | List[SyslogServerModel]  | Yes      | None    | List of server configurations                          |
| `format`  | Optional[FormatModel]    | No       | None    | Format settings for different log types                |
| `folder`  | str                      | No*      | None    | The folder in which the resource is defined            |
| `snippet` | str                      | No*      | None    | The snippet in which the resource is defined           |
| `device`  | str                      | No*      | None    | The device in which the resource is defined            |
| `id`      | UUID                     | Yes**    | None    | The UUID of the syslog server profile                  |

\* Exactly one of folder, snippet, or device must be provided for create operations.
\*\* Only required for response model.

### Server Configuration Attributes

| Attribute   | Type                                   | Required | Default | Description                              |
|-------------|----------------------------------------|----------|---------|------------------------------------------|
| `name`      | str                                    | Yes      | None    | Syslog server name                       |
| `server`    | str                                    | Yes      | None    | Syslog server address                    |
| `transport` | Literal["UDP", "TCP"]                  | Yes      | None    | Transport protocol for the syslog server |
| `port`      | int                                    | Yes      | None    | Syslog server port (1-65535)             |
| `format`    | Literal["BSD", "IETF"]                 | Yes      | None    | Syslog format                            |
| `facility`  | Literal["LOG_USER", "LOG_LOCAL0", ...] | Yes      | None    | Syslog facility                          |

## Exceptions

| Exception                    | HTTP Code | Description                                                                |
|------------------------------|-----------|----------------------------------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid input data (e.g., invalid max_limit, invalid container parameters) |
| `MissingQueryParameterError` | 400       | Required parameter is missing or empty (e.g., empty folder name)           |
| `InvalidObjectError`         | 500       | Invalid response format from the API                                       |

## Basic Configuration

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access syslog server profiles directly through the client
# No need to initialize a separate SyslogServerProfile object
```

## Usage Examples

### Creating a Syslog Server Profile

```python
# Create a basic syslog server profile with a single UDP server
syslog_profile = client.syslog_server_profile.create({
    "name": "my-syslog-profile",
    "server": [
        {
            "name": "server1",
            "server": "192.168.1.100",
            "transport": "UDP",
            "port": 514,
            "format": "BSD",
            "facility": "LOG_USER"
        }
    ],
    "folder": "Prisma Access"
})

# Create a profile with multiple TCP servers
tcp_profile = client.syslog_server_profile.create({
    "name": "tcp-logging-profile",
    "server": [
        {
            "name": "primary",
            "server": "logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL0"
        },
        {
            "name": "backup",
            "server": "backup-logs.example.com",
            "transport": "TCP",
            "port": 1514,
            "format": "IETF",
            "facility": "LOG_LOCAL1"
        }
    ],
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

### Retrieving a Syslog Server Profile

```python
# Get profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
syslog_profile = client.syslog_server_profile.get(profile_id)

# Access profile attributes
print(f"Profile Name: {syslog_profile.name}")
print(f"Number of servers: {len(syslog_profile.server)}")
for srv in syslog_profile.server:
    print(f"  - {srv.name}: {srv.transport}://{srv.server}:{srv.port}")

# Fetch profile by name (requires exactly one container parameter)
profile_by_name = client.syslog_server_profile.fetch(
    name="tcp-logging-profile",
    folder="Prisma Access"
)
```

### Updating a Syslog Server Profile

```python
# Fetch existing profile
existing_profile = client.syslog_server_profile.fetch(
    name="tcp-logging-profile",
    folder="Prisma Access"
)

# Modify server configuration using dot notation
# Update the first server's address
existing_profile.server[0].server = "new-logs.example.com"

# Add format settings
existing_profile.format = {
    "traffic": "updated-traffic-format",
    "threat": "updated-threat-format"
}

# Pass modified object to update()
updated_profile = client.syslog_server_profile.update(existing_profile)
print(f"Updated profile: {updated_profile.name}")
```

### Listing Syslog Server Profiles

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
    for srv in profile.server:
        print(f"  Server: {srv.name} - {srv.transport}://{srv.server}:{srv.port}")
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `transport` and `format`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

```python
# Only return profiles defined exactly in 'Prisma Access'
exact_profiles = client.syslog_server_profile.list(
    folder='Prisma Access',
    exact_match=True
)

for profile in exact_profiles:
    print(f"Exact match: {profile.name} in {profile.folder}")

# Exclude all profiles from the 'All' folder
no_all_profiles = client.syslog_server_profile.list(
    folder='Prisma Access',
    exclude_folders=['All']
)

for profile in no_all_profiles:
    assert profile.folder != 'All'
    print(f"Filtered out 'All': {profile.name}")

# Combine exact_match with exclusions
combined_filters = client.syslog_server_profile.list(
    folder='Prisma Access',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default']
)

for profile in combined_filters:
    print(f"Combined filters result: {profile.name} in {profile.folder}")
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

# Configure max_limit on the syslog_server_profile service
client.syslog_server_profile.max_limit = 1000

# List all profiles - auto-paginates through results
all_profiles = client.syslog_server_profile.list(folder='Prisma Access')

# The list() method will retrieve up to 1000 objects per API call
# and auto-paginate through all available objects.
print(f"Retrieved {len(all_profiles)} profiles")
```

### Deleting a Syslog Server Profile

```python
# Delete a profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.syslog_server_profile.delete(profile_id)
print(f"Profile {profile_id} deleted successfully")
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Prisma Access"],
    "description": "Updated syslog server profiles",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly on the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job directly from the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs directly from the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

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

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.syslog_server_profile`) for simpler code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)

2. **Container Management**
    - Always specify exactly one container type (folder, snippet, or device)
    - Use consistent container references across operations
    - Consider environment-specific folder structures for organization

3. **Performance**
    - Set an appropriate `max_limit` using the property setter pattern
    - Use specific filters to reduce the number of results when listing profiles
    - Use `exact_match=True` when you know the exact container path
    - Consider pagination for large datasets

4. **Error Handling**
    - Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
    - Implement retry logic for transient network errors
    - Log detailed error information for troubleshooting

5. **Syslog Server Configuration**
    - Follow RFC 3164 (BSD) or RFC 5424 (IETF) standards for syslog messages
    - Consider using TCP transport for critical logs where reliability is important
    - Use appropriate syslog facilities to categorize different types of logs
    - Configure server redundancy for critical logging

## Example Script

See a complete example script for syslog server profiles in the [examples directory](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/syslog_server_profiles.py).

## Related Models

- [Syslog Server Profile Models](../../models/objects/syslog_server_profiles_models.md) - Pydantic models for syslog server profiles
