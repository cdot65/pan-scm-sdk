# HTTP Server Profiles

The `HTTPServerProfile` service manages HTTP server profile configurations in Strata Cloud Manager, defining HTTP servers that can receive logs and other data for forwarding.

## Class Overview

The `HTTPServerProfile` class provides CRUD operations for HTTP server profile objects. It is accessed through the `client.http_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the HTTPServerProfile service
http_profiles = client.http_server_profile
```

### Key Attributes

| Attribute          | Type                          | Required | Description                                         |
|--------------------|-------------------------------|----------|-----------------------------------------------------|
| `name`             | `str`                         | Yes      | Name of the HTTP server profile (max 63 chars)      |
| `id`               | `UUID`                        | Yes*     | Unique identifier (*response only)                  |
| `server`           | `List[ServerModel]`           | Yes      | List of server configurations                       |
| `tag_registration` | `bool`                        | No       | Whether to register tags on match                   |
| `description`      | `str`                         | No       | Description of the profile                          |
| `format`           | `Dict[str, PayloadFormatModel]` | No    | Format settings for different log types             |
| `folder`           | `str`                         | Yes**    | Folder location (**one container required)          |
| `snippet`          | `str`                         | Yes**    | Snippet location (**one container required)         |
| `device`           | `str`                         | Yes**    | Device location (**one container required)          |

\* Exactly one of `folder`, `snippet`, or `device` is required.

#### Server Model Attributes

| Attribute             | Type   | Required | Description                               |
|-----------------------|--------|----------|-------------------------------------------|
| `name`                | `str`  | Yes      | HTTP server name                          |
| `address`             | `str`  | Yes      | HTTP server address                       |
| `protocol`            | `str`  | Yes      | Protocol: `"HTTP"` or `"HTTPS"`           |
| `port`                | `int`  | Yes      | HTTP server port                          |
| `tls_version`         | `str`  | No       | TLS version: `"1.0"`, `"1.1"`, `"1.2"`, `"1.3"` |
| `certificate_profile` | `str` | No       | Certificate profile name                  |
| `http_method`         | `str`  | No       | HTTP method: `"GET"`, `"POST"`, `"PUT"`, `"DELETE"` |

## Methods

### List HTTP Server Profiles

Retrieves a list of HTTP server profiles with optional filtering.

```python
profiles = client.http_server_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}")
    for server in profile.server:
        print(f"  Server: {server.protocol}://{server.address}:{server.port}")
```

### Fetch an HTTP Server Profile

Retrieves a single HTTP server profile by name and container.

```python
profile = client.http_server_profile.fetch(
    name="secure-logging-profile",
    folder="Texas"
)
print(f"Found profile: {profile.name}")
```

### Create an HTTP Server Profile

Creates a new HTTP server profile.

```python
new_profile = client.http_server_profile.create({
    "name": "secure-logging-profile",
    "description": "HTTPS logging server with TLS 1.2",
    "server": [
        {
            "name": "secure-server",
            "address": "192.168.1.100",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "certificate_profile": "default-cert-profile",
            "http_method": "POST"
        }
    ],
    "tag_registration": True,
    "folder": "Texas"
})
```

### Update an HTTP Server Profile

Updates an existing HTTP server profile.

```python
existing = client.http_server_profile.fetch(
    name="secure-logging-profile",
    folder="Texas"
)
existing.description = "Updated HTTPS logging profile"
existing.server.append({
    "name": "backup-server",
    "address": "192.168.1.101",
    "protocol": "HTTP",
    "port": 8080
})

updated = client.http_server_profile.update(existing)
```

### Delete an HTTP Server Profile

Deletes an HTTP server profile by ID.

```python
client.http_server_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Setting Up Secure Logging

Create HTTP server profiles for secure log forwarding.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Basic HTTP logging profile
client.http_server_profile.create({
    "name": "basic-http-profile",
    "server": [
        {
            "name": "primary-server",
            "address": "192.168.1.100",
            "protocol": "HTTP",
            "port": 8080
        }
    ],
    "folder": "Texas"
})

# Secure HTTPS logging with TLS and tag registration
client.http_server_profile.create({
    "name": "secure-https-profile",
    "description": "Secure logging with TLS 1.2",
    "server": [
        {
            "name": "secure-server",
            "address": "logs.example.com",
            "protocol": "HTTPS",
            "port": 443,
            "tls_version": "1.2",
            "http_method": "POST"
        }
    ],
    "tag_registration": True,
    "folder": "Texas"
})
```

### Filtering HTTP Server Profiles

Use advanced filtering to find specific profiles.

```python
# Exact match with exclusions
filtered = client.http_server_profile.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["Temporary", "Test"]
)

for profile in filtered:
    print(f"Profile: {profile.name}")
    for server in profile.server:
        print(f"  {server.protocol}://{server.address}:{server.port}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    profiles = client.http_server_profile.list()
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")

try:
    profile = client.http_server_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Related Topics

- [HTTP Server Profile Models](../../models/objects/http_server_profiles_models.md)
- [Log Forwarding Profile](log_forwarding_profile.md)
- [Syslog Server Profiles](syslog_server_profiles.md)
