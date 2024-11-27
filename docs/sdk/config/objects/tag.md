# Tag Configuration Object

The `Tag` class provides functionality to manage tag objects in Palo Alto Networks' Strata Cloud Manager. Tags are used
to label and organize objects for easier management and policy application.

## Overview

Tags in Strata Cloud Manager allow you to:

- Create color-coded labels for objects
- Organize resources within folders, snippets, or devices
- Filter and search objects based on tags
- Apply consistent labeling across your infrastructure

The SDK provides comprehensive error handling and logging capabilities to help troubleshoot issues during tag
management.

## Methods

| Method     | Description                        |
|------------|------------------------------------|
| `create()` | Creates a new tag                  |
| `get()`    | Retrieves a tag by ID              |
| `update()` | Updates an existing tag            |
| `delete()` | Deletes a tag                      |
| `list()`   | Lists tags with optional filtering |
| `fetch()`  | Retrieves a single tag by name     |

## Exceptions

The SDK uses a hierarchical exception system for error handling:

### Client Errors (4xx)

- `InvalidObjectError`: Raised when tag data is invalid or for invalid response formats
- `MissingQueryParameterError`: Raised when required parameters (folder, name) are empty
- `NotFoundError`: Raised when a tag doesn't exist
- `AuthenticationError`: Raised for authentication failures
- `AuthorizationError`: Raised for permission issues
- `ConflictError`: Raised when tag names conflict
- `NameNotUniqueError`: Raised when creating duplicate tag names
- `ReferenceNotZeroError`: Raised when deleting tags still referenced by other objects

### Server Errors (5xx)

- `ServerError`: Base class for server-side errors
- `APINotImplementedError`: When API endpoint isn't implemented
- `GatewayTimeoutError`: When request times out

## Creating Tags

The `create()` method allows you to create new tags with proper error handling.

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Tag
from scm.exceptions import InvalidObjectError, NameNotUniqueError

# Initialize client with logging
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
    log_level="DEBUG"  # Enable detailed logging
)

tags = Tag(client)

try:
    tag_data = {
        "name": "Production",
        "color": "Red",
        "description": "Production environment resources",
        "folder": "Texas"
    }

    new_tag = tags.create(tag_data)
    print(f"Created tag: {new_tag.name}")

except NameNotUniqueError as e:
    print(f"Tag name already exists: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid tag data: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

</div>

## Getting Tags

Use the `get()` method to retrieve a tag by its ID.

<div class="termy">

<!-- termynal -->

```python
try:
    tag_id = "123e4567-e89b-12d3-a456-426655440000"
    tag = tags.get(tag_id)
    print(f"Tag Name: {tag.name}")
    print(f"Color: {tag.color}")

except NotFoundError as e:
    print(f"Tag not found: {e.message}")
```

</div>

## Updating Tags

The `update()` method allows you to modify existing tags using Pydantic models.

<div class="termy">

<!-- termynal -->

```python
try:
    # First fetch the existing tag as a Pydantic model
    tag = tags.fetch(name="Production", folder="Texas")

    # Update the tag's attributes
    tag.color = "Blue"
    tag.description = "Updated production tag"

    updated_tag = tags.update(tag)
    print(f"Updated tag: {updated_tag.name}")

except NotFoundError as e:
    print(f"Tag not found: {e.message}")
except InvalidObjectError as e:
    print(f"Invalid update data: {e.message}")
```

</div>

## Deleting Tags

Use the `delete()` method to remove a tag.

<div class="termy">

<!-- termynal -->

```python
try:
    tag_id = "123e4567-e89b-12d3-a456-426655440000"
    tags.delete(tag_id)
    print("Tag deleted successfully")

except NotFoundError as e:
    print(f"Tag not found: {e.message}")
except ReferenceNotZeroError as e:
    print(f"Tag still in use: {e.message}")
```

</div>

## Listing Tags

The `list()` method retrieves multiple tags with optional filtering. You can filter the results using the
following kwargs:

- `colors`: List[str] - Filter by tag colors (e.g., ['Red', 'Blue', 'Green'])

<div class="termy">

<!-- termynal -->

```python
try:
    # List all tags in a folder
    all_tags = tags.list(folder="Texas")

    # List tags with specific colors
    colored_tags = tags.list(
        folder="Texas",
        colors=['Red', 'Blue']
    )

    # Print the results
    for tag in all_tags:
        print(f"Name: {tag.name}, Color: {tag.color}")

except InvalidObjectError as e:
    print(f"Invalid filter parameters: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Fetching Tags

The `fetch()` method retrieves a single tag by name from a specific container, returning a Pydantic model.

<div class="termy">

<!-- termynal -->

```python
try:
    # Fetch a tag by name from a specific folder
    prod_tag = tags.fetch(
        name="Production",
        folder="Texas"
    )
    print(f"Found tag: {prod_tag.name}")
    print(f"Color: {prod_tag.color}")

except NotFoundError as e:
    print(f"Tag not found: {e.message}")
except MissingQueryParameterError as e:
    print(f"Missing required parameter: {e.message}")
```

</div>

## Full Workflow Example

Here's a complete example demonstrating the full lifecycle of a tag with proper error handling:

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.objects import Tag
from scm.exceptions import (
    InvalidObjectError,
    NotFoundError,
    AuthenticationError,
    NameNotUniqueError,
    ReferenceNotZeroError
)

try:
    # Initialize client with debug logging
    client = Scm(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id",
        log_level="DEBUG"
    )

    # Initialize tag object
    tags = Tag(client)

    try:
        # Create new tag
        create_data = {
            "name": "test_tag",
            "color": "Blue",
            "description": "Test tag",
            "folder": "Texas"
        }

        new_tag = tags.create(create_data)
        print(f"Created tag: {new_tag.name}")

        # Fetch and update the tag
        try:
            fetched_tag = tags.fetch(
                name="test_tag",
                folder="Texas"
            )
            print(f"Found tag: {fetched_tag.name}")

            # Update the tag using Pydantic model
            fetched_tag.description = "Updated test tag"
            updated_tag = tags.update(fetched_tag)
            print(f"Updated description: {updated_tag.description}")

        except NotFoundError as e:
            print(f"Tag not found: {e.message}")

        # Clean up
        try:
            tags.delete(new_tag.id)
            print("Tag deleted successfully")
        except ReferenceNotZeroError as e:
            print(f"Cannot delete tag - still in use: {e.message}")

    except NameNotUniqueError as e:
        print(f"Tag name conflict: {e.message}")
    except InvalidObjectError as e:
        print(f"Invalid tag data: {e.message}")
        if e.details:
            print(f"Details: {e.details}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Status code: {e.http_status_code}")
```

</div>

## Related Models

- [TagCreateModel](../../models/objects/tag_models.md#Overview)
- [TagUpdateModel](../../models/objects/tag_models.md#Overview)
- [TagResponseModel](../../models/objects/tag_models.md#Overview)