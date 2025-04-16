# Snippet Configuration Object

## Table of Contents

1. [Overview](#overview)
2. [Core Methods](#core-methods)
3. [Snippet Model Attributes](#snippet-model-attributes)
4. [Exceptions](#exceptions)
5. [Basic Configuration](#basic-configuration)
6. [Usage Examples](#usage-examples)
    - [Creating Snippets](#creating-snippets)
    - [Retrieving Snippets](#retrieving-snippets)
    - [Updating Snippets](#updating-snippets)
    - [Listing Snippets](#listing-snippets)
    - [Filtering Responses](#filtering-responses)
    - [Deleting Snippets](#deleting-snippets)
7. [Folder Associations](#folder-associations)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [Full Script Examples](#full-script-examples)
11. [Related Models](#related-models)

## Overview

The `Snippet` class provides functionality to manage snippet objects in Palo Alto Networks' Strata Cloud Manager. This
class inherits from `BaseObject` and provides methods for creating, retrieving, updating, and deleting snippet objects,
which are used to store reusable configuration elements.

## Core Methods

| Method                  | Description                           | Parameters                           | Return Type                      |
|-------------------------|---------------------------------------|--------------------------------------|----------------------------------|
| `create()`              | Creates a new snippet                 | `name: str`, etc.                    | `SnippetResponseModel`           |
| `get()`                 | Retrieves a snippet by ID             | `object_id: Union[str, UUID]`        | `SnippetResponseModel`           |
| `update()`              | Updates an existing snippet           | `snippet_id: Union[str, UUID]`, etc. | `SnippetResponseModel`           |
| `delete()`              | Deletes a snippet                     | `object_id: Union[str, UUID]`        | `None`                           |
| `list()`                | Lists snippets with filtering         | `name: str`, etc.                    | `List[SnippetResponseModel]`     |
| `fetch()`               | Gets a snippet by its name            | `name: str`                          | `Optional[SnippetResponseModel]` |
| `associate_folder()`    | Associates a snippet with a folder    | `snippet_id`, `folder_id`            | `SnippetResponseModel`           |
| `disassociate_folder()` | Disassociates a snippet from a folder | `snippet_id`, `folder_id`            | `SnippetResponseModel`           |

## Snippet Model Attributes

| Attribute       | Type                | Required | Description                                     |
|-----------------|---------------------|----------|-------------------------------------------------|
| `name`          | str                 | Yes      | Name of the snippet                             |
| `id`            | UUID                | Yes*     | Unique identifier (*response only)              |
| `description`   | Optional[str]       | No       | Optional description of the snippet             |
| `labels`        | Optional[List[str]] | No       | Optional list of labels to apply to the snippet |
| `enable_prefix` | bool                | No       | Whether to enable prefix for this snippet       |

## Exceptions

The Snippet class can raise the following exceptions:

- `APIError`: Base class for all API-related errors
- `InvalidObjectError`: Raised when an invalid object or parameter is provided
- `ObjectNotPresentError`: Raised when a requested snippet does not exist
- `NotImplementedError`: Raised when trying to use unimplemented folder association functionality

## Basic Configuration

```python
from scm.client import Scm
from scm.config.setup import Snippet

# Initialize client
client = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

## Usage Examples

### Creating Snippets

```python
# Create a basic snippet
snippet = client.snippet.create(
    name="Security Policy Snippet",
    description="Common security policy configurations"
)
print(f"Created snippet: {snippet.name} (ID: {snippet.id})")

# Create a snippet with all optional parameters
detailed_snippet = client.snippet.create(
    name="Network Config Snippet",
    description="Network configuration template",
    labels=["network", "template"],
    enable_prefix=True
)
print(f"Created detailed snippet: {detailed_snippet.name}")
```

### Retrieving Snippets

```python
# Get a snippet by ID
snippet_id = "12345678-1234-1234-1234-123456789012"
snippet = client.snippet.get(object_id=snippet_id)
print(f"Retrieved snippet: {snippet.name}")

# Fetch a snippet by name
snippet_by_name = client.snippet.fetch(name="Security Policy Snippet")
if snippet_by_name:
    print(f"Found snippet with ID: {snippet_by_name.id}")
else:
    print("Snippet not found")
```

### Updating Snippets

```python
# Update a snippet
updated_snippet = client.snippet.update(
    snippet_id="12345678-1234-1234-1234-123456789012",
    name="Updated Security Policy",
    description="Updated security policy configurations",
    labels=["security", "updated"]
)
print(f"Updated snippet: {updated_snippet.name}")

# Update only specific fields
partial_update = client.snippet.update(
    snippet_id="12345678-1234-1234-1234-123456789012",
    description="New description only"
)
print(f"Partially updated snippet: {partial_update.name}")
```

### Listing Snippets

```python
# List all snippets
all_snippets = client.snippet.list()
print(f"Found {len(all_snippets)} snippets")

# List snippets with pagination
paginated_snippets = client.snippet.list(offset=10, limit=5)
print(f"Page of snippets: {len(paginated_snippets)}")
```

### Filtering Responses

```python
# Filter by name
filtered_snippets = client.snippet.list(name="Security")
print(f"Found {len(filtered_snippets)} snippets with 'Security' in the name")

# Exact match filter
exact_snippets = client.snippet.list(name="Network Config Snippet", exact_match=True)
print(f"Found {len(exact_snippets)} snippets with exact name match")

# Filter by type
type_snippets = client.snippet.list(type="predefined")
print(f"Found {len(type_snippets)} predefined snippets")
```

### Deleting Snippets

```python
# Delete a snippet
client.snippet.delete(object_id="12345678-1234-1234-1234-123456789012")
print("Snippet deleted successfully")

try:
    # Verify deletion
    client.snippet.get(object_id="12345678-1234-1234-1234-123456789012")
except ObjectNotPresentError:
    print("Snippet was successfully deleted")
```

## Folder Associations

The API supports associating snippets with folders, although this functionality is currently in development:

```python
try:
    # Associate a snippet with a folder
    snippet_id = "12345678-1234-1234-1234-123456789012"
    folder_id = "87654321-4321-4321-4321-210987654321"
    
    updated_snippet = client.snippet.associate_folder(
        snippet_id=snippet_id,
        folder_id=folder_id
    )
    print(f"Associated snippet {snippet_id} with folder {folder_id}")
    
    # Disassociate a snippet from a folder
    result = client.snippet.disassociate_folder(
        snippet_id=snippet_id,
        folder_id=folder_id
    )
    print(f"Disassociated snippet from folder")
except NotImplementedError as e:
    print(f"Folder association not yet implemented: {e}")
```

## Error Handling

```python
from scm.exceptions import APIError, InvalidObjectError, ObjectNotPresentError

try:
    # Attempt to get a non-existent snippet
    non_existent = client.snippet.get("00000000-0000-0000-0000-000000000000")
except ObjectNotPresentError:
    print("Snippet does not exist")
except APIError as e:
    print(f"API error occurred: {str(e)}")

try:
    # Attempt to create with invalid data
    invalid_snippet = client.snippet.create(name="")
except InvalidObjectError as e:
    print(f"Invalid data: {str(e)}")
```

## Best Practices

1. **Error Handling**: Always wrap API calls in try-except blocks to handle potential exceptions
2. **Pagination**: Use pagination parameters (`offset` and `limit`) when working with large datasets
3. **Validation**: Ensure that data meets the requirements before attempting to create or update snippets
4. **Naming**: Use consistent naming conventions for snippets to make them easier to find and manage

## Full Script Examples

### Creating and Managing Snippets

```python
from scm.client import Scm
from scm.exceptions import APIError, ObjectNotPresentError

def manage_snippets():
    try:
        # Initialize client
        client = Scm(
            client_id="your_client_id",
            client_secret="your_client_secret"
        )
        
        # Create a new snippet
        snippet = client.snippet.create(
            name="Configuration Template",
            description="Base configuration template",
            labels=["template", "base"],
            enable_prefix=True
        )
        print(f"Created snippet with ID: {snippet.id}")
        
        # Update the snippet
        updated = client.snippet.update(
            snippet_id=snippet.id,
            description="Updated base configuration template",
            labels=["template", "base", "updated"]
        )
        print(f"Updated snippet: {updated.name}")
        
        # List all snippets
        snippets = client.snippet.list()
        print(f"Available snippets:")
        for s in snippets:
            print(f"- {s.name} (ID: {s.id})")
        
        # Delete the snippet
        client.snippet.delete(snippet.id)
        print(f"Deleted snippet {snippet.id}")
        
    except ObjectNotPresentError as e:
        print(f"Object not found: {str(e)}")
    except APIError as e:
        print(f"API error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    manage_snippets()
```

## Related Models

- [SnippetResponseModel](../models/setup/snippet_models.md) - The model used for snippet responses
