# URL Categories Configuration Object

Manages custom URL category objects for granular policy control in Palo Alto Networks Strata Cloud Manager.

## Class Overview

The `URLCategories` class inherits from `BaseObject` and provides CRUD operations for custom URL categories that can be used in security policies and profiles.

### Methods

| Method     | Description                     | Parameters                          | Return Type                        |
|------------|---------------------------------|-------------------------------------|------------------------------------|
| `create()` | Creates a new URL category      | `data: Dict[str, Any]`              | `URLCategoriesResponseModel`       |
| `get()`    | Retrieves a category by ID      | `object_id: str`                    | `URLCategoriesResponseModel`       |
| `update()` | Updates an existing category    | `profile: URLCategoriesUpdateModel` | `URLCategoriesResponseModel`       |
| `delete()` | Deletes a category              | `object_id: str`                    | `None`                             |
| `list()`   | Lists categories with filtering | `folder: str`, `**filters`          | `List[URLCategoriesResponseModel]` |
| `fetch()`  | Gets category by name           | `name: str`, `folder: str`          | `URLCategoriesResponseModel`       |

### Model Attributes

| Attribute     | Type                      | Required | Default  | Description                               |
|---------------|---------------------------|----------|----------|-------------------------------------------|
| `name`        | str                       | Yes      | None     | Name of URL category                      |
| `id`          | UUID                      | Yes*     | None     | Unique identifier (*response/update only) |
| `list`        | List[str]                 | No       | []       | List of URLs or patterns                  |
| `type`        | URLCategoriesListTypeEnum | No       | URL List | Category type (URL List/Category Match)   |
| `description` | str                       | No       | None     | Category description                      |
| `folder`      | str                       | No**     | None     | Folder location. Max 64 chars             |
| `snippet`     | str                       | No**     | None     | Snippet location. Max 64 chars            |
| `device`      | str                       | No**     | None     | Device location. Max 64 chars             |

\* Only required for response and update models
\** Exactly one container (`folder`, `snippet`, or `device`) must be provided for create operations

### Exceptions

| Exception                    | HTTP Code | Description                     |
|------------------------------|-----------|---------------------------------|
| `InvalidObjectError`         | 400       | Invalid category data or format |
| `MissingQueryParameterError` | 400       | Missing required parameters     |
| `NameNotUniqueError`         | 409       | Category name already exists    |
| `ObjectNotPresentError`      | 404       | Category not found              |
| `ReferenceNotZeroError`      | 409       | Category still referenced       |
| `AuthenticationError`        | 401       | Authentication failed           |
| `ServerError`                | 500       | Internal server error           |

### Basic Configuration

```python
from scm.client import Scm

client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

url_categories = client.url_categories
```

## Methods

### List URL Categories

```python
filtered_categories = client.url_category.list(
    folder='Texas',
    members=['example.com']
)

for category in filtered_categories:
    print(f"Name: {category.name}")
    print(f"Type: {category.type}")
    print(f"URLs: {category.list}")
```

**Filtering responses:**

```python
exact_categories = client.url_category.list(
    folder='Texas',
    exact_match=True
)

combined_filters = client.url_category.list(
    folder='Texas',
    exact_match=True,
    exclude_folders=['All'],
    exclude_snippets=['default'],
    exclude_devices=['DeviceA']
)
```

**Controlling pagination with max_limit:**

```python
client.url_categories.max_limit = 4000

all_categories = client.url_categories.list(folder='Texas')
```

### Fetch a URL Category

```python
category = client.url_category.fetch(name="blocked_sites", folder="Texas")
print(f"Found category: {category.name}")
```

### Create a URL Category

```python
# URL List category
url_list_config = {
    "name": "blocked_sites",
    "type": "URL List",
    "list": ["example.com", "test.com"],
    "description": "Blocked websites list",
    "folder": "Texas"
}
url_list = client.url_category.create(url_list_config)

# Category Match configuration
category_match_config = {
    "name": "social_media",
    "type": "Category Match",
    "list": ["social-networking", "personal-sites-and-blogs"],
    "description": "Social media categories",
    "folder": "Texas"
}
category_match = client.url_category.create(category_match_config)
```

### Update a URL Category

```python
existing_category = client.url_category.fetch(name="blocked_sites", folder="Texas")

existing_category.list.extend(["newsite.com", "anothersite.com"])
existing_category.description = "Updated blocked websites list"

updated_category = client.url_category.update(existing_category)
```

### Delete a URL Category

```python
client.url_category.delete("123e4567-e89b-12d3-a456-426655440000")
```

### Get a URL Category by ID

```python
category_by_id = client.url_category.get(category.id)
print(f"Retrieved category: {category_by_id.name}")
print(f"URL list: {category_by_id.list}")
```

## Use Cases

### Committing Changes

```python
result = client.commit(
    folders=["Texas"],
    description="Updated URL categories",
    sync=True,
    timeout=300
)
print(f"Commit job ID: {result.job_id}")
```

### Monitoring Jobs

```python
job_status = client.get_job_status(result.job_id)
print(f"Job status: {job_status.data[0].status_str}")

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
    category_config = {
        "name": "test_category",
        "type": "URL List",
        "list": ["example.com", "test.com"],
        "folder": "Texas",
        "description": "Test URL category"
    }
    new_category = client.url_category.create(category_config)
    result = client.commit(
        folders=["Texas"],
        description="Added test category",
        sync=True
    )
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

## Related Topics

- [URL Categories Models](../../models/security_services/url_categories_models.md#Overview)
- [Security Services Overview](index.md)
- [API Client](../../client.md)
- [Full Example Scripts](https://github.com/cdot65/pan-scm-sdk/blob/main/examples/scm/config/security/url_categories.py)
