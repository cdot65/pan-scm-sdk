# GlobalProtect Agent Versions Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Model Attributes](#model-attributes)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Related Documentation](#related-documentation)

## Overview {#Overview}
<span id="overview"></span>

The `AgentVersions` models provide data structures for GlobalProtect agent version information in the Strata Cloud Manager API. These are read-only models used to represent the available GlobalProtect agent versions.

## Model Types

There are two primary models for handling GlobalProtect agent version data:

- **AgentVersionsModel**: Used to represent the collection of available agent versions
- **AgentVersionModel**: Represents an individual agent version with additional metadata

## Model Attributes

### AgentVersionsModel

| Attribute       | Type        | Required | Description                                        |
|-----------------|-------------|----------|----------------------------------------------------|
| `agent_versions`| `List[str]` | Yes      | List of available GlobalProtect agent versions     |

### AgentVersionModel

| Attribute        | Type   | Required | Description                                        |
|------------------|--------|----------|----------------------------------------------------|
| `version`        | `str`  | Yes      | The version string of the GlobalProtect agent      |
| `release_date`   | `str`  | No       | The release date of the version (if available)     |
| `is_recommended` | `bool` | No       | Whether this version is recommended (if available) |

## Usage Examples

### Reading Agent Versions

```python
from scm.client import ScmClient
from scm.models.mobile_agent.agent_versions import AgentVersionsModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get the API response
response = client.get("/mobile-agent/v1/agent-versions")

# Convert the API response to AgentVersionsModel
agent_versions = AgentVersionsModel(**response)

# Access the list of versions
for version in agent_versions.agent_versions:
    print(f"Available version: {version}")
```

### Using the Model with the Service

```python
from scm.client import ScmClient
from scm.models.mobile_agent.agent_versions import AgentVersionModel

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Get agent versions using the service
versions = client.agent_version.list()

# Create AgentVersionModel instances for versions with additional metadata
version_objects = []
for ver in versions:
    # This is hypothetical - in a real scenario,
    # you might have additional metadata from elsewhere
    metadata = {
        "version": ver,
        "release_date": "2023-06-15",  # Example date
        "is_recommended": ver == "5.3.0"  # Example logic
    }
    version_obj = AgentVersionModel(**metadata)
    version_objects.append(version_obj)

# Use the objects
for v_obj in version_objects:
    recommendation = "RECOMMENDED" if v_obj.is_recommended else ""
    print(f"GlobalProtect {v_obj.version} (Released: {v_obj.release_date}) {recommendation}")
```

## Error Handling

```python
from scm.client import ScmClient
from scm.models.mobile_agent.agent_versions import AgentVersionsModel
from pydantic import ValidationError

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Get a response from the API
    response = client.get("/mobile-agent/v1/agent-versions")

    # Validate the response against the model
    versions_model = AgentVersionsModel(**response)

    # Access the validated data
    print(f"Found {len(versions_model.agent_versions)} versions")

except ValidationError as e:
    print(f"Response validation failed: {e}")
```

## Related Documentation

- [Agent Versions Configuration](../../config/mobile_agent/agent_versions.md) - Working with agent versions API
