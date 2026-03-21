# Log Forwarding Profile

The `LogForwardingProfile` service manages log forwarding profile configurations in Strata Cloud Manager, defining how logs are handled and forwarded to external systems with configurable match criteria for different log types.

## Class Overview

The `LogForwardingProfile` class provides CRUD operations for log forwarding profile objects. It is accessed through the `client.log_forwarding_profile` attribute on an initialized `Scm` instance.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the LogForwardingProfile service
log_profiles = client.log_forwarding_profile
```

### Key Attributes

| Attribute                      | Type                  | Required | Description                                              |
|--------------------------------|-----------------------|----------|----------------------------------------------------------|
| `name`                         | `str`                 | Yes      | Name of the profile (max 63 chars)                       |
| `id`                           | `UUID`                | Yes*     | Unique identifier (*response only)                       |
| `description`                  | `str`                 | No       | Profile description (max 255 chars)                      |
| `match_list`                   | `List[MatchListItem]` | No       | List of match profile configurations                     |
| `enhanced_application_logging` | `bool`                | No       | Flag for enhanced application logging                    |
| `folder`                       | `str`                 | Yes**    | Folder location (**one container required)               |
| `snippet`                      | `str`                 | Yes**    | Snippet location (**one container required)              |
| `device`                       | `str`                 | Yes**    | Device location (**one container required)               |

\* Exactly one of `folder`, `snippet`, or `device` is required.

#### MatchListItem Attributes

| Attribute          | Type        | Required | Description                                |
|--------------------|-------------|----------|--------------------------------------------|
| `name`             | `str`       | Yes      | Name of the match profile (max 63 chars)   |
| `log_type`         | `str`       | Yes      | Log type (traffic, threat, wildfire, etc.)  |
| `filter`           | `str`       | No       | Filter match criteria                      |
| `send_http`        | `List[str]` | No       | HTTP server profiles for forwarding        |
| `send_syslog`      | `List[str]` | No       | Syslog server profiles for forwarding      |
| `send_to_panorama` | `bool`      | No       | Flag to send logs to Panorama              |

## Methods

### List Log Forwarding Profiles

Retrieves a list of log forwarding profiles with optional filtering.

```python
profiles = client.log_forwarding_profile.list(folder="Texas")

for profile in profiles:
    print(f"Name: {profile.name}")
    if profile.match_list:
        for match in profile.match_list:
            print(f"  Log Type: {match.log_type}")
```

### Fetch a Log Forwarding Profile

Retrieves a single log forwarding profile by name and container.

```python
profile = client.log_forwarding_profile.fetch(
    name="security-logs-profile",
    folder="Texas"
)
print(f"Found profile: {profile.name}")
```

### Create a Log Forwarding Profile

Creates a new log forwarding profile.

```python
new_profile = client.log_forwarding_profile.create({
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
    "folder": "Texas"
})
```

### Update a Log Forwarding Profile

Updates an existing log forwarding profile.

```python
existing = client.log_forwarding_profile.fetch(
    name="security-logs-profile",
    folder="Texas"
)
existing.description = "Updated security log forwarding profile"

if existing.match_list is None:
    existing.match_list = []

existing.match_list.append({
    "name": "url-logs",
    "log_type": "url",
    "filter": "category eq social-networking",
    "send_syslog": ["url-syslog-profile"]
})

updated = client.log_forwarding_profile.update(existing)
```

### Delete a Log Forwarding Profile

Deletes a log forwarding profile by ID.

```python
client.log_forwarding_profile.delete("123e4567-e89b-12d3-a456-426655440000")
```

## Use Cases

### Setting Up Multi-Destination Logging

Forward different log types to appropriate destinations.

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

client.log_forwarding_profile.create({
    "name": "comprehensive-logging",
    "description": "Forward all critical logs to multiple destinations",
    "match_list": [
        {
            "name": "critical-threats",
            "log_type": "threat",
            "filter": "severity eq critical",
            "send_http": ["security-http-profile"],
            "send_syslog": ["security-syslog-profile"]
        },
        {
            "name": "traffic-logs",
            "log_type": "traffic",
            "filter": "addr.src in 192.168.0.0/24",
            "send_http": ["http-profile-1"]
        },
        {
            "name": "malware-logs",
            "log_type": "wildfire",
            "filter": "verdict eq malware",
            "send_http": ["malware-http-profile"]
        }
    ],
    "folder": "Texas"
})
```

### Filtering Log Forwarding Profiles

Use filtering to find profiles handling specific log types.

```python
# Filter by log type
threat_profiles = client.log_forwarding_profile.list(
    folder="Texas",
    log_type="threat"
)

# Filter with multiple log types
security_profiles = client.log_forwarding_profile.list(
    folder="Texas",
    log_types=["threat", "wildfire"]
)

# Exact match with exclusions
filtered = client.log_forwarding_profile.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["Temporary", "Test"]
)
```

## Error Handling

```python
from scm.client import Scm
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    profiles = client.log_forwarding_profile.list()
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")

try:
    profile = client.log_forwarding_profile.fetch(name="my-profile", folder="")
except MissingQueryParameterError as e:
    print(f"Missing parameter error: {e.message}")
```

## Related Topics

- [Log Forwarding Profile Models](../../models/objects/log_forwarding_profile_models.md)
- [HTTP Server Profiles](http_server_profiles.md)
- [Syslog Server Profiles](syslog_server_profiles.md)
