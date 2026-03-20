# Agent Versions Configuration Object

Provides read-only access to available GlobalProtect agent version information in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `AgentVersions` class inherits from `BaseObject` and offers methods for listing and retrieving available GlobalProtect agent versions. This is a read-only resource supporting only list and fetch operations.

### Methods

| Method    | Description                    | Parameters   | Return Type |
|-----------|--------------------------------|--------------|-------------|
| `list()`  | Lists available agent versions | `**filters`  | `List[str]` |
| `fetch()` | Retrieves a specific version   | `version: str` | `str`     |

### Model Attributes

| Attribute        | Type      | Required | Default | Description                                    |
|------------------|-----------|----------|---------|------------------------------------------------|
| `agent_versions` | List[str] | Yes      | None    | List of available GlobalProtect agent versions |

### Exceptions

| Exception                    | HTTP Code | Description                       |
|------------------------------|-----------|-----------------------------------|
| `InvalidObjectError`         | 400       | Invalid configuration or parameters |
| `MissingQueryParameterError` | 400       | Missing required parameters       |
| `ObjectNotPresentError`      | 404       | Requested agent version not found |
| `AuthenticationError`        | 401       | Authentication failed             |
| `ServerError`                | 500       | Internal server error             |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

agent_versions = client.agent_version
```

## Methods

### List Agent Versions

```python
versions = client.agent_version.list()

print(f"Found {len(versions)} GlobalProtect agent versions:")
for version in versions:
    print(f"- {version}")
```

**Filtering responses:**

```python
# Filter versions by substring
filtered_versions = client.agent_version.list(version="5.2")

# Filter versions by prefix
prefix_versions = client.agent_version.list(prefix="5.3")

# Combine filters
combined_versions = client.agent_version.list(
    version="5.2",
    prefix="5.2.8"
)
```

**Controlling pagination with max_limit:**

```python
client.agent_version.max_limit = 1000

all_versions = client.agent_version.list()
```

### Fetch an Agent Version

```python
from scm.exceptions import InvalidObjectError

try:
    version = client.agent_version.fetch("5.3.0")
    print(f"Found version: {version}")
except InvalidObjectError:
    print("Version not found")
```

## Error Handling

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    ObjectNotPresentError
)

try:
    version = client.agent_version.fetch("5.3.0")
    print(f"Found version: {version}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid object error: {e.message}")
```

## Related Topics

- [Agent Version Models](../../models/mobile_agent/agent_versions_models.md#Overview)
- [Mobile Agent Overview](index.md)
- [API Client](../../client.md)
