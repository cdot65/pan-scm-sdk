# Syslog Server Profiles

The `SyslogServerProfile` service manages syslog server profile configurations in Strata Cloud Manager, defining syslog servers that can receive logs from the platform.

## Class Overview

The `SyslogServerProfile` class provides CRUD operations for syslog server profile objects. It is accessed through the `client.syslog_server_profile` attribute on an initialized `ScmClient` instance.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the SyslogServerProfile service
syslog_profiles = client.syslog_server_profile
```

### Key Attributes

| Attribute | Type                    | Required | Description                                       |
|-----------|-------------------------|----------|---------------------------------------------------|
| `name`    | `str`                   | Yes      | Name of the syslog server profile (max 31 chars)  |
| `id`      | `UUID`                  | Yes*     | Unique identifier (*response only)                |
| `server`  | `List[SyslogServerModel]` | Yes    | List of server configurations                     |
| `format`  | `FormatModel`           | No       | Format settings for different log types            |
| `folder`  | `str`                   | Yes**    | Folder location (**one container required)        |
| `snippet` | `str`                   | Yes**    | Snippet location (**one container required)       |
| `device`  | `str`                   | Yes**    | Device location (**one container required)        |

\* Exactly one of `folder`, `snippet`, or `device` is required.

#### Server Configuration Attributes

| Attribute   | Type  | Required | Description                              |
|-------------|-------|----------|------------------------------------------|
| `name`      | `str` | Yes      | Syslog server name                       |
| `server`    | `str` | Yes      | Syslog server address                    |
| `transport` | `str` | Yes      | Transport protocol: `"UDP"` or `"TCP"`   |
| `port`      | `int` | Yes      | Syslog server port (1-65535)             |
| `format`    | `str` | Yes      | Syslog format: `"BSD"` or `"IETF"`      |
| `facility`  | `str` | Yes      | Syslog facility (e.g., `"LOG_USER"`)     |

## Methods

### List Syslog Server Profiles

Retrieves a list of syslog server profiles with optional filtering.

```python
profiles = client.syslog_server_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}")
    for srv in profile.server:
        print(f"  Server: {srv.transport}://{srv.server}:{srv.port}")
```

### Fetch a Syslog Server Profile

Retrieves a single syslog server profile by name and container.

```python
profile = client.syslog_server_profile.fetch(
    name="tcp-logging-profile",
    folder="Texas"
)
print(f"Found profile: {profile.name}")
```

### Create a Syslog Server Profile

Creates a new syslog server profile.

```python
new_profile = client.syslog_server_profile.create({
    "name": "tcp-logging-profile",
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
    "folder": "Texas"
})
```

### Update a Syslog Server Profile

Updates an existing syslog server profile.

```python
existing = client.syslog_server_profile.fetch(
    name="tcp-logging-profile",
    folder="Texas"
)
existing.server[0].server = "192.168.1.200"
existing.format = {
    "traffic": "updated-traffic-format",
    "threat": "updated-threat-format"
}

updated = client.syslog_server_profile.update(existing)
```

### Delete a Syslog Server Profile

Deletes a syslog server profile by ID.

```python
client.syslog_server_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Setting Up UDP and TCP Syslog Servers

Create profiles for different transport protocols.

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Basic UDP syslog profile
client.syslog_server_profile.create({
    "name": "udp-syslog",
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
    "folder": "Texas"
})

# Redundant TCP syslog profile
client.syslog_server_profile.create({
    "name": "tcp-syslog-redundant",
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
    "format": {
        "traffic": "traffic-format",
        "threat": "threat-format"
    },
    "folder": "Texas"
})
```

### Filtering Syslog Profiles

Use advanced filtering to find specific profiles.

```python
# Filter by transport protocol
udp_profiles = client.syslog_server_profile.list(
    folder="Texas",
    transport=["UDP"]
)

# Exact match with exclusions
filtered = client.syslog_server_profile.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"]
)

for profile in filtered:
    print(f"Profile: {profile.name} in {profile.folder}")
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
    profiles = client.syslog_server_profile.list()
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")

try:
    profile = client.syslog_server_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Related Topics

- [Syslog Server Profile Models](../../models/objects/syslog_server_profiles_models.md)
- [Log Forwarding Profile](log_forwarding_profile.md)
- [HTTP Server Profiles](http_server_profiles.md)
