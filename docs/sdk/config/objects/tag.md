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
colors and attributes for resource organization and policy application.

## Core Methods

| Method     | Description                    | Parameters                 | Return Type              |
|------------|--------------------------------|----------------------------|--------------------------|
| `create()` | Creates a new tag              | `data: Dict[str, Any]`     | `TagResponseModel`       |
| `get()`    | Retrieves a tag by ID          | `object_id: str`           | `TagResponseModel`       |
| `update()` | Updates an existing tag        | `tag: TagUpdateModel`      | `TagResponseModel`       |
| `delete()` | Deletes a tag                  | `object_id: str`           | `None`                   |
| `list()`   | Lists tags with filtering      | `folder: str`, `**filters` | `List[TagResponseModel]` |
| `fetch()`  | Gets tag by name and container | `name: str`, `folder: str` | `TagResponseModel`       |

## Tag Model Attributes

| Attribute  | Type | Required | Description                                 |
|------------|------|----------|---------------------------------------------|
| `name`     | str  | Yes      | Name of tag (max 63 chars)                  |
| `id`       | UUID | Yes*     | Unique identifier (*response only)          |
| `color`    | str  | No       | Color from predefined list                  |
| `comments` | str  | No       | Comments (max 1023 chars)                   |
| `folder`   | str  | Yes**    | Folder location (**one container required)  |
| `snippet`  | str  | Yes**    | Snippet location (**one container required) |
| `device`   | str  | Yes**    | Device location (**one container required)  |

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

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Tag

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize Tag object
tags = Tag(client)
```

</div>

## Usage Examples

### Creating Tags

<div class="termy">

<!-- termynal -->

```python
# Basic tag configuration
basic_tag = {
    "name": "Production",
    "color": "Red",
    "comments": "Production environment resources",
    "folder": "Texas"
}

# Create basic tag
basic_tag_obj = tags.create(basic_tag)

# Tag with different color
dev_tag = {
    "name": "Development",
    "color": "Blue",
    "comments": "Development environment resources",
    "folder": "Texas"
}

# Create development tag
dev_tag_obj = tags.create(dev_tag)

# Tag for specific application
app_tag = {
    "name": "Web-Servers",
    "color": "Green",
    "comments": "Web server resources",
    "folder": "Texas"
}

# Create application tag
app_tag_obj = tags.create(app_tag)
```

</div>

### Retrieving Tags

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
tag = tags.fetch(name="Production", folder="Texas")
print(f"Found tag: {tag.name}")
print(f"Color: {tag.color}")

# Get by ID
tag_by_id = tags.get(tag.id)
print(f"Retrieved tag: {tag_by_id.name}")
```

</div>

### Updating Tags

<div class="termy">

<!-- termynal -->

```python
# Fetch existing tag
existing_tag = tags.fetch(name="Production", folder="Texas")

# Update attributes
existing_tag.color = "Azure Blue"
existing_tag.comments = "Updated production environment tag"

# Perform update
updated_tag = tags.update(existing_tag)
```

</div>

### Listing Tags

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_tags = tags.list(
    folder='Texas',
    colors=['Red', 'Blue']
)

# Process results
for tag in filtered_tags:
    print(f"Name: {tag.name}")
    print(f"Color: {tag.color}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "colors": ["Green", "Yellow"]
}

# List with filters as kwargs
filtered_tags = tags.list(**list_params)
```

</div>

### Deleting Tags

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
tag_id = "123e4567-e89b-12d3-a456-426655440000"
tags.delete(tag_id)
```

</div>

## Managing Configuration Changes

### Performing Commits

<div class="termy">

<!-- termynal -->

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated tag definitions",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = tags.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = tags.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = tags.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

</div>

## Error Handling

<div class="termy">

<!-- termynal -->

```python
from scm.exceptions import (
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
    ReferenceNotZeroError
)

try:
    # Create tag configuration
    tag_config = {
        "name": "test_tag",
        "color": "Red",
        "folder": "Texas",
        "comments": "Test tag"
    }

    # Create the tag
    new_tag = tags.create(tag_config)

    # Commit changes
    result = tags.commit(
        folders=["Texas"],
        description="Added test tag",
        sync=True
    )

    # Check job status
    status = tags.get_job_status(result.job_id)

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

</div>

## Best Practices

1. **Color Management**
    - Use standard color names from predefined list
    - Maintain consistent color schemes
    - Document color meanings
    - Validate colors before creation
    - Consider color visibility

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related tags

3. **Naming Conventions**
    - Use descriptive names
    - Follow consistent patterns
    - Avoid special characters
    - Document naming standards
    - Consider hierarchical naming

4. **Performance**
    - Cache frequently used tags
    - Use appropriate pagination
    - Implement proper retry logic
    - Monitor API limits
    - Batch operations when possible

5. **Error Handling**
    - Validate input data
    - Handle specific exceptions
    - Log error details
    - Monitor commit status
    - Track job completion

## Full Script Examples

Refer to
the [tag.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/objects/tag.py).

## Related Models

- [TagCreateModel](../../models/objects/tag_models.md#Overview)
- [TagUpdateModel](../../models/objects/tag_models.md#Overview)
- [TagResponseModel](../../models/objects/tag_models.md#Overview)