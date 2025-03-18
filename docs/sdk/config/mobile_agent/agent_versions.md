# Agent Versions Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Agent Version Model Attributes](#agent-version-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Listing Agent Versions](#listing-agent-versions)
    - [Fetching Specific Versions](#fetching-specific-versions)
    - [Filtering Versions](#filtering-versions)
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Related Models](#related-models)

## Overview

The `AgentVersions` class provides read-only access to GlobalProtect agent version information in Palo Alto Networks' Strata Cloud Manager. This class inherits from `BaseObject` and offers methods for listing and retrieving available GlobalProtect agent versions. This is a read-only resource, supporting only listing and fetching operations.

## Core Methods

| Method     | Description                        | Parameters                        | Return Type     |
|------------|------------------------------------|-----------------------------------|-----------------|
| `list()`   | Lists available agent versions     | `**filters`                       | `List[str]`     |
| `fetch()`  | Retrieves a specific version       | `version: str`                    | `str`           |

## Agent Version Model Attributes

| Attribute       | Type      | Description                                   |
|-----------------|-----------|-----------------------------------------------|
| `agent_versions`| List[str] | List of available GlobalProtect agent versions|

## Exceptions

| Exception                    | HTTP Code | Description                                    |
|------------------------------|-----------|------------------------------------------------|
| `InvalidObjectError`         | 400       | Invalid configuration or parameters            |
| `MissingQueryParameterError` | 400       | Missing required parameters                    |
| `ObjectNotPresentError`      | 404       | Requested agent version not found              |
| `AuthenticationError`        | 401       | Authentication failed                          |
| `ServerError`                | 500       | Internal server error                          |

## Basic Configuration

The AgentVersions service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the AgentVersions service directly through the client
agent_versions = client.agent_version
```

</div>

### Traditional Service Instantiation (Legacy)

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.mobile_agent.agent_versions import AgentVersions

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize AgentVersions object explicitly
agent_versions = AgentVersions(client)
```

</div>

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Listing Agent Versions

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# List all available GlobalProtect agent versions
versions = client.agent_version.list()

# Print the versions
print(f"Found {len(versions)} GlobalProtect agent versions:")
for version in versions:
   print(f"- {version}")
```

</div>

### Fetching Specific Versions

<div class="termy">

<!-- termynal -->

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
    # Fetch a specific version
    version = client.agent_version.fetch("5.3.0")
    print(f"Found version: {version}")
except InvalidObjectError:
    print("Version not found")
```

</div>

### Filtering Versions

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Filter versions by substring
filtered_versions = client.agent_version.list(version="5.2")
print(f"Found {len(filtered_versions)} versions containing '5.2':")
for version in filtered_versions:
   print(f"- {version}")

# Filter versions by prefix
prefix_versions = client.agent_version.list(prefix="5.3")
print(f"Found {len(prefix_versions)} versions starting with '5.3':")
for version in prefix_versions:
   print(f"- {version}")

# Use multiple filters
combined_versions = client.agent_version.list(
    version="5.2",
    prefix="5.2.8"
)
print(f"Found {len(combined_versions)} versions matching both filters:")
for version in combined_versions:
   print(f"- {version}")
```

</div>

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 200. The API itself imposes a maximum allowed value of 1000. If you set `max_limit` higher than 1000, it will be capped to the API's maximum.

**Example:**

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.config.mobile_agent.agent_versions import AgentVersions

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom AgentVersions instance with max_limit
agent_versions_service = AgentVersions(client, max_limit=1000)
all_versions1 = agent_versions_service.list()

# Option 2: Use the unified client interface directly
# This will use the default max_limit (200)
all_versions2 = client.agent_version.list()

# Both options will retrieve all available versions,
# but the first one will do it in larger batches.
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.client import ScmClient
from scm.exceptions import (
   InvalidObjectError,
   MissingQueryParameterError,
   ObjectNotPresentError
)

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
   print(f"Invalid object error: {e.message}")
except Exception as e:
   print(f"Unexpected error: {str(e)}")
```

</div>

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.agent_version`) for streamlined code
    - Create a single client instance and reuse it across your application
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Performance**
    - Use filtering to reduce the amount of data processed
    - Implement specific version matching in fetch operations
    - Cache version information when appropriate

3. **Error Handling**
    - Implement comprehensive error handling for all operations
    - Handle specific exceptions before generic ones
    - Log error details for troubleshooting

## Related Models

- [AgentVersionsModel](../../models/mobile_agent/agent_versions_models.md#Overview)
- [AgentVersionModel](../../models/mobile_agent/agent_versions_models.md#Overview)
