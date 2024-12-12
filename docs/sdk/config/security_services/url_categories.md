# URL Categories Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [URL Category Model Attributes](#url-category-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating URL Categories](#creating-url-categories)
    - [Retrieving URL Categories](#retrieving-url-categories)
    - [Updating URL Categories](#updating-url-categories)
    - [Listing URL Categories](#listing-url-categories)
    - [Filtering Responses](#filtering-responses)
    - [Deleting URL Categories](#deleting-url-categories)
7. [Managing Configuration Changes](#managing-configuration-changes)
    - [Performing Commits](#performing-commits)
    - [Monitoring Jobs](#monitoring-jobs)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `URLCategories` class provides functionality to manage URL category objects in Palo Alto Networks' Strata Cloud
Manager. This class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting
custom URL categories that can be used in security policies and profiles.

## Core Methods

| Method     | Description                     | Parameters                          | Return Type                        |
|------------|---------------------------------|-------------------------------------|------------------------------------|
| `create()` | Creates a new URL category      | `data: Dict[str, Any]`              | `URLCategoriesResponseModel`       |
| `get()`    | Retrieves a category by ID      | `object_id: str`                    | `URLCategoriesResponseModel`       |
| `update()` | Updates an existing category    | `profile: URLCategoriesUpdateModel` | `URLCategoriesResponseModel`       |
| `delete()` | Deletes a category              | `object_id: str`                    | `None`                             |
| `list()`   | Lists categories with filtering | `folder: str`, `**filters`          | `List[URLCategoriesResponseModel]` |
| `fetch()`  | Gets category by name           | `name: str`, `folder: str`          | `URLCategoriesResponseModel`       |

## URL Category Model Attributes

| Attribute     | Type      | Required | Description                                 |
|---------------|-----------|----------|---------------------------------------------|
| `name`        | str       | Yes      | Name of URL category                        |
| `id`          | UUID      | Yes*     | Unique identifier (*response only)          |
| `list`        | List[str] | Yes      | List of URLs or patterns                    |
| `type`        | Enum      | No       | Category type (URL List/Category Match)     |
| `description` | str       | No       | Category description                        |
| `folder`      | str       | Yes**    | Folder location (**one container required)  |
| `snippet`     | str       | Yes**    | Snippet location (**one container required) |
| `device`      | str       | Yes**    | Device location (**one container required)  |

## Exceptions

| Exception                    | HTTP Code | Description                     |
|------------------------------|-----------|---------------------------------|
| `InvalidObjectError`         | 400       | Invalid category data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters     |
| `NameNotUniqueError`         | 409       | Category name already exists    |
| `ObjectNotPresentError`      | 404       | Category not found              |
| `ReferenceNotZeroError`      | 409       | Category still referenced       |
| `AuthenticationError`        | 401       | Authentication failed           |
| `ServerError`                | 500       | Internal server error           |

## Basic Configuration

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import URLCategories

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Initialize URLCategories object
url_categories = URLCategories(client)
```

</div>

## Usage Examples

### Creating URL Categories

<div class="termy">

<!-- termynal -->

```python
# URL List category configuration
url_list_config = {
    "name": "blocked_sites",
    "type": "URL List",
    "list": ["example.com", "test.com"],
    "description": "Blocked websites list",
    "folder": "Texas"
}

# Create URL List category
url_list = url_categories.create(url_list_config)

# Category Match configuration
category_match_config = {
    "name": "social_media",
    "type": "Category Match",
    "list": ["social-networking", "personal-sites-and-blogs"],
    "description": "Social media categories",
    "folder": "Texas"
}

# Create Category Match category
category_match = url_categories.create(category_match_config)
```

</div>

### Retrieving URL Categories

<div class="termy">

<!-- termynal -->

```python
# Fetch by name and folder
category = url_categories.fetch(name="blocked_sites", folder="Texas")
print(f"Found category: {category.name}")

# Get by ID
category_by_id = url_categories.get(category.id)
print(f"Retrieved category: {category_by_id.name}")
print(f"URL list: {category_by_id.list}")
```

</div>

### Updating URL Categories

<div class="termy">

<!-- termynal -->

```python
# Fetch existing category
existing_category = url_categories.fetch(name="blocked_sites", folder="Texas")

# Update URL list
existing_category.list.extend(["newsite.com", "anothersite.com"])
existing_category.description = "Updated blocked websites list"

# Perform update
updated_category = url_categories.update(existing_category)
```

</div>

### Listing URL Categories

<div class="termy">

<!-- termynal -->

```python
# List with direct filter parameters
filtered_categories = url_categories.list(
    folder='Texas',
    members=['example.com']
)

# Process results
for category in filtered_categories:
    print(f"Name: {category.name}")
    print(f"Type: {category.type}")
    print(f"URLs: {category.list}")

# Define filter parameters as dictionary
list_params = {
    "folder": "Texas",
    "members": ["social-networking"]
}

# List with filters as kwargs
filtered_categories = url_categories.list(**list_params)
```

</div>


### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**
- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned. Inherited or propagated objects are filtered out.
- `exclude_folders (List[str])`: Provide a list of folder names that you do not want included in the results.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude from the results.
- `exclude_devices (List[str])`: Provide a list of device values to exclude from the results.

**Examples:**

<div class="termy">

<!-- termynal -->

```python
# Only return url_categories defined exactly in 'Texas'
exact_url_categories = url_categories.list(
  folder='Texas',
  exact_match=True
)

for app in exact_url_categories:
  print(f"Exact match: {app.name} in {app.folder}")

# Exclude all url_categories from the 'All' folder
no_all_url_categories = url_categories.list(
  folder='Texas',
  exclude_folders=['All']
)

for app in no_all_url_categories:
  assert app.folder != 'All'
  print(f"Filtered out 'All': {app.name}")

# Exclude url_categories that come from 'default' snippet
no_default_snippet = url_categories.list(
  folder='Texas',
  exclude_snippets=['default']
)

for app in no_default_snippet:
  assert app.snippet != 'default'
  print(f"Filtered out 'default' snippet: {app.name}")

# Exclude url_categories associated with 'DeviceA'
no_deviceA = url_categories.list(
  folder='Texas',
  exclude_devices=['DeviceA']
)

for app in no_deviceA:
  assert app.device != 'DeviceA'
  print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = url_categories.list(
  folder='Texas',
  exact_match=True,
  exclude_folders=['All'],
  exclude_snippets=['default'],
  exclude_devices=['DeviceA']
)

for app in combined_filters:
  print(f"Combined filters result: {app.name} in {app.folder}")
```

### Deleting URL Categories

<div class="termy">

<!-- termynal -->

```python
# Delete by ID
category_id = "123e4567-e89b-12d3-a456-426655440000"
url_categories.delete(category_id)
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
    "description": "Updated URL categories",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes
result = url_categories.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

</div>

### Monitoring Jobs

<div class="termy">

<!-- termynal -->

```python
# Get status of specific job
job_status = url_categories.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs
recent_jobs = url_categories.list_jobs(limit=10)
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
    # Create category configuration
    category_config = {
        "name": "test_category",
        "type": "URL List",
        "list": ["example.com", "test.com"],
        "folder": "Texas",
        "description": "Test URL category"
    }

    # Create the category
    new_category = url_categories.create(category_config)

    # Commit changes
    result = url_categories.commit(
        folders=["Texas"],
        description="Added test category",
        sync=True
    )

    # Check job status
    status = url_categories.get_job_status(result.job_id)

except InvalidObjectError as e:
    print(f"Invalid category data: {e.message}")
except NameNotUniqueError as e:
    print(f"Category name already exists: {e.message}")
except ObjectNotPresentError as e:
    print(f"Category not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Category still in use: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing parameter: {e.message}")
```

</div>

## Best Practices

1. **URL List Management**
    - Use descriptive category names
    - Group related URLs together
    - Validate URL patterns before adding
    - Keep lists manageable in size
    - Document category purposes

2. **Container Management**
    - Always specify exactly one container (folder, snippet, or device)
    - Use consistent container names
    - Validate container existence
    - Group related categories

3. **Category Types**
    - Choose appropriate type (URL List vs Category Match)
    - Validate category match patterns
    - Consider URL resolution impact
    - Document type selection rationale

4. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed categories
    - Implement proper retry logic
    - Monitor URL resolution times

5. **Security**
    - Follow least privilege principle
    - Validate input URLs
    - Use secure connection settings
    - Monitor category usage

## Full Script Examples

Refer to
the [url_categories.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/url_categories.py).

## Related Models

- [URLCategoriesCreateModel](../../models/security_services/url_categories_models.md#Overview)
- [URLCategoriesUpdateModel](../../models/security_services/url_categories_models.md#Overview)
- [URLCategoriesResponseModel](../../models/security_services/url_categories_models.md#Overview)