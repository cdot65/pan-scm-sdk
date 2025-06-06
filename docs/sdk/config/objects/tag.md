# Tag Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Tag Model Attributes](#tag-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
   - [Creating Tags](#creating-tags)
   - [Retrieving Tags](#retrieving-tags)
   - [Updating Tags](#updating-tags)
   - [Listing Tags](#listing-tags)
   - [Filtering Responses](#filtering-responses)
   - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
   - [Deleting Tags](#deleting-tags)
7. [Managing Configuration Changes](#managing-configuration-changes)
   - [Performing Commits](#performing-commits)
   - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Tag` class provides functionality to manage tag objects in Palo Alto Networks' Strata Cloud Manager. This class
inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting tags with specific
colors and attributes. In addition, it offers flexible filtering capabilities when listing tags, enabling you to
apply color-based filters, limit results to exact matches of a configuration container, and exclude certain folders,
snippets, or devices as needed.

## Core Methods

| Method     | Description                                     | Parameters                                                                                                              | Return Type              |
|------------|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|--------------------------|
| `create()` | Creates a new tag                               | `data: Dict[str, Any]`                                                                                                  | `TagResponseModel`       |
| `get()`    | Retrieves a tag by ID                           | `object_id: str`                                                                                                        | `TagResponseModel`       |
| `update()` | Updates an existing tag                         | `tag: TagUpdateModel`                                                                                                   | `TagResponseModel`       |
| `delete()` | Deletes a tag                                   | `object_id: str`                                                                                                        | `None`                   |
| `list()`   | Lists tags with comprehensive filtering options | `folder` or `snippet` or `device`, `exact_match`, `exclude_folders`, `exclude_snippets`, `exclude_devices`, `**filters` | `List[TagResponseModel]` |
| `fetch()`  | Gets tag by name and container                  | `name: str` and one container (`folder`, `snippet`, or `device`)                                                        | `TagResponseModel`       |

## Tag Model Attributes

| Attribute  | Type | Required | Description                                   |
|------------|------|----------|-----------------------------------------------|
| `name`     | str  | Yes      | Name of the tag object (max 127 chars)        |
| `id`       | UUID | Yes*     | Unique identifier (*response only)            |
| `color`    | str  | No       | Color from a predefined list                  |
| `comments` | str  | No       | Comments (max 1023 chars)                     |
| `folder`   | str  | Yes**    | Folder location (**one container required**)  |
| `snippet`  | str  | Yes**    | Snippet location (**one container required**) |
| `device`   | str  | Yes**    | Device location (**one container required**)  |

## Exceptions

| Exception                    | HTTP Code | Description                 |
|------------------------------|-----------|-----------------------------|
| `InvalidObjectError`         | 400       | Invalid tag data or format  |
| `MissingQueryParameterError` | 400       | Missing required parameters |
| `NameNotUniqueError`         | 409       | Tag name already exists     |
| `ObjectNotPresentError`      | 404       | Tag not found               |
| `ReferenceNotZeroError`      | 409       | Tag still referenced        |
| `AuthenticationError`        | 401       | Authentication failed       |
| `ServerError`                | 500       | Internal server error       |

## Basic Configuration

The Tag service can be accessed using either the unified client interface (recommended) or the traditional service instantiation.

### Unified Client Interface (Recommended)

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access the Tag service directly through the client
# No need to create a separate Tag instance
tags = client.tag
```

### Traditional Service Instantiation (Legacy)

```python
from scm.client import Scm
from scm.config.objects import Tag

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Tag object explicitly
tags = Tag(client)
```

!!! note
    While both approaches work, the unified client interface is recommended for new development as it provides a more streamlined developer experience and ensures proper token refresh handling across all services.

## Usage Examples

### Creating Tags

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Basic tag configuration
basic_tag = {
    "name": "Production",
    "color": "Red",
    "comments": "Production environment resources",
    "folder": "Texas"
}

# Create basic tag using the unified client interface
basic_tag_obj = client.tag.create(basic_tag)

# Tag with different color
dev_tag = {
    "name": "Development",
    "color": "Blue",
    "comments": "Development environment resources",
    "folder": "Texas"
}

dev_tag_obj = client.tag.create(dev_tag)

# Tag for a specific application
app_tag = {
    "name": "Web-Servers",
    "color": "Green",
    "comments": "Web server resources",
    "folder": "Texas"
}

app_tag_obj = client.tag.create(app_tag)
```

### Retrieving Tags

```python
# Fetch by name and folder using the unified client interface
tag = client.tag.fetch(name="Production", folder="Texas")
print(f"Found tag: {tag.name}")
print(f"Color: {tag.color}")

# Get by ID using the unified client interface
tag_by_id = client.tag.get(tag.id)
print(f"Retrieved tag: {tag_by_id.name}")
```

### Updating Tags

```python
# Fetch existing tag using the unified client interface
existing_tag = client.tag.fetch(name="Production", folder="Texas")

# Update attributes
existing_tag.color = "Azure Blue"
existing_tag.comments = "Updated production environment tag"

# Perform update using the unified client interface
updated_tag = client.tag.update(existing_tag)
```

### Listing Tags

```python
# List tags from a specific folder using the unified client interface
filtered_tags = client.tag.list(
    folder='Texas'
)

# Apply color filters using the unified client interface
filtered_tags = client.tag.list(
    folder='Texas',
    colors=['Red', 'Blue']
)

for tag in filtered_tags:
    print(f"Name: {tag.name}, Color: {tag.color}")
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `colors`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and `exclude_devices`
parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned.
- `exclude_folders (List[str])`: List of folders to exclude.
- `exclude_snippets (List[str])`: List of snippets to exclude.
- `exclude_devices (List[str])`: List of devices to exclude.
- `colors (List[str])`: Filter tags by specified colors.

**Examples:**

```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Only return tags defined exactly in 'Texas' using the unified client interface
exact_tags = client.tag.list(
    folder='Texas',
    exact_match=True
)

for tag in exact_tags:
    print(f"Exact match: {tag.name} in {tag.folder}")

# Exclude all tags from the 'All' folder using the unified client interface
no_all_tags = client.tag.list(
    folder='Texas',
    exclude_folders=['All']
)

for tag in no_all_tags:
    assert tag.folder != 'All'
    print(f"Filtered out 'All': {tag.name}")

# Exclude tags that come from 'default' snippet using the unified client interface
no_default_snippet = client.tag.list(
    folder='Texas',
    exclude_snippets=['default']
)

for tag in no_default_snippet:
    assert tag.snippet != 'default'
    print(f"Filtered out 'default' snippet: {tag.name}")

# Exclude tags associated with 'DeviceA' using the unified client interface
no_deviceA = client.tag.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for tag in no_deviceA:
    assert tag.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {tag.name}")

# Combine exact_match with multiple exclusions and colors using the unified client interface
refined_tags = client.tag.list(
    folder="Texas",
    exact_match=True,
    exclude_folders=["All"],
    exclude_snippets=["default"],
    exclude_devices=["DeviceA"],
    colors=["Red", "Blue"]
)

for tag in refined_tags:
    print(f"Refined filter result: {tag.name} in {tag.folder}, Color: {tag.color}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

```python
from scm.client import ScmClient
from scm.config.objects import Tag

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Two options for setting max_limit:

# Option 1: Use the unified client interface but create a custom Tag instance with max_limit
tag_service = Tag(client, max_limit=4321)
all_tags1 = tag_service.list(folder='Texas')

# Option 2: Use the unified client interface directly
# This will use the default max_limit (2500)
all_tags2 = client.tag.list(folder='Texas')

# Both options will auto-paginate through all available objects.
# The tags are fetched in chunks according to the max_limit.
```

### Deleting Tags

```python
# Delete by ID using the unified client interface
tag_id = "123e4567-e89b-12d3-a456-426655440000"
client.tag.delete(tag_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated tag definitions",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly using the client
# Note: Commits should always be performed on the client object directly, not on service objects
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
from scm.client import ScmClient
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

# Initialize client
client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

try:
    # Create tag configuration
    tag_config = {
        "name": "test_tag",
        "color": "Red",
        "folder": "Texas",
        "comments": "Test tag"
    }

    # Create the tag using the unified client interface
    new_tag = client.tag.create(tag_config)

    # Commit changes directly from the client
    result = client.commit(
        folders=["Texas"],
        description="Added test tag",
        sync=True
    )

    # Check job status directly from the client
    status = client.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid tag data: {e.message}")
except NameNotUniqueError as e:
    print(f"Tag name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Tag not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Tag still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

## Best Practices

1. **Client Usage**
    - Use the unified client interface (`client.tag`) for streamlined code
    - Create a single client instance and reuse it across your application
    - Perform commit operations directly on the client object (`client.commit()`)
    - For custom max_limit settings, create a dedicated service instance if needed

2. **Color Management**
   - Use standard color names from predefined list
   - Maintain consistent color schemes
   - Document color meanings
   - Validate colors before creation
   - Consider color visibility

3. **Container Management**
   - Always specify exactly one container (folder, snippet, or device)
   - Use consistent container names
   - Validate container existence
   - Group related tags

4. **Naming Conventions**
   - Use descriptive names
   - Follow consistent patterns
   - Avoid special characters
   - Document naming standards
   - Consider hierarchical naming

5. **Performance**
   - Create a single client instance and reuse it
   - Use appropriate pagination
   - Implement proper retry logic
   - Monitor API limits
   - Batch operations when possible

6. **Error Handling**
   - Validate input data
   - Handle specific exceptions
   - Log error details
   - Monitor commit status
   - Track job completion

## Full Script Examples

Refer to the [tag.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/tag.py).

## Related Models

- [TagCreateModel](../../models/objects/tag_models.md#Overview)
- [TagUpdateModel](../../models/objects/tag_models.md#Overview)
- [TagResponseModel](../../models/objects/tag_models.md#Overview)
