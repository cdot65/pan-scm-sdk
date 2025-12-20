# HTTP Server Profile Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [HTTP Server Profile Attributes](#http-server-profile-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating an HTTP Server Profile](#creating-an-http-server-profile)
    - [Retrieving an HTTP Server Profile](#retrieving-an-http-server-profile)
    - [Updating an HTTP Server Profile](#updating-an-http-server-profile)
    - [Listing HTTP Server Profiles](#listing-http-server-profiles)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
    - [Deleting an HTTP Server Profile](#deleting-an-http-server-profile)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Example Script](#example-script)
10. [Related Models](#related-models)

## Overview

The `HTTPServerProfile` class facilitates the management of HTTP Server Profile objects in Palo Alto Networks' Strata
Cloud Manager. HTTP Server Profiles define configurations for HTTP servers that can receive logs and other data from the
Strata Cloud Manager.

The `HTTPServerProfile` class inherits from the `BaseObject` class and provides methods for creating, retrieving,
updating, listing, and deleting HTTP server profile configurations.

## Core Methods

| Method   | Description                                        | Parameters                                                        | Return Type                          |
|----------|----------------------------------------------------|-------------------------------------------------------------------|--------------------------------------|
| `create` | Creates a new HTTP server profile                  | `data` (Dict[str, Any]): Profile data                             | HTTPServerProfileResponseModel       |
| `get`    | Retrieves an HTTP server profile by ID             | `object_id` (str): Profile ID                                     | HTTPServerProfileResponseModel       |
| `update` | Updates an existing HTTP server profile            | `http_server_profile` (HTTPServerProfileUpdateModel): Update data | HTTPServerProfileResponseModel       |
| `delete` | Deletes an HTTP server profile                     | `object_id` (str): Profile ID                                     | None                                 |
| `list`   | Lists HTTP server profiles with optional filtering | See [list parameters](#list-method-parameters)                    | List[HTTPServerProfileResponseModel] |
| `fetch`  | Retrieves a single HTTP server profile by name     | See [fetch parameters](#fetch-method-parameters)                  | HTTPServerProfileResponseModel       |

### List Method Parameters

| Parameter          | Type                | Required | Default | Description                                                                       |
|--------------------|---------------------|----------|---------|-----------------------------------------------------------------------------------|
| `folder`           | Optional[str]       | No*      | None    | Folder in which the profiles are defined                                          |
| `snippet`          | Optional[str]       | No*      | None    | Snippet in which the profiles are defined                                         |
| `device`           | Optional[str]       | No*      | None    | Device in which the profiles are defined                                          |
| `exact_match`      | bool                | No       | False   | If True, only return profiles whose container exactly matches                     |
| `exclude_folders`  | Optional[List[str]] | No       | None    | List of folder names to exclude                                                   |
| `exclude_snippets` | Optional[List[str]] | No       | None    | List of snippet values to exclude                                                 |
| `exclude_devices`  | Optional[List[str]] | No       | None    | List of device values to exclude                                                  |
| `**filters`        | Any                 | No       | None    | Additional filters including `tag_registration` (bool) and `protocol` (List[str]) |

*\* Exactly one of folder, snippet, or device must be provided.*

### Fetch Method Parameters

| Parameter | Type          | Required | Default | Description                             |
|-----------|---------------|----------|---------|-----------------------------------------|
| `name`    | str           | Yes      | -       | The name of the HTTP server profile     |
| `folder`  | Optional[str] | No*      | None    | Folder in which the profile is defined  |
| `snippet` | Optional[str] | No*      | None    | Snippet in which the profile is defined |
| `device`  | Optional[str] | No*      | None    | Device in which the profile is defined  |

*\* Exactly one of folder, snippet, or device must be provided.*

## HTTP Server Profile Attributes

| Attribute          | Type                          | Required      | Default | Description                                          |
|--------------------|-------------------------------|---------------|---------|------------------------------------------------------|
| `name`             | str                           | Yes           | None    | The name of the HTTP server profile (max length: 63) |
| `server`           | List[ServerModel]             | Yes           | None    | List of server configurations                        |
| `tag_registration` | bool                          | No            | None    | Whether to register tags on match                    |
| `description`      | str                           | No            | None    | Description of the HTTP server profile               |
| `format`           | Dict[str, PayloadFormatModel] | No            | None    | Format settings for different log types              |
| `folder`           | str                           | No*           | None    | The folder in which the resource is defined          |
| `snippet`          | str                           | No*           | None    | The snippet in which the resource is defined         |
| `device`           | str                           | No*           | None    | The device in which the resource is defined          |
| `id`               | UUID                          | Response only | None    | The UUID of the HTTP server profile (response only)  |

*\* Exactly one of folder, snippet, or device must be provided.*

### Server Model Attributes

| Attribute             | Type                                              | Required | Default | Description                               |
|-----------------------|---------------------------------------------------|----------|---------|-------------------------------------------|
| `name`                | str                                               | Yes      | None    | HTTP server name                          |
| `address`             | str                                               | Yes      | None    | HTTP server address                       |
| `protocol`            | Literal["HTTP", "HTTPS"]                          | Yes      | None    | HTTP server protocol                      |
| `port`                | int                                               | Yes      | None    | HTTP server port                          |
| `tls_version`         | Optional[Literal["1.0", "1.1", "1.2", "1.3"]]     | No       | None    | HTTP server TLS version                   |
| `certificate_profile` | Optional[str]                                     | No       | None    | HTTP server certificate profile           |
| `http_method`         | Optional[Literal["GET", "POST", "PUT", "DELETE"]] | No       | None    | HTTP operation to perform                 |
| `username`            | Optional[str]                                     | No       | None    | Username for HTTP server authentication   |
| `password`            | Optional[str]                                     | No       | None    | Password for HTTP server authentication   |

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

# Access the http_server_profile module directly through the client
# client.http_server_profile is automatically initialized for you
```

You can also use the traditional approach if preferred:

```python
from scm.client import Scm
from scm.config.objects import HTTPServerProfile

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize HTTPServerProfile object
http_server_profiles = HTTPServerProfile(client)
```

## Usage Examples

### Creating an HTTP Server Profile

```python
# Create a basic HTTP server profile with a single HTTP server
http_profile = client.http_server_profile.create({
    "name": "my-http-profile",
    "server": [
        {
            "name": "primary-server",
            "address": "10.0.0.1",
            "protocol": "HTTP",
            "port": 8080
        }
    ],
    "folder": "Prisma Access"
})

# Create a profile with HTTPS server and tag registration
https_profile = client.http_server_profile.create({
    "name": "secure-logging-profile",
    "description": "HTTPS logging server with TLS 1.2",
    "server": [
        {
            "name": "secure-server",
            "address": "logs.example.com",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "certificate_profile": "default-cert-profile",
            "http_method": "POST"
        }
    ],
    "tag_registration": True,
    "folder": "Prisma Access"
})

# Print the created profile ID
print(f"Created profile with ID: {https_profile.id}")
```

### Retrieving an HTTP Server Profile

```python
# Get profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
http_profile = client.http_server_profile.get(profile_id)

# Access profile attributes
print(f"Profile Name: {http_profile.name}")
print(f"Servers: {len(http_profile.server)}")
for server in http_profile.server:
    print(f"  - {server.name}: {server.protocol}://{server.address}:{server.port}")

# Fetch profile by name (requires exactly one container parameter)
profile_by_name = client.http_server_profile.fetch(
    name="secure-logging-profile",
    folder="Prisma Access"
)
```

### Updating an HTTP Server Profile

```python
# Fetch existing HTTP server profile
existing_profile = client.http_server_profile.fetch(
    name="secure-logging-profile",
    folder="Prisma Access"
)

# Modify attributes using dot notation
existing_profile.description = "Updated description for HTTP server profile"

# Add a backup server to the existing server list
existing_profile.server.append({
    "name": "backup-server",
    "address": "10.0.0.2",
    "protocol": "HTTP",
    "port": 8080
})

# Perform update
updated_profile = client.http_server_profile.update(existing_profile)
print(f"Updated profile: {updated_profile.name}")
```

### Listing HTTP Server Profiles

```python
# List all profiles in a folder
all_profiles = client.http_server_profile.list(folder="Prisma Access")

# List profiles with exact container match
exact_profiles = client.http_server_profile.list(
    folder="Prisma Access",
    exact_match=True
)

# List profiles with filtering
http_only_profiles = client.http_server_profile.list(
    folder="Prisma Access",
    protocol=["HTTP"]  # Only profiles with HTTP servers
)

# List profiles with tag registration enabled
tagged_profiles = client.http_server_profile.list(
    folder="Prisma Access",
    tag_registration=True
)

# List profiles with exclusions
filtered_profiles = client.http_server_profile.list(
    folder="Prisma Access",
    exclude_folders=["Temporary", "Test"]
)

# Print profile information
for profile in filtered_profiles:
    print(f"ID: {profile.id}, Name: {profile.name}")
    for server in profile.server:
        print(f"  Server: {server.protocol}://{server.address}:{server.port}")
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

# Configure max_limit on the http_server_profile service
client.http_server_profile.max_limit = 1000

# List all HTTP server profiles - auto-paginates through results
all_profiles = client.http_server_profile.list(folder="Prisma Access")

# The list() method will retrieve up to 1000 objects per API call (max 5000)
# and auto-paginate through all available objects.
print(f"Retrieved {len(all_profiles)} profiles")
```

### Deleting an HTTP Server Profile

```python
# Delete a profile by ID
profile_id = "123e4567-e89b-12d3-a456-426655440000"
client.http_server_profile.delete(profile_id)
print(f"Profile {profile_id} deleted successfully")
```

## Error Handling

```python
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

try:
    # Attempt to list profiles with invalid container parameters
    profiles = client.http_server_profile.list()  # No container specified
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"HTTP status: {e.http_status_code}")
    print(f"Details: {e.details}")

try:
    # Attempt to fetch a profile with an empty folder name
    profile = client.http_server_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")

try:
    # Attempt to filter by tag_registration with invalid type
    profiles = client.http_server_profile.list(
        folder="Prisma Access",
        tag_registration="yes"  # Should be boolean
    )
except InvalidObjectError as e:
    print(f"Invalid filter error: {e.message}")
```

## Best Practices

### Client Usage

- Use the unified client interface (`client.http_server_profile`) for simpler code
- Initialize the client once and reuse across different object types
- Set appropriate max_limit parameters during client initialization

### Container Management

- Always specify exactly one container type (folder, snippet, or device) in operations
- Use consistent container references across operations for the same profiles
- Consider environment-specific folder structures for organization

### Performance

- Set an appropriate `http_server_profile_max_limit` when initializing the client
- Use specific filters to reduce the number of results when listing profiles
- Use `exact_match=True` when you know the exact container path
- Consider pagination for large datasets

### Error Handling

- Always handle specific exceptions (`InvalidObjectError`, `MissingQueryParameterError`)
- Implement retry logic for transient network errors
- Log detailed error information for troubleshooting

### Security

- Use HTTPS servers with TLS 1.2 or higher for secure logging
- Implement proper certificate validation for HTTPS servers
- Rotate certificates and credentials regularly
- Avoid hardcoding sensitive information in profiles

## Example Script

See a complete example script for HTTP server profiles in
the [examples directory](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/http_server_profiles.py).

## Related Models

- [HTTP Server Profile Models](../../models/objects/http_server_profiles_models.md) - Pydantic models for HTTP server
  profiles
