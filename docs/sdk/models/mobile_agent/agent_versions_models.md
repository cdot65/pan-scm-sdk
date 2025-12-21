# GlobalProtect Agent Versions Models

## Table of Contents

1. [Overview](#overview)
2. [Model Attributes](#model-attributes)
3. [Usage Examples](#usage-examples)
4. [Error Handling](#error-handling)
5. [Related Documentation](#related-documentation)

## Overview {#Overview}

The `AgentVersions` models provide data structures for GlobalProtect agent version information in the Strata Cloud Manager API. These are read-only models used to represent the available GlobalProtect agent versions.

### Models

The module provides the following Pydantic models:

- `AgentVersionsModel`: Used to represent the collection of available agent versions
- `AgentVersionModel`: Represents an individual agent version with additional metadata

All models use `extra="forbid"` configuration, which rejects any fields not explicitly defined in the model.

## Model Attributes

### AgentVersionsModel

| Attribute       | Type      | Required | Default | Description                                    |
|-----------------|-----------|----------|---------|------------------------------------------------|
| `agent_versions`| List[str] | Yes      | None    | List of available GlobalProtect agent versions |

### AgentVersionModel

| Attribute        | Type | Required | Default | Description                                        |
|------------------|------|----------|---------|----------------------------------------------------|
| `version`        | str  | Yes      | None    | The version string of the GlobalProtect agent      |
| `release_date`   | str  | No       | None    | The release date of the version (if available)     |
| `is_recommended` | bool | No       | None    | Whether this version is recommended (if available) |

## Usage Examples

### Listing Agent Versions

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get agent versions using the service
versions = client.agent_version.list()

# Access the list of versions
for version in versions:
    print(f"Available version: {version}")
```

### Fetching a Specific Version

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Fetch a specific version by exact match
    version = client.agent_version.fetch("5.3.0")
    print(f"Found version: {version}")
except InvalidObjectError:
    print("Version not found")
```

### Filtering Versions

```python
# Filter versions by substring
filtered_versions = client.agent_version.list(version="5.2")
print(f"Found {len(filtered_versions)} versions containing '5.2'")

# Filter versions by prefix
prefix_versions = client.agent_version.list(prefix="5.3")
print(f"Found {len(prefix_versions)} versions starting with '5.3'")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.exceptions import InvalidObjectError, MissingQueryParameterError

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Fetch a specific version
    version = client.agent_version.fetch("5.3.0")
    print(f"Found version: {version}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
except InvalidObjectError as e:
    print(f"Version not found: {e.message}")
```

## Related Documentation

- [Agent Versions Configuration](../../config/mobile_agent/agent_versions.md) - Working with agent versions API
