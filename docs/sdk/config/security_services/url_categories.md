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
    - [Controlling Pagination with max_limit](#controlling-pagination-with-max_limit)
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

```python
from scm.client import Scm

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access URL categories directly through the client
# No need to initialize a separate URLCategories object
```

## Usage Examples

### Creating URL Categories

```python
# URL List category configuration
url_list_config = {
    "name": "blocked_sites",
    "type": "URL List",
    "list": ["example.com", "test.com"],
    "description": "Blocked websites list",
    "folder": "Texas"
}

# Create URL List category using the client
url_list = client.url_category.create(url_list_config)

# Category Match configuration
category_match_config = {
    "name": "social_media",
    "type": "Category Match",
    "list": ["social-networking", "personal-sites-and-blogs"],
    "description": "Social media categories",
    "folder": "Texas"
}

# Create Category Match category
category_match = client.url_category.create(category_match_config)
```

### Retrieving URL Categories

```python
# Fetch by name and folder
category = client.url_category.fetch(name="blocked_sites", folder="Texas")
print(f"Found category: {category.name}")

# Get by ID
category_by_id = client.url_category.get(category.id)
print(f"Retrieved category: {category_by_id.name}")
print(f"URL list: {category_by_id.list}")
```

### Updating URL Categories

```python
# Fetch existing category
existing_category = client.url_category.fetch(name="blocked_sites", folder="Texas")

# Update URL list
existing_category.list.extend(["newsite.com", "anothersite.com"])
existing_category.description = "Updated blocked websites list"

# Perform update
updated_category = client.url_category.update(existing_category)
```

### Listing URL Categories

```python
# List with direct filter parameters
filtered_categories = client.url_category.list(
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
filtered_categories = client.url_category.list(**list_params)
```

### Filtering Responses

The `list()` method supports additional parameters to refine your query results even further. Alongside basic filters
(like `types`, `values`, and `tags`), you can leverage the `exact_match`, `exclude_folders`, `exclude_snippets`, and
`exclude_devices` parameters to control which objects are included or excluded after the initial API response is fetched.

**Parameters:**

- `exact_match (bool)`: When `True`, only objects defined exactly in the specified container (`folder`, `snippet`, or `device`) are returned.
- `exclude_folders (List[str])`: Provide a list of folder names to exclude.
- `exclude_snippets (List[str])`: Provide a list of snippet values to exclude.
- `exclude_devices (List[str])`: Provide a list of device values to exclude.

**Examples:**

```python
# Only return url_category defined exactly in 'Texas'
exact_url_categories = client.url_category.list(
    folder='Texas',
    exact_match=True
)

for app in exact_url_categories:
    print(f"Exact match: {app.name} in {app.folder}")

# Exclude all url_categories from the 'All' folder
no_all_url_categories = client.url_category.list(
    folder='Texas',
    exclude_folders=['All']
)

for app in no_all_url_categories:
    assert app.folder != 'All'
    print(f"Filtered out 'All': {app.name}")

# Exclude url_categories that come from 'default' snippet
no_default_snippet = client.url_category.list(
    folder='Texas',
    exclude_snippets=['default']
)

for app in no_default_snippet:
    assert app.snippet != 'default'
    print(f"Filtered out 'default' snippet: {app.name}")

# Exclude url_categories associated with 'DeviceA'
no_deviceA = client.url_category.list(
    folder='Texas',
    exclude_devices=['DeviceA']
)

for app in no_deviceA:
    assert app.device != 'DeviceA'
    print(f"Filtered out 'DeviceA': {app.name}")

# Combine exact_match with multiple exclusions
combined_filters = client.url_category.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)

for app in combined_filters:
    print(f"Combined filters result: {app.name} in {app.folder}")
```

### Controlling Pagination with max_limit

The SDK supports pagination through the `max_limit` parameter, which defines how many objects are retrieved per API call. By default, `max_limit` is set to 2500. The API itself imposes a maximum allowed value of 5000. If you set `max_limit` higher than 5000, it will be capped to the API's maximum. The `list()` method will continue to iterate through all objects until all results have been retrieved. Adjusting `max_limit` can help manage retrieval performance and memory usage when working with large datasets.

```python
# Initialize the client with a custom max_limit for URL categories
# This will retrieve up to 4321 objects per API call, up to the API limit of 5000.
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    url_categories_max_limit=4321
)

# Now when we call list(), it will use the specified max_limit for each request
# while auto-paginating through all available objects.
all_categories = client.url_category.list(folder='Texas')

# 'all_categories' contains all objects from 'Texas', fetched in chunks of up to 4321 at a time.
```

### Deleting URL Categories

```python
# Delete by ID
category_id = "123e4567-e89b-12d3-a456-426655440000"
client.url_category.delete(category_id)
```

## Managing Configuration Changes

### Performing Commits

```python
# Prepare commit parameters
commit_params = {
    "folders": ["Texas"],
    "description": "Updated URL categories",
    "sync": True,
    "timeout": 300  # 5 minute timeout
}

# Commit the changes directly using the client
result = client.commit(**commit_params)

print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
# Get status of specific job using the client
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

# List recent jobs using the client
recent_jobs = client.list_jobs(limit=10)
for job in recent_jobs.data:
    print(f"Job {job.id}: {job.type_str} - {job.status_str}")
```

## Error Handling

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

    # Create the category using the client
    new_category = client.url_category.create(category_config)

    # Commit changes using the client
    result = client.commit(
        folders=["Texas"],
        description="Added test category",
        sync=True
    )

    # Check job status using the client
    status = client.get_job_status(result.job_id)

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

3. **Client Usage**
    - Use the unified client interface (`client.url_category`) for simpler code
    - Perform commits directly on the client (`client.commit()`)
    - Monitor jobs using client methods (`client.get_job_status()`, `client.list_jobs()`)
    - Initialize the client once and reuse across different object types

4. **Category Types**
    - Choose appropriate type (URL List vs Category Match)
    - Validate category match patterns
    - Consider URL resolution impact
    - Document type selection rationale

5. **Performance**
    - Use appropriate pagination
    - Cache frequently accessed categories
    - Implement proper retry logic
    - Monitor URL resolution times

6. **Security**
    - Follow least privilege principle
    - Validate input URLs
    - Use secure connection settings
    - Monitor category usage

## Full Script Examples

Refer to
the [url_categories.py example](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/url_categories.py).

## Related Models

- [URLCategoriesCreateModel](../../models/security_services/url_categories_models.md)
- [URLCategoriesUpdateModel](../../models/security_services/url_categories_models.md)
- [URLCategoriesResponseModel](../../models/security_services/url_categories_models.md)
