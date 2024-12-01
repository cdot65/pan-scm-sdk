# URL Categories Configuration Object

The `URLCategories` class provides functionality to manage URL category objects in Palo Alto Networks' Strata Cloud
Manager.
URL categories allow you to define custom lists of URLs and categories for use in security policies and profiles.

## Overview

URL Categories in Strata Cloud Manager allow you to:

- Create custom URL categories with lists of URLs
- Define category match patterns
- Organize categories within folders, snippets, or devices
- Apply filtering and management capabilities

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during URL category
management.

## Methods

| Method     | Description                                  |
|------------|----------------------------------------------|
| `create()` | Creates a new URL category                   |
| `get()`    | Retrieves a URL category by ID               |
| `update()` | Updates an existing URL category             |
| `delete()` | Deletes a URL category                       |
| `list()`   | Lists URL categories with optional filtering |
| `fetch()`  | Retrieves a single URL category by name      |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when URL category data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when a URL category doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when URL category names conflict
- `NameNotUniqueError`: Raised when creating duplicate category names

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating URL Categories

The `create()` method allows you to define new URL categories with proper error handling.

**Example: Creating a URL List Category**

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import URLCategories
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

url_categories = URLCategories(client)

try:
    category_data = {
        "name": "blocked_sites",
        "description": "Custom blocked URLs",
        "type": "URL List",
        "list": ["example.com", "test.com"],
        "folder": "Texas"
    }

    new_category = url_categories.create(category_data)
    print(f"Created category: {new_category.name}")

except NameNotUniqueError as e:
    print(f"Category name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid category data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting URL Categories

Use the `get()` method to retrieve a URL category by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    category_id = "123e4567-e89b-12d3-a456-426655440000"
    category = url_categories.get(category_id)
    print(f"Category Name: {category.name}")
    print(f"Type: {category.type}")
    print(f"URLs: {category.list}")

except NotFoundError as e:
    print(f"Category not found: {e.message}")
```

</div>

## Updating URL Categories

The `update()` method allows you to modify existing URL categories using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    # Fetch existing category as a Pydantic model
    blocked_sites = url_categories.fetch(folder='Texas', name='blocked_sites')

    # Update the model's attributes
    blocked_sites.description = "Updated blocked sites list"
    blocked_sites.list.append("newsite.com")

    # Push changes to the SCM API
    updated_category = url_categories.update(blocked_sites)
    print(f"Updated category: {updated_category.name}")
    print(f"New URL list: {updated_category.list}")

except NotFoundError as e:
    print(f"Category not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting URL Categories

Use the `delete()` method to remove a URL category.

<div class="termy">

<!-- termynal -->

```python
try:
    category_id = "123e4567-e89b-12d3-a456-426655440000"
    url_categories.delete(category_id)
    print("Category deleted successfully")

except NotFoundError as e:
    print(f"Category not found: {e.message}")
```

</div>

## Listing URL Categories

The `list()` method retrieves multiple URL categories with optional filtering. You can filter the results using the
following kwargs:

- `members`: List[str] - Filter by entries within a URL category list

<div class="termy">

<!-- termynal -->

```python
try:
    # List all categories in a folder
    categories = url_categories.list(folder="Texas")

    # List categories containing specific URLs
    filtered_categories = url_categories.list(
        folder="Texas",
        members=["example.com", "test.com"]
    )

    # Print the results
    for category in categories:
        print(f"Name: {category.name}")
        print(f"Type: {category.type}")
        print(f"URLs: {category.list}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching URL Categories

The `fetch()` method retrieves a single URL category by name from a specific container, returning a Pydantic model.

<div class="termy">

<!-- termynal -->

```python
try:
    # Fetch a category by name from a specific folder
    category = url_categories.fetch(
        name="blocked_sites",
        folder="Texas"
    )
    print(f"Found category: {category.name}")
    print(f"Current URL list: {category.list}")

except NotFoundError as e:
    print(f"Category not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a URL category with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import URLCategories
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"
    )

    # Initialize URL categories object
    url_categories = URLCategories(client)

    try:
        # Create new category
        category_data = {
            "name": "test_category",
            "description": "Test URL category",
            "type": "URL List",
            "list": ["example.com", "test.com"],
            "folder": "Texas"
        }

        new_category = url_categories.create(category_data)
        print(f"Created category: {new_category.name}")

        # Fetch and update the category
        try:
            fetched_category = url_categories.fetch(
                name="test_category",
                folder="Texas"
            )
            print(f"Found category: {fetched_category.name}")

            # Update the category using Pydantic model
            fetched_category.description = "Updated test category"
            fetched_category.list.append("newsite.com")

            updated_category = url_categories.update(fetched_category)
            print(f"Updated category: {updated_category.name}")
            print(f"New URL list: {updated_category.list}")

        except NotFoundError as e:
            print(f"Category not found: {e.message}")

        # Clean up
        url_categories.delete(new_category.id)
        print("Category deleted successfully")

    except NameNotUniqueError as e:
        print(f"Category name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid category data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Full script examples

Refer to the [examples](../../../../examples/scm/config/security) directory.

## Related Models

- [URLCategoriesCreateModel](../../models/security_services/url_categories_models.md#Overview)
- [URLCategoriesUpdateModel](../../models/security_services/url_categories_models.md#Overview)
- [URLCategoriesResponseModel](../../models/security_services/url_categories_models.md#Overview)